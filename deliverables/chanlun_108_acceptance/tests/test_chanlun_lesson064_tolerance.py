import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson064_tolerance.py"))
near=m["near"];ex=m["example"]
class Tolerance(unittest.TestCase):
 def test_nontransitive(self):
    x=ex();self.assertTrue(x["a_b"] and x["b_c"]);self.assertFalse(x["a_c"])
 def test_symmetric(self):self.assertEqual(near("0.49","0"),near("0","0.49"))
 def test_reflexive(self):self.assertTrue(near("0.31","0.31"))
 def test_boundary_inclusive(self):self.assertTrue(near("1","1.5"))
 def test_boundary_exceeded(self):self.assertFalse(near("1","1.5001"))
 def test_invalid_tolerance(self):
    with self.assertRaises(ValueError):near(1,2,-.1)
 def test_not_market_data(self):self.assertFalse(ex()["real_market_data_used"])
if __name__=="__main__":unittest.main()
