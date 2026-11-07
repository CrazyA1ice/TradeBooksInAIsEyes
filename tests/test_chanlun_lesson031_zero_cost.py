import runpy,unittest
from pathlib import Path
f=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson031_zero_cost.py"))
L=f["PositionLedger"]; demo=f["demo"]
class CostRecoveryTests(unittest.TestCase):
 def test_recovery_does_not_remove_remaining_risk(self):
  x=demo();self.assertTrue(x["initial_capital_fully_recovered"]);self.assertFalse(x["zero_economic_risk"])
 def test_wealth_drawdown_is_accounted(self):
  x=demo();self.assertEqual(x["remaining_market_value_drawdown"],800);self.assertEqual(x["wealth_after_price_move"],1200)
 def test_fully_sold_has_no_remaining_stock_exposure(self):
  x=L(100,10,100,20,1).calculate();self.assertTrue(x["zero_economic_risk"]);self.assertEqual(x["remaining_shares"],0)
 def test_invalid_share_count_fails(self):
  with self.assertRaises(AssertionError):L(10,5,12,10,1).calculate()
 def test_synthetic_not_actual(self):
  self.assertFalse(demo()["actual_market_data_used"])
if __name__=="__main__":unittest.main()
