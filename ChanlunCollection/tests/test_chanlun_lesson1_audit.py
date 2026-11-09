import copy
import json
import runpy
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
verify=runpy.run_path(str(ROOT/"tools/verify_chanlun_lesson1_analysis.py"))["verify"]

def fixtures():
    index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    evidence=json.loads((ROOT/"knowledge/evidence/chanlun_lesson001.json").read_text(encoding="utf-8"))
    report=(ROOT/"analyses/books/chanlun/chapters/lesson_001.md").read_text(encoding="utf-8")
    return index,evidence,report

class LessonOneEvidenceAuditTests(unittest.TestCase):
    def test_current_analysis_is_source_consistent(self):
        index,evidence,report=fixtures()
        self.assertGreaterEqual(verify(index,evidence,report),8)

    def test_reject_changed_source_sha(self):
        index,evidence,report=fixtures()
        evidence["source"]["sha256"]="unrelated"
        with self.assertRaises(AssertionError):
            verify(index,evidence,report)

    def test_reject_unverified_hypothesis_mislabel(self):
        index,evidence,report=fixtures()
        h=next(x for x in evidence["claims"] if x["kind"]=="HYPOTHESIS")
        h["test_status"]="verified"
        with self.assertRaises(AssertionError):
            verify(index,evidence,report)

    def test_reject_claim_page_outside_source(self):
        index,evidence,report=fixtures()
        evidence["claims"][0]["pages"]=[6]
        with self.assertRaises(AssertionError):
            verify(index,evidence,report)

    def test_reject_missing_seventh_layer(self):
        index,evidence,report=fixtures()
        with self.assertRaises(AssertionError):
            verify(index,evidence,report.replace("第七重","自由探索"))

if __name__=="__main__":
    unittest.main()
