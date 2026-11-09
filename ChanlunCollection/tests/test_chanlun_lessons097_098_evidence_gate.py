import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lessons097_098_evidence_gate.py"))
b=m["observed_branch"];g=m["execution_gate"];e=m["example"]
class ConditionAndExecution(unittest.TestCase):
 def test_future_branch_unknown(self):self.assertEqual(e()["future_unknown"],"WAIT_FOR_EVIDENCE")
 def test_present_retest(self):self.assertEqual(e()["retest"],"RETEST_CONFIRMED")
 def test_present_continue(self):self.assertEqual(b(10,continuation_at=10),"CONTINUATION_CONFIRMED")
 def test_conflict(self):self.assertEqual(b(10,1,2),"CONFLICT_REVIEW")
 def test_tplus1(self):self.assertEqual(e()["tplus1_block"],"EXECUTION_BLOCKED_TPLUS1_OR_INELIGIBLE")
 def test_not_filled_automatically(self):self.assertEqual(e()["unfilled"],"ELIGIBLE_NOT_PROVEN_FILLED")
 def test_not_approved(self):self.assertEqual(g("RETEST_CONFIRMED",False,100,10),"PLAN_NOT_APPROVED")
 def test_no_signal(self):self.assertEqual(g("WAIT_FOR_EVIDENCE",True,100,10),"WAIT_FOR_SIGNAL")
 def test_filled(self):self.assertEqual(g("CONTINUATION_CONFIRMED",True,100,10,10),"FILLED")
 def test_partial(self):self.assertEqual(g("CONTINUATION_CONFIRMED",True,100,10,5),"PARTIAL_OR_UNFILLED")
 def test_overfill_rejected(self):
  with self.assertRaises(ValueError):g("CONTINUATION_CONFIRMED",True,100,10,11)
 def test_no_orders(self):self.assertFalse(e()["live_market_orders"])
if __name__=="__main__":unittest.main()
