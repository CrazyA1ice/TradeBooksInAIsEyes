import json,runpy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
v=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons066_070.py"))["validate"]
def fixture():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    s=json.loads((ROOT/"catalog/chanlun_lessons066_070_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(66,71)]
    r=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(66,71)]
    o=(ROOT/"analyses/books/chanlun/volumes/LESSONS_066_070_SYNTHESIS.md").read_text(encoding="utf-8")
    ext=json.loads((ROOT/"knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json").read_text(encoding="utf-8"))
    graph=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    sha={a["volume"]:a["sha256"] for a in idx["volumes"][:4]}
    return [idx,s,ev,r,o,ext,graph,sha]
class Source(unittest.TestCase):
 def test_valid(self):self.assertEqual(v(*fixture())["claims"],34)
 def test_volume4_sha_changed(self):
    x=fixture();x[-1][4]="bad"
    with self.assertRaises(AssertionError):v(*x)
 def test_terminal_lesson_of_vol3_ends_at_405(self):
    x=fixture();self.assertEqual(v(*x)["pages"],100)
    self.assertEqual(x[1]["lessons"][1]["last_page"],x[0]["volumes"][2]["pdf_page_count"])
 def test_volume_3_labeled_4(self):
    x=fixture();x[2][0]["source"]["volume"]=4
    with self.assertRaises(AssertionError):v(*x)
 def test_unknown_image_preview_claim(self):
    x=fixture();x[2][3]["quality"]["visual_preview_pages"]=[28]
    with self.assertRaises(AssertionError):v(*x)
 def test_figures_not_numeric_verified(self):
    x=fixture();x[2][4]["quality"]["numeric_chart_values_verified"]=True
    with self.assertRaises(AssertionError):v(*x)
 def test_editorial_disagreement_required(self):
    x=fixture();x[1]["editorial_flags"]=[a for a in x[1]["editorial_flags"] if a["lesson"]!=67]
    with self.assertRaises(AssertionError):v(*x)
 def test_invalid_claim_page(self):
    x=fixture();x[2][2]["claims"][0]["pdf_pages"]=[80]
    with self.assertRaises(AssertionError):v(*x)
 def test_unproven_hypothesis(self):
    x=fixture();next(k for k in x[2][4]["claims"] if k["kind"]=="HYPOTHESIS")["test_status"]="passed"
    with self.assertRaises(AssertionError):v(*x)
 def test_bad_graph_ref(self):
    x=fixture();x[5]["edges"][0]["to"]="UNKNOWN"
    with self.assertRaises(AssertionError):v(*x)
 def test_extra_legacy_volume_sha_rejected(self):
    x=fixture();x[6]["source_pdf_sha256_by_volume"]["4"]=x[7][4]
    with self.assertRaises(AssertionError):v(*x)
 def test_missing_seventh_lens(self):
    x=fixture();x[3][1]=x[3][1].replace("第七重","备注")
    with self.assertRaises(AssertionError):v(*x)
if __name__=="__main__":unittest.main()
