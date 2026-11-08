import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson078_normalized_view.py"))
R=m["RawSegment"];norm=m["normalize"];ex=m["example"]
class Projection(unittest.TestCase):
 def test_raw_end_retained(self):self.assertEqual(ex()["raw_endpoint"],12)
 def test_extremum_projection(self):self.assertEqual(ex()["derived_endpoint"],15)
 def test_immutable_input(self):self.assertTrue(ex()["raw_unchanged"])
 def test_projection_is_derived(self):self.assertTrue(ex()["derived"]["derived_only"])
 def test_confirmation_not_earlier(self):self.assertEqual(ex()["derived"]["confirmed_at"],4)
 def test_idempotent_projection(self):
  raw=R("x","UP",((1,10),(2,15),(3,12)),4);self.assertEqual(norm(raw),norm(raw))
 def test_downward_extreme(self):
  raw=R("x","DOWN",((1,10),(2,4),(3,8)),4);self.assertEqual(norm(raw)["display_end"],4)
 def test_invalid_time_order(self):
  with self.assertRaises(ValueError):R("x","UP",((1,10),(1,12),(2,15)),3)
 def test_invalid_confirm_at(self):
  with self.assertRaises(ValueError):R("x","UP",((1,10),(2,12),(3,15)),2)
 def test_not_full_parser(self):self.assertFalse(ex()["full_segment_parser"])
if __name__=="__main__":unittest.main()
