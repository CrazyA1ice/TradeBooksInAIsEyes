import runpy,unittest
from pathlib import Path
ns=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson039_branches.py"))
check=ns["classify_upward_comparison"];demo=ns["synthetic_example"]
class BranchCoverage(unittest.TestCase):
 def test_extending_high_not_automatically_trade(self):
  self.assertEqual(check(10,12,True)["source_coverage"],"NEEDS_FURTHER_CONDITIONS")
 def test_equal_high_uncovered(self):
  x=check(10,10,True);self.assertEqual(x["source_coverage"],"SOURCE_UNSPECIFIED");self.assertIsNone(x["order"])
 def test_non_new_high_uncovered(self):
  x=check(10,9,False);self.assertEqual(x["source_coverage"],"SOURCE_UNSPECIFIED");self.assertIsNone(x["order"])
 def test_pending_divergence(self):self.assertEqual(check(10,12,None)["source_coverage"],"PENDING_DIVERGENCE")
 def test_wrong_divergence_type_rejected(self):
  with self.assertRaises(ValueError):check(10,12,"yes")
 def test_no_market_data(self):self.assertFalse(demo()["uses_real_market_data"])
if __name__=="__main__":unittest.main()
