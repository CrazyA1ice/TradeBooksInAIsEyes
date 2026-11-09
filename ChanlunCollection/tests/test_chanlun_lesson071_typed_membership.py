import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson071_typed_membership.py"))
E=m["Element"];gate=m["containment_decision"];boundary=m["three_stroke_boundary"];example=m["example"]
class Types(unittest.TestCase):
 def test_strict_same_sequence(self):self.assertEqual(example()["same"],"ELIGIBLE_CONTAINMENT")
 def test_auxiliary_not_merged(self):self.assertEqual(example()["auxiliary"],"NOT_ELIGIBLE_NONSTRICT")
 def test_cross_sequence_not_merged(self):self.assertEqual(example()["cross"],"NOT_ELIGIBLE_CROSS_SEQUENCE")
 def test_same_sequence_disjoint(self):
  self.assertEqual(gate(E("a","STRICT",0,1,1),E("a","STRICT",2,3,2)),"NOT_CONTAINING")
 def test_pending_third(self):self.assertEqual(example()["third_pending"]["status"],"PENDING_THIRD_STROKE")
 def test_third_breaks_first_end(self):self.assertEqual(example()["third_completed"]["status"],"LOCAL_NEW_SEGMENT")
 def test_old_segment_continues(self):self.assertEqual(boundary(10,8,11,True,9)["status"],"LOCAL_OLD_SEGMENT_CONTINUES")
 def test_undetermined_range(self):self.assertEqual(boundary(10,8,9,True,9)["status"],"PENDING_DIRECTION")
 def test_no_direction(self):
  with self.assertRaises(ValueError):boundary(10,10,11,True,9)
 def test_cannot_confirm_without_timestamp(self):
  with self.assertRaises(ValueError):boundary(10,8,7,True)
 def test_not_full_parser(self):self.assertFalse(example()["third_completed"]["full_segment_parser"])
if __name__=="__main__":unittest.main()
