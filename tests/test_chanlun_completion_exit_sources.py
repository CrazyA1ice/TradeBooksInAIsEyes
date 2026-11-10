"""Targeted guards for newly found author-reply completion conditions."""
from copy import deepcopy
import json
import unittest

from tools.audit_chanlun_completion_exit_sources import CATALOG, OLDER, REPORT, validate


class CompletionExitSourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.old = json.loads(OLDER.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")

    def denied(self, edit):
        d = deepcopy(self.data)
        edit(d)
        with self.assertRaises(ValueError):
            validate(d, self.old, self.report)

    def test_current_provenance(self):
        validate(self.data, self.old, self.report)

    def test_cannot_attrib_1620_comment_to_lesson72_prose(self):
        self.denied(lambda d: d["attribution_correction"].update(comment_part_of_canonical_lesson72_body=True))

    def test_cannot_claim_original_sina_comment_authenticated(self):
        self.denied(lambda d: d["findings"][1].update(original_sina_comment_directly_authenticated=True))

    def test_cannot_remove_completed_first_retrace(self):
        self.denied(lambda d: d["typed_events"][2]["required_conditions"].remove("FIRST_FULL_LOWER_TYPE_RETRACE"))

    def test_cannot_make_third_point_certify_its_own_child(self):
        self.denied(lambda d: d["typed_events"][2].update(third_point_cannot_certify_its_own_retrace_without_independent_child_completion=False))

    def test_cannot_skip_actual_trend_pullback(self):
        self.denied(lambda d: d["typed_events"][3]["required_conditions"].remove("ACTUAL_PULLBACK_TO_LAST_CENTER_WITH_DEFINED_BOUNDARY"))

    def test_cannot_infer_finished_movement_from_segment_end(self):
        self.denied(lambda d: d["typed_events"][0].update(finished_child_movement_implied=True))

    def test_cannot_conflate_ending_with_minimum_center(self):
        self.denied(lambda d: d["typed_events"][1].update(finished_parent_movement_implied=True))

    def test_cannot_claim_market_first_knowable(self):
        self.denied(lambda d: d.update(market_asof="ESTABLISHED"))

    def test_cannot_claim_empirical_validation(self):
        self.denied(lambda d: d.update(empirical_status="DONE"))


if __name__ == "__main__":
    unittest.main()
