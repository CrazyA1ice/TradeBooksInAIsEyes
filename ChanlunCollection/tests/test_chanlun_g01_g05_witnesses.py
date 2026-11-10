"""Negative tests for explicit G01/G05 assumptions and proof status."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.audit_chanlun_g01_g05_witnesses import audit,decide,ROOT,DATA

def fixture():
    t=tempfile.TemporaryDirectory()
    root=Path(t.name)
    obj=json.loads((ROOT/DATA).read_text(encoding="utf-8"))
    for p in [DATA,*{f"knowledge/evidence/chanlun_lesson{s['lesson']:03d}.json"
                     for sources in obj["source_evidence"].values() for s in sources}]:
        f=root/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes((ROOT/p).read_bytes())
    return t,root,obj

class G01G05Tests(unittest.TestCase):
    def test_live_cases(self):
        self.assertEqual(audit()["cases"],10)

    def test_g01_asof_boundary(self):
        t,root,d=fixture()
        with t:
            c=next(x for x in d["cases"] if x["id"]=="G01-W05")
            self.assertEqual(decide(c),"ASOF_CHILD_PENDING")
            c["assumptions"]["as_of"]=9
            self.assertEqual(decide(c),"CONDITIONAL_PARENT_OVERLAP_NOT_AUTHOR_CERTIFIED")
            (root/DATA).write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):audit(root)

    def test_g01_no_auto_certification(self):
        t,root,d=fixture()
        with t:
            c=next(x for x in d["cases"] if x["id"]=="G01-W03")
            c["assumptions"]["member_completion_author_verified"]=True
            (root/DATA).write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):audit(root)

    def test_g05_rule_domain_and_distinct_cuts(self):
        t,root,d=fixture()
        with t:
            c=next(x for x in d["cases"] if x["id"]=="G05-W01")
            c["assumptions"]["candidate_parses"][1]["rule_id"]="R_B"
            self.assertEqual(decide(c),"CROSS_RULE_COMPARISON_NOT_COUNTEREXAMPLE")
            (root/DATA).write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):audit(root)

    def test_fake_proof_or_source_rejected(self):
        t,root,d=fixture()
        with t:
            d["proof_status"]="PROVEN"
            (root/DATA).write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):audit(root)
            d["proof_status"]="OPEN"
            d["source_evidence"]["G01"][0]["claim_id"]="FABRICATED"
            (root/DATA).write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):audit(root)

if __name__=="__main__":
    unittest.main()
