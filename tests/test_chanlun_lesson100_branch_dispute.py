import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson100_branch_dispute.py"))
C=m["Claim"];f=m["adjudicate"];e=m["example"]
A=lambda:C("AUTHOR_ORIGINAL","2008-02-25 16:32:23",224,"THIRD_SELL_YES_OR_NO")
B=lambda:C("EDITOR_LATER","2008-02-26 15:14:39",225,"OUTSIDE_TWO_BRANCHES")
class Disagreement(unittest.TestCase):
 def test_review_required(self):self.assertEqual(e()["dispute"],"REVIEW_REQUIRED_NO_INDEPENDENT_DATA")
 def test_separate_roles(self):self.assertNotEqual(e()["author"]["role"],e()["editor"]["role"])
 def test_independent_flag_not_enough(self):self.assertEqual(f(A(),B(),True),"INDEPENDENT_REVIEW_REQUIRED")
 def test_no_counterclaim(self):self.assertEqual(f(A(),C("EDITOR_LATER","2008-02-26",225,"NO_COMMENT")),"NO_RECORDED_COUNTERCLAIM")
 def test_role_swapped(self):
  with self.assertRaises(ValueError):f(B(),A())
 def test_bad_role(self):
  with self.assertRaises(ValueError):C("UNKNOWN","2008",225,"BIFURCATION")
 def test_bad_page(self):
  with self.assertRaises(ValueError):C("AUTHOR_ORIGINAL","2008",226,"BIFURCATION")
 def test_reverse_chronology(self):
  with self.assertRaises(ValueError):f(C("AUTHOR_ORIGINAL","2008-02-27",224,"BIFURCATION"),B())
 def test_bad_original_label(self):
  with self.assertRaises(ValueError):f(C("AUTHOR_ORIGINAL","2008-02-25",224,"CONFIRMED_PROFIT"),B())
 def test_no_backtest(self):self.assertFalse(e()["actual_market_backtest"])
if __name__=="__main__":unittest.main()
