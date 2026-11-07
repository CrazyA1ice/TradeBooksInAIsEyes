import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson049_objectives.py"))
fn=m["evaluate"];example=m["example"]
class TargetObjective(unittest.TestCase):
 def test_fast_per_day_not_max_wealth(self):
  x=example();self.assertGreater(x["B"]["rate_per_occupied_day"],x["A"]["rate_per_occupied_day"]);self.assertLess(x["B"]["end_wealth"],x["A"]["end_wealth"])
 def test_expected_wealth(self):
  self.assertAlmostEqual(example()["A"]["end_wealth"],120)
 def test_no_hypothetical_reinvesting(self):
  self.assertTrue(example()["B"]["assume_no_followup_opportunity"])
 def test_invalid_time(self):
  with self.assertRaises(ValueError):fn(100,.1,11,10)
 def test_no_real_data(self):
  self.assertFalse(example()["A"]["real_market_data_used"])
if __name__=="__main__":unittest.main()
