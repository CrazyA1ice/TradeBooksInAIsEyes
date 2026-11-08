import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson090_boll_asof.py"))
b=m["boll"];c=m["classify_squeeze"];ex=m["example"]
class Boll(unittest.TestCase):
 def test_initial_available(self):self.assertEqual(ex()["before"]["state"],"AVAILABLE")
 def test_squeeze(self):self.assertEqual(ex()["squeeze_without_center"]["auxiliary"],"AUXILIARY_SQUEEZE")
 def test_no_structure_from_boll(self):self.assertEqual(ex()["squeeze_without_center"]["geometry"],"CENTER_NOT_CONFIRMED")
 def test_population_mean(self):self.assertAlmostEqual(ex()["before"]["mean"],100)
 def test_no_future_leak(self):
  self.assertEqual(b([100,110,90,999],[1,2,3,4],3),b([100,110,90],[1,2,3],3))
 def test_window_warmup(self):self.assertEqual(b([10,11],[1,2],2,3)["state"],"INSUFFICIENT_WINDOW")
 def test_invalid_duplicated_time(self):
  with self.assertRaises(ValueError):b([10,11],[1,1],2)
 def test_invalid_unsorted_time(self):
  with self.assertRaises(ValueError):b([10,11],[2,1],2)
 def test_invalid_price(self):
  with self.assertRaises(ValueError):b([10,-11],[1,2],2)
 def test_invalid_std_multiplier(self):
  with self.assertRaises(ValueError):b([10,11,9],[1,2,3],3,k=0)
 def test_invalid_squeeze_threshold(self):
  with self.assertRaises(ValueError):c(ex()["before"],ex()["after"],1)
 def test_explicit_geometry_is_separate(self):
  self.assertEqual(c(ex()["before"],ex()["after"],geometry_confirmed=True)["geometry"],"CENTER_BREAK_CONFIRMED")
 def test_no_order(self):self.assertFalse(ex()["orders_sent"])
if __name__=="__main__":unittest.main()
