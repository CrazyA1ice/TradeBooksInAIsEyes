"""Negative source and causal-prefix checks for original three equal trades."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/audit_chanlun_primitive_trades_prefix.py"
spec = importlib.util.spec_from_file_location("primitive_base", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PrimitiveTradePrefixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = m.read(m.CONTRACT)
        cls.fixtures = m.read(m.CASES)
        cls.inventory = m.read(m.INV)
        cls.pins = m.verified_original_pins()
        cls.cards = {
            n: m.read(ROOT / f"knowledge/evidence/chanlun_lesson{n:03d}.json")
            for n in (18, 20, 35)
        }

    def validate(self, contract=None, pins=None, cards=None):
        return m.verify_contract(
            self.contract if contract is None else contract,
            self.inventory, self.pins if pins is None else pins,
            self.cards if cards is None else cards)

    def case(self, name):
        return copy.deepcopy(next(c["input"] for c in self.fixtures["cases"] if c["id"] == name))

    def test_source_35_18_20_original_page_fingerprints_and_roles(self):
        self.validate()
        self.assertEqual(len(self.contract["author_source_links"]), 3)
        self.assertEqual(len(self.contract["unverified"]), 6)
        self.assertFalse(self.contract["actual_center_completed"])

    def test_original_pdf_native_text_tamper_rejected(self):
        pins = dict(self.pins)
        pins[(2, 291)] = "0" * 64
        with self.assertRaisesRegex(ValueError, "native-text page SHA drift"):
            self.validate(pins=pins)
        pins = dict(self.pins)
        pins[(1, 245)] = "0" * 64
        with self.assertRaisesRegex(ValueError, "native-text page SHA drift"):
            self.validate(pins=pins)

    def test_author_editor_source_misattribution_rejected(self):
        cards = copy.deepcopy(self.cards)
        claim = next(c for c in cards[18]["claims"] if c["id"] == "CL018-S07")
        claim["kind"] = "EDITORIAL"
        with self.assertRaisesRegex(ValueError, "author main-text"):
            self.validate(cards=cards)
        contract = copy.deepcopy(self.contract)
        contract["author_source_links"][2]["role"] = "UNDATED_EDITORIAL"
        with self.assertRaisesRegex(ValueError, "Original author source link altered"):
            self.validate(contract=contract)

    def test_remove_unverified_or_promote_completed_center_fails(self):
        contract = copy.deepcopy(self.contract)
        contract["actual_center_completed"] = True
        with self.assertRaisesRegex(ValueError, "Fake actual center"):
            self.validate(contract=contract)
        contract = copy.deepcopy(self.contract)
        contract["unverified"].pop()
        with self.assertRaisesRegex(ValueError, "may not be erased"):
            self.validate(contract=contract)

    def test_eleven_full_primitive_cases_pass_with_zero_actual_centers(self):
        receipt = m.run_fixtures(self.fixtures, self.contract)
        self.assertEqual(receipt["status"], "SOURCE_PINNED_PRIMITIVE_TRADE_PREFIX_WITNESS_ONLY")
        self.assertEqual(receipt["synthetic_prefix_cases"], 11)
        self.assertEqual(receipt["status_counts"], {
            "BASE_PATTERN_WITNESSED_NOT_CENTER_CERTIFIED": 7,
            "NO_VISIBLE_BASE_TRIPLE": 3,
            "RULE_VERSION_INCOMPATIBLE_NOT_EVALUATED": 1,
        })
        self.assertEqual(receipt["actual_completed_centers"], 0)
        self.assertFalse(receipt["legal_child_trajectory_membership_confirmed"])
        self.assertFalse(receipt["market_data_accessed"])

    def test_first_observed_witness_requires_three_not_two_trades(self):
        two = m.inspect_prefix(self.case("before_third"), self.contract)
        three = m.inspect_prefix(self.case("first_three_equal"), self.contract)
        self.assertEqual(two["visible_trades"], 2)
        self.assertEqual(two["witnesses"], [])
        self.assertEqual(three["witnesses"][0]["third_trade_id"], 3)
        self.assertEqual(three["witnesses"][0]["first_observable_at"],
                         "2026-11-08T09:02:00+00:00")
        self.assertFalse(three["actual_center_completed"])

    def test_more_equal_trades_extend_same_witness_without_higher_center(self):
        row = m.inspect_prefix(self.case("extend_equal_fourth"), self.contract)
        self.assertEqual(len(row["witnesses"]), 1)
        self.assertEqual(row["witnesses"][0]["observed_same_price_run_length"], 4)
        self.assertEqual(row["witnesses"][0]["third_trade_id"], 3)
        self.assertFalse(row["witnesses"][0]["legally_completed"])

    def test_price_break_separates_equal_runs_even_if_price_returns(self):
        row = m.inspect_prefix(self.case("two_equal_runs_separated"), self.contract)
        self.assertEqual([(x["start_trade_id"], x["third_trade_id"])
                          for x in row["witnesses"]], [(1, 3), (5, 7)])
        row = m.inspect_prefix(self.case("noncontiguous_equal_not_a_triple"),
                               self.contract)
        self.assertEqual(row["witnesses"][0]["start_trade_id"], 3)

    def test_decimal_normalization_equality_not_string_format(self):
        row = m.inspect_prefix(self.case("exact_decimal_canonical_equal"), self.contract)
        self.assertEqual(row["witnesses"][0]["price"], "2")
        self.assertEqual(row["witnesses"][0]["third_trade_id"], 3)

    def test_future_trade_price_and_future_rule_version_cannot_leak(self):
        original = m.inspect_prefix(self.case("first_three_equal"), self.contract)
        for key in ("future_change_not_asof_visible",
                    "future_rule_change_does_not_backdate"):
            result = m.inspect_prefix(self.case(key), self.contract)
            self.assertEqual(result, original)

    def test_mixed_visible_rule_versions_block_pattern(self):
        row = m.inspect_prefix(self.case("observed_mixed_version_blocks"),
                               self.contract)
        self.assertEqual(row["status"], "RULE_VERSION_INCOMPATIBLE_NOT_EVALUATED")
        self.assertEqual(row["witnesses"], [])

    def test_forged_completed_center_field_and_market_kind_rejected(self):
        case = self.case("first_three_equal")
        case["events"][0]["center_completed"] = True
        with self.assertRaisesRegex(ValueError, "legal-center certification"):
            m.inspect_prefix(case, self.contract)
        case = self.case("first_three_equal")
        case["kind"] = "REAL_EXCHANGE_TRADES"
        with self.assertRaisesRegex(ValueError, "Real market"):
            m.inspect_prefix(case, self.contract)

    def test_duplicate_trade_id_or_backward_time_rejected(self):
        case = self.case("first_three_equal")
        case["events"][1]["trade_id"] = 1
        with self.assertRaisesRegex(ValueError, "out-of-order"):
            m.inspect_prefix(case, self.contract)
        case = self.case("first_three_equal")
        case["events"][1]["observed_at"] = case["events"][0]["observed_at"]
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            m.inspect_prefix(case, self.contract)

    def test_float_negative_nan_and_naive_timestamp_rejected(self):
        for invalid in (2.0, "-1", "NaN", "1e-2"):
            with self.subTest(invalid=invalid):
                case = self.case("first_three_equal")
                case["events"][0]["price"] = invalid
                with self.assertRaises(ValueError):
                    m.inspect_prefix(case, self.contract)
        case = self.case("first_three_equal")
        case["as_of"] = "2026-11-08T09:02:00"
        with self.assertRaisesRegex(ValueError, "UTC offsets"):
            m.inspect_prefix(case, self.contract)

    def test_asof_before_first_trade_has_no_spurious_candidate(self):
        row = m.inspect_prefix(self.case("asof_before_first_event"), self.contract)
        self.assertEqual(row["visible_trades"], 0)
        self.assertEqual(row["witnesses"], [])

    def test_report_and_acceptance_indexes_present_and_bound_scope(self):
        article = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/25_第35课三笔同价交易的原始事件证据与未完成边界.md"
        body = article.read_text(encoding="utf-8")
        for word in ("CL35-SO-2", "CL018-S07", "CL020-S01", "第三笔",
                     "first_observable_at", "不等于", "未完成",
                     "SOURCE_PINNED_PRIMITIVE_TRADE_PREFIX_WITNESS_ONLY",
                     "NOT_RUN", "OB38-UNIQUE"):
            self.assertIn(word, body)
        for idx in (
            ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/README.md",
            ROOT / "deliverables/chanlun_108_acceptance/README.md",
        ):
            self.assertIn(article.name, idx.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
