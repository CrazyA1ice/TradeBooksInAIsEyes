import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson082_fractal_outcome.py"))
C=m["Candidate"];ex=m["example"]
class FractalOutcome(unittest.TestCase):
 def test_fractal_starts_pending(self):self.assertEqual(ex()["first_state"],"PENDING_OUTCOME")
 def test_later_pen_completion(self):self.assertEqual(ex()["final"],"EXTENDED_TO_PEN")
 def test_continuation_other_outcome(self):
  c=C(1);c.event(2,"FRACTAL_OBSERVED");self.assertEqual(c.event(5,"CONTINUATION_CONFIRMED"),"CONTINUATION")
 def test_no_immediate_outcome(self):
  c=C(1)
  with self.assertRaises(ValueError):c.event(2,"PEN_COMPLETED")
 def test_retrocausal_time_rejected(self):
  c=C(3)
  with self.assertRaises(ValueError):c.event(2,"FRACTAL_OBSERVED")
 def test_not_equal_timestamp(self):
  c=C(1);c.event(2,"FRACTAL_OBSERVED")
  with self.assertRaises(ValueError):c.event(2,"PEN_COMPLETED")
 def test_terminal_not_reopened(self):
  c=C(1);c.event(2,"FRACTAL_OBSERVED");c.event(3,"CONTINUATION_CONFIRMED")
  with self.assertRaises(ValueError):c.event(4,"PEN_COMPLETED")
 def test_prior_history_retained(self):self.assertTrue(ex()["first_event_immutable"])
 def test_no_market_model(self):self.assertFalse(ex()["full_pen_detector"])
if __name__=="__main__":unittest.main()
