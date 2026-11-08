import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson101_second_buy.py"))
I=m["Input"];f=m["classify"];e=m["example"]
class Second(unittest.TestCase):
 def test_second_below_first_still_eligible(self):self.assertEqual(e()["weak"]["state"],"SECOND_BUY_ELIGIBLE_LOCAL")
 def test_weak_is_below(self):self.assertEqual(e()["weak"]["price_relation"],"BELOW")
 def test_high_is_above(self):self.assertEqual(e()["strong"]["price_relation"],"ABOVE")
 def test_second_third_needs_external_confirmation(self):self.assertEqual(e()["strong"]["state"],"SECOND_THIRD_COINCIDE")
 def test_no_external_third(self):self.assertEqual(f(I(10,12,1,2,4,5,None,True))["state"],"SECOND_BUY_ELIGIBLE_LOCAL")
 def test_future_third_cannot_match(self):self.assertEqual(f(I(10,12,1,2,4,4,9,True))["state"],"SECOND_BUY_ELIGIBLE_LOCAL")
 def test_equal(self):self.assertEqual(f(I(10,10,1,2,4,4))["price_relation"],"EQUAL")
 def test_incomplete_retest(self):self.assertEqual(e()["incomplete"]["state"],"SECOND_BUY_PENDING")
 def test_missing_leg(self):self.assertEqual(f(I(10,9,1,None,4,4))["state"],"SECOND_BUY_PENDING")
 def test_wrong_order(self):self.assertEqual(f(I(10,9,1,4,3,5))["state"],"SECOND_BUY_PENDING")
 def test_no_real_market(self):self.assertFalse(e()["weak"]["real_market_proof"])
if __name__=="__main__":unittest.main()
