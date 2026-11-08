import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson067_feature_gap.py"))
F=m["Feature"];cls=m["classify"];ex=m["example"]
class Sequence(unittest.TestCase):
 def test_no_gap_local_end(self):self.assertEqual(ex()["no_gap"]["status"],"LOCAL_END_CONDITION_NO_GAP")
 def test_gap_pending(self):self.assertEqual(ex()["with_gap_pending"]["status"],"PENDING_OPPOSITE")
 def test_gap_opposite(self):self.assertEqual(ex()["with_gap_after_opposite"]["status"],"LOCAL_END_CONDITION_WITH_GAP")
 def test_different_end_and_confirmation_time(self):
    r=ex()["with_gap_after_opposite"];self.assertLess(r["candidate_extremum_index"],r["confirmed_at"])
 def test_not_yet_three(self):self.assertEqual(cls([F(1,3,1)])["status"],"PENDING_THREE_FEATURES")
 def test_unordered_indices(self):
    with self.assertRaises(ValueError):cls([F(0,2,0),F(1,3,0),F(0,2,2)])
 def test_missing_late_evidence_time(self):
    with self.assertRaises(ValueError):cls([F(0,1,0),F(2,3,1),F(1,2,2)],opposite_fractal_observed=True,opposite_index=2)
 def test_not_full_segment(self):self.assertFalse(ex()["no_gap"]["full_segment_algorithm_implemented"])
if __name__=="__main__":unittest.main()
