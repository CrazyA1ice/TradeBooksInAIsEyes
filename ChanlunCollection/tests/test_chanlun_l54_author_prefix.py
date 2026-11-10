"""Checks the exact author-narrative prefix contract, not an OHLC or live trade backtest."""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from tools.replay_chanlun_l54_author_prefix import (
    LESSON_EVIDENCE, PRIOR_VISUAL, load_record, replay, validate
)


class Lesson54AsOfTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = load_record()
        cls.evidence = json.loads(LESSON_EVIDENCE.read_text(encoding="utf-8"))
        cls.visual = json.loads(PRIOR_VISUAL.read_text(encoding="utf-8"))

    def assert_rejects(self, mutate):
        item = deepcopy(self.record)
        mutate(item)
        with self.assertRaises(ValueError):
            validate(item, self.evidence, self.visual)

    def test_original_contract_passes(self):
        validate(self.record, self.evidence, self.visual)

    def test_at_g5_alpha_formed_beta_not_yet(self):
        a = replay(self.record, "g5", "ALPHA")
        b = replay(self.record, "g5", "BETA")
        self.assertEqual(a["center_assertion"], {"interval": "[d2,g5]", "at": "g5"})
        self.assertIsNone(b["center_assertion"])
        self.assertIsNone(a["g7_structural_assertion"])
        self.assertIsNone(b["g7_structural_assertion"])

    def test_at_g6_both_formed_distinct_intervals(self):
        a = replay(self.record, "g6", "ALPHA")
        b = replay(self.record, "g6", "BETA")
        self.assertEqual(a["center_assertion"]["interval"], "[d2,g5]")
        self.assertEqual(b["center_assertion"]["interval"], "[d3,g5]")
        self.assertNotEqual(a["center_assertion"], b["center_assertion"])

    def test_at_g7_types_differ_qualitative_author_note_agrees(self):
        a = replay(self.record, "g7", "ALPHA")
        b = replay(self.record, "g7", "BETA")
        self.assertEqual(a["g7_structural_assertion"], "THIRD_SELL")
        self.assertEqual(b["g7_structural_assertion"], "CENTER_OSCILLATION_NOT_THIRD_SELL")
        self.assertEqual(a["author_qualitative_g7_conclusion"], b["author_qualitative_g7_conclusion"])
        self.assertIsNone(a["order_or_pnl"])
        self.assertIsNone(b["order_or_pnl"])

    def test_post_g7_price_not_visible_at_g7(self):
        for policy in ("ALPHA", "BETA"):
            self.assertIsNone(replay(self.record, "g7", policy)["chart_rightmost_price_label"])
            self.assertEqual(replay(self.record, "AFTER_G7", policy)["chart_rightmost_price_label"], "18.03")
            self.assertIsNone(replay(self.record, "AFTER_G7", policy)["market_first_knowable_timestamp"])

    def test_at_d2_not_g5_reframed(self):
        item = replay(self.record, "d2", "ALPHA")
        self.assertIn("L54-E03", item["evidence_ids"])
        self.assertIsNone(item["center_assertion"])
        self.assertIsNone(item["g7_structural_assertion"])

    def test_denies_early_beta_center(self):
        self.assert_rejects(lambda j: next(e for e in j["events"] if e["id"] == "L54-E08").update(stage="g5"))

    def test_denies_early_g7_structural_label(self):
        self.assert_rejects(lambda j: next(e for e in j["events"] if e["id"] == "L54-E09").update(stage="g6"))

    def test_denies_early_future_chart_price(self):
        self.assert_rejects(lambda j: next(e for e in j["events"] if e["id"] == "L54-E12").update(stage="g7"))

    def test_denies_forged_equal_g7_labels(self):
        self.assert_rejects(lambda j: next(e for e in j["events"] if e["id"] == "L54-E10").update(value="THIRD_SELL"))

    def test_denies_silent_repair_of_source_endpoint(self):
        self.assert_rejects(lambda j: j["source_notation_anomalies"][0].update(allowed_correction_claim="g0d3"))

    def test_denies_fake_market_asof(self):
        self.assert_rejects(lambda j: j.update(market_asof_certification="VERIFIED"))

    def test_denies_invented_trading_results(self):
        self.assert_rejects(lambda j: j.update(empirical_trading_tests="DONE"))

    def test_denies_forged_author_source_claim(self):
        self.assert_rejects(lambda j: j["source_claim_ids"].append("CL54-EDITORIAL-5"))


if __name__ == "__main__":
    unittest.main()
