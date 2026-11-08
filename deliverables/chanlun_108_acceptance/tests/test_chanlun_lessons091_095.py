import json,runpy,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
validate=runpy.run_path(str(R/"tools/verify_chanlun_lessons091_095.py"))["validate"]
def data():
    i=json.loads((R/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    s=json.loads((R/"catalog/chanlun_lessons091_095_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((R/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(91,96)]
    md=[(R/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(91,96)]
    syn=(R/"analyses/books/chanlun/volumes/LESSONS_091_095_SYNTHESIS.md").read_text(encoding="utf-8")
    new=json.loads((R/"knowledge/claims/chanlun_lessons091_095_semantic_dependencies.json").read_text(encoding="utf-8"))
    olds=[json.loads((R/p).read_text(encoding="utf-8")) for p in (
        "knowledge/claims/chanlun_early_core_dependencies.json",
        "knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json",
        "knowledge/claims/chanlun_lessons071_075_semantic_dependencies.json",
        "knowledge/claims/chanlun_lessons076_080_semantic_dependencies.json",
        "knowledge/claims/chanlun_lessons081_085_semantic_dependencies.json",
        "knowledge/claims/chanlun_lessons086_090_crossvolume_dependencies.json")]
    hashes={v["volume"]:v["sha256"] for v in i["volumes"]}
    return [i,s,ev,md,syn,new,olds,hashes]
class Evidence(unittest.TestCase):
 def test_valid(self):self.assertEqual(validate(*data())["claims"],35)
 def test_source_sha_mismatch(self):
  x=data();x[-1][5]="bad"
  with self.assertRaises(AssertionError):validate(*x)
 def test_first_page_and_last_page(self):self.assertEqual([data()[1]["lessons"][0]["start"],data()[1]["lessons"][-1]["end"]],[64,154])
 def test_bad_page(self):
  x=data();x[2][0]["claims"][0]["pdf_pages"]=[40]
  with self.assertRaises(AssertionError):validate(*x)
 def test_exaggerated_visual(self):
  x=data();x[2][0]["quality"]["visually_inspected_pages"]=[65,72]
  with self.assertRaises(AssertionError):validate(*x)
 def test_precise_chart_values_not_verified(self):
  x=data();x[1]["visual"]["precise_price_labels_verified"]=True
  with self.assertRaises(AssertionError):validate(*x)
 def test_past_later_post(self):
  x=data();x[1]["provenance"]=[z for z in x[1]["provenance"] if z["lesson"]!=95]
  with self.assertRaises(AssertionError):validate(*x)
 def test_editor_in_93(self):
  x=data();x[1]["provenance"]=[z for z in x[1]["provenance"] if z["role"]!="EDITORIAL_EXPANSION"]
  with self.assertRaises(AssertionError):validate(*x)
 def test_91_state_report(self):
  x=data();x[3][0]=x[3][0].replace("四态","四个")
  with self.assertRaises(AssertionError):validate(*x)
 def test_hypotheses_not_tested(self):
  x=data();next(z for z in x[2][3]["claims"] if z["kind"]=="HYPOTHESIS")["test_status"]="proven"
  with self.assertRaises(AssertionError):validate(*x)
 def test_unknown_graph_target(self):
  x=data();x[5]["edges"][0]["to"]="MISSING"
  with self.assertRaises(AssertionError):validate(*x)
 def test_old_graph_not_modified(self):
  x=data();x[6][0]["source_pdf_sha256_by_volume"]["5"]=x[-1][5]
  with self.assertRaises(AssertionError):validate(*x)
 def test_market_honesty(self):
  x=data();x[2][4]["market_backtest"]="passed"
  with self.assertRaises(AssertionError):validate(*x)
 def test_seven_lenses(self):
  x=data();x[3][3]=x[3][3].replace("第七重","附录")
  with self.assertRaises(AssertionError):validate(*x)
if __name__=="__main__":unittest.main()
