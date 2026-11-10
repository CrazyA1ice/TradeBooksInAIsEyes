"""Assumption-scoped G01 transitions and G05 normalization policy regression tests."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.audit_chanlun_g01_g05_typed_rule_contract import audit,evaluate,ROOT,DATA

def fixture():
    t=tempfile.TemporaryDirectory()
    root=Path(t.name)
    d=json.loads((ROOT/DATA).read_text(encoding="utf-8"))
    files={DATA,*d["prior_contracts"]}
    files|={f"knowledge/evidence/chanlun_lesson{s['lesson']:03d}.json"
            for cues in d["evidence"].values() for s in cues}
    for p in files:
        f=root/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes((ROOT/p).read_bytes())
    return t,root,d

class TypedContractTests(unittest.TestCase):
    def test_live_contract(self):
        self.assertEqual(audit()["cases"],12)

    def test_g01_future_confirmation_is_not_current(self):
        t,root,d=fixture()
        with t:
            c=next(x for x in d["cases"] if x["id"]=="G01-T03")
            self.assertEqual(evaluate(c)[0],"PENDING_GAP_OPPOSITE_FRACTAL")
            c["input"]["as_of"]=12
            self.assertEqual(evaluate(c)[0],"PENDING_LEGAL_REVERSE_SEGMENT")
            (root/DATA).write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):audit(root)

    def test_g01_external_reverse_is_not_child_completion(self):
        c=json.loads((ROOT/DATA).read_text(encoding="utf-8"))["cases"][5]
        self.assertEqual(evaluate(c)[0],"EXTERNAL_REVERSE_SEGMENT_ASSUMED_NOT_FINISHED_LOWER_TYPE")

    def test_g05_lexicographic_policy_is_ai_only(self):
        t,root,d=fixture()
        with t:
            c=next(x for x in d["cases"] if x["id"]=="G05-T05")
            status,selected=evaluate(c)
            self.assertEqual(status,"AI_ONLY_DETERMINISTIC_SELECTION_NOT_AUTHOR_UNIQUENESS")
            self.assertEqual(selected,[1,4])
            c["input"]["tie_policy"]="UNSPECIFIED"
            self.assertEqual(evaluate(c)[0],"MULTIPLE_ASSUMED_PARSES_UNRESOLVED")

    def test_false_author_proof_and_fabricated_source_fail(self):
        t,root,d=fixture()
        with t:
            d["proof_status"]="PROVEN"
            (root/DATA).write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):audit(root)
            d["proof_status"]="OPEN"
            d["evidence"]["G05"][0]["claim_id"]="FAKE-CLAIM"
            (root/DATA).write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):audit(root)

if __name__=="__main__":unittest.main()
