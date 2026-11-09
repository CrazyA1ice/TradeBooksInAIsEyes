import json,runpy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
audit=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons046_050.py"))["audit"]
def fixtures():
    i=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    s=json.loads((ROOT/"catalog/chanlun_lessons046_050_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(46,51)]
    r=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(46,51)]
    summary=(ROOT/"analyses/books/chanlun/volumes/LESSONS_046_050_SYNTHESIS.md").read_text(encoding="utf-8")
    graph=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    hashes={v["volume"]:v["sha256"] for v in i["volumes"][:3]}
    return [i,s,ev,r,summary,graph,hashes]
class Verify(unittest.TestCase):
 def test_valid(self):self.assertEqual(audit(*fixtures())["claims"],36)
 def test_tampered_source_sha(self):
  x=fixtures();x[-1][3]="WRONG"
  with self.assertRaises(AssertionError):audit(*x)
 def test_wrong_page(self):
  x=fixtures();x[2][1]["claims"][0]["pdf_pages"]=[999]
  with self.assertRaises(AssertionError):audit(*x)
 def test_mislabeled_volume(self):
  x=fixtures();x[2][0]["source"]["volume"]=2
  with self.assertRaises(AssertionError):audit(*x)
 def test_hypothesis_not_proven(self):
  x=fixtures();next(c for c in x[2][4]["claims"] if c["kind"]=="HYPOTHESIS")["test_status"]="passed"
  with self.assertRaises(AssertionError):audit(*x)
 def test_image_page_not_omitted(self):
  x=fixtures();x[2][0]["quality"]["image_pages"]=[]
  with self.assertRaises(AssertionError):audit(*x)
 def test_required_lens(self):
  x=fixtures();x[3][4]=x[3][4].replace("第七重","随笔")
  with self.assertRaises(AssertionError):audit(*x)
 def test_duplicate_claims_rejected(self):
  x=fixtures();x[2][1]["claims"][0]["id"]=x[2][0]["claims"][0]["id"]
  with self.assertRaises(AssertionError):audit(*x)
 def test_graph_bad_target(self):
  x=fixtures();x[5]["edges"][0]["to"]="MISSING"
  with self.assertRaises(AssertionError):audit(*x)
 def test_missing_objective_node(self):
  x=fixtures();x[5]["nodes"]=[z for z in x[5]["nodes"] if z["id"]!="L49-PROFIT-OPTIMUM"]
  with self.assertRaises(AssertionError):audit(*x)
if __name__=="__main__":unittest.main()
