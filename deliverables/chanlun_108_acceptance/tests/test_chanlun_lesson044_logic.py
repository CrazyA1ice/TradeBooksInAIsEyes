import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson044_logic.py"))
ev=m["evaluate"]; rows=m["truth_table"]; ex=m["counterexample"]
class Necessity(unittest.TestCase):
 def test_necessary_not_sufficient(self):
  r=ev(True,True,False);self.assertTrue(r["necessary"]);self.assertFalse(r["incorrect_sufficiency"])
 def test_missing_necessary_condition_can_reject_greater_reversal(self):
  self.assertFalse(ev(True,False,True)["necessary"])
 def test_no_big_reversal_makes_necessity_vacuously_true(self):
  self.assertTrue(ev(True,False,False)["necessary"])
 def test_full_truth_table(self):
  self.assertEqual(len(rows()),8)
 def test_nothing_construed_as_market_example(self):
  self.assertFalse(ex()["real_market_path_constructed"])
if __name__=="__main__":unittest.main()
