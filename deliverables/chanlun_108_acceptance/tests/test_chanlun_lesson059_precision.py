import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson059_precision.py"))
fn=m["quantize"];compare=m["compare"];ex=m["example"]
class Precision(unittest.TestCase):
 def test_truncation_makes_levels_equal(self):self.assertTrue(compare("3994.57","3994.21","TRUNCATE_TOWARD_ZERO")["equal"])
 def test_round_half_up_is_different(self):self.assertFalse(compare("3994.57","3994.21","ROUND_HALF_UP")["equal"])
 def test_exact_cents_is_different(self):self.assertFalse(compare("3994.57","3994.21","EXACT_CENTS")["equal"])
 def test_invalid_policy_rejected(self):
    with self.assertRaises(ValueError):fn("3994.57","UNDEFINED")
 def test_negative_truncate_toward_zero(self):self.assertEqual(str(fn("-1.8","TRUNCATE_TOWARD_ZERO")),"-1")
 def test_bad_quantum_rejected(self):
    with self.assertRaises(ValueError):fn("2","ROUND_HALF_UP",0)
 def test_no_real_data(self):self.assertFalse(ex()["real_market_data_used"])
if __name__=="__main__":unittest.main()
