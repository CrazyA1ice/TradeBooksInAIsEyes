import json
import runpy
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
verify=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons002_005.py"))["verify"]
def fixtures():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{i:03d}.json").read_text(encoding="utf-8")) for i in range(2,6)]
    reports=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{i:03d}.md").read_text(encoding="utf-8") for i in range(2,6)]
    graph=json.loads((ROOT/"knowledge/relations/chanlun_lessons001_005.json").read_text(encoding="utf-8"))
    synthesis=(ROOT/"analyses/books/chanlun/volumes/LESSONS_001_005_SYNTHESIS.md").read_text(encoding="utf-8")
    return [idx,ev,reports,graph,synthesis,idx["volumes"][0]["sha256"]]
class TestSourceAudit(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(verify(*fixtures())["lessons"],4)
    def test_wrong_sha(self):
        a=fixtures();a[-1]="wrong"
        with self.assertRaises(AssertionError):verify(*a)
    def test_claim_outside_page(self):
        a=fixtures();a[1][0]["claims"][0]["pages"]=[999]
        with self.assertRaises(AssertionError):verify(*a)
    def test_false_hypothesis_status(self):
        a=fixtures();next(x for x in a[1][0]["claims"] if x["kind"]=="HYPOTHESIS")["test_status"]="tested"
        with self.assertRaises(AssertionError):verify(*a)
    def test_invalid_claim_type(self):
        a=fixtures();a[1][0]["claims"][0]["kind"]="EVERYTHING_PROVEN"
        with self.assertRaises(AssertionError):verify(*a)
    def test_image_overclaim(self):
        a=fixtures();a[1][2]["page_audit"][1]["image_semantics_verified"]=True
        with self.assertRaises(AssertionError):verify(*a)
    def test_missing_layer(self):
        a=fixtures();a[2][1]=a[2][1].replace("第七重","结束")
        with self.assertRaises(AssertionError):verify(*a)
    def test_invalid_relation(self):
        a=fixtures();a[3]["edges"][0]["to"]="L999"
        with self.assertRaises(AssertionError):verify(*a)
if __name__=="__main__":unittest.main()
