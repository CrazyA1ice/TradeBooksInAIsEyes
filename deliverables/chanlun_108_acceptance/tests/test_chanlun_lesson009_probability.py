import runpy
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
demonstrate=runpy.run_path(str(ROOT/"tools/check_chanlun_lesson009_probability.py"))["demonstrate"]
class ProbabilityCounterexampleTests(unittest.TestCase):
    def test_individual_rates_match_book_illustration(self):
        self.assertEqual(demonstrate()["single_failure_rates"],[0.3,0.4,0.3])
    def test_product_is_valid_but_not_conditional_result(self):
        x=demonstrate()
        self.assertAlmostEqual(x["naive_product"],0.036)
        self.assertAlmostEqual(x["joint_screen_failure_rate"],6/55)
        self.assertNotEqual(x["naive_product"],x["joint_screen_failure_rate"])
    def test_this_is_not_empirical_backtest(self):
        self.assertIs(demonstrate()["has_real_market_data"],False)
if __name__=="__main__":unittest.main()
