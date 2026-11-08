import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson046_day_prefix.py"))
inspect=m["inspect"];example=m["example"]
class IntradayPrefix(unittest.TestCase):
 def test_shared_prefix_cannot_identify_end_of_day(self):
  self.assertIsNone(example()["prefix"]["complete_day_any_overlap"])
 def test_same_prefix_different_futures(self):
  x=example();self.assertTrue(x["future_a"]["complete_day_any_overlap"]);self.assertFalse(x["future_b"]["complete_day_any_overlap"])
 def test_actual_window_can_be_confirmed_later(self):
  self.assertGreater(len(example()["future_a"]["confirmed_three_bar_windows"]),0)
 def test_invalid_range_rejected(self):
  with self.assertRaises(ValueError):inspect([[3,2]])
 def test_too_many_bars_rejected(self):
  with self.assertRaises(ValueError):inspect([[1,2]]*9)
 def test_not_full_center_parser(self):
  self.assertFalse(example()["future_a"]["full_center_classification_implemented"])
 def test_not_real_data(self):
  self.assertFalse(example()["prefix"]["real_market_data_used"])
if __name__=="__main__":unittest.main()
