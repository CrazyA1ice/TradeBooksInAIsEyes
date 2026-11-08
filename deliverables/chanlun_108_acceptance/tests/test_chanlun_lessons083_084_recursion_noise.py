import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lessons083_084_recursion_noise.py"))
hl=m["high_level"];n=m["near_boundary_sensitivity"];ex=m["example"]
class Recursion(unittest.TestCase):
 def test_two_seeds_produce_different_output(self):self.assertNotEqual(ex()["same_f2_a"],ex()["same_f2_b"])
 def test_exact_base_a(self):self.assertEqual(ex()["same_f2_a"],[1,2,3])
 def test_exact_base_b(self):self.assertEqual(ex()["same_f2_b"],[2,3,4])
 def test_noise_changes_boundary_label(self):self.assertNotEqual(ex()["noise"]["before"],ex()["noise"]["after"])
 def test_no_unproven_robustness(self):self.assertFalse(ex()["noise"]["relative_segment_robustness_proven"])
 def test_no_noise_change(self):self.assertEqual(n(8,.1,10)["before"],n(8,.1,10)["after"])
 def test_negative_noise(self):
  with self.assertRaises(ValueError):n(10,-.1,10)
 def test_f2_output_type(self):
  with self.assertRaises(ValueError):hl(1,lambda x:"X",2)
 def test_no_actual_market(self):self.assertFalse(ex()["real_market_data"])
if __name__=="__main__":unittest.main()
