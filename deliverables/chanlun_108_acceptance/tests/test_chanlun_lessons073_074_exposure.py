import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lessons073_074_exposure.py"))
Holding=m["Holding"];classify=m["policy_exposure"];exit_gate=m["gap_exit"];example=m["example"]
class Risk(unittest.TestCase):
 def test_zero_cost_still_has_value_risk(self):self.assertEqual(example()["loss"],160)
 def test_broad_exposure_synthetic(self):self.assertEqual(example()["broad"],"BROAD_MARKET_EXPOSURE")
 def test_local_exposure_synthetic(self):self.assertEqual(example()["local"],"LOCAL_SECTOR_EXPOSURE")
 def test_uncertain_risk_class(self):self.assertEqual(classify(2,5),"UNKNOWN")
 def test_bad_breadth(self):self.assertEqual(classify(6,5),"UNKNOWN")
 def test_no_overnight_hypothetical_fill(self):self.assertEqual(example()["gap"],"NOT_EXECUTABLE_OR_UNFILLED")
 def test_only_actual_fill_after_open(self):self.assertEqual(exit_gate(1,4,4,True),"FILLED_AT_MARKET_TIME")
 def test_unauthorized_preopen_fill(self):self.assertEqual(exit_gate(1,4,3,True),"NOT_EXECUTABLE_OR_UNFILLED")
 def test_negative_holding_rejected(self):
  with self.assertRaises(ValueError):Holding(-1,10)
 def test_no_real_orders(self):self.assertFalse(example()["orders_sent"])
if __name__=="__main__":unittest.main()
