"""Adversarial checks only; zero original market data or trading."""
import unittest,json
from copy import deepcopy
from tools.audit_chanlun_second_method_disambiguation import SPEC,REPORT,audit,ordered_intersection,envelope
class TestDisambiguation(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=json.loads(SPEC.read_text(encoding="utf-8"));cls.r=REPORT.read_text(encoding="utf-8")
 def deny(self,change):
  s=deepcopy(self.s);change(s)
  with self.assertRaises(ValueError):audit(s,self.r)
 def test_source_pins(self):self.assertEqual(audit(self.s,self.r)["author_source_anchors"],16)
 def test_center_core_vs_rolling_and_envelope(self):
  v=[[5,12],[4,13],[6,11],[8,10]]
  self.assertEqual(ordered_intersection(v[:3]),[6,11])
  self.assertEqual(ordered_intersection(v),[8,10])
  self.assertEqual(envelope(v),[4,13])
 def test_empty_and_inverted_interval_rejected(self):
  with self.assertRaises(ValueError):ordered_intersection([])
  with self.assertRaises(ValueError):ordered_intersection([[12,5]])
 def test_unconfirmed_expert_original(self):self.deny(lambda s:s["provenance"].update(expert_author_public_post_verified=True))
 def test_cannot_certify_unique_second_method(self):self.deny(lambda s:s["provenance"].update(second_method_unique_identity_confirmed=True))
 def test_cannot_forge_sina(self):self.deny(lambda s:s["provenance"].update(original_sina_comment_bytes_verified=True))
 def test_cannot_claim_laohu_read(self):self.deny(lambda s:s["provenance"].update(laohu_edition_bytes_reviewed=True))
 def test_cannot_misclassify_lesson54_as_center_axiom(self):self.deny(lambda s:s["candidate_referents"][0].update(role="COMPETING_INTERVAL_FORMULA"))
 def test_cannot_claim_pure_second_always_superior(self):self.deny(lambda s:s["candidate_referents"][0].update(author_declares_second_pure_center_definition_universally_superior=True))
 def test_cannot_misattribute_lesson20_as_new_formula(self):self.deny(lambda s:s["candidate_referents"][5].update(role="COMPETING_INTERVAL_FORMULA"))
 def test_cannot_bring_g6_into_g5(self):self.deny(lambda s:s["lesson54_author_chart_checkpoints"][1].update(second_cut_higher_center="[d3,g5]"))
 def test_g7_tags_differ(self):self.deny(lambda s:s["lesson54_author_chart_checkpoints"][3].update(second_cut_g7_tag="THIRD_SELL"))
 def test_original_pdf_page(self):self.deny(lambda s:s["original_author_evidence"][11].update(pages=[9999]))
 def test_invented_claim_id(self):self.deny(lambda s:s["original_author_evidence"][12].update(id="INVENTED"))
 def test_market_not_run(self):self.deny(lambda s:s["provenance"].update(market_data_or_backtest_run=True))
 def test_open_frontier(self):self.deny(lambda s:s["special_limits"].remove("OB38_OPEN"))
if __name__=="__main__":unittest.main()
