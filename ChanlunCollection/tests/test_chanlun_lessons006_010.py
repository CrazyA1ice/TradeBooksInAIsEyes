import copy
import json
import runpy
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
audit=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons006_010.py"))["audit"]
def fixtures():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    layers=json.loads((ROOT/"catalog/chanlun_lessons006_010_layers.json").read_text(encoding="utf-8"))
    evidence=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{i:03d}.json").read_text(encoding="utf-8")) for i in range(6,11)]
    reports=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{i:03d}.md").read_text(encoding="utf-8") for i in range(6,11)]
    overview=(ROOT/"analyses/books/chanlun/volumes/LESSONS_001_010_SYNTHESIS.md").read_text(encoding="utf-8")
    return [idx,layers,evidence,reports,overview,idx["volumes"][0]["sha256"]]
class SourceAuditTests(unittest.TestCase):
    def test_valid_documents(self):
        self.assertEqual(audit(*fixtures())["pages"],69)
    def test_source_fingerprint_mismatch_fails(self):
        a=fixtures();a[-1]="wrong"
        with self.assertRaises(AssertionError):audit(*a)
    def test_claim_page_outside_lesson_fails(self):
        a=fixtures();a[2][0]["claims"][0]["pdf_pages"]=[99]
        with self.assertRaises(AssertionError):audit(*a)
    def test_mislabeled_hypothesis_fails(self):
        a=fixtures()
        next(x for x in a[2][3]["claims"] if x["kind"]=="HYPOTHESIS")["test_status"]="passed"
        with self.assertRaises(AssertionError):audit(*a)
    def test_invalid_type_fails(self):
        a=fixtures();a[2][1]["claims"][0]["kind"]="TRUE_ALWAYS"
        with self.assertRaises(AssertionError):audit(*a)
    def test_missing_layer_fails(self):
        a=fixtures();a[3][0]=a[3][0].replace("第七重","随笔")
        with self.assertRaises(AssertionError):audit(*a)
    def test_undisclosed_image_page_fails(self):
        a=fixtures();a[2][3]["source_quality"]["image_pages"]=[]
        with self.assertRaises(AssertionError):audit(*a)
    def test_altered_source_layer_counts_fail(self):
        a=fixtures();a[1]["lessons"][0]["pages"][0]["native_text_characters"]+=1
        with self.assertRaises(AssertionError):audit(*a)
    def test_duplicate_claim_id_fails(self):
        a=fixtures();a[2][1]["claims"][0]["id"]=a[2][0]["claims"][0]["id"]
        with self.assertRaises(AssertionError):audit(*a)
if __name__=="__main__":unittest.main()
