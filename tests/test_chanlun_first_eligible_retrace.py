import json,unittest
from copy import deepcopy
from tools.audit_chanlun_first_eligible_retrace import SPEC, REPORT, audit_spec, inspect_prefix
class TestFirstEligibleRetrace(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=json.loads(SPEC.read_text(encoding="utf-8"));cls.r=REPORT.read_text(encoding="utf-8")
 def denied(self,change):
  x=deepcopy(self.s);change(x)
  with self.assertRaises(ValueError):audit_spec(x,self.r)
 def by(self,id):
  return next(x for x in self.s["synthetic_scenarios"] if x["id"]==id)
 def test_contract_and_cases(self):
  self.assertEqual(audit_spec(self.s,self.r)["synthetic_scenarios"],9)
 def test_inside_then_first_outside(self):
  v=inspect_prefix(self.s["sample_center"],self.by("FAIL_THEN_FIRST_THIRD")["events"],12)
  self.assertEqual([x["state"] for x in v["milestones"]],
                   ["RETURNED_INSIDE_CENTER_OSCILLATION","NEW_THIRD_BUY_CONDITIONAL"])
 def test_prior_failure_does_not_consume_first(self):
  self.assertEqual(inspect_prefix(self.s["sample_center"],self.by("FAIL_THEN_FIRST_THIRD")["events"],6)["state"],
                   "RETURNED_INSIDE_CENTER_OSCILLATION")
 def test_no_future_label_on_extremum(self):
  self.assertEqual(inspect_prefix(self.s["sample_center"],self.by("PREMATURE_AT_HISTORICAL_EXTREMUM")["events"],10)["state"],
                   "AWAITING_RETRACE_COMPLETION")
 def test_label_at_first_known_not_endpoint(self):
  v=inspect_prefix(self.s["sample_center"],self.by("FAIL_THEN_FIRST_THIRD")["events"],12)
  self.assertEqual(v["first_third_known_at"],12)
  self.assertEqual(v["milestones"][1]["historical_retrace_endpoint"],10)
 def test_third_not_repeated_same_center(self):
  self.assertEqual(inspect_prefix(self.s["sample_center"],self.by("LATER_NOT_REPEAT_THIRD")["events"],17)["state"],
                   "LATER_OUTSIDE_RETRACE_NOT_THIRD")
 def test_same_tail_different_prior_history(self):
  s1=self.by("FAIL_THEN_FIRST_THIRD")["events"]
  s2=self.by("SAME_LAST_PAIR_PREV_THIRD")["events"]
  self.assertEqual([(x["leg"],x["low"],x["high"]) for x in s1[2:4]],
                   [(x["leg"],x["low"],x["high"]) for x in s2[2:4]])
  self.assertNotEqual(inspect_prefix(self.s["sample_center"],s1,12)["state"],
                      inspect_prefix(self.s["sample_center"],s2,12)["state"])
 def test_touch_not_erased_by_false_strict_inequality(self):
  self.assertEqual(inspect_prefix(self.s["sample_center"],self.by("EQUALITY_TOUCH")["events"],5)["state"],
                   "BOUNDARY_TOUCH_SEMANTIC_FORK")
 def test_touch_blocks_future_firstness_without_boundary_policy(self):
  self.assertEqual(inspect_prefix(self.s["sample_center"],self.by("FIRSTNESS_BLOCKED_BY_EARLIER_EQUALITY")["events"],12)["state"],
                   "BLOCKED_FIRSTNESS_AFTER_TOUCH")
 def test_unfinished_child_not_author_finished(self):
  self.assertEqual(inspect_prefix(self.s["sample_center"],self.by("UNFINISHED_RETRACE")["events"],5)["state"],
                   "PENDING_DECLARED_CHILD_COMPLETION")
 def test_primary_comment_not_original(self):
  self.denied(lambda x:x["sources"][2].update(role="DIRECT_AUTHOR_SINA_MAIN_POST"))
 def test_malformed_claim_id_rejected(self):
  self.denied(lambda x:x["course_anchors"][3].update(id="FAKE"))
 def test_wrong_pdf_page_rejected(self):
  self.denied(lambda x:x["course_anchors"][4].update(pages=[999]))
 def test_no_original_archive_authentication(self):
  self.denied(lambda x:x["scope_flags"].update(archive_original_sina_comment_database_authenticated=True))
 def test_no_real_market_claim(self):
  self.denied(lambda x:x["scope_flags"].update(real_market_replay_or_backtest=True))
 def test_no_false_closed_proof(self):
  self.denied(lambda x:x["proof_frontier"].update(F01="CLOSED"))
 def test_no_fake_completed_oracle(self):
  self.denied(lambda x:x["operator_scope"].update(no_complete_finished_child_generator=False))
 def test_no_loss_of_weak_equal_bound(self):
  self.denied(lambda x:x["operator_scope"].update(lower_retrace_low_must_not_break_ZG="low > zg"))
 def test_wrong_case_expected_detected(self):
  self.denied(lambda x:x["synthetic_scenarios"][0].update(expected="AUTHOR_CERTIFIED_THIRD"))
 def test_nonsequential_duplicate_rejected(self):
  v=deepcopy(self.by("FAIL_THEN_FIRST_THIRD")["events"])
  v[1]["id"]=v[0]["id"]
  with self.assertRaises(ValueError):inspect_prefix(self.s["sample_center"],v,12)
 def test_wrong_level_rejected(self):
  v=deepcopy(self.by("FIRST_VALID")["events"])
  v[1]["child_level"]="30min"
  with self.assertRaises(ValueError):inspect_prefix(self.s["sample_center"],v,5)
 def test_wrong_policy_rejected(self):
  v=deepcopy(self.by("FIRST_VALID")["events"])
  v[1]["policy_id"]="OTHER_POLICY"
  with self.assertRaises(ValueError):inspect_prefix(self.s["sample_center"],v,5)
 def test_clock_backdate_rejected(self):
  v=deepcopy(self.by("FIRST_VALID")["events"])
  v[1]["first_known"]=2
  with self.assertRaises(ValueError):inspect_prefix(self.s["sample_center"],v,5)
 def test_cannot_fake_authenticated_event_role(self):
  v=deepcopy(self.by("FIRST_VALID")["events"])
  v[0]["source_role"]="AUTHOR_AUTHENTICATED"
  with self.assertRaises(ValueError):inspect_prefix(self.s["sample_center"],v,5)
 def test_market_authenticated_never_true(self):
  self.assertFalse(inspect_prefix(self.s["sample_center"],self.by("FIRST_VALID")["events"],5)["market_authenticated"])
if __name__=="__main__":unittest.main()
