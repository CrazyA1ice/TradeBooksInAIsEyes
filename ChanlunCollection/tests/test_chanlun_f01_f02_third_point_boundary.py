"""Regression guard for real author textual threshold vs invented strict nonreturn."""
import copy
import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("f01f02",ROOT/"tools/audit_chanlun_f01_f02_third_point_boundary.py")
mod=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(mod)

class LessonBoundaryInterpretationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract=mod.load(mod.CONTRACT)
        cls.cases=mod.load(mod.CASES)["cases"]
    def case(self,name):
        return copy.deepcopy(next(c["input"] for c in self.cases if c["input"]["id"]==name))
    def test_six_source_claims_and_two_original_volume_pages_remain_stable(self):
        mod.source_guard(self.contract)
        self.assertEqual(mod.verify()["cases"],8)
    def test_third_buy_equality_true_while_strict_nonreturn_false(self):
        x=mod.evaluate(self.case("buy_touch_meets_nonbreak_but_not_strict"))
        self.assertTrue(x["third_point_weak_price_condition"])
        self.assertFalse(x["strict_nonreturn_numeric"])
        self.assertTrue(x["point_touch"])
        self.assertFalse(x["author_center_destroyed_certified"])
    def test_third_sell_equality_true_while_strict_nonreturn_false(self):
        x=mod.evaluate(self.case("sell_touch_meets_nonbreak_but_not_strict"))
        self.assertTrue(x["third_point_weak_price_condition"])
        self.assertFalse(x["strict_nonreturn_numeric"])
        self.assertTrue(x["point_touch"])
        self.assertFalse(x["author_third_point_certified"])
    def test_strict_price_boundary_not_center_destroy_or_real_trend(self):
        for n in ("buy_strict_above_numeric_only","sell_strict_below_numeric_only"):
            with self.subTest(n=n):
                x=mod.evaluate(self.case(n))
                self.assertTrue(x["third_point_weak_price_condition"])
                self.assertTrue(x["strict_nonreturn_numeric"])
                self.assertFalse(x["author_center_destroyed_certified"])
                self.assertFalse(x["completed_trajectory_certified"])
    def test_future_low_not_leaked_and_nonfirst_retreat_not_confirmed(self):
        pending=mod.evaluate(self.case("future_completed_low_must_not_leak"))
        self.assertEqual(pending["status"],"PENDING_CHILD_COMPLETION_ASOF")
        self.assertIsNone(pending["third_point_weak_price_condition"])
        second=mod.evaluate(self.case("declared_second_retest_does_not_get_first_status"))
        self.assertEqual(second["status"],"NOT_FIRST_RETEST_DECLARED")
        self.assertIsNone(second["strict_nonreturn_numeric"])
    def test_author_source_role_or_inequality_weakening_forbidden(self):
        wrong=copy.deepcopy(self.contract)
        wrong["numeric_truths"]["third_buy_no_break"]="retest_low > center_ZG"
        with self.assertRaisesRegex(ValueError,"illegally conflated"):
            mod.source_guard(wrong)
        wrong=copy.deepcopy(self.contract)
        wrong["claims"][4]["id"]="CL020-I05"
        with self.assertRaisesRegex(ValueError,"source"):
            mod.source_guard(wrong)
if __name__=="__main__":
    unittest.main()
