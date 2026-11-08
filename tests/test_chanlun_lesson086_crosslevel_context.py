import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson086_crosslevel_context.py"))
f=m["contextualize"];ex=m["example"]
class Gate(unittest.TestCase):
 def test_rising(self):self.assertEqual(ex()["rising"]["state"],"RISK_WARNING")
 def test_falling(self):self.assertEqual(ex()["falling"]["state"],"FALLING_CONTEXT")
 def test_oscillating(self):self.assertEqual(ex()["oscillating"]["state"],"OSCILLATION_BRANCH")
 def test_unknown_pending(self):self.assertEqual(ex()["unknown"]["state"],"HIGHER_CONTEXT_PENDING")
 def test_future_higher_rejected(self):self.assertEqual(f("CENTER_RISING","THIRD_SELL",20,21,15)["state"],"HIGHER_CONTEXT_PENDING")
 def test_future_lower_rejected(self):self.assertEqual(f("CENTER_RISING","THIRD_SELL",20,10,21)["state"],"LOWER_EVENT_PENDING")
 def test_missing_lower_rejected(self):self.assertEqual(f("CENTER_RISING","THIRD_SELL",20,10)["state"],"LOWER_EVENT_PENDING")
 def test_bad_parent(self):
  with self.assertRaises(ValueError):f("INVALID","THIRD_SELL",20,10,10)
 def test_no_orders(self):self.assertIsNone(ex()["rising"]["order"])
 def test_no_market_data(self):self.assertFalse(ex()["real_market_data"])
if __name__=="__main__":unittest.main()
