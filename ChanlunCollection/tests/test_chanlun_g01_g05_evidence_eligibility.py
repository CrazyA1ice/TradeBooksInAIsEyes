"""Fail-closed source and as-of gate tests for G01/G05 research eligibility."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.audit_chanlun_g01_g05_evidence_eligibility import audit,evaluate,ROOT,DATA

class EligibilityTests(unittest.TestCase):
    def test_real_cases(self):
        self.assertEqual(audit()["cases"],11)
    def test_auxiliary_must_not_become_strict(self):
        d=json.loads((ROOT/DATA).read_text(encoding="utf-8"))
        case=next(c for c in d["cases"] if c["id"]=="G01-E02")
        self.assertEqual(evaluate(case),"INVALID_STRICT_SEQUENCE")
        case["input"]["features"][2]["role"]="STRICT"
        self.assertEqual(evaluate(case),"PENDING_REVERSE_SEGMENT_EVIDENCE")
    def test_future_confirmation_not_available_now(self):
        d=json.loads((ROOT/DATA).read_text(encoding="utf-8"))
        case=next(c for c in d["cases"] if c["id"]=="G01-E03")
        self.assertEqual(evaluate(case),"FEATURE_NOT_YET_ASOF")
        case["input"]["as_of"]=8
        self.assertEqual(evaluate(case),"PENDING_REVERSE_SEGMENT_EVIDENCE")
    def test_ai_tie_policy_not_author_uniqueness(self):
        d=json.loads((ROOT/DATA).read_text(encoding="utf-8"))
        case=next(c for c in d["cases"] if c["id"]=="G05-E05")
        self.assertEqual(evaluate(case),"AI_SELECTION_NOT_AUTHOR_CONFLUENCE")
        case["input"]["tie_status"]="UNRESOLVED"
        self.assertEqual(evaluate(case),"COMPETING_CUTPOINTS_RULE_UNPROVEN")
    def test_fake_source_and_proof_blocked(self):
        d=json.loads((ROOT/DATA).read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            paths=[DATA,d["prior_contract"]]
            paths += list({f"knowledge/evidence/chanlun_lesson{x['lesson']:03d}.json" for refs in d["source_evidence"].values() for x in refs})
            for p in paths:
                out=root/p;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes((ROOT/p).read_bytes())
            d["proof_status"]="PROVEN"
            (root/DATA).write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):audit(root)
            d["proof_status"]="OPEN"
            d["source_evidence"]["G01"][0]["claim_id"]="FAKE"
            (root/DATA).write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):audit(root)

if __name__=="__main__":unittest.main()
