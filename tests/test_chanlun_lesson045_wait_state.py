import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson045_wait_state.py"))
State=m["WaitState"]; example=m["example"]
class WaitStates(unittest.TestCase):
 def test_buy_requires_confirmation_and_fill(self):
  x=State();self.assertEqual(x.step("BUY",False,True),"NO_EXECUTION");self.assertEqual(x.position,"HOLD_CASH")
 def test_confirmed_buy_fill_updates_position(self):
  x=State();self.assertEqual(x.step("BUY",True,True),"BOUGHT");self.assertEqual(x.position,"HOLD_STOCK")
 def test_failed_sell_retains_stock(self):
  x=State(position="HOLD_STOCK");x.step("SELL",True,False);self.assertEqual(x.position,"HOLD_STOCK")
 def test_buy_does_not_double_buy(self):
  x=State(position="HOLD_STOCK");self.assertEqual(x.step("BUY",True,True),"INVALID_DIRECTION_NO_EXECUTION")
 def test_sell_updates_cash(self):
  x=State(position="HOLD_STOCK");self.assertEqual(x.step("SELL",True,True),"SOLD");self.assertEqual(x.position,"HOLD_CASH")
 def test_unknown_signal_rejected(self):
  with self.assertRaises(ValueError):State().step("WAIT",True,True)
 def test_no_real_orders(self):
  self.assertFalse(example()["real_orders_sent"])
if __name__=="__main__":unittest.main()
