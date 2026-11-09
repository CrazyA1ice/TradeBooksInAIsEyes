import json,runpy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
check=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons056_060.py"))["audit"]
def fixture():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    src=json.loads((ROOT/"catalog/chanlun_lessons056_060_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(56,61)]
    rep=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(56,61)]
    overview=(ROOT/"analyses/books/chanlun/volumes/LESSONS_056_060_SYNTHESIS.md").read_text(encoding="utf-8")
    graph=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    shas={v["volume"]:v["sha256"] for v in idx["volumes"][:3]}
    return [idx,src,ev,rep,overview,graph,shas]
class Source(unittest.TestCase):
 def test_valid(self):self.assertEqual(check(*fixture())["claims"],35)
 def test_wrong_pdf_sha(self):
    x=fixture();x[-1][3]="wrong"
    with self.assertRaises(AssertionError):check(*x)
 def test_wrong_price_verification_claim(self):
    x=fixture();x[2][0]["quality"]["figure_prices_verified"]=True
    with self.assertRaises(AssertionError):check(*x)
 def test_wrong_thumbnail_review_page(self):
    x=fixture();x[1]["visual_review"]["pdf_pages"][0]=206
    with self.assertRaises(AssertionError):check(*x)
 def test_false_unseen_picture_page(self):
    x=fixture();x[2][3]["quality"]["thumbnail_pages_visual_reviewed"]=[251]
    with self.assertRaises(AssertionError):check(*x)
 def test_wrong_claim_location(self):
    x=fixture();x[2][3]["claims"][0]["pdf_pages"]=[100]
    with self.assertRaises(AssertionError):check(*x)
 def test_unproven_hypothesis_must_stay_not_tested(self):
    x=fixture();next(c for c in x[2][4]["claims"] if c["kind"]=="HYPOTHESIS")["test_status"]="proved"
    with self.assertRaises(AssertionError):check(*x)
 def test_seven_lenses_required(self):
    x=fixture();x[3][0]=x[3][0].replace("第七重","其他观点")
    with self.assertRaises(AssertionError):check(*x)
 def test_missing_precision_concept(self):
    x=fixture();x[5]["nodes"]=[n for n in x[5]["nodes"] if n["id"]!="L59-PRICE-QUANTIZATION"]
    with self.assertRaises(AssertionError):check(*x)
 def test_bad_graph_target(self):
    x=fixture();x[5]["edges"][0]["to"]="MISSING"
    with self.assertRaises(AssertionError):check(*x)
if __name__=="__main__":unittest.main()
