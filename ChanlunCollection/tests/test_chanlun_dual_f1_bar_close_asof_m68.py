"""M68: source-derived first-known for trades and FULLY closed bars, separate f1 domains."""
import copy
import json
import unittest
from pathlib import Path
from tools.audit_chanlun_dual_f1_bar_close_asof_m68 import (
    SPEC, OLD, audit, inspect, first_known, witnesses, TRUE_STATE,
)

class M68ThreeInitializers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(SPEC.read_text(encoding="utf-8"))
        cls.src=witnesses()
        cls.cases={x["id"]:x for x in cls.data["cases"]}

    def test_actual_sources_are_same_prior_v434_synthetic_tape(self):
        self.assertEqual(len(self.src),3)
        self.assertEqual(self.src["W17_YES_35_NO"]["prices"],["10","14","11","15","12","16"])
        self.assertFalse(self.src["W17_YES_35_NO"]["market_actual"])
        self.assertTrue(self.data["distinction"]["bar_complete_must_have_a_separate_close_receipt"])

    def test_all_nine_recompute_prior_source_predicates_asof(self):
        self.assertEqual(len(self.cases),9)
        for case in self.cases.values():
            with self.subTest(case=case["id"]):
                actual=inspect(self.src[case["witness"]],case["bar_close_first_known"],case["asof"])
                self.assertEqual(actual["states"],case["expected"])
                self.assertFalse(actual["source_authenticated"])
                self.assertEqual(actual["base_pan_exit"],"OPEN")

    def test_kline_future_bar_trades_must_not_be_used_until_close(self):
        before=self.cases["W17_PREFIX_BEFORE_BAR3_CLOSE"]
        after=self.cases["W17_FINAL_BAR_CLOSED"]
        a=inspect(self.src[before["witness"]],before["bar_close_first_known"],before["asof"])
        b=inspect(self.src[after["witness"]],after["bar_close_first_known"],after["asof"])
        self.assertEqual(a["closed_bars"],2)
        self.assertEqual(b["closed_bars"],3)
        self.assertEqual(a["states"]["L17_UNIT_BAR"],"NOT_ESTABLISHED_IN_PREFIX")
        self.assertEqual(b["states"]["L17_UNIT_BAR"],TRUE_STATE)

    def test_trade_equal_prints_need_not_wait_for_close(self):
        at_three=self.cases["W35_STRICT_BEFORE_FIRST_BAR_CLOSED"]
        actual=inspect(self.src[at_three["witness"]],at_three["bar_close_first_known"],at_three["asof"])
        self.assertEqual(actual["closed_bars"],0)
        self.assertEqual(actual["states"]["L35_TICK_STRICT"],TRUE_STATE)
        self.assertEqual(actual["states"]["L17_UNIT_BAR"],"NOT_ESTABLISHED_IN_PREFIX")

    def test_late_close_and_first_known_change_without_price_change(self):
        early=self.cases["W17_FINAL_BAR_CLOSED"]
        late=self.cases["LATE_CLOSE_RECEIPT_NOT_IN_PREFIX"]
        self.assertEqual(early["witness"],late["witness"])
        self.assertEqual(early["asof"],late["asof"])
        self.assertNotEqual(inspect(self.src[early["witness"]],early["bar_close_first_known"],7)["states"]["L17_UNIT_BAR"],
                            inspect(self.src[late["witness"]],late["bar_close_first_known"],7)["states"]["L17_UNIT_BAR"])
        self.assertEqual(first_known(self.src[late["witness"]],late["bar_close_first_known"])["L17_UNIT_BAR"],10)

    def test_exact_first_known_three_original_witnesses(self):
        for k,exp in self.data["expected_asof_first_known"].items():
            case=next(c for c in self.data["cases"] if c["witness"]==k and not c["id"].startswith("LATE_"))
            self.assertEqual(first_known(self.src[k],case["bar_close_first_known"]),exp)

    def test_practical_segment_cannot_be_derived_from_unitbar_or_tick(self):
        for case in self.cases.values():
            actual=inspect(self.src[case["witness"]],case["bar_close_first_known"],case["asof"])
            self.assertEqual(actual["states"]["L60_PRACTICAL_SEGMENT"],"NO_SEGMENT_EVIDENCE")
            self.assertFalse(actual["f2_completed_child"])

    def test_no_premature_bar_close_receipt(self):
        case=self.cases["W17_FINAL_BAR_CLOSED"]
        with self.assertRaisesRegex(ValueError,"bar-close receipt cannot predate"):
            inspect(self.src[case["witness"]],[2,5,7],7)

    def test_no_future_time_or_float_clock(self):
        w=self.src["W17_YES_35_NO"]
        with self.assertRaisesRegex(ValueError,"nonnegative"):
            inspect(w,[3,5,7],-1)
        with self.assertRaisesRegex(ValueError,"nonnegative"):
            inspect(w,[3,5,7],3.5)
        with self.assertRaisesRegex(ValueError,"typed"):
            inspect(w,[3,"5",7],7)

    def test_source_tape_cannot_be_changed_with_same_id(self):
        bad=copy.deepcopy(self.src["W17_YES_35_NO"])
        bad["prices"][0]="999"
        with self.assertRaisesRegex(ValueError,"cannot replace prior"):
            inspect(bad,[3,5,7],7)

    def test_no_claimed_market_or_finished_root_pan(self):
        w=self.src["W17_YES_35_NO"]
        for kw in ({"claims_market":True},{"claims_pan_finished":True},
                   {"claims_f2_child_finished":True}):
            with self.subTest(kw=kw):
                with self.assertRaisesRegex(ValueError,"cannot forge"):
                    inspect(w,[3,5,7],7,**kw)

    def test_no_source_grade_laundering(self):
        with self.assertRaisesRegex(ValueError,"prior artificial"):
            inspect(self.src["W17_YES_35_NO"],[3,5,7],7,source_grade="PROVIDER_AUTHENTICATED")

    def test_prior_real_f01_and_dual_checkers_reexecuted(self):
        out=audit(self.data)
        self.assertEqual(out["f01_negatives_reexecuted"],6)
        self.assertEqual(out["F01"],"OPEN")
        self.assertEqual(out["market"],"NOT_RUN")
        self.assertEqual(out["orders"],0)

if __name__=="__main__":
    unittest.main()
