import runpy,unittest
from pathlib import Path
f=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson035_recursion_and_associativity.py"))
d=f["demo"];eq=f["has_three_consecutive_equal"];flat=f["flat"]
class RecursiveLogicTests(unittest.TestCase):
 def test_concat_associative_not_commutative(self):
  x=d();self.assertEqual(x["flat_sequence"],["a","b","c"])
 def test_different_groupings_have_same_flat_sequence(self):
  self.assertEqual(flat((("a","b"),"c")),flat(("a",("b","c"))))
 def test_base_case_may_not_appear(self):
  self.assertTrue(eq([2,2,2]));self.assertFalse(eq([2,3,4,5]))
 def test_equal_nonadjacent_not_base_case(self):
  self.assertFalse(eq([2,3,2,3,2]))
 def test_full_parser_not_proven(self):
  self.assertFalse(d()["unique_market_segmentation_proven"])
 def test_not_historical_trading(self):
  self.assertFalse(d()["actual_market_data_used"])
if __name__=="__main__":unittest.main()
