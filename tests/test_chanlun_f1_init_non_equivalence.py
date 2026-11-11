"""Two independent direction witnesses; NO historical trade or market data."""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from tools.audit_chanlun_f1_init_non_equivalence import (
    SPEC, PREVIOUS, REPORT, evaluate_trace, audit
)


class TestF1InitializerNonEquivalence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.old = json.loads(PREVIOUS.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.w = {x["id"]: x for x in cls.spec["witnesses"]}

    def mutate_rejected(self, mutate):
        s = deepcopy(self.spec)
        mutate(s)
        with self.assertRaises(ValueError):
            audit(s, self.old, self.report)

    def test_source_contract_and_witnesses(self):
        self.assertEqual(audit(self.spec, self.old, self.report)["audit"],
                         "PASS_CONSTRUCTIVE_LOCAL_NON_EQUIVALENCE_ONLY")

    def test_17_bar_center_but_not_35_same_tick(self):
        a = self.w["W17_YES_35_NO"]
        x = evaluate_trace(a["prices"], a["bar_ids"])
        self.assertTrue(x["f1_17_3_complete_bars_overlap"])
        self.assertFalse(x["f1_35_3_consecutive_identical_trades"])
        self.assertEqual(x["bar_overlap"], ["12","14"])

    def test_35_same_tick_but_not_17_bar_center(self):
        a = self.w["W35_YES_17_NO"]
        x = evaluate_trace(a["prices"], a["bar_ids"])
        self.assertTrue(x["f1_35_3_consecutive_identical_trades"])
        self.assertFalse(x["f1_17_3_complete_bars_overlap"])
        self.assertIsNone(x["bar_overlap"])

    def test_one_price_bar_overlap_without_three_same_prints(self):
        a = self.w["W_DEGENERATE_17_ONLY"]
        x = evaluate_trace(a["prices"], a["bar_ids"])
        self.assertEqual(x["bar_overlap"], ["11","11"])
        self.assertFalse(x["f1_35_3_consecutive_identical_trades"])

    def test_exactly_three_equal_trades_not_required_in_same_bar(self):
        x = evaluate_trace(["7","7","7","10","12","11","13"], [0,1,1,1,1,2,2])
        self.assertTrue(x["f1_35_3_consecutive_identical_trades"])
        self.assertFalse(x["f1_17_3_complete_bars_overlap"])

    def test_partial_bar_membership_not_ignored(self):
        with self.assertRaises(ValueError):
            evaluate_trace(["10","14","11","15","12","16"], [0,0,2,2,3,3])

    def test_nonchronological_bar_membership_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_trace(["10","14","11","15","12","16"], [0,1,0,1,2,2])

    def test_altering_fixed_bars_changes_author_predicate_and_requires_new_policy(self):
        a = self.w["W17_YES_35_NO"]
        self.assertEqual(evaluate_trace(a["prices"], a["bar_ids"])["bar_overlap"], ["12","14"])
        # Same trade prices, different partition. Must not be treated as the
        # same frozen f1 policy even if the output happens to agree.
        with self.assertRaises(ValueError):
            evaluate_trace(a["prices"], [0,0,1,1,3,3])

    def test_price_float_forbidden(self):
        with self.assertRaises(ValueError):
            evaluate_trace([1.0,"10","10"], [0,1,2])

    def test_price_nan_forbidden(self):
        with self.assertRaises(ValueError):
            evaluate_trace(["10","NaN","10"], [0,1,2])

    def test_price_infinite_forbidden(self):
        with self.assertRaises(ValueError):
            evaluate_trace(["Infinity","1","1"], [0,1,2])

    def test_false_claim_that_bar_center_finishes_pan_rejected(self):
        self.mutate_rejected(lambda s: s["bottom_pan_obligation"].update(
            l17_f1_outputs_center_exists_not_pan_fully_terminated=False))

    def test_false_claim_that_trade_center_finishes_pan_rejected(self):
        self.mutate_rejected(lambda s: s["bottom_pan_obligation"].update(
            l35_f1_outputs_center_exists_not_pan_fully_terminated=False))

    def test_forged_original_sina_verification_rejected(self):
        self.mutate_rejected(lambda s: s["limits"].update(original_sina_first_publication_bytes_verified=True))

    def test_forged_author_source_page_rejected(self):
        self.mutate_rejected(lambda s: s["sources"][0].update(pdf_pages=[99999]))

    def test_forged_l17_date_rejected(self):
        self.mutate_rejected(lambda s: s["sources"][0].update(original_date="2007-03-09"))

    def test_fake_market_replay_rejected(self):
        self.mutate_rejected(lambda s: s["frontier_status"].update(market="DONE"))

    def test_f1_same_outputs_under_all_policies_cannot_be_assumed(self):
        self.mutate_rejected(lambda s: s.update(formal_answer="EQUIVALENT"))

    def test_witness_source_prices_modified_but_expected_overlap_unchanged_rejected(self):
        self.mutate_rejected(lambda s: s["witnesses"][0]["prices"].__setitem__(3,"13"))

    def test_witness_result_forgery_rejected(self):
        self.mutate_rejected(lambda s: s["witnesses"][1].update(f1_17=True))

    def test_frozen_rg_axis_not_silently_collapsed(self):
        self.mutate_rejected(lambda s: s["policy_axes"][1].update(id="AX_F1"))

    def test_no_fictitious_test_can_claim_real_market(self):
        self.mutate_rejected(lambda s: s["witnesses"][2].update(market_actual=True))


if __name__ == "__main__":
    unittest.main()
