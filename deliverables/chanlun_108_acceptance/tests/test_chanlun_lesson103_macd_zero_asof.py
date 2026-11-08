import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson103_macd_zero_asof.py"))
f=m["filter_zero_axis"];e=m["example"]
class MACD(unittest.TestCase):
 def test_defensive(self):self.assertEqual(e()["negative"]["state"],"DEFENSIVE_RISK_FLAG")
 def test_mixed(self):self.assertEqual(e()["mixed"]["state"],"MIXED_UNCERTAIN")
 def test_future_pending(self):self.assertEqual(e()["future"]["state"],"PENDING_COMPLETED_BAR")
 def test_above(self):self.assertEqual(f(.2,.4,10,10,30)["state"],"ABOVE_ZERO")
 def test_exact_zero_mixed(self):self.assertEqual(f(0,0,10,10,60)["state"],"MIXED_UNCERTAIN")
 def test_bad_period(self):
  with self.assertRaises(ValueError):f(1,1,1,1,0)
 def test_not_finite(self):
  with self.assertRaises(ValueError):f(float("nan"),0,1,1,60)
 def test_no_auto_order(self):self.assertIsNone(e()["negative"]["order"])
 def test_no_backtest(self):self.assertFalse(e()["negative"]["backtest"])
if __name__=="__main__":unittest.main()
