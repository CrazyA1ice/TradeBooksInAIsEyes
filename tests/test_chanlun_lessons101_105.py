import json,runpy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
f=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons101_105.py"))["validate"]
def setup():
    index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text("utf8"))
    source=json.loads((ROOT/"catalog/chanlun_lessons101_105_source_layers.json").read_text("utf8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text("utf8")) for n in range(101,106)]
    md=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text("utf8") for n in range(101,106)]
    syn=(ROOT/"analyses/books/chanlun/volumes/LESSONS_101_105_SYNTHESIS.md").read_text("utf8")
    graph=json.loads((ROOT/"knowledge/claims/chanlun_lessons101_105_semantic_dependencies.json").read_text("utf8"))
    old=[json.loads((ROOT/p).read_text("utf8")) for p in (
        "knowledge/claims/chanlun_early_core_dependencies.json","knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json",
        "knowledge/claims/chanlun_lessons071_075_semantic_dependencies.json","knowledge/claims/chanlun_lessons076_080_semantic_dependencies.json",
        "knowledge/claims/chanlun_lessons081_085_semantic_dependencies.json","knowledge/claims/chanlun_lessons086_090_crossvolume_dependencies.json",
        "knowledge/claims/chanlun_lessons091_095_semantic_dependencies.json","knowledge/claims/chanlun_lessons096_100_semantic_dependencies.json")]
    h={v["volume"]:v["sha256"] for v in index["volumes"]}
    return [index,source,ev,md,syn,graph,old,h]
class Source(unittest.TestCase):
 def test_complete(self):self.assertEqual(f(*setup())["claims"],35)
 def test_source_sha_wrong(self):
  x=setup();x[-1][5]="fake"
  with self.assertRaises(AssertionError):f(*x)
 def test_page_outside(self):
  x=setup();x[2][0]["claims"][0]["pdf_pages"]=[100]
  with self.assertRaises(AssertionError):f(*x)
 def test_visual_overclaim(self):
  x=setup();x[2][0]["quality"]["actually_inspected_pages"]=[234,238]
  with self.assertRaises(AssertionError):f(*x)
 def test_precision_overclaim(self):
  x=setup();x[1]["visual"]["fine_chart_price_labels_verified"]=True
  with self.assertRaises(AssertionError):f(*x)
 def test_2010_editor_must_remain(self):
  x=setup();x[1]["source_role_flags"]=[a for a in x[1]["source_role_flags"] if a["kind"]!="LATER_DATED_EDIT"]
  with self.assertRaises(AssertionError):f(*x)
 def test_101_buy_low_must_remain(self):
  x=setup();x[3][0]=x[3][0].replace("低于","少于")
  with self.assertRaises(AssertionError):f(*x)
 def test_hypotheses_unproven(self):
  x=setup();next(c for c in x[2][1]["claims"] if c["kind"]=="HYPOTHESIS")["test_status"]="proven"
  with self.assertRaises(AssertionError):f(*x)
 def test_bad_graph_link(self):
  x=setup();x[5]["edges"][0]["to"]="UNKNOWN"
  with self.assertRaises(AssertionError):f(*x)
 def test_graph_old_contract(self):
  x=setup();x[6][0]["source_pdf_sha256_by_volume"]["5"]=x[-1][5]
  with self.assertRaises(AssertionError):f(*x)
 def test_7_lenses(self):
  x=setup();x[3][2]=x[3][2].replace("第七重","建议")
  with self.assertRaises(AssertionError):f(*x)
 def test_no_real_backtest(self):
  x=setup();x[2][4]["real_market_backtest"]="completed"
  with self.assertRaises(AssertionError):f(*x)
if __name__=="__main__":unittest.main()
