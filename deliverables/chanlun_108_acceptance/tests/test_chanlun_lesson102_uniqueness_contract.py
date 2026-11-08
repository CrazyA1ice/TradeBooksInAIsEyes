import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson102_uniqueness_contract.py"))
f=m["uniqueness_gate"];e=m["example"]
class Unique(unittest.TestCase):
 def test_unspecified(self):self.assertEqual(e()["underspecified"],"NEEDS_COMPLETE_FORMAL_SPEC")
 def test_two_possible_requires_tiebreak(self):self.assertEqual(e()["two_candidates"],"MULTIPLE_CANDIDATES_REQUIRE_TIEBREAK_PROOF")
 def test_one_candidate_is_only_local(self):self.assertEqual(e()["one_candidate"],"UNIQUE_WITHIN_PROVIDED_CANDIDATES_ONLY")
 def test_empty(self):self.assertEqual(f([],True),"NO_LEGAL_PARSE")
 def test_duplicate_same_candidate(self):self.assertEqual(f([[["a","b"]],[["a","b"]]],True),"UNIQUE_WITHIN_PROVIDED_CANDIDATES_ONLY")
 def test_extra_candidate(self):self.assertEqual(f([[["a"]],[["b"]]],True),"MULTIPLE_CANDIDATES_REQUIRE_TIEBREAK_PROOF")
 def test_not_actual_chanlun(self):self.assertFalse(e()["valid_chanlun_parse_tested"])
if __name__=="__main__":unittest.main()
