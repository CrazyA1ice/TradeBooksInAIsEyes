import json,runpy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
audit=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons026_030.py"))["audit"]
def fixtures():
    i=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    s=json.loads((ROOT/"catalog/chanlun_lessons026_030_source_layers.json").read_text(encoding="utf-8"))
    e=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(26,31)]
    m=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(26,31)]
    o=(ROOT/"analyses/books/chanlun/volumes/LESSONS_026_030_SYNTHESIS.md").read_text(encoding="utf-8")
    return [i,s,e,m,o,i["volumes"][1]["sha256"]]
class SourceAudit(unittest.TestCase):
    def test_valid(self):self.assertEqual(audit(*fixtures())["pages"],123)
    def test_source_sha_tamper(self):
        x=fixtures();x[-1]="bad"
        with self.assertRaises(AssertionError):audit(*x)
    def test_source_page_removed(self):
        x=fixtures();x[1]["lessons"][0]["pages"].pop()
        with self.assertRaises(AssertionError):audit(*x)
    def test_claim_wrong_page(self):
        x=fixtures();x[2][1]["claims"][0]["pdf_pages"]=[999]
        with self.assertRaises(AssertionError):audit(*x)
    def test_hypothesis_overclaim(self):
        x=fixtures();next(c for c in x[2][3]["claims"] if c["kind"]=="HYPOTHESIS")["test_status"]="proved"
        with self.assertRaises(AssertionError):audit(*x)
    def test_duplicate_id(self):
        x=fixtures();x[2][1]["claims"][0]["id"]=x[2][0]["claims"][0]["id"]
        with self.assertRaises(AssertionError):audit(*x)
    def test_image_metadata_omission(self):
        x=fixtures();x[2][1]["quality"]["image_pages"]=[]
        with self.assertRaises(AssertionError):audit(*x)
    def test_missing_seventh_layer(self):
        x=fixtures();x[3][4]=x[3][4].replace("第七重","其他结论")
        with self.assertRaises(AssertionError):audit(*x)
if __name__=="__main__":unittest.main()
