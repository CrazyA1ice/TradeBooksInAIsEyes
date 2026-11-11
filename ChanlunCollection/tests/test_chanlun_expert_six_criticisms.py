"""Tests preserve original attribution and distinguish formal theory from live claims.

They do NOT decide whether the expert's unknown original verbatim text is true.
"""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from tools.audit_chanlun_expert_six_criticisms import CATALOG, REPORT, audit


class TestExpertSixCriticisms(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")

    def rejected(self, edit) -> None:
        changed = deepcopy(self.spec)
        edit(changed)
        with self.assertRaises(ValueError):
            audit(changed, self.report)

    def test_source_matrix_six_points(self):
        self.assertEqual(audit(self.spec, self.report)["issues"], 6)

    def test_cannot_forge_verbatim_expert_quote(self):
        self.rejected(lambda s: s["provenance"].update(critic_literal_original_quote_retrieved=True))

    def test_cannot_forge_expert_first_post_url(self):
        self.rejected(lambda s: s["provenance"].update(critic_original_post_url_authenticated=True))

    def test_cannot_claim_15_and_17_are_same_domain_contradiction(self):
        self.rejected(lambda s: s["six_objections"][0].update(
            assessment="SAME_DOMAIN_LOGICAL_CONTRADICTION_PROVEN"))

    def test_one_center_is_not_automatically_completed_pan(self):
        self.rejected(lambda s: s["six_objections"][1].update(
            hard_limit="ONE_CENTER_IS_AUTOMATICALLY_COMPLETE_PAN"))

    def test_f1_change_does_not_disprove_fixed_policy_unique_parse(self):
        self.rejected(lambda s: s["six_objections"][2].update(
            hard_limit="DIFFERENT_F1_DISPROVES_FIXED_RG_UNIQUENESS"))

    def test_l44_small_divergence_is_not_sufficient_for_big_turn(self):
        self.rejected(lambda s: s["six_objections"][3].update(
            hard_limit="SMALL_DIVERGENCE_CERTIFIES_ALL_BIG_TURNS"))

    def test_l83_explicitly_admits_pen_instability(self):
        self.rejected(lambda s: s["six_objections"][4].update(
            assessment="AUTHOR_NEVER_MENTIONED_PEN_UNSTABILITY"))

    def test_l54_l69_some_image_references_exist(self):
        self.rejected(lambda s: s["image_evidence"].update(
            lesson54_html_image_reference_observed=False))

    def test_original_sina_images_have_not_been_verified(self):
        self.rejected(lambda s: s["image_evidence"].update(
            original_sina_image_bytes_independently_authenticated=True))

    def test_l99_midstate_and_l102_completeness_not_silently_identical(self):
        self.rejected(lambda s: s["important_separations"].remove(
            "FINISHED_HISTORICAL_DECOMPOSITION_NOT_SAME_AS_ONLINE_PREFIX_LABEL"))

    def test_third_layer_is_not_falsely_ascribed_to_author(self):
        self.rejected(lambda s: s.update(author_called_our_L3_third_layer_in_original_lesson17=True))

    def test_conditional_prefix_argument_not_global_disproof(self):
        self.rejected(lambda s: s["finite_prefix_lemma"].update(
            scope="NO_LIVE_ALGORITHM_CAN_EVER_EXIST"))

    def test_author_lesson_and_editorial_annotation_are_separate(self):
        self.rejected(lambda s: s["provenance"].update(
            later_editorial_notes_treated_separately=False))

    def test_forged_original_author_source_claim_rejected(self):
        self.rejected(lambda s: s["six_objections"][2]["author_claims"][1].update(
            id="CL33-SO-INVENTED"))

    def test_forged_source_pdf_page_rejected(self):
        self.rejected(lambda s: s["six_objections"][4]["author_claims"][3].update(
            pdf_pages=[999]))

    def test_author_date_timeline_cannot_be_reordered(self):
        def move(s):
            s["author_date_order"][0], s["author_date_order"][1] = (
                s["author_date_order"][1], s["author_date_order"][0])
        self.rejected(move)

    def test_l4_not_treated_as_l3(self):
        self.rejected(lambda s: s["strength_layers"][3].update(
            name="RECURSIVE_FIXED_POLICY_UNIQUENESS_COMPLETE_CLASSIFICATION"))

    def test_open_ob38_not_promoted(self):
        self.rejected(lambda s: s["status"].update(
            fixed_policy_global_unique_parse="PROVEN"))

    def test_open_f01_not_promoted(self):
        self.rejected(lambda s: s["status"].update(
            asof_complete_lower_movement="PROVEN"))

    def test_no_fictitious_market_backtest(self):
        self.rejected(lambda s: s["status"].update(
            market_backtest="DONE"))


if __name__ == "__main__":
    unittest.main()
