import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lessons088_089_transition_center.py"))
T=m["Transition"];cl=m["classify_geometry"];ex=m["example"]
class TransitionChecks(unittest.TestCase):
 def test_initial_pending(self):
  t=T();self.assertEqual(t.record(1,"OLD_END_CANDIDATE"),"TRANSITION_PENDING")
 def test_new_confirmed_only_on_event(self):self.assertEqual(ex()["state"],"NEW_CONTEXT_CONFIRMED")
 def test_first_event_not_repainted(self):self.assertTrue(ex()["first_event_unchanged"])
 def test_premature_new_event(self):
  with self.assertRaises(ValueError):T().record(1,"NEW_STRUCTURE_CONFIRMED")
 def test_reverse_time(self):
  t=T();t.record(3,"OLD_END_CANDIDATE")
  with self.assertRaises(ValueError):t.record(2,"NEW_STRUCTURE_CONFIRMED")
 def test_same_time(self):
  t=T();t.record(3,"OLD_END_CANDIDATE")
  with self.assertRaises(ValueError):t.record(3,"NEW_STRUCTURE_CONFIRMED")
 def test_center_not_equivalent_movement(self):self.assertTrue(ex()["center_is_component_not_movement"])
 def test_one_complete(self):self.assertEqual(cl(1,True),"CONSOLIDATION_MOVEMENT")
 def test_one_incomplete(self):self.assertEqual(cl(1,False),"MOVEMENT_PENDING")
 def test_two_centers(self):self.assertEqual(cl(2,True),"MULTICENTER_MOVEMENT_CANDIDATE")
 def test_no_centers(self):self.assertEqual(cl(0,True),"NO_COMPLETED_CENTER")
 def test_invalid_count(self):
  with self.assertRaises(ValueError):cl(-1,True)
 def test_not_full_parser(self):self.assertFalse(ex()["full_geometry_parser"])
if __name__=="__main__":unittest.main()
