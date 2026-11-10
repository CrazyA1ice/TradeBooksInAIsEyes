"""Conservative tests: do not elevate author claims to proved theorems."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.audit_chanlun_strong_theses import audit,ROOT,DATA

def fixture():
    temp=tempfile.TemporaryDirectory()
    root=Path(temp.name)
    obj=json.loads((ROOT/DATA).read_text(encoding="utf-8"))
    target=root/DATA
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes((ROOT/DATA).read_bytes())
    for n in {s["lesson"] for t in obj["theses"] for s in t["source"]}:
        path=f"knowledge/evidence/chanlun_lesson{n:03d}.json"
        p=root/path
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes((ROOT/path).read_bytes())
    return temp,root,obj

class ThesesAuditTests(unittest.TestCase):
    def test_real_textual_sources(self):
        r=audit()
        self.assertEqual(r["theses"],4)
        self.assertEqual(r["non_entailment_relations"],6)

    def test_reject_fabricated_source_and_wrong_page(self):
        temp,root,obj=fixture()
        with temp:
            target=root/DATA
            first=obj["theses"][0]["source"][0]
            old=first["claim_id"]
            first["claim_id"]="FABRICATED-CLAIM"
            target.write_text(json.dumps(obj,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)
            first["claim_id"]=old
            first["pages"]=[999999]
            target.write_text(json.dumps(obj,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)

    def test_reject_proven_safety_or_entailment_claim(self):
        temp,root,obj=fixture()
        with temp:
            target=root/DATA
            obj["theses"][1]["status"]="PROVEN_SAFE"
            target.write_text(json.dumps(obj,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)
            obj["theses"][1]["status"]="AUTHOR_STRONG_CLAIM_WITH_OPEN_FORMAL_AND_EMPIRICAL_PROOF"
            obj["relations"][0]["relation"]="PROVEN_IMPLICATION"
            target.write_text(json.dumps(obj,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)

    def test_reject_no_open_proof_obligations(self):
        temp,root,obj=fixture()
        with temp:
            obj["theses"][2]["open_obligations"]=[]
            (root/DATA).write_text(json.dumps(obj,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)

if __name__=="__main__":
    unittest.main()
