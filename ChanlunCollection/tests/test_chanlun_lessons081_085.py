import json,runpy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
verify=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons081_085.py"))["validate"]
def fixture():
    index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    source=json.loads((ROOT/"catalog/chanlun_lessons081_085_source_layers.json").read_text(encoding="utf-8"))
    e=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(81,86)]
    r=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(81,86)]
    summary=(ROOT/"analyses/books/chanlun/volumes/LESSONS_081_085_SYNTHESIS.md").read_text(encoding="utf-8")
    new=json.loads((ROOT/"knowledge/claims/chanlun_lessons081_085_semantic_dependencies.json").read_text(encoding="utf-8"))
    older=[json.loads((ROOT/p).read_text(encoding="utf-8")) for p in (
       "knowledge/claims/chanlun_early_core_dependencies.json",
       "knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json",
       "knowledge/claims/chanlun_lessons071_075_semantic_dependencies.json",
       "knowledge/claims/chanlun_lessons076_080_semantic_dependencies.json")]
    hashes={v["volume"]:v["sha256"] for v in index["volumes"][:4]}
    return [index,source,e,r,summary,new,older,hashes]
class Source(unittest.TestCase):
 def test_good(self):self.assertEqual(verify(*fixture())["claims"],35)
 def test_wrong_pdf_hash(self):
    x=fixture();x[-1][4]="bad"
    with self.assertRaises(AssertionError):verify(*x)
 def test_not_all_figures_numerically_verified(self):
    x=fixture();x[1]["visual"]["precise_chart_numbers_verified"]=True
    with self.assertRaises(AssertionError):verify(*x)
 def test_unknown_visual_page(self):
    x=fixture();x[2][0]["quality"]["visually_inspected_pages"]=[234,237,300]
    with self.assertRaises(AssertionError):verify(*x)
 def test_81_author_date_rule_revision_must_be_distinct(self):
    x=fixture();x[1]["provenance_flags"]=[f for f in x[1]["provenance_flags"] if f["role"]!="DIFFERENT_DATED_AUTHOR_RULE_REVISION"]
    with self.assertRaises(AssertionError):verify(*x)
 def test_84_self_terminology_revision(self):
    x=fixture();x[1]["provenance_flags"]=[f for f in x[1]["provenance_flags"] if f["role"]!="AUTHOR_TERMINOLOGY_REVISION"]
    with self.assertRaises(AssertionError):verify(*x)
 def test_85_unverified_legal_evidence(self):
    x=fixture();x[1]["provenance_flags"]=[f for f in x[1]["provenance_flags"] if f["lesson"]!=85]
    with self.assertRaises(AssertionError):verify(*x)
 def test_out_of_chapter_claim(self):
    x=fixture();x[2][3]["claims"][0]["pdf_pages"]=[405]
    with self.assertRaises(AssertionError):verify(*x)
 def test_unverified_hypothesis(self):
    x=fixture();next(y for y in x[2][2]["claims"] if y["kind"]=="HYPOTHESIS")["test_status"]="true"
    with self.assertRaises(AssertionError):verify(*x)
 def test_source_date_precision(self):
    x=fixture();x[2][2]["source"]["original_date"]="2007-09-26 00:00:00"
    with self.assertRaises(AssertionError):verify(*x)
 def test_missing_seventh_lens(self):
    x=fixture();x[3][1]=x[3][1].replace("第七重","附件")
    with self.assertRaises(AssertionError):verify(*x)
 def test_graph_link_unknown(self):
    x=fixture();x[5]["edges"][0]["to"]="NONEXISTENT"
    with self.assertRaises(AssertionError):verify(*x)
 def test_history_graph_preserved(self):
    x=fixture();x[6][0]["source_pdf_sha256_by_volume"]["4"]=x[-1][4]
    with self.assertRaises(AssertionError):verify(*x)
if __name__=="__main__":unittest.main()
