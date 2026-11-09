import json,runpy,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
verify=runpy.run_path(str(R/"tools/verify_chanlun_lessons086_090.py"))["validate"]
def data():
    index=json.loads((R/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    source=json.loads((R/"catalog/chanlun_lessons086_090_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((R/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(86,91)]
    reports=[(R/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(86,91)]
    syn=(R/"analyses/books/chanlun/volumes/LESSONS_086_090_SYNTHESIS.md").read_text(encoding="utf-8")
    graph=json.loads((R/"knowledge/claims/chanlun_lessons086_090_crossvolume_dependencies.json").read_text(encoding="utf-8"))
    old=[json.loads((R/p).read_text(encoding="utf-8")) for p in (
      "knowledge/claims/chanlun_early_core_dependencies.json",
      "knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json",
      "knowledge/claims/chanlun_lessons071_075_semantic_dependencies.json",
      "knowledge/claims/chanlun_lessons076_080_semantic_dependencies.json",
      "knowledge/claims/chanlun_lessons081_085_semantic_dependencies.json")]
    hashes={v["volume"]:v["sha256"] for v in index["volumes"]}
    return [index,source,ev,reports,syn,graph,old,hashes]
class SourceChecks(unittest.TestCase):
 def test_valid(self):self.assertEqual(verify(*data())["typed_claims"],35)
 def test_bad_volume5_sha(self):
  x=data();x[-1][5]="bad"
  with self.assertRaises(AssertionError):verify(*x)
 def test_crossvolume_last_page_bound(self):
  x=data();self.assertEqual(verify(*x)["physical_pages"],123)
  self.assertEqual(x[1]["lessons"][2]["last_page"],x[0]["volumes"][3]["pdf_page_count"])
 def test_bad_volume_assignment(self):
  x=data();x[2][3]["source"]["volume"]=4
  with self.assertRaises(AssertionError):verify(*x)
 def test_unviewed_image_claim(self):
  x=data();x[2][3]["quality"]["actually_visually_reviewed"]=[5,14]
  with self.assertRaises(AssertionError):verify(*x)
 def test_fine_prices_not_verified(self):
  x=data();x[1]["figure_review"]["fine_chart_prices_verified"]=True
  with self.assertRaises(AssertionError):verify(*x)
 def test_missing_editorial_role(self):
  x=data();x[1]["provenance"]=[f for f in x[1]["provenance"] if f["role"]!="EDITORIAL_COMPLETION"]
  with self.assertRaises(AssertionError):verify(*x)
 def test_aux_boll_not_absoulte(self):
  x=data();x[1]["provenance"]=[f for f in x[1]["provenance"] if f["role"]!="AUTHOR_AUXILIARY_NOT_ABSOLUTE"]
  with self.assertRaises(AssertionError):verify(*x)
 def test_claim_not_in_own_volume_page(self):
  x=data();x[2][4]["claims"][0]["pdf_pages"]=[400]
  with self.assertRaises(AssertionError):verify(*x)
 def test_hypotheses_remain_unproven(self):
  x=data();next(cl for cl in x[2][4]["claims"] if cl["kind"]=="HYPOTHESIS")["test_status"]="proven"
  with self.assertRaises(AssertionError):verify(*x)
 def test_graph_source_provenance(self):
  x=data();x[5]["source_pdf_sha256_by_volume"]["5"]="bad"
  with self.assertRaises(AssertionError):verify(*x)
 def test_unknown_reference(self):
  x=data();x[5]["edges"][0]["to"]="UNDEFINED"
  with self.assertRaises(AssertionError):verify(*x)
 def test_old_graph_stays_immutable(self):
  x=data();x[6][0]["source_pdf_sha256_by_volume"]["4"]=x[-1][4]
  with self.assertRaises(AssertionError):verify(*x)
 def test_seven_lenses(self):
  x=data();x[3][3]=x[3][3].replace("第七重","备注")
  with self.assertRaises(AssertionError):verify(*x)
if __name__=="__main__":unittest.main()
