import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson099_resegmentation.py"))
S=m["Segment"];c=m["center_asof"];r=m["regroup"];e=m["example"]
class Regrouping(unittest.TestCase):
 def test_future_center_not_confirmed(self):self.assertEqual(e()["early"]["state"],"CENTER_PENDING")
 def test_completed_center(self):self.assertEqual(e()["later"]["state"],"CENTER_CONFIRMED")
 def test_overlap(self):self.assertEqual(e()["later"]["intersection"],(10,12))
 def test_derived_unchanged(self):self.assertTrue(e()["derived"]["source_unchanged"])
 def test_missing_component(self):self.assertEqual(c([S("a",1,0,3)],1)["state"],"CENTER_PENDING")
 def test_touch_only_not_center(self):self.assertEqual(c([S("a",1,0,2),S("b",2,2,3),S("c",3,2,4)],3)["state"],"NO_POSITIVE_OVERLAP")
 def test_invalid_interval(self):
  with self.assertRaises(ValueError):S("a",1,4,1)
 def test_duplicate_partition(self):
  p=[S("a",1,0,4),S("b",2,1,3),S("c",3,2,3)]
  with self.assertRaises(ValueError):r(p,[["a","b"],["b","c"]],3)
 def test_missing_partition(self):
  p=[S("a",1,0,4),S("b",2,1,3),S("c",3,2,3)]
  with self.assertRaises(ValueError):r(p,[["a"],["c"]],3)
 def test_future_regroup_not_retroactive(self):
  p=[S("a",1,0,4),S("b",2,1,3),S("c",3,2,3)]
  self.assertEqual(r(p,[["a"],["b","c"]],2)["state"],"DERIVED_VIEW_PENDING")
 def test_not_full_parser(self):self.assertFalse(e()["full_chanlun_parser"])
if __name__=="__main__":unittest.main()
