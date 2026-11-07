import runpy
import unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson015_early_classification.py"))
class EarlyDefinitionTests(unittest.TestCase):
    def test_four_nonzero_quadrants(self):
        f=m["classify_early"]
        self.assertEqual(f(10,11,5,6),"up")
        self.assertEqual(f(10,9,5,4),"down")
        self.assertEqual(f(10,11,5,4),"consolidation")
        self.assertEqual(f(10,9,5,6),"consolidation")
    def test_equal_extrema_undefined(self):
        f=m["classify_early"]
        self.assertEqual(f(10,10,5,6),"underdetermined_equal_extremum")
        self.assertEqual(f(10,11,5,5),"underdetermined_equal_extremum")
        self.assertEqual(f(10,10,5,5),"underdetermined_equal_extremum")
    def test_pivot_requires_future_bar(self):
        p=m["local_high_confirmation"]
        self.assertEqual(p([10,12,9,14,8],3),{"occurrence_index":3,"earliest_confirmation_index":4})
        self.assertIsNone(p([10,12,9,14],3))
    def test_no_empirical_claim(self):
        self.assertFalse(m["example"]()["uses_market_history"])
if __name__=="__main__":unittest.main()
