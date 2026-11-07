import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson054_connections.py"))
S=m["Segment"];check=m["validate_same_level_group"];ex=m["example"]
class Groupings(unittest.TestCase):
 def test_connector_required_for_same_level(self):self.assertEqual(check([S("CENTER",1),S("CENTER",1)])["status"],"INVALID_SAME_LEVEL_ADJACENCY")
 def test_lower_level_connector_accepted_locally(self):self.assertEqual(check([S("CENTER",1),S("LINK",0),S("CENTER",1)])["status"],"LOCAL_CONNECTOR_CONDITION_SATISFIED")
 def test_same_level_link_not_enough(self):self.assertEqual(check([S("CENTER",1),S("LINK",1),S("CENTER",1)])["status"],"INVALID_SAME_LEVEL_ADJACENCY")
 def test_higher_extension_is_distinct_rule(self):self.assertEqual(check([S("CENTER",1),S("HIGHER_LEVEL_EXTENSION",2),S("CENTER",1)])["status"],"REQUIRES_DIFFERENT_HIGHER_LEVEL_ANALYSIS")
 def test_wrong_token(self):
    with self.assertRaises(ValueError):check([S("UNKNOWN",1)])
 def test_not_full_parser(self):self.assertFalse(ex()["with_connector"]["full_parser_proven"])
 def test_synthetic(self):self.assertFalse(ex()["used_real_market_data"])
if __name__=="__main__":unittest.main()
