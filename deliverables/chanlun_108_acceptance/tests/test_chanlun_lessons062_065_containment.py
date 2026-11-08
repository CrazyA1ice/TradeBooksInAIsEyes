import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lessons062_065_containment.py"))
Bar=m["Bar"];contains=m["containment"];reduce=m["ordered_reduce"];fractal=m["fractal_complete"];ex=m["example"]
class Containment(unittest.TestCase):
 def test_nontransitive(self):
    a,b,c=Bar(0,6),Bar(0,10),Bar(4,10)
    self.assertTrue(contains(a,b));self.assertTrue(contains(b,c));self.assertFalse(contains(a,c))
 def test_up_merge_preserves_sources(self):
    x=reduce([(0,6),(0,10),(4,10)],"UP");self.assertEqual(len(x),1);self.assertEqual(x[0].source_indices,(0,1,2));self.assertEqual((x[0].low,x[0].high),(4,10))
 def test_down_merge_differs(self):
    x=reduce([(0,6),(0,10),(4,10)],"DOWN");self.assertEqual((x[0].low,x[0].high),(0,6))
 def test_no_containment_keeps_separate(self):
    self.assertEqual(len(reduce([(1,3),(4,5)],"UP")),2)
 def test_unset_direction_rejected(self):
    with self.assertRaises(ValueError):reduce([(1,3)],"UNKNOWN")
 def test_invalid_interval_rejected(self):
    with self.assertRaises(ValueError):reduce([(3,1)],"UP")
 def test_two_bars_pending(self):
    self.assertEqual(fractal([Bar(1,3),Bar(3,5)])["status"],"PENDING_THIRD_COMPLETED_BAR")
 def test_top_fractal(self):self.assertEqual(ex()["top"]["kind"],"TOP")
 def test_bottom_fractal(self):
    self.assertEqual(fractal([Bar(3,5),Bar(1,3),Bar(2,4)])["kind"],"BOTTOM")
 def test_tie_not_assumed_top(self):
    self.assertEqual(fractal([Bar(1,3),Bar(2,5),Bar(3,4)])["kind"],"UNDETERMINED")
 def test_confirm_time_last_source(self):
    self.assertEqual(ex()["top"]["confirm_source_index"],2)
 def test_not_complete_parser(self):
    self.assertFalse(ex()["full_chanlun_parser_implemented"]);self.assertFalse(ex()["real_market_data_used"])
if __name__=="__main__":unittest.main()
