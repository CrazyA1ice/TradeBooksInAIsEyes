import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson077_pen_boundary.py"))
F=m["Fractal"];same=m["same_kind_filter"];pen=m["pen_candidates"];ex=m["example"]
class Pen(unittest.TestCase):
 def test_equal_top_pending(self):self.assertEqual(ex()["equal_tops"]["state"],"TIE_PENDING")
 def test_choose_higher_top(self):self.assertEqual(ex()["higher_top"]["candidate_centers"],[5])
 def test_choose_lower_bottom(self):self.assertEqual(same(F("BOTTOM",3,5),F("BOTTOM",6,2))["candidate_centers"],[6])
 def test_eligible_candidate(self):self.assertEqual(ex()["pen"],"LOCAL_ELIGIBLE_PEN_CANDIDATE")
 def test_shared_three_kline(self):self.assertEqual(pen(F("TOP",3,12),F("BOTTOM",6,5)),"NO_INDEPENDENT_KLINE")
 def test_price_order_invalid(self):self.assertEqual(pen(F("TOP",3,5),F("BOTTOM",7,10)),"INVALID_PRICE_ORDER")
 def test_same_type_invalid(self):self.assertEqual(pen(F("TOP",3,12),F("TOP",7,10)),"NOT_OPPOSITE_FRACTALS")
 def test_time_reversed_invalid(self):self.assertEqual(pen(F("TOP",7,12),F("BOTTOM",3,5)),"BAD_TIME_ORDER")
 def test_invalid_kind(self):
  with self.assertRaises(ValueError):F("UNKNOWN",3,10)
 def test_not_real_market(self):self.assertFalse(ex()["real_market_data"])
if __name__=="__main__":unittest.main()
