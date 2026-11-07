import json
import runpy
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
audit=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons016_020.py"))["audit"]
def data():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    source=json.loads((ROOT/"catalog/chanlun_lessons016_020_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{i:03d}.json").read_text(encoding="utf-8")) for i in range(16,21)]
    report=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{i:03d}.md").read_text(encoding="utf-8") for i in range(16,21)]
    overview=(ROOT/"analyses/books/chanlun/volumes/LESSONS_016_020_SYNTHESIS.md").read_text(encoding="utf-8")
    return [idx,source,ev,report,overview,idx["volumes"][0]["sha256"]]
class EvidenceAudit(unittest.TestCase):
    def test_accepted(self):self.assertEqual(audit(*data())["claims"],32)
    def test_wrong_pdf_sha_rejected(self):
        x=data();x[-1]="wrong"
        with self.assertRaises(AssertionError):audit(*x)
    def test_missing_page_rejected(self):
        x=data();x[1]["lessons"][0]["pages"].pop()
        with self.assertRaises(AssertionError):audit(*x)
    def test_wrong_page_claim_rejected(self):
        x=data();x[2][0]["claims"][0]["pdf_pages"]=[800]
        with self.assertRaises(AssertionError):audit(*x)
    def test_duplicate_id_rejected(self):
        x=data();x[2][1]["claims"][0]["id"]=x[2][0]["claims"][0]["id"]
        with self.assertRaises(AssertionError):audit(*x)
    def test_image_omission_rejected(self):
        x=data();x[2][1]["audit"]["image_pages"]=[]
        with self.assertRaises(AssertionError):audit(*x)
    def test_hypothesis_fabrication_rejected(self):
        x=data()
        next(c for c in x[2][4]["claims"] if c["kind"]=="HYPOTHESIS")["status"]="verified"
        with self.assertRaises(AssertionError):audit(*x)
    def test_seventh_layer_missing_rejected(self):
        x=data();x[3][4]=x[3][4].replace("第七重","自由评论")
        with self.assertRaises(AssertionError):audit(*x)
if __name__=="__main__":unittest.main()
