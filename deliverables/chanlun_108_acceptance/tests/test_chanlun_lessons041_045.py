import json,runpy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
audit=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons041_045.py"))["audit"]
def fixture():
    i=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    s=json.loads((ROOT/"catalog/chanlun_lessons041_045_source_layers.json").read_text(encoding="utf-8"))
    e=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(41,46)]
    m=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(41,46)]
    o=(ROOT/"analyses/books/chanlun/volumes/LESSONS_041_045_SYNTHESIS.md").read_text(encoding="utf-8")
    g=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    h={v["volume"]:v["sha256"] for v in i["volumes"][:3]}
    return [i,s,e,m,o,g,h]
class CrossVolume(unittest.TestCase):
 def test_valid_claims(self):self.assertEqual(audit(*fixture())["claims"],35)
 def test_wrong_third_volume_sha(self):
  x=fixture();x[-1][3]="wrong"
  with self.assertRaises(AssertionError):audit(*x)
 def test_wrong_second_volume_sha(self):
  x=fixture();x[-1][2]="wrong"
  with self.assertRaises(AssertionError):audit(*x)
 def test_crossvolume_reference_rejected(self):
  x=fixture();x[2][2]["claims"][0]["pdf_pages"]=[390]
  with self.assertRaises(AssertionError):audit(*x)
 def test_wrong_volume_number_rejected(self):
  x=fixture();x[2][3]["source"]["volume"]=2
  with self.assertRaises(AssertionError):audit(*x)
 def test_missing_img_metadata_rejected(self):
  x=fixture();x[2][3]["quality"]["image_pages"]=[]
  with self.assertRaises(AssertionError):audit(*x)
 def test_hypothesis_does_not_claim_confirmed(self):
  x=fixture();next(k for k in x[2][3]["claims"] if k["kind"]=="HYPOTHESIS")["test_status"]="proved"
  with self.assertRaises(AssertionError):audit(*x)
 def test_seventh_lens_required(self):
  x=fixture();x[3][4]=x[3][4].replace("第七重","随笔")
  with self.assertRaises(AssertionError):audit(*x)
 def test_missing_necessity_node_fails(self):
  x=fixture();x[5]["nodes"]=[n for n in x[5]["nodes"] if n["id"]!="L44-NECESSARY-NOT-SUFFICIENT"]
  with self.assertRaises(AssertionError):audit(*x)
 def test_all_volume_boundaries(self):self.assertEqual(audit(*fixture())["volumes"],[2,3])
if __name__=="__main__":unittest.main()
