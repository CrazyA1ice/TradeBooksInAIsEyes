"""Generator tests: real composition with lesson 67/71 and full finite span enumeration."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from tools.audit_chanlun_g01_g05_local_generators import (
    ROOT, DATA, audit, local_feature_candidate, enumerate_conditional_parses
)

class LocalGeneratorTests(unittest.TestCase):
    def test_catalog_and_sources(self):
        self.assertEqual(audit()["cases"], 11)

    def test_gap_confirmation_is_asof_gated(self):
        doc=json.loads((ROOT/DATA).read_text(encoding="utf-8"))
        case=next(x for x in doc["cases"] if x["id"]=="G01-R03")
        v=copy.deepcopy(case["input"])
        self.assertEqual(local_feature_candidate(v)["candidate_at"],6)
        v["as_of"]=5
        self.assertEqual(local_feature_candidate(v)["status"],"PENDING_OPPOSITE")

    def test_third_feature_role_and_confirmed_time(self):
        doc=json.loads((ROOT/DATA).read_text(encoding="utf-8"))
        case=next(x for x in doc["cases"] if x["id"]=="G01-R01")
        v=copy.deepcopy(case["input"])
        v["features"][2]["role"]="AUXILIARY"
        self.assertEqual(local_feature_candidate(v)["status"],"INVALID_STRICT_MEMBER")
        v["features"][2]["role"]="STRICT"
        v["features"][2]["confirmed_at"]=20
        self.assertEqual(local_feature_candidate(v)["status"],"FEATURE_NOT_YET_ASOF")

    def test_exhaustive_span_enumerator_not_greedy(self):
        x={"n":4,"input_complete":True,"allowed_spans":[[0,2],[2,4],[0,1],[1,4]]}
        r=enumerate_conditional_parses(x)
        self.assertEqual(r["cutpoints"],[[1],[2]])
        self.assertEqual(r["status"],"MULTIPLE_PARSES_UNDER_EXTERNAL_SPANS")

    def test_dedupe_and_missing_existence(self):
        x={"n":4,"input_complete":True,"allowed_spans":[[0,2],[2,4],[0,2],[2,4]]}
        self.assertEqual(enumerate_conditional_parses(x)["cutpoints"],[[2]])
        x["allowed_spans"]=[[0,2]]
        self.assertEqual(enumerate_conditional_parses(x)["status"],"NO_PARSE_UNDER_EXTERNAL_SPANS")

    def test_invalid_inputs_fail_closed(self):
        x={"n":4,"input_complete":True,"allowed_spans":[[0,2],[2,5]]}
        with self.assertRaises(AssertionError):
            enumerate_conditional_parses(x)
        doc=json.loads((ROOT/DATA).read_text(encoding="utf-8"))
        x=copy.deepcopy(doc["cases"][0]["input"])
        x["features"][1]["index"]=1
        with self.assertRaises(AssertionError):
            local_feature_candidate(x)

    def test_invented_source_or_false_proof_rejected(self):
        doc=json.loads((ROOT/DATA).read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            names=[DATA,doc["prior_contract"],
                   "tools/audit_chanlun_lesson067_feature_gap.py",
                   "tools/audit_chanlun_lesson071_typed_membership.py"]
            names += list({f"knowledge/evidence/chanlun_lesson{e['lesson']:03d}.json" for e in doc["source_evidence"]})
            for p in names:
                dst=root/p
                dst.parent.mkdir(parents=True,exist_ok=True)
                dst.write_bytes((ROOT/p).read_bytes())
            doc["proof_status"]="PROVEN"
            (root/DATA).write_text(json.dumps(doc,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)
            doc["proof_status"]="OPEN"
            doc["source_evidence"][0]["claim_id"]="FABRICATED"
            (root/DATA).write_text(json.dumps(doc,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)

if __name__=="__main__":
    unittest.main()
