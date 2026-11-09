import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson092_midpoint_monitor.py"))
I=m["Interval"];f=m["monitor"];e=m["example"]
class Monitor(unittest.TestCase):
 def test_center_mid(self):self.assertEqual(e()["outside_unconfirmed"]["center_midpoint"],15)
 def test_sub_mid(self):self.assertEqual(e()["outside_unconfirmed"]["sub_midpoint"],22)
 def test_outside_warning(self):self.assertEqual(e()["outside_unconfirmed"]["warning"],"OUTSIDE_WARNING")
 def test_no_third_point(self):self.assertEqual(e()["outside_unconfirmed"]["structural"],"THIRD_POINT_NOT_CONFIRMED")
 def test_warning_not_sufficient(self):self.assertTrue(e()["outside_unconfirmed"]["third_point_not_inferred_from_midpoint"])
 def test_pending_data(self):self.assertEqual(e()["premature"]["warning"],"PENDING_COMPLETION")
 def test_inside(self):self.assertEqual(f(I(10,20,2),I(11,13,3),3)["warning"],"INSIDE_MONITOR")
 def test_below(self):self.assertEqual(f(I(10,20,2),I(5,13,3),3)["strength"],"MIDPOINT_BELOW")
 def test_equal(self):self.assertEqual(f(I(10,20,2),I(14,16,3),3)["strength"],"MIDPOINT_EQUAL")
 def test_explicit_external_third_point(self):self.assertEqual(f(I(10,20,2),I(19,25,3),3,True)["structural"],"THIRD_POINT_INDEPENDENTLY_CONFIRMED")
 def test_invalid_range(self):
  with self.assertRaises(ValueError):I(20,10,3)
 def test_not_real_market(self):self.assertFalse(e()["market_data"])
if __name__=="__main__":unittest.main()
