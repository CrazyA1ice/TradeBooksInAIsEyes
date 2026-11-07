import json,runpy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
verify=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons071_075.py"))["verify"]
def setup():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    src=json.loads((ROOT/"catalog/chanlun_lessons071_075_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(71,76)]
    reports=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(71,76)]
    syn=(ROOT/"analyses/books/chanlun/volumes/LESSONS_071_075_SYNTHESIS.md").read_text(encoding="utf-8")
    graph=json.loads((ROOT/"knowledge/claims/chanlun_lessons071_075_semantic_dependencies.json").read_text(encoding="utf-8"))
    base=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    old=json.loads((ROOT/"knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json").read_text(encoding="utf-8"))
    hashes={v["volume"]:v["sha256"] for v in idx["volumes"][:4]}
    return [idx,src,ev,reports,syn,graph,base,old,hashes]
class Evidence(unittest.TestCase):
 def test_valid(self):self.assertEqual(verify(*setup())["typed_claims"],35)
 def test_pdf_sha_must_match(self):
    x=setup();x[-1][4]="wrong"
    with self.assertRaises(AssertionError):verify(*x)
 def test_undocumented_visual_count_rejected(self):
    x=setup();x[1]["visual"]["actually_visually_inspected_pages"].append(105)
    with self.assertRaises(AssertionError):verify(*x)
 def test_visual_numeric_false(self):
    x=setup();x[2][0]["quality"]["fine_price_labels_verified"]=True
    with self.assertRaises(AssertionError):verify(*x)
 def test_later_post_not_author(self):
    x=setup();x[1]["provenance_flags"]=[f for f in x[1]["provenance_flags"] if f["lesson"]!=72]
    with self.assertRaises(AssertionError):verify(*x)
 def test_editor_policy_disagreement_must_survive(self):
    x=setup();x[1]["provenance_flags"]=[f for f in x[1]["provenance_flags"] if f["lesson"]!=74]
    with self.assertRaises(AssertionError):verify(*x)
 def test_wrong_page_claim(self):
    x=setup();x[2][4]["claims"][0]["pdf_pages"]=[200]
    with self.assertRaises(AssertionError):verify(*x)
 def test_hypothesis_not_proven(self):
    x=setup();next(c for c in x[2][0]["claims"] if c["kind"]=="HYPOTHESIS")["test_status"]="passed"
    with self.assertRaises(AssertionError):verify(*x)
 def test_missing_lens(self):
    x=setup();x[3][2]=x[3][2].replace("第七重","附记")
    with self.assertRaises(AssertionError):verify(*x)
 def test_bad_cross_graph_ref(self):
    x=setup();x[5]["edges"][0]["to"]="nonexistent"
    with self.assertRaises(AssertionError):verify(*x)
 def test_legacy_graph_is_still_only_first_three_volumes(self):
    x=setup();x[6]["source_pdf_sha256_by_volume"]["4"]=x[-1][4]
    with self.assertRaises(AssertionError):verify(*x)
 def test_report_no_market_proof(self):
    x=setup();x[2][3]["empirical_status"]="passed"
    with self.assertRaises(AssertionError):verify(*x)
if __name__=="__main__":unittest.main()
