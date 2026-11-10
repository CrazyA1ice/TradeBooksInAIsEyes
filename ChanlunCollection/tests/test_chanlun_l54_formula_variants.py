"""Regression: L54 textual witnesses and endpoint repairs cannot be over-attributed."""
from copy import deepcopy
import json
import unittest

from tools.verify_chanlun_l54_formula_variants import (
    RECORD, PREVIOUS, EVIDENCE, REPORT, endpoint_span, endpoints, is_contiguous, validate
)


class Lesson54VariantWitnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.witness = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
        cls.lesson = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")

    def expect_invalid(self, modify):
        item = deepcopy(self.witness)
        modify(item)
        with self.assertRaises(ValueError):
            validate(item, self.previous, self.lesson, self.report)

    def test_authored_witnesses_pass(self):
        validate(self.witness, self.previous, self.lesson, self.report)

    def test_right_hand_end_is_d3(self):
        self.assertEqual(
            endpoint_span(self.witness["path_semantics"]["right_hand_segments"]),
            ("g0", "d3")
        )
        self.assertNotEqual(endpoints("g0g3"), ("g0", "d3"))

    def test_appending_d3g3_changes_to_later_end(self):
        tokens = self.witness["path_semantics"]["right_hand_segments"]
        self.assertTrue(is_contiguous(tokens + ["d3g3"]))
        self.assertEqual(endpoint_span(tokens + ["d3g3"]), ("g0", "g3"))
        self.assertFalse(self.witness["path_semantics"]["possible_repairs"][1]["stage_d3_compatible"])

    def test_discontinuous_path_is_rejected(self):
        self.assertFalse(is_contiguous(["g0d1", "g2d3"]))
        with self.assertRaises(ValueError):
            endpoint_span(["g0d1", "g2d3"])

    def test_forged_direct_original_source_is_rejected(self):
        self.expect_invalid(lambda d: d.update(original_sina_page_for_this_article_retrieved=True))

    def test_forged_independence_is_rejected(self):
        self.expect_invalid(lambda d: d.update(source_family_independence_established=True))

    def test_forged_author_erratum_is_rejected(self):
        self.expect_invalid(lambda d: d["path_semantics"]["possible_repairs"][0].update(author_issued_erratum_verified=True))

    def test_silent_editor_normalization_not_author_is_enforced(self):
        self.expect_invalid(lambda d: d["witnesses"][4].update(role="AUTHOR_CORRECTION"))

    def test_editor_question_not_author_is_enforced(self):
        self.expect_invalid(lambda d: d["witnesses"][5].update(role="AUTHOR_CORRECTION"))

    def test_original_mismatch_not_silently_fixed(self):
        self.expect_invalid(lambda d: d["path_semantics"].update(displayed_original_endpoints_match=True))

    def test_one_point_overlap_cannot_be_automatically_discarded(self):
        self.expect_invalid(lambda d: d["edge_touching_center"].update(center_overlap_price_count_under_author_text="EXCLUDED"))

    def test_archived_comment_not_primary_reply(self):
        self.expect_invalid(lambda d: d["edge_touching_center"].update(original_sina_comment_directly_verified=True))

    def test_no_fabricated_chart_year(self):
        self.expect_invalid(lambda d: d["figure_identification"].update(year_visible_on_chart=True))

    def test_no_fabricated_raw_minute_data(self):
        self.expect_invalid(lambda d: d["figure_identification"].update(raw_minute_ohlc_found_and_authenticated=True))

    def test_no_fabricated_empirical_profit(self):
        self.expect_invalid(lambda d: d.update(market_experiments="EMPIRICALLY_VALIDATED"))


if __name__ == "__main__":
    unittest.main()
