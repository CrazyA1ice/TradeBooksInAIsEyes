import json,runpy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
audit=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons051_055.py"))["audit"]
def fixture():
    i=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    s=json.loads((ROOT/"catalog/chanlun_lessons051_055_source_layers.json").read_text(encoding="utf-8"))
    e=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(51,56)]
    r=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(51,56)]
    summary=(ROOT/"analyses/books/chanlun/volumes/LESSONS_051_055_SYNTHESIS.md").read_text(encoding="utf-8")
    g=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    sha={v["volume"]:v["sha256"] for v in i["volumes"][:3]}
    return [i,s,e,r,summary,g,sha]
class ProvenanceAudit(unittest.TestCase):
 def test_valid(self):self.assertEqual(audit(*fixture())["claims"],35)
 def test_bad_source_sha(self):
    x=fixture();x[-1][3]="WRONG"
    with self.assertRaises(AssertionError):audit(*x)
 def test_2009_boundary_must_exist(self):
    x=fixture();x[1]["editorial_boundary_overrides"].pop(0)
    with self.assertRaises(AssertionError):audit(*x)
 def test_2009_not_2007(self):
    x=fixture();x[1]["editorial_boundary_overrides"][0]["date"]="2007-05-23 08:47:18"
    with self.assertRaises(AssertionError):audit(*x)
 def test_2009_source_cannot_be_author_2007(self):
    x=fixture();x[2][2]["claims"][0]["pdf_pages"]=[163]
    with self.assertRaises(AssertionError):audit(*x)
 def test_wrong_claim_page(self):
    x=fixture();x[2][3]["claims"][0]["pdf_pages"]=[300]
    with self.assertRaises(AssertionError):audit(*x)
 def test_wrong_figures(self):
    x=fixture();x[2][3]["quality"]["image_pages"]=[]
    with self.assertRaises(AssertionError):audit(*x)
 def test_hypothesis_marked_proven(self):
    x=fixture();next(c for c in x[2][4]["claims"] if c["kind"]=="HYPOTHESIS")["test_status"]="proven"
    with self.assertRaises(AssertionError):audit(*x)
 def test_removed_lens(self):
    x=fixture();x[3][1]=x[3][1].replace("第七重","其他")
    with self.assertRaises(AssertionError):audit(*x)
 def test_unknown_graph_target(self):
    x=fixture();x[5]["edges"][0]["to"]="UNDEFINED"
    with self.assertRaises(AssertionError):audit(*x)
if __name__=="__main__":unittest.main()
