"""Negative tests prevent turning a visual cross-check into author theorem or trade certification."""
from __future__ import annotations

from copy import deepcopy
import json
import unittest
from pathlib import Path

from tools.verify_chanlun_l54_visual_record import validate_record

ROOT = Path(__file__).resolve().parents[1]


class Lesson54VisualRecordTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads((ROOT / "catalog/chanlun_l54_cross_archive_figure_and_decision_v1.json").read_text(encoding="utf-8"))
        cls.evidence = json.loads((ROOT / "knowledge/evidence/chanlun_lesson054.json").read_text(encoding="utf-8"))
        cls.report = (ROOT / "deliverables/chanlun_108_acceptance/00_REVIEW/LESSON54_SOURCE_FIGURE_AND_STRUCTURAL_VS_DECISION_AGREEMENT.md").read_text(encoding="utf-8")

    def test_real_record(self):
        validate_record(self.record, self.evidence, self.report)

    def test_forged_pdf_identity_is_rejected(self):
        wrong = deepcopy(self.record)
        wrong["source_author"]["canonical_repository_pdf_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            validate_record(wrong, self.evidence, self.report)

    def test_confusing_two_structural_labels_is_rejected(self):
        wrong = deepcopy(self.record)
        wrong["author_same_chart_two_parses"]["beta"]["g7_structure_label"] = "THIRD_SELL"
        with self.assertRaises(ValueError):
            validate_record(wrong, self.evidence, self.report)

    def test_saying_same_execution_is_rejected(self):
        wrong = deepcopy(self.record)
        wrong["author_same_chart_two_parses"]["same_exact_order_time_or_size_implied"] = True
        with self.assertRaises(ValueError):
            validate_record(wrong, self.evidence, self.report)

    def test_fake_canonical_visual_verification_is_rejected(self):
        wrong = deepcopy(self.record)
        wrong["source_author"]["canonical_pdf_independently_opened_this_step"] = True
        with self.assertRaises(ValueError):
            validate_record(wrong, self.evidence, self.report)

    def test_fake_empirical_result_is_rejected(self):
        wrong = deepcopy(self.record)
        wrong["real_market_experiments"] = "DONE"
        with self.assertRaises(ValueError):
            validate_record(wrong, self.evidence, self.report)

    def test_editorial_comment_cannot_be_author_source(self):
        wrong = deepcopy(self.record)
        wrong["source_author"]["source_claim_ids"].append("CL54-EDITORIAL-5")
        with self.assertRaises(ValueError):
            validate_record(wrong, self.evidence, self.report)


if __name__ == "__main__":
    unittest.main()
