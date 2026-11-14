"""M54 author source symbol/typed topology checks, no market execution."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/"tools/audit_chanlun_l54_dual_policy_witness_m54.py"
spec=importlib.util.spec_from_file_location("m54_audit",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
DOC=json.loads(m.CONTRACT.read_text(encoding="utf-8"))
POL={p["id"]:p for p in DOC["policies"]}

class M54SourceWitnessTest(unittest.TestCase):
    def test_contract(self):
        a=m.audit(DOC)
        self.assertEqual(a["author_symbolic_members"],18)
        self.assertTrue(a["phi20_open"])
        self.assertFalse(a["verified_market"])

    def test_A_3_groups(self):
        a=m.inspect_policy(POL["R_A"])
        self.assertEqual(a["member_count"],9)
        self.assertEqual(a["end_symbol"],"g5")

    def test_B_3_groups(self):
        b=m.inspect_policy(POL["R_B"])
        self.assertEqual(b["member_count"],9)
        self.assertEqual(b["end_symbol"],"g6")

    def test_policy_groups_are_different(self):
        self.assertNotEqual(POL["R_A"]["groups"],POL["R_B"]["groups"])
        self.assertNotEqual(POL["R_A"]["higher_price_interval_symbolic"],
                            POL["R_B"]["higher_price_interval_symbolic"])

    def test_g5_exists_but_not_forall(self):
        r=m.checkpoint(DOC,"g5")
        self.assertEqual(r["by_policy"],{"R_A":True,"R_B":False})
        self.assertTrue(r["exists_r"])
        self.assertFalse(r["forall_r"])

    def test_g6_both_author_attested(self):
        r=m.checkpoint(DOC,"g6")
        self.assertTrue(r["exists_r"] and r["forall_r"])

    def test_no_future_g6_group_at_g5(self):
        self.assertFalse(m.checkpoint(DOC,"g5")["by_policy"]["R_B"])
        self.assertTrue(any("d6g6" in g for g in POL["R_B"]["groups"]))

    def test_samelevel_two_no_connector_rejected(self):
        self.assertEqual(m.topology("TWO_SAME_LEVEL_CENTERS",False,DOC),
                         "REJECT_SAMELEVEL_MISSING_CONNECTOR")

    def test_three_child_groups_have_different_topology(self):
        self.assertEqual(m.topology("THREE_CHILD_CENTERS_FOR_PARENT",False,DOC),
                         "ALLOWED_AUTHOR_TOPOLOGY_NOT_COMPLETION_PROOF")

    def test_no_higher_movement_proof(self):
        for p in POL.values():
            r=m.inspect_policy(p)
            self.assertFalse(r["independently_verified_completed_g_movements"])
            self.assertFalse(r["phi20_authenticated"])
            self.assertIsNone(r["first_known_actual_market_time"])

    def test_cross_boundary_validity(self):
        for p in POL.values():
            self.assertTrue(m.valid_chain(p["prefix_connector"]+
                            [s for group in p["groups"] for s in group]))

    def test_bad_group_token_refused(self):
        p=copy.deepcopy(POL["R_A"])
        p["groups"][1][1]="g3d5"
        self.assertEqual(m.inspect_policy(p)["status"],"AUTHOR_GROUP_TOKEN_MISMATCH")

    def test_wrong_forming_milestone_refused(self):
        p=copy.deepcopy(POL["R_B"])
        p["author_attested_higher_at"]="g5"
        self.assertEqual(m.inspect_policy(p)["status"],"AUTHOR_ATTESTATION_OR_PRICE_SYMBOL_MISMATCH")

    def test_altered_core_symbol_refused(self):
        p=copy.deepcopy(POL["R_A"])
        p["higher_price_interval_symbolic"][0]="d3"
        self.assertEqual(m.inspect_policy(p)["status"],"AUTHOR_ATTESTATION_OR_PRICE_SYMBOL_MISMATCH")

    def test_invalid_chain_rejected(self):
        self.assertFalse(m.valid_chain(["d1g1","d3g3"]))
        self.assertTrue(m.valid_chain(["d1g1","g1d2","d2g2"]))

    def test_numeric_levels_not_inferred(self):
        self.assertEqual(POL["R_A"]["higher_price_interval_symbolic"][0],"d2")
        self.assertEqual(POL["R_B"]["higher_price_interval_symbolic"][0],"d3")

    def test_unknown_checkpoint_rejected(self):
        self.assertEqual(m.checkpoint(DOC,"g4"),{"status":"UNKNOWN_CHECKPOINT"})

if __name__=="__main__":
    unittest.main()
