import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lessons093_094_policy_fills.py"))
p=m["plan"];sell=m["sell_gate"];e=m["example"]
class PolicyAndFills(unittest.TestCase):
 def test_conservative(self):self.assertEqual(e()["conservative"],"PARTIAL_EXIT_PLAN")
 def test_oscillation(self):self.assertEqual(e()["oscillation"],"OBSERVE_OSCILLATION_PLAN")
 def test_wait(self):self.assertEqual(p((1,0),10,11,"NO_TRADE"),"WAIT")
 def test_not_target_state(self):self.assertEqual(p((-1,1),10,11,"CONSERVATIVE"),"STATE_NOT_TARGETED")
 def test_future_signal_not_used(self):self.assertEqual(p((1,0),12,11,"CONSERVATIVE"),"SIGNAL_PENDING")
 def test_invalid_profile(self):
  with self.assertRaises(ValueError):p((1,0),10,11,"ALL_IN")
 def test_tplus1_new_position_blocked(self):self.assertEqual(e()["new_shares_blocked"],"RESTRICTED_TPLUS1")
 def test_settled_but_unfilled(self):self.assertEqual(e()["older_settled_unfilled"],"UNFILLED_OR_PARTIAL")
 def test_settled_confirmed_filled(self):self.assertEqual(sell(100,100,50,50),"FILLED")
 def test_partial(self):self.assertEqual(sell(100,100,50,20),"UNFILLED_OR_PARTIAL")
 def test_overfill_rejected(self):
  with self.assertRaises(ValueError):sell(100,100,50,60)
 def test_negative_holding_rejected(self):
  with self.assertRaises(ValueError):sell(-1,0,1)
 def test_no_real_orders(self):self.assertFalse(e()["real_orders"])
if __name__=="__main__":unittest.main()
