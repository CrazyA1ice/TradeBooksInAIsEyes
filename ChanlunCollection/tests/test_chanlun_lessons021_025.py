import json
import runpy
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
audit=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons021_025.py"))["audit"]
def inputs():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    src=json.loads((ROOT/"catalog/chanlun_lessons021_025_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(21,26)]
    report=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(21,26)]
    synth=(ROOT/"analyses/books/chanlun/volumes/LESSONS_021_025_SYNTHESIS.md").read_text(encoding="utf-8")
    sha={v["volume"]:v["sha256"] for v in idx["volumes"][:2]}
    return [idx,src,ev,report,synth,sha]
class SourceTests(unittest.TestCase):
    def test_valid(self):self.assertEqual(audit(*inputs())["claim_ids"],31)
    def test_reject_bad_vol1_fingerprint(self):
        x=inputs();x[5][1]="wrong"
        with self.assertRaises(AssertionError):audit(*x)
    def test_reject_bad_vol2_fingerprint(self):
        x=inputs();x[5][2]="wrong"
        with self.assertRaises(AssertionError):audit(*x)
    def test_reject_volume_mislabel(self):
        x=inputs();x[2][3]["source"]["volume"]=1
        with self.assertRaises(AssertionError):audit(*x)
    def test_reject_crossvolume_page(self):
        x=inputs();x[2][3]["claims"][0]["pdf_pages"]=[253]
        with self.assertRaises(AssertionError):audit(*x)
    def test_reject_hypothesis_overclaim(self):
        x=inputs();next(c for c in x[2][3]["claims"] if c["kind"]=="HYPOTHESIS")["test_status"]="tested"
        with self.assertRaises(AssertionError):audit(*x)
    def test_reject_missing_seventh_layer(self):
        x=inputs();x[3][4]=x[3][4].replace("第七重","自由写作")
        with self.assertRaises(AssertionError):audit(*x)
    def test_reject_image_omission(self):
        x=inputs();x[2][4]["page_audit"]["image_pages"]=[]
        with self.assertRaises(AssertionError):audit(*x)
    def test_reject_duplicate_claim(self):
        x=inputs();x[2][1]["claims"][0]["id"]=x[2][0]["claims"][0]["id"]
        with self.assertRaises(AssertionError):audit(*x)
if __name__=="__main__":unittest.main()
