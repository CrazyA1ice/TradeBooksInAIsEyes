import json
import runpy
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
verify=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons011_015.py"))["verify"]
def fixtures():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    source=json.loads((ROOT/"catalog/chanlun_lessons011_015_source_layers.json").read_text(encoding="utf-8"))
    evidence=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(11,16)]
    chapters=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(11,16)]
    synthesis=(ROOT/"analyses/books/chanlun/volumes/LESSONS_011_015_SYNTHESIS.md").read_text(encoding="utf-8")
    return [idx,source,evidence,chapters,synthesis,idx["volumes"][0]["sha256"]]
class ReviewAuditTests(unittest.TestCase):
    def test_all_5_lessons_source_consistent(self):
        self.assertEqual(verify(*fixtures())["pages"],87)
    def test_version_mismatch_rejected(self):
        a=fixtures();a[-1]="wrong";self.assertRaises(AssertionError,verify,*a)
    def test_invalid_claim_page_rejected(self):
        a=fixtures();a[2][0]["claims"][0]["pdf_pages"]=[1];self.assertRaises(AssertionError,verify,*a)
    def test_hypothesis_overclaim_rejected(self):
        a=fixtures();next(x for x in a[2][1]["claims"] if x["kind"]=="HYPOTHESIS")["test_status"]="success"
        self.assertRaises(AssertionError,verify,*a)
    def test_missing_page_rejected(self):
        a=fixtures();a[1]["lessons"][0]["pages"].pop();self.assertRaises(AssertionError,verify,*a)
    def test_image_omission_rejected(self):
        a=fixtures();a[2][3]["quality"]["pages_with_images"]=[]
        self.assertRaises(AssertionError,verify,*a)
    def test_later_definition_note_required(self):
        a=fixtures();a[3][4]=a[3][4].replace("后期","新版")
        self.assertRaises(AssertionError,verify,*a)
    def test_duplicate_claim_rejected(self):
        a=fixtures();a[2][1]["claims"][0]["id"]=a[2][0]["claims"][0]["id"]
        self.assertRaises(AssertionError,verify,*a)
if __name__=="__main__":unittest.main()
