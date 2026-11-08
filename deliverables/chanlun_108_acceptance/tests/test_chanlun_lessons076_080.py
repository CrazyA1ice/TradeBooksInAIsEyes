import json,runpy,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
v=runpy.run_path(str(R/"tools/verify_chanlun_lessons076_080.py"))["validate"]
def fixture():
    i=json.loads((R/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    s=json.loads((R/"catalog/chanlun_lessons076_080_source_layers.json").read_text(encoding="utf-8"))
    e=[json.loads((R/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(76,81)]
    m=[(R/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(76,81)]
    z=(R/"analyses/books/chanlun/volumes/LESSONS_076_080_SYNTHESIS.md").read_text(encoding="utf-8")
    graph=json.loads((R/"knowledge/claims/chanlun_lessons076_080_semantic_dependencies.json").read_text(encoding="utf-8"))
    gs=[json.loads((R/p).read_text(encoding="utf-8")) for p in (
       "knowledge/claims/chanlun_early_core_dependencies.json",
       "knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json",
       "knowledge/claims/chanlun_lessons071_075_semantic_dependencies.json")]
    sha={x["volume"]:x["sha256"] for x in i["volumes"][:4]}
    return [i,s,e,m,z,graph,gs,sha]
class Sources(unittest.TestCase):
 def test_pass(self):self.assertEqual(v(*fixture())["claims"],35)
 def test_wrong_source_sha(self):
  x=fixture();x[-1][4]="bad"
  with self.assertRaises(AssertionError):v(*x)
 def test_wrong_page(self):
  x=fixture();x[2][2]["claims"][0]["pdf_pages"]=[88]
  with self.assertRaises(AssertionError):v(*x)
 def test_visual_scope_not_exaggerated(self):
  x=fixture();x[2][1]["quality"]["visually_inspected_pages"]=[160,163,165]
  with self.assertRaises(AssertionError):v(*x)
 def test_fine_chart_values_not_verified(self):
  x=fixture();x[1]["visual"]["fine_chart_values_verified"]=True
  with self.assertRaises(AssertionError):v(*x)
 def test_postdated_material_separated(self):
  x=fixture();x[1]["provenance"]=[y for y in x[1]["provenance"] if y["lesson"]!=80]
  with self.assertRaises(AssertionError):v(*x)
 def test_editorial_dispute_preserved(self):
  x=fixture();x[1]["provenance"]=[y for y in x[1]["provenance"] if y["kind"]!="author_vs_editor_dispute"]
  with self.assertRaises(AssertionError):v(*x)
 def test_hypotheses_not_run(self):
  x=fixture();next(z for z in x[2][4]["claims"] if z["kind"]=="HYPOTHESIS")["test_status"]="proven"
  with self.assertRaises(AssertionError):v(*x)
 def test_bad_graph_target(self):
  x=fixture();x[5]["edges"][0]["to"]="MISSING"
  with self.assertRaises(AssertionError):v(*x)
 def test_graph_legacy_unchanged(self):
  x=fixture();x[6][0]["source_pdf_sha256_by_volume"]["4"]=x[-1][4]
  with self.assertRaises(AssertionError):v(*x)
 def test_seven_lenses(self):
  x=fixture();x[3][0]=x[3][0].replace("第七重","附加")
  with self.assertRaises(AssertionError):v(*x)
if __name__=="__main__":unittest.main()
