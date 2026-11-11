import json
import unittest
from copy import deepcopy
from tools.audit_chanlun_recursive_center_333_author_reply import SPEC,REPORT,audit,overlap,envelope
class TestAuthor333(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=json.loads(SPEC.read_text(encoding="utf-8"))
  cls.report=REPORT.read_text(encoding="utf-8")
 def rejects(self,modify):
  data=deepcopy(self.source)
  modify(data)
  with self.assertRaises(ValueError):audit(data,self.report)
 def test_grounded_replies(self):
  self.assertEqual(audit(self.source,self.report)["replies"],5)
 def test_grouped_operator_noncommutes(self):
  e=self.source["illustrative_math"]
  xs=e["raw_lower_unit_ranges"]
  self.assertEqual(overlap(xs),[6,8])
  self.assertEqual(overlap([envelope(xs[i:i+3]) for i in range(0,9,3)]),[2,12])
 def test_empty_intervals_rejected(self):
  with self.assertRaises(ValueError):overlap([])
 def test_inverted_interval_rejected(self):
  with self.assertRaises(ValueError):envelope([[8,2]])
 def test_early_pdf_not_assumed_original(self):
  self.rejects(lambda x:x["provenance"].update(original_sina_comments_cryptographically_authenticated=True))
 def test_expert_identity_unverified(self):
  self.rejects(lambda x:x["provenance"].update(expert_original_post_authenticated=True))
 def test_no_laohu(self):
  self.rejects(lambda x:x["provenance"].update(laohu_pdf_or_docx_examined=True))
 def test_copyright_no_redistribution(self):
  self.rejects(lambda x:x["provenance"].update(early_compilation_copyright_text_or_pdf_redistributed=True))
 def test_may21_timestamp_cannot_be_july(self):
  self.rejects(lambda x:x["new_author_reply_chronology"][0].update(posted_at="2007-07-21 16:41:03"))
 def test_july31_two_questions_must_separate(self):
  self.rejects(lambda x:x["new_author_reply_chronology"][3].update(posted_at="2007-07-31 16:43:17"))
 def test_nonexistent_author_legal_second_rule(self):
  self.rejects(lambda x:x["operator_contract"].update(author_claims_two_equally_valid_competing_center_axioms=True))
 def test_no_raw_nine_fold_equivalence(self):
  self.rejects(lambda x:x["operator_contract"].update(equal_output_guaranteed=True))
 def test_required_completed_membership(self):
  self.rejects(lambda x:x["operator_contract"].update(completed_submovement_gate_required=False))
 def test_no_forged_source_claim(self):
  self.rejects(lambda x:x["additional_original_course_anchors"][0].update(id="FAKE-SOURCE"))
 def test_no_wrong_author_pdf_page(self):
  self.rejects(lambda x:x["additional_original_course_anchors"][1].update(pages=[999]))
 def test_nine_fold_raw_not_higher_real_center(self):
  self.rejects(lambda x:x["illustrative_math"].update(kind="VALID_REAL_MARKET_CHANLUN_9_BARS"))
 def test_cannot_claim_author_name_for_the_expert(self):
  self.rejects(lambda x:x["interpretation_update"].update(expert_identity_of_second_method="PROVEN"))
 def test_open_unique_proof(self):
  self.rejects(lambda x:x["open"].remove("OB38_OPEN"))
if __name__=="__main__":unittest.main()
