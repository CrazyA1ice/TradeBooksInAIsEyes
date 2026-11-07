import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lessons072_075_attribution.py"))
C=m["ClaimSource"];f=m["attribute"];ex=m["example"]
class Sources(unittest.TestCase):
 def test_editor_not_original(self):self.assertEqual(ex()["editor"],"EDITORIAL_ARGUMENT_NOT_ORIGINAL_AUTHOR")
 def test_later_dated_post(self):self.assertEqual(ex()["later"],"SEPARATE_DATED_POST")
 def test_anecdote_unverified(self):self.assertEqual(ex()["anecdote"],"UNVERIFIED_NARRATIVE")
 def test_author_only_source_claim(self):self.assertEqual(f(C(73,98,"AUTHOR_ORIGINAL","2007-08-23")),"SOURCE_STATED_NOT_INDEPENDENTLY_VALIDATED")
 def test_independent_evidence_is_explicit(self):self.assertEqual(f(C(75,121,"FIRST_PERSON_ANECDOTE","2007-08-29",True)),"INDEPENDENT_EVIDENCE_PRESENT")
 def test_unknown_role(self):
  with self.assertRaises(ValueError):C(72,88,"AUTHOR_OR_EDITOR","2007")
 def test_never_infer_regulatory_finding(self):self.assertFalse(ex()["regulatory_finding_inferred"])
 def test_no_real_data(self):self.assertFalse(ex()["market_data_used"])
if __name__=="__main__":unittest.main()
