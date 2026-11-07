import runpy
import unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson027_nested_intervals.py"))
C=m["Candidate"];chk=m["check_chain"];demo=m["demo"]
class NestedAudit(unittest.TestCase):
    def test_finite_nested_nonpoint(self):
        x=demo()["valid"]
        self.assertEqual(x["status"],"nested")
        self.assertFalse(x["unique_point"])
        self.assertEqual(x["narrowest"],[3,7])
    def test_non_nested_detected(self):
        self.assertEqual(demo()["invalid"]["status"],"not_nested")
    def test_premature_trading_rejected(self):
        self.assertEqual(demo()["premature"]["status"],"not_yet_tradable")
    def test_invalid_interval(self):
        with self.assertRaises(ValueError):C(5,3,1,2)
    def test_time_ordering(self):
        with self.assertRaises(ValueError):C(0,5,9,4)
    def test_empty_chain(self):
        with self.assertRaises(ValueError):chk([])
    def test_point_touch_handled_without_profit_claim(self):
        x=chk([C(1,4,0,1),C(2,2,1,2)],2)
        self.assertTrue(x["unique_point"])
    def test_no_real_market_data(self):
        self.assertFalse(demo()["real_market_backtest"])
if __name__=="__main__":unittest.main()
