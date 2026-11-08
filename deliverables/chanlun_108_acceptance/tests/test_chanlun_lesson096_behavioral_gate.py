import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson096_behavioral_gate.py"))
D=m["Decision"];f=m["inspect"];g=m["capital_addition"];e=m["example"]
class Decisions(unittest.TestCase):
 def test_anchor_not_market(self):self.assertEqual(e()["anchor"],"ANCHOR_ONLY_NOT_MARKET_SIGNAL")
 def test_future_rejected(self):self.assertEqual(e()["future"],"FUTURE_DATA_REJECTED")
 def test_loss_topup_rejected(self):self.assertEqual(e()["loss_topup"],"REJECT_UNBUDGETED_TOPUP")
 def test_known_signal(self):self.assertEqual(f(D("KNOWN_MARKET_SIGNAL",9,10)),"AUDITABLE_DECISION_NO_PROFIT_GUARANTEE")
 def test_missing_signal(self):self.assertEqual(f(D("KNOWN_MARKET_SIGNAL",None,10)),"SIGNAL_UNCONFIRMED")
 def test_approved_budget_not_order(self):self.assertEqual(g(D("PRECOMMITTED_RISK_RULE",None,10,True,True)),"BUDGET_REVIEW_REQUIRED")
 def test_unsupported_reason(self):
  with self.assertRaises(ValueError):f(D("BUY_BECAUSE_FEAR",None,10))
 def test_no_real_orders(self):self.assertFalse(e()["orders_sent"])
 def test_no_market_backtest(self):self.assertFalse(e()["market_tested"])
if __name__=="__main__":unittest.main()
