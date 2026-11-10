"""Reject source and type upgrades unsupported by the lesson 54/67/83/18 record."""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from tools.audit_chanlun_l54_f1_f2_typed_bridge import RECORD, REPORT, reachable, validate


class TestTypedBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")

    def rejected(self, change):
        r = deepcopy(self.record)
        change(r)
        with self.assertRaises(ValueError):
            validate(r, self.report)

    def test_valid_record(self):
        validate(self.record, self.report)

    def test_54_abstraction_does_not_certify_upper_center(self):
        self.assertNotIn("L18_PARENT_CENTER", reachable("L54_VIEW_LINE", self.record["licensed_links"]))

    def test_three_completed_child_types_conditional_parent(self):
        self.assertIn("L18_PARENT_CENTER", reachable("L18_FINISHED_CHILD_TYPE", self.record["licensed_links"]))

    def test_formal_segment_not_a_completed_movement(self):
        self.assertNotIn("L18_FINISHED_CHILD_TYPE", reachable("L67_FORMAL_SEGMENT", self.record["licensed_links"]))

    def test_reject_inserting_missing_54_67_equivalence(self):
        def modify(r):
            r["licensed_links"][0]["from"] = "L54_VIEW_LINE"
            r["licensed_links"][0]["to"] = "L67_FORMAL_SEGMENT"
        self.rejected(modify)

    def test_reject_fabricated_source_claim(self):
        self.rejected(lambda r: r["canonical_source_cards"][0].update(id="CL18-NOT-REAL"))

    def test_reject_editorial_claim_as_author_source(self):
        self.rejected(lambda r: r["canonical_source_cards"][0].update(role="EDITORIAL"))

    def test_reject_wrong_pdf_page(self):
        self.rejected(lambda r: r["canonical_source_cards"][0].update(physical_pages=[9999]))

    def test_reject_open_gap_claimed_to_be_proven(self):
        self.rejected(lambda r: r["unlicensed_bridges"][1].update(state="PROVEN"))

    def test_reject_author_proof_of_cross_initializer_equivalence(self):
        self.rejected(lambda r: r["unlicensed_bridges"][6].update(is_author_quoted_theorem=True))

    def test_reject_fabricated_market_replay(self):
        self.rejected(lambda r: r.update(asof_market_data="EXECUTED"))

    def test_reject_missing_level_policy_fact(self):
        self.rejected(lambda r: r["policy_facts"][0].update(source_id="CL54-SOURCE-1"))

    def test_reject_cross_level_policy_guarantee(self):
        self.rejected(lambda r: r["methodological_guardrails"].update(f1_f2_different_is_allowed_by_author=False))


if __name__ == "__main__":
    unittest.main()
