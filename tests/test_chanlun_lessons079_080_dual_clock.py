import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lessons079_080_dual_clock.py"))
f=m["asof_signals"];p=m["opportunity"];e=m["example"]
class AsOf(unittest.TestCase):
 def test_intraday_fractal_pending(self):self.assertEqual(e()["before"]["daily_fractal_status"],"PENDING_DAILY_BAR")
 def test_minute_valid_does_not_force_daily(self):self.assertEqual(e()["before"]["minute_status"],"LOWER_LEVEL_SIGNAL_CONFIRMED")
 def test_future_minute_block(self):
  with self.assertRaises(ValueError):f(1500,1430,1435,"minute_v1")
 def test_rule_identifier_needed(self):
  with self.assertRaises(ValueError):f(1500,1430,1425,None)
 def test_day_close_can_evaluate(self):self.assertEqual(f(1500,1500)["daily_fractal_status"],"READY_TO_EVALUATE_DAILY")
 def test_ready_does_not_mean_fractal_confirmed(self):self.assertFalse(e()["after"]["daily_final_fractal_claimed"])
 def test_selling_not_guaranteed_best(self):self.assertEqual(e()["sell_rises"]["opportunity_cost"],"2")
 def test_price_loss_opportunity_can_be_negative(self):self.assertEqual(p(10,8)["opportunity_cost"],"-2")
 def test_invalid_price(self):
  with self.assertRaises(ValueError):p(-1,10)
 def test_orders_not_sent(self):self.assertFalse(e()["before"]["orders_sent"])
if __name__=="__main__":unittest.main()
