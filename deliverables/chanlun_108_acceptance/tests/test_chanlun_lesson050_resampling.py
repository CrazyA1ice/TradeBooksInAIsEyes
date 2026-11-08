import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson050_resampling.py"))
ema=m["ema"];example=m["example"]
class Resample(unittest.TestCase):
 def test_noncommuting_smoothing(self):
  self.assertNotEqual(example()["raw_ema_last"],example()["coarse_ema_last"])
 def test_last_ema_exact(self):
  self.assertEqual(ema([0,10,0,10],.5)[-1],6.25)
 def test_constant_prices_stay_constant(self):
  self.assertEqual(ema([5,5,5],.5),[5,5,5])
 def test_bad_input_rejected(self):
  with self.assertRaises(ValueError):ema([],0.5)
 def test_not_market_macd(self):
  self.assertFalse(example()["actual_macd_or_market_data_used"])
if __name__=="__main__":unittest.main()
