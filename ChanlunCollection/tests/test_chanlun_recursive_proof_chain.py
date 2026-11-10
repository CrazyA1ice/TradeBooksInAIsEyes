"""Fail-closed checks for exact SOURCE and open recursion/uniqueness obligations."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.audit_chanlun_recursive_proof_chain import audit,ROOT,DATA

def fixture():
    t=tempfile.TemporaryDirectory()
    p=Path(t.name)
    d=json.loads((ROOT/DATA).read_text(encoding="utf-8"))
    files={f"knowledge/evidence/chanlun_lesson{a['lesson']:03d}.json" for s in d["steps"] for a in s["evidence"]}
    for f in [DATA,*files]:
        x=p/f;x.parent.mkdir(parents=True,exist_ok=True);x.write_bytes((ROOT/f).read_bytes())
    return t,p,d

class RecursiveChainTests(unittest.TestCase):
    def test_original_chain(self):
        self.assertEqual(audit()["steps"],9)

    def test_invented_id_and_pages_fail(self):
        t,p,d=fixture()
        with t:
            src=d["steps"][0]["evidence"][0]
            real=src["claim_id"]
            src["claim_id"]="FABRICATED"
            (p/DATA).write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):audit(p)
            src["claim_id"]=real;src["physical_pages"]=[9999]
            (p/DATA).write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):audit(p)

    def test_proof_must_stay_open(self):
        t,p,d=fixture()
        with t:
            d["gates"][0]["status"]="PROVEN"
            (p/DATA).write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):audit(p)

    def test_cannot_upgrade_author_proof_identity(self):
        t,p,d=fixture()
        with t:
            d["identity"]="AUTHOR_VERIFIED_FORMAL_PROOF"
            (p/DATA).write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):audit(p)
if __name__=="__main__":unittest.main()
