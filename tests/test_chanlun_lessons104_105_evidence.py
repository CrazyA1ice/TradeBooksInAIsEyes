import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lessons104_105_evidence.py"))
S=m["SourceAssertion"];f=m["theoretical_physics_gate"];g=m["mechanical_gate"];e=m["example"]
class Gates(unittest.TestCase):
 def test_author_analogy_unverified(self):self.assertEqual(e()["analogy"],"ANALOGY_ONLY_UNVERIFIED")
 def test_2010_editor_distinct(self):self.assertEqual(e()["editor_not_author"],"SEPARATE_LATER_EDITORIAL_CLAIM")
 def test_not_real_market_law(self):self.assertFalse(e()["real_market_test"])
 def test_proxy_not_physical_proof(self):
  a=S("ORIGINAL_AUTHOR","2008-03-26 15:47:42","MARKET_GEOMETRY_PHYSICS_ANALOGY")
  self.assertEqual(f(a,"price_std",True),"OPERATIONAL_PROXY_READY_NOT_PHYSICAL_LAW")
 def test_bad_role(self):
  with self.assertRaises(ValueError):S("UNKNOWN","2010","MARKET_GEOMETRY_PHYSICS_ANALOGY")
 def test_rule_unspecified(self):self.assertEqual(g(False,None,10,True,False),"RULE_UNSPECIFIED")
 def test_future_signal_pending(self):self.assertEqual(g(True,11,10,True,False),"NO_ACTION_PENDING")
 def test_risk_rejected(self):self.assertEqual(g(True,2,3,False,False),"RISK_REJECTED")
 def test_without_fill(self):self.assertEqual(e()["mechanical_without_fill"],"ELIGIBLE_NOT_FILLED")
 def test_fill_does_not_prove_profit(self):self.assertEqual(g(True,2,3,True,True),"FILL_EVIDENCE_PRESENT_PNL_UNPROVEN")
if __name__=="__main__":unittest.main()
