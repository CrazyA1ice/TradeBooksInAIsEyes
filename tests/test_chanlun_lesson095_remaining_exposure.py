import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson095_remaining_exposure.py"))
f=m["snapshot"];e=m["example"]
class Exposure(unittest.TestCase):
 def test_initial_cash_recovered(self):self.assertTrue(e()["s"]["initial_cash_recovered"])
 def test_remaining_economic_value(self):self.assertEqual(e()["s"]["remaining_value"],"20")
 def test_remaining_value_falls(self):self.assertEqual(e()["s"]["change_from_prior_mark"],"-80")
 def test_remaining_exposure_nonzero(self):self.assertTrue(e()["s"]["risk_exposure_still_positive"])
 def test_no_profit_guarantee(self):self.assertTrue(e()["s"]["no_guaranteed_wealth"])
 def test_without_recovered_cash(self):self.assertFalse(f(100,50,10,10)["initial_cash_recovered"])
 def test_zero_shares_zero_exposure(self):self.assertFalse(f(100,100,0,10)["risk_exposure_still_positive"])
 def test_negative_price_rejected(self):
  with self.assertRaises(ValueError):f(100,100,10,-1)
 def test_negative_shares_rejected(self):
  with self.assertRaises(ValueError):f(100,100,-1,10)
 def test_no_orders(self):self.assertFalse(e()["orders_sent"])
if __name__=="__main__":unittest.main()
