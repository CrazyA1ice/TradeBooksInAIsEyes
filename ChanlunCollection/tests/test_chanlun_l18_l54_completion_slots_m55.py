"""M55 check 6 exact source groups, completion typing, and no historical lookahead."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/"tools/audit_chanlun_l18_l54_completion_slots_m55.py"
spec=importlib.util.spec_from_file_location("m55",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
S=json.loads(m.CONTRACT.read_text(encoding="utf-8"))
M=json.loads(m.SOURCE.read_text(encoding="utf-8"))

class M55CompletionTypingTest(unittest.TestCase):
    def audit_copy(self):
        return m.audit(copy.deepcopy(S),copy.deepcopy(M))
    def rejects(self,change):
        d=copy.deepcopy(S)
        change(d)
        with self.assertRaises(ValueError):
            m.audit(d,copy.deepcopy(M))

    def test_all_six_source_slots_checked(self):
        self.assertEqual(self.audit_copy()["six_policy_qualified_slots"],6)
    def test_source_ids_frozen(self):
        self.assertTrue(self.audit_copy()["m54_symbol_lineage_intact"])
    def test_center_does_not_entail_parent_movement_completed(self):
        self.assertFalse(S["lesson18_semantics"]["formed_center_implies_containing_movement_finished_now"])
    def test_two_hypothetical_worlds_not_market(self):
        self.assertEqual({w["containing_g_movement_finished_at_t"] for w in S["lesson18_semantics"]["countermodels"]},{True,False})
    def test_R_A_author_claim_g5(self):
        self.assertTrue(self.audit_copy()["author_g5"]["R_A"])
    def test_R_B_g5_not_asof(self):
        self.assertFalse(self.audit_copy()["author_g5"]["R_B"])
    def test_R_B_author_claim_g6(self):
        self.assertTrue(self.audit_copy()["author_g6"]["R_B"])
    def test_all_independent_completion_receipts_missing(self):
        self.assertEqual(self.audit_copy()["market_movement_certifications"],0)
    def test_wrong_group_member_rejected(self):
        self.rejects(lambda d:d["group_slots"][0]["source_group_members"].__setitem__(0,"fake"))
    def test_removed_policy_group_rejected(self):
        self.rejects(lambda d:d["group_slots"].pop())
    def test_duplicate_source_slot_rejected(self):
        self.rejects(lambda d:d["group_slots"][0].__setitem__("slot_id","R_A:G2"))
    def test_fake_completed_movement_receipt_rejected(self):
        self.rejects(lambda d:d["group_slots"][0].__setitem__("independent_movement_completion_receipt",{"complete":True}))
    def test_fake_raw_digest_rejected(self):
        self.rejects(lambda d:d["group_slots"][1].__setitem__("raw_source_digest","fake"))
    def test_fake_asof_timestamp_rejected(self):
        self.rejects(lambda d:d["group_slots"][2].__setitem__("market_first_known","g5"))
    def test_fake_strict_f1_f2_R_rejected(self):
        self.rejects(lambda d:d["group_slots"][3].__setitem__("strict_f1_f2_R_receipt","fake"))
    def test_center_mislabeled_as_movement_rejected(self):
        self.rejects(lambda d:d["group_slots"][4].__setitem__("source_typed_role","FINISHED_G_MOVEMENT"))
    def test_coarse_segment_mislabeled_strict_rejected(self):
        self.rejects(lambda d:d["group_slots"][5].__setitem__("coarse_segmentation_grade","STRICT_COMPLETE"))
    def test_full_chart_to_prefix_overclaim_rejected(self):
        self.rejects(lambda d:d["full_chart_vs_prefix"].__setitem__("author_assumption","EVERY_PREFIX_PROVEN"))
    def test_overwrite_R_B_g5_future_claim_rejected(self):
        self.rejects(lambda d:d["checkpoints"][0]["author_attested"].__setitem__("R_B",True))
    def test_fake_verified_market_status_rejected(self):
        self.rejects(lambda d:d["checkpoints"][1]["market_verified"].__setitem__("R_A","VERIFIED"))
    def test_L20_two_centers_not_automatically_implied(self):
        self.rejects(lambda d:d["phi20_proof_missing"].remove("TWO_INDEPENDENT_CONSECUTIVE_VALID_G_CENTERS"))
    def test_unauthorized_real_market_claim_rejected(self):
        self.rejects(lambda d:d["guard_flags"].__setitem__("market_completion_claim",True))
    def test_unauthorized_phi20_completion_rejected(self):
        self.rejects(lambda d:d["guard_flags"].__setitem__("phi20_solution",True))
    def test_m54_external_source_mutation_fails(self):
        src=copy.deepcopy(M)
        src["policies"][0]["groups"][0][0]="fake"
        with self.assertRaises(ValueError):
            m.audit(copy.deepcopy(S),src)

if __name__=="__main__":
    unittest.main()
