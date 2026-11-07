import runpy,unittest
from decimal import Decimal
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson068_boundary_policy.py"))
B=m["Boundary"];f=m["categorize"];ex=m["example"]
class Boundaries(unittest.TestCase):
 def test_all_three_classes(self):
    self.assertEqual({ex()[k]["state"] for k in ("below","equal","above")},{"BELOW","EQUAL","ABOVE"})
 def test_equal_is_not_below(self):self.assertEqual(ex()["equal"]["state"],"EQUAL")
 def test_boundary_known_before_data(self):
    with self.assertRaises(ValueError):f(B(Decimal(10),5,"v1"),9,4)
 def test_nonfinite_input_rejected(self):
    with self.assertRaises(ValueError):f(B(Decimal(10),0,"v1"),"NaN",1)
 def test_nonfinite_boundary_rejected(self):
    with self.assertRaises(ValueError):f(B(Decimal("Infinity"),0,"v1"),5,1)
 def test_rule_version_remains(self):self.assertEqual(ex()["above"]["policy_version"],"v1")
 def test_no_order(self):self.assertFalse(ex()["equal"]["orders_sent"])
if __name__=="__main__":unittest.main()
