import runpy
import unittest
from pathlib import Path
scope=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson024_macd_partial_area.py"))
check=scope["check"];example=scope["example"]
class PartialAreaAudit(unittest.TestCase):
    def test_same_prefix_different_future(self):
        x=example()
        self.assertEqual((x["observed"],x["estimate_2x"]), (3,6))
        self.assertEqual((x["final_one"],x["final_two"]),(3,15))
    def test_opposite_final_outcomes_under_same_prediction(self):
        x=example()
        self.assertTrue(x["estimate_below_reference"])
        self.assertTrue(x["actual_one_below_reference"])
        self.assertFalse(x["actual_two_below_reference"])
    def test_validation(self):
        for args in [([],[],[],10),([1],[-2],[],10),([1],[],[], -1)]:
            with self.assertRaises(ValueError):check(*args)
    def test_not_a_market_backtest(self):
        self.assertFalse(example()["actual_macd_calculated"])
if __name__=="__main__":unittest.main()
