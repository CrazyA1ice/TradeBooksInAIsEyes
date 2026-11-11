"""Negative cases show two a0 meanings, no backwards time or forged author exits."""
import json,unittest
from copy import deepcopy
from tools.audit_chanlun_base_pan_cutoff_dual import SPEC,REPORT,audit,inspect_case
class BasePanDual(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=json.loads(SPEC.read_text(encoding="utf-8"))
  cls.r=REPORT.read_text(encoding="utf-8")
 def reject(self,mod):
  s=deepcopy(self.s)
  mod(s)
  with self.assertRaises(ValueError):audit(s,self.r)
 def one(self,id):
  return next(s for s in self.s["synthetic_receipt_cases"] if s["id"]==id)
 def check(self,c):
  return inspect_case({"source_class":"EXTERNAL_SYNTHETIC_UNVERIFIED"},c,self.s)
 def test_complete_source_contract(self):
  self.assertEqual(audit(self.s,self.r)["synthetic_prefix_cases"],10)
 def test_three_real_trade_shaped_events_center_not_finish(self):
  self.assertEqual(self.check(self.one("STRICT_THREE_EQUAL_CENTER_ONLY"))["state"],
                   "CENTER_EXISTS_PAN_TERMINAL_UNKNOWN")
 def test_no_center_before_third_tick(self):
  self.assertEqual(self.check(self.one("STRICT_THREE_EQUAL_BEFORE_END"))["state"],
                   "AWAITING_BASE_CENTER")
 def test_no_same_price_triple(self):
  self.assertEqual(self.check(self.one("STRICT_THREE_PRICE_NOT_IDENTICAL"))["state"],
                   "NO_THREE_EQUAL_PRICE_CENTER")
 def test_wait_future_exit_asof(self):
  self.assertEqual(self.check(self.one("STRICT_ADDITIONAL_EXIT_BEFORE_ARRIVAL"))["state"],
                   "AWAITING_EXTERNAL_EXIT")
 def test_conditional_unverified_author_claim(self):
  x=self.check(self.one("STRICT_EXTERNAL_EXIT_DECLARED_AT5"))
  self.assertEqual(x["conditionally_first_known_at"],5)
  self.assertFalse(x["market_or_author_exit_authenticated"])
 def test_practical_center_missing(self):
  self.assertEqual(self.check(self.one("PRACTICAL_NO_INITIAL_SEGMENT"))["state"],
                   "AWAITING_PRACTICAL_CENTER_SOURCE")
 def test_practical_center_after_asof(self):
  self.assertEqual(self.check(self.one("PRACTICAL_CENTER_NOT_YET_KNOWN"))["state"],
                   "AWAITING_PRACTICAL_CENTER_SOURCE")
 def test_practical_center_is_not_finished_pan(self):
  self.assertEqual(self.check(self.one("PRACTICAL_CENTER_READY_NOT_EXIT"))["state"],
                   "PRACTICAL_CENTER_CONDITIONAL_PAN_TERMINAL_UNKNOWN")
 def test_practical_research_exit_not_author_theorem(self):
  x=self.check(self.one("PRACTICAL_CUTOFF_EXTERNAL_EXIT_T6"))
  self.assertEqual(x["state"],"PRACTICAL_CONDITIONAL_EXIT_UNVERIFIED_NOT_AUTHOR")
  self.assertFalse(x["finite_source_proof_completed"])
 def test_two_futures_have_identical_prefix(self):
  p=self.s["prefix_nonidentifiability"]
  self.assertEqual(len(p["shared_raw_prefix"]),3)
  self.assertGreater(p["possible_future_A"]["observed_at"],p["common_asof"])
  self.assertGreater(p["possible_future_B"]["observed_at"],p["common_asof"])
  self.assertTrue(p["source_existence_of_future_B_not_established"])
 def test_dont_upgrade_archive_to_original_sina_comment(self):
  self.reject(lambda x:x["source_layers"][1].update(kind="ORIGINAL_SINA_VERIFIED_COMMENT"))
 def test_reply_not_original_lesson_body_card(self):
  self.reject(lambda x:x["important_attribution_clarification"].update(
              lesson19_article_claim_card_source_is_not_author_reply=False))
 def test_2006_value_center_not_three_tick_proof(self):
  self.reject(lambda x:x["important_attribution_clarification"].update(
              lesson19_early_value_center_identical_to_lesson35_three_transaction_center="PROVED"))
 def test_exact_lesson60_date(self):
  self.reject(lambda x:x["source_layers"][3].update(original_at="2007-09-17 22:57:16"))
 def test_original_source_claim_id(self):
  self.reject(lambda x:x["original_pdf_source_claim_pins"][0].update(id="INVENTED_CLAIM"))
 def test_source_page_provenance(self):
  self.reject(lambda x:x["original_pdf_source_claim_pins"][9].update(pages=[999]))
 def test_practical_cutoff_is_not_strict_none(self):
  self.reject(lambda x:x["base_contracts"][1].update(
              negative_level_child_movement="DOES_NOT_EXIST_IN_REAL_MARKET"))
 def test_strict_root_has_no_finished_negative_level_type(self):
  self.reject(lambda x:x["base_contracts"][0].update(
              negative_level_child_movement="FULLY_DEFINED_FINISHED_L_MINUS_ONE"))
 def test_cannot_turn_center_into_exit(self):
  self.reject(lambda x:x["separated_propositions"][0].update(not_implies="NOTHING"))
 def test_no_fabricated_market_counterexample(self):
  self.reject(lambda x:x["prefix_nonidentifiability"].update(is_a_market_valid_chanlun_counterexample=True))
 def test_no_authored_total_oracle_claim(self):
  self.reject(lambda x:x["unverified"].update(author_licensed_total_bottom_pan_exit_algorithm=True))
 def test_f01_still_open(self):
  self.reject(lambda x:x["proof_frontier"].update(F01="CLOSED"))
 def test_wrong_external_author_claim_for_practical_policy_rejected(self):
  c=deepcopy(self.one("PRACTICAL_CUTOFF_EXTERNAL_EXIT_T6"))
  c["exit"]["kind"]="EXTERNAL_UNVERIFIED_AUTHOR_END"
  with self.assertRaises(ValueError):self.check(c)
 def test_exit_clock_cannot_precede_center_source(self):
  c=deepcopy(self.one("PRACTICAL_CUTOFF_EXTERNAL_EXIT_T6"))
  c["exit"]["first_known"]=2
  with self.assertRaises(ValueError):self.check(c)
 def test_nonfinite_real_price_rejected(self):
  c=deepcopy(self.one("STRICT_THREE_EQUAL_CENTER_ONLY"))
  c["amended_prices"]=["NaN","8.00","8.00"]
  with self.assertRaises(ValueError):self.check(c)
 def test_wrong_source_assumption_rejected(self):
  with self.assertRaises(ValueError):
   inspect_case({"source_class":"AUTHOR_MARKET_CERTIFIED"},
                self.one("STRICT_THREE_EQUAL_CENTER_ONLY"),self.s)
if __name__=="__main__":unittest.main()
