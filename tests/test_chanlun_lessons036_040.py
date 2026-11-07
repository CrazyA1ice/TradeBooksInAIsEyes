import json,runpy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
check=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons036_040.py"))["audit"]
def fixture():
    index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    src=json.loads((ROOT/"catalog/chanlun_lessons036_040_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n}.json").read_text(encoding="utf-8")) for n in range(36,41)]
    md=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n}.md").read_text(encoding="utf-8") for n in range(36,41)]
    overview=(ROOT/"analyses/books/chanlun/volumes/LESSONS_036_040_SYNTHESIS.md").read_text(encoding="utf-8")
    graph=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    hashes={v["volume"]:v["sha256"] for v in index["volumes"][:2]}
    return [index,src,ev,md,overview,graph,hashes]
class SourceAudit(unittest.TestCase):
    def test_valid_source_claims(self):self.assertEqual(check(*fixture())["claims"],35)
    def test_wrong_fingerprint_fails(self):
        x=fixture();x[-1][2]="BAD"
        with self.assertRaises(AssertionError):check(*x)
    def test_wrong_pdf_page_fails(self):
        x=fixture();x[2][2]["claims"][0]["pdf_pages"]=[1]
        with self.assertRaises(AssertionError):check(*x)
    def test_later_editor_note_required(self):
        x=fixture();x[3][3]=x[3][3].replace("编者","编辑者")
        with self.assertRaises(AssertionError):check(*x)
    def test_unverified_hypothesis_must_stay_not_tested(self):
        x=fixture();next(c for c in x[2][4]["claims"] if c["kind"]=="HYPOTHESIS")["test_status"]="verified"
        with self.assertRaises(AssertionError):check(*x)
    def test_missing_image_metadata_rejected(self):
        x=fixture();x[2][0]["quality"]["image_pages"]=[]
        with self.assertRaises(AssertionError):check(*x)
    def test_last_lens_cannot_be_dropped(self):
        x=fixture();x[3][0]=x[3][0].replace("第七重","自由评论")
        with self.assertRaises(AssertionError):check(*x)
    def test_graph_referential_integrity(self):
        x=fixture();x[5]["nodes"].pop()
        with self.assertRaises(AssertionError):check(*x)
    def test_l36_no_divider_is_explicit(self):
        x=fixture();self.assertIsNone(x[1]["lessons"][0]["first_appendix"])
    def test_graph_volume1_sha_pin(self):
        x=fixture();x[5]["source_pdf_sha256_by_volume"]["1"]="wrong"
        with self.assertRaises(AssertionError):check(*x)
if __name__=="__main__":unittest.main()
