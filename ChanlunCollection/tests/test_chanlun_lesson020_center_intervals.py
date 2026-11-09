import runpy
import unittest
from pathlib import Path
ns=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson020_center_intervals.py"))
I=ns["Interval"]; overlap=ns["triple_overlap"]; third=ns["third_buy_candidate"]; ex=ns["synthetic_profit_counterexample"]
class CenterAudit(unittest.TestCase):
    def test_three_way_common_interval(self):
        self.assertEqual(overlap([I(8,12),I(10,14),I(9,11)]),{"status":"positive_width_overlap","lower":10,"upper":11})
    def test_three_way_no_overlap(self):
        self.assertEqual(overlap([I(0,1),I(3,4),I(0,5)])["status"],"no_overlap")
    def test_point_touch_separate_from_positive_width(self):
        self.assertEqual(overlap([I(1,3),I(3,5),I(2,4)])["status"],"point_touch_only")
    def test_unfinished_segment_does_not_confirm_center(self):
        self.assertEqual(overlap([I(1,4),I(2,5),I(2,3,False)])["status"],"pending_uncompleted_lower_level_segment")
    def test_wrong_count_rejected(self):
        with self.assertRaises(ValueError):overlap([I(1,2),I(3,4)])
    def test_invalid_interval_rejected(self):
        with self.assertRaises(ValueError):I(5,4)
    def test_third_buy_strict_and_boundary(self):
        self.assertEqual(third(I(10,11),True,True,11.5),"strictly_above_center_candidate")
        self.assertEqual(third(I(10,11),True,True,11.0),"touching_upper_boundary_candidate")
        self.assertEqual(third(I(10,11),True,True,10.5),"condition_not_met")
    def test_third_buy_waits_for_completed_retest(self):
        self.assertEqual(third(I(10,11),True,False,11.5),"pending_completion")
    def test_geometry_does_not_ensure_profit(self):
        self.assertFalse(ex()["guaranteed_profit"])
        self.assertFalse(ex()["real_market_prices_used"])
if __name__=="__main__":unittest.main()
