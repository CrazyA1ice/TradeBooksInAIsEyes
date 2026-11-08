import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson081_pen_rule_versions.py"))
C=m["Conditions"];old=m["old_rule"];new=m["proposed_new_rule"];compare=m["compare"];e=m["example"]
class Version(unittest.TestCase):
 def test_old_reject_new_accept(self):
  self.assertEqual(e()["after_proposal"]["old"],"LOCAL_REJECT")
  self.assertEqual(e()["after_proposal"]["new_proposal"],"LOCAL_ELIGIBLE")
 def test_new_not_eligible_before_post(self):self.assertFalse(e()["historical"]["new_known_at_decision"])
 def test_new_available_after_post(self):self.assertTrue(e()["after_proposal"]["new_known_at_decision"])
 def test_shared_kline_blocks_both(self):
  x=C(True,True,4);self.assertEqual(old(x),"LOCAL_REJECT");self.assertEqual(new(x),"LOCAL_REJECT")
 def test_raw_bars_insufficient(self):self.assertEqual(new(C(False,True,2)),"LOCAL_REJECT")
 def test_old_independent_satisfied(self):self.assertEqual(old(C(False,True,4)),"LOCAL_ELIGIBLE")
 def test_old_independent_missing(self):self.assertEqual(old(C(False,False,4)),"LOCAL_REJECT")
 def test_negative_count(self):
  with self.assertRaises(ValueError):C(False,True,-1)
 def test_exact_posting_timestamp(self):self.assertTrue(compare(C(False,True,3),"2007-09-18 22:53:57")["new_known_at_decision"])
 def test_not_full_pen(self):self.assertFalse(e()["after_proposal"]["full_pen_parser"])
if __name__=="__main__":unittest.main()
