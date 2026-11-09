import json,runpy,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
validate=runpy.run_path(str(R/"tools/verify_chanlun_lessons096_100.py"))["validate"]
def setup():
    idx=json.loads((R/"catalog/chanlun_lesson_index.json").read_text(encoding="utf8"))
    source=json.loads((R/"catalog/chanlun_lessons096_100_source_layers.json").read_text(encoding="utf8"))
    claims=[json.loads((R/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf8")) for n in range(96,101)]
    reports=[(R/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf8") for n in range(96,101)]
    syn=(R/"analyses/books/chanlun/volumes/LESSONS_096_100_SYNTHESIS.md").read_text(encoding="utf8")
    graph=json.loads((R/"knowledge/claims/chanlun_lessons096_100_semantic_dependencies.json").read_text(encoding="utf8"))
    old=[json.loads((R/p).read_text(encoding="utf8")) for p in (
      "knowledge/claims/chanlun_early_core_dependencies.json",
      "knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json",
      "knowledge/claims/chanlun_lessons071_075_semantic_dependencies.json",
      "knowledge/claims/chanlun_lessons076_080_semantic_dependencies.json",
      "knowledge/claims/chanlun_lessons081_085_semantic_dependencies.json",
      "knowledge/claims/chanlun_lessons086_090_crossvolume_dependencies.json",
      "knowledge/claims/chanlun_lessons091_095_semantic_dependencies.json")]
    hashes={v["volume"]:v["sha256"] for v in idx["volumes"]}
    return [idx,source,claims,reports,syn,graph,old,hashes]
class SourceTests(unittest.TestCase):
 def test_good(self):self.assertEqual(validate(*setup())["typed_claims"],35)
 def test_wrong_sha(self):
  x=setup();x[-1][5]="bad"
  with self.assertRaises(AssertionError):validate(*x)
 def test_wrong_page(self):
  x=setup();x[2][4]["claims"][0]["pdf_pages"]=[300]
  with self.assertRaises(AssertionError):validate(*x)
 def test_claimed_visual_exaggeration(self):
  x=setup();x[2][1]["quality"]["actually_inspected_pages"]=[173]
  with self.assertRaises(AssertionError):validate(*x)
 def test_full_chart_numbers_not_verified(self):
  x=setup();x[1]["visual"]["all_fine_numeric_labels_verified"]=True
  with self.assertRaises(AssertionError):validate(*x)
 def test_explicit_editor_disagreement_required(self):
  x=setup();x[1]["role_flags"]=[z for z in x[1]["role_flags"] if z["kind"]!="EDITORIAL_COUNTEREXAMPLE"]
  with self.assertRaises(AssertionError):validate(*x)
 def test_further_source_chronology(self):
  x=setup();x[1]["role_flags"]=[z for z in x[1]["role_flags"] if z["lesson"]!=96]
  with self.assertRaises(AssertionError):validate(*x)
 def test_no_hypothesis_proven(self):
  x=setup();next(z for z in x[2][3]["claims"] if z["kind"]=="HYPOTHESIS")["test_status"]="proven"
  with self.assertRaises(AssertionError):validate(*x)
 def test_old_graph_intact(self):
  x=setup();x[6][0]["source_pdf_sha256_by_volume"]["5"]=x[-1][5]
  with self.assertRaises(AssertionError):validate(*x)
 def test_graph_target_exists(self):
  x=setup();x[5]["edges"][0]["to"]="MISSING"
  with self.assertRaises(AssertionError):validate(*x)
 def test_100_requires_dispute_text(self):
  x=setup();x[3][4]=x[3][4].replace("娇注","注")
  with self.assertRaises(AssertionError):validate(*x)
 def test_not_a_real_market_backtest(self):
  x=setup();x[2][0]["real_market_backtest"]="passed"
  with self.assertRaises(AssertionError):validate(*x)
 def test_seven_lenses(self):
  x=setup();x[3][2]=x[3][2].replace("第七重","尾声")
  with self.assertRaises(AssertionError):validate(*x)
if __name__=="__main__":unittest.main()
