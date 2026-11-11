import json,unittest
from copy import deepcopy
from tools.audit_chanlun_nested_retrace_base_pan import SPEC, REPORT, audit, inspect_nested, bottom_pan_blocked
class TestNestedBase(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads(SPEC.read_text(encoding="utf-8"))
  cls.report=REPORT.read_text(encoding="utf-8")
 def mutate_reject(self,op):
  d=deepcopy(self.d);op(d)
  with self.assertRaises(ValueError):audit(d,self.report)
 def case(self,id):
  return next(x for x in self.d["example_receipts"] if x["id"]==id)
 def test_valid_contract(self):
  self.assertEqual(audit(self.d,self.report)["synthetic_prefix_checks"],8)
 def test_one_parent_two_micro_retraces(self):
  x=inspect_nested(self.d,self.case("S3_TWO_MICRO_PULLBACKS_BUT_NO_EXIT"))
  self.assertEqual((x["observed_micro_retraces"],x["represented_parent_movements"]),(2,1))
 def test_three_components_can_finish_but_not_done(self):
  self.assertEqual(inspect_nested(self.d,self.case("S2_COMPLETE_3_MICRO_NO_EXIT"))["state"],
                   "CAN_FINISH_NOT_ACTUALLY_CERTIFIED")
 def test_two_components_not_minimum(self):
  self.assertEqual(inspect_nested(self.d,self.case("S1_FIRST_MICRO_ONLY"))["state"],
                   "WAITING_MINIMUM_THREE_COMPONENTS")
 def test_unobserved_future_third_component(self):
  self.assertEqual(inspect_nested(self.d,self.case("S7_THREE_LOWER_IN_FUTURE"))["state"],
                   "WAITING_MINIMUM_THREE_COMPONENTS")
 def test_future_parent_finish_not_backdated(self):
  self.assertEqual(inspect_nested(self.d,self.case("S4_DECLARED_EXIT_IN_FUTURE"))["state"],
                   "AWAITING_EXTERNAL_PARENT_FINISH")
 def test_abstract_declaration_at_t12_not_authenticated(self):
  x=inspect_nested(self.d,self.case("S5_DECLARED_EXIT_NOW"))
  self.assertEqual(x["conditional_parent_first_known"],12)
  self.assertFalse(x["market_authenticated"])
  self.assertFalse(x["author_theorem_proved"])
 def test_unfinished_micro_not_parent_finished(self):
  self.assertEqual(inspect_nested(self.d,self.case("S6_ONE_MICRO_COMPONENT_NOT_COMPLETE"))["state"],
                   "LOWER_COMPONENT_UNFINISHED")
 def test_early_declaration_rejected(self):
  with self.assertRaises(ValueError):
   inspect_nested(self.d,self.case("S8_EXIT_EARLIER_THAN_LAST_CHILD"))
 def test_missing_negative_level_base(self):
  self.assertIn("NO_FINISHED_NEGATIVE_LEVEL_CHILD",bottom_pan_blocked(self.d))
 def test_dont_rebrand_archive_as_sina_original(self):
  self.mutate_reject(lambda x:x["reply_evidence"][1].update(role="DIRECT_SINA_AUTHENTICATED_REPLY"))
 def test_wrong_reply_timestamp(self):
  self.mutate_reject(lambda x:x["reply_evidence"][1].update(reply_at="2007-03-20 18:20:10"))
 def test_source_must_match_exact_page(self):
  self.mutate_reject(lambda x:x["original_author_lessons"][0].update(pages=[999]))
 def test_source_must_match_claim(self):
  self.mutate_reject(lambda x:x["original_author_lessons"][1].update(id="FORGED"))
 def test_missing_auth_source_cannot_be_claimed(self):
  self.mutate_reject(lambda x:x["provenance_flags"].update(
      archived_author_reply_original_2007_sina_bytes_verified=True))
 def test_no_completed_market(self):
  self.mutate_reject(lambda x:x["provenance_flags"].update(real_market_data_or_trading_backtest=True))
 def test_no_absolute_base_rule_invented(self):
  self.mutate_reject(lambda x:x["root_panzheng"].update(negative_level_author_initializer_supplied=True))
 def test_a_center_does_not_imply_pan_end(self):
  self.mutate_reject(lambda x:x["bounded_research_model"].update(
      automatic_movement_completion_from_center_present=True))
 def test_two_micro_not_two_parent(self):
  self.mutate_reject(lambda x:x["bounded_research_model"].update(
      two_micro_observations_not_two_parent_complete_retraces=False))
 def test_no_fake_F01_closure(self):
  self.mutate_reject(lambda x:x["proof_status"].update(F01="CLOSED"))
 def test_micro_identity_must_match_parent(self):
  x=deepcopy(self.d)
  x["synthetic_events"][1]["parent_id"]="ANOTHER_PARENT"
  with self.assertRaises(ValueError):
   inspect_nested(x,self.case("S3_TWO_MICRO_PULLBACKS_BUT_NO_EXIT"))
 def test_clock_backdating_in_micro(self):
  x=deepcopy(self.d)
  x["synthetic_events"][2]["first_known"]=3
  with self.assertRaises(ValueError):
   inspect_nested(x,self.case("S3_TWO_MICRO_PULLBACKS_BUT_NO_EXIT"))
 def test_future_unknown_child_is_not_used(self):
  x=inspect_nested(self.d,self.case("S7_THREE_LOWER_IN_FUTURE"))
  self.assertEqual(x["observed_micro_components"],2)
 def test_never_author_certifies_from_external_receipt(self):
  x=deepcopy(self.d)
  c=deepcopy(self.case("S5_DECLARED_EXIT_NOW"))
  c["finish_receipt"]["role"]="ORIGINAL_AUTHOR_VERIFIED"
  with self.assertRaises(ValueError):inspect_nested(x,c)
 def test_open_ob38(self):
  self.mutate_reject(lambda x:x["proof_status"].update(OB38="PROVED"))
if __name__=="__main__":unittest.main()
