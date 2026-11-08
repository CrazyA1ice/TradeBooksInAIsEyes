import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson085_provenance_roles.py"))
R=m["Record"];f=m["classify"];ex=m["example"]
class Sources(unittest.TestCase):
 def test_self_legal_no_official(self):self.assertEqual(ex()["legal"],"LEGALITY_NOT_INDEPENDENTLY_ESTABLISHED")
 def test_story_unverified(self):self.assertEqual(ex()["story"],"UNVERIFIED_FIRST_PERSON")
 def test_followup_dated(self):self.assertEqual(ex()["next_day"],"SEPARATE_DATED_SOURCE")
 def test_editor_distinct(self):self.assertEqual(f(R("EDITORIAL_NOTE",341,"2007")),"EDITORIAL_NOT_AUTHOR")
 def test_regulatory_needs_document(self):self.assertEqual(f(R("EXTERNAL_REGULATORY_FINDING",338,"2026")),"UNVERIFIED_EXTERNAL_REFERENCE")
 def test_regulatory_document_explicit(self):self.assertEqual(f(R("EXTERNAL_REGULATORY_FINDING",338,"2026",True)),"CITABLE_EXTERNAL_FINDING")
 def test_invalid_role(self):
  with self.assertRaises(ValueError):R("UNKNOWN",1,"2007")
 def test_never_infer_legal_truth(self):self.assertFalse(ex()["legal_verdict_inferred"])
 def test_no_orders(self):self.assertFalse(ex()["orders_sent"])
if __name__=="__main__":unittest.main()
