import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson091_four_state_fsm.py"))
P=m["PenState"];allow=m["next_allowed"];rep=m["replay"];e=m["example"]
class StateTests(unittest.TestCase):
 def test_four_states(self):self.assertEqual(e()["canonical_states"],4)
 def test_forward_up(self):self.assertTrue(allow(P(1,1),P(1,0)))
 def test_forward_down(self):self.assertTrue(allow(P(-1,1),P(-1,0)))
 def test_up_pending_continues(self):self.assertTrue(allow(P(1,0),P(1,1)))
 def test_up_pending_reverses(self):self.assertTrue(allow(P(1,0),P(-1,1)))
 def test_down_pending_continues(self):self.assertTrue(allow(P(-1,0),P(-1,1)))
 def test_down_pending_reverses(self):self.assertTrue(allow(P(-1,0),P(1,1)))
 def test_up_skipping_candidate_rejected(self):self.assertFalse(allow(P(1,1),P(-1,1)))
 def test_down_skipping_candidate_rejected(self):self.assertFalse(allow(P(-1,1),P(1,1)))
 def test_invalid_phase_rejected(self):
  with self.assertRaises(ValueError):P(1,2)
 def test_incomplete_data_unknown(self):self.assertEqual(rep([]),"UNKNOWN_NO_CONFIRMED_INPUT")
 def test_valid_path(self):self.assertEqual(e()["valid"],"CANONICAL_GRAMMAR_ACCEPTED_NOT_MARKET_PROOF")
 def test_invalid_path(self):self.assertEqual(e()["invalid"],"INVALID_TRANSITION")
 def test_no_profit_claim(self):self.assertFalse(e()["whole_market_coverage_proven"])
if __name__=="__main__":unittest.main()
