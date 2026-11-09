"""Integrated source-scoped lesson67, 71, 78 segment termination audit."""
import importlib.util
import copy
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("f01_segment",ROOT/"tools/audit_chanlun_f01_segment_termination_reconciliation.py")
m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)

class SegmentSourceReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries=m.load(m.FIXTURES)["cases"]
    def row(self,id_):
        return copy.deepcopy(next(z["input"] for z in self.entries if z["input"]["id"]==id_))
    def test_eleventh_source_claim_and_original_volume_role_pins(self):
        self.assertTrue(m.audit_origins())
        self.assertEqual(m.audit()["source_claims"],11)
    def test_nogap_local_endpoint_not_autoconverted_into_source_segment_break(self):
        o=m.gate(self.row("up_no_gap_local_only"))
        self.assertEqual(o["status"],"LOCAL_67_CONDITION_ONLY_REVERSE_SEGMENT_NOT_YET_EVIDENCED")
        self.assertEqual(o["local_feature_condition_confirmed_at"],3)
        self.assertFalse(o["author_full_segment_end_certified"])
    def test_gap_top_needs_later_opposite_before_local_confirmation(self):
        x=m.gate(self.row("up_gap_pending_opposite"))
        self.assertEqual(x["status"],"PENDING_OPPOSITE_FRACTAL_ASOF")
        self.assertIsNone(x["local_feature_condition_confirmed_at"])
        y=m.gate(self.row("up_gap_opposite_arrived_but_not_reverse"))
        self.assertEqual(y["local_feature_condition_confirmed_at"],6)
        self.assertFalse(y["author_finished_lower_trend_certified"])
    def test_declared_reverse_segment_never_is_author_source_certificate(self):
        for id_ in ("up_no_gap_reverse_assumed","up_gap_opposite_and_reverse_declared"):
            x=m.gate(self.row(id_))
            self.assertTrue(x["declared_reversal_seen_asof"])
            self.assertEqual(x["status"],"CONDITIONAL_78_REVERSE_SEGMENT_IF_EXTERNAL_LEGALITY_ACCEPTED_NOT_AUTHOR_CERTIFIED")
            self.assertFalse(x["higher_center_eligible"])
    def test_explicit_time_and_membership_blocks_future_leakage(self):
        self.assertEqual(m.gate(self.row("up_gap_opposite_known_only_in_future"))["status"],
                         "PENDING_OPPOSITE_FRACTAL_ASOF")
        self.assertEqual(m.gate(self.row("down_gap_third_feature_in_future"))["status"],
                         "PENDING_COMPLETED_FEATURES")
        for id_ in ("up_no_gap_aux_feature_blocked","up_no_gap_cross_sequence_blocked"):
            self.assertEqual(m.gate(self.row(id_))["status"],"PENDING_STRICT_FEATURE_MEMBERSHIP")
    def test_bad_reverse_past_timestamp_or_invalid_feature_role_rejected(self):
        x=self.row("up_no_gap_reverse_assumed")
        x["reverse_segment"]["confirmed_at"]=2
        with self.assertRaisesRegex(ValueError,"Reverse segment cannot predate"):
            m.gate(x)
        x=self.row("up_no_gap_local_only")
        x["features"][1]["role"]="AUTHOR_VERIFIED"
        with self.assertRaisesRegex(ValueError,"Malformed"):
            m.gate(x)
    def test_prior_source_limitation_and_finite_all_cases(self):
        r=m.audit()
        self.assertEqual(r["cases"],10)
        self.assertEqual(r["unresolved_original_source_semantics"],4)
        self.assertEqual(r["author_completed_segments"],0)
        self.assertEqual(r["author_completed_lower_trends"],0)
        self.assertEqual(r["market_data"],"NOT_RUN")
    def test_source_editor_scope_unverified_unchanged(self):
        c=m.load(m.CONTRACT)
        self.assertFalse(c["full_original_chart_visuals_verified"])
        self.assertFalse(c["unresolved_editorial_comments_backdated"])
        self.assertFalse(c["complete_Rg_frozen"])
        self.assertTrue(all(x["status"].startswith("OPEN_") for x in c["unresolved_text_scope"]))
if __name__=="__main__":
    unittest.main()
