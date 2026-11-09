import json,runpy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
audit=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons031_035.py"))["audit"]
def docs():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    src=json.loads((ROOT/"catalog/chanlun_lessons031_035_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(31,36)]
    reports=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(31,36)]
    overview=(ROOT/"analyses/books/chanlun/volumes/LESSONS_031_035_SYNTHESIS.md").read_text(encoding="utf-8")
    graph=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    h={v["volume"]:v["sha256"] for v in idx["volumes"][:2]}
    return [idx,src,ev,reports,overview,graph,h]
class ProvenanceTests(unittest.TestCase):
    def test_all_source_claims(self):
        self.assertEqual(audit(*docs())["claims"],33)
        card = docs()[2][4]
        claim = next(x for x in card["claims"] if x["id"] == "CL35-SO-9")
        self.assertEqual(claim["kind"], "SOURCE")
        self.assertEqual(claim["pdf_pages"], [291])
        self.assertEqual(
            claim["source_anchor"]["native_text_sha256"],
            "1a2c291cff189ea4de5bef2ecf152e9888773d1194b0ed4e7218f4cd0f3b846b")

    def test_tampered_pdf_hash(self):
        x=docs();x[-1][2]="wrong"
        with self.assertRaises(AssertionError):audit(*x)
    def test_wrong_evidence_page(self):
        x=docs();x[2][1]["claims"][0]["pdf_pages"]=[1]
        with self.assertRaises(AssertionError):audit(*x)
    def test_image_page_omitted(self):
        x=docs();x[2][0]["source_quality"]["image_pages"]=[]
        with self.assertRaises(AssertionError):audit(*x)
    def test_hypothesis_mislabeled(self):
        x=docs();next(c for c in x[2][4]["claims"] if c["kind"]=="HYPOTHESIS")["test_status"]="passed"
        with self.assertRaises(AssertionError):audit(*x)
    def test_no_seventh_lens(self):
        x=docs();x[3][2]=x[3][2].replace("第七重","无标题")
        with self.assertRaises(AssertionError):audit(*x)
    def test_graph_missing_ancestor(self):
        x=docs();x[5]["nodes"].pop()
        with self.assertRaises(AssertionError):audit(*x)
    def test_graph_wrong_volume_hash(self):
        x=docs();x[5]["source_pdf_sha256_by_volume"]["1"]="wrong"
        with self.assertRaises(AssertionError):audit(*x)
    def test_graph_unknown_target(self):
        x=docs();x[5]["edges"][0]["to"]="MISSING"
        with self.assertRaises(AssertionError):audit(*x)
if __name__=="__main__":unittest.main()
