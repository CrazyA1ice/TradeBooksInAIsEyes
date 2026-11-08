"""Negative-path tests for authored N>2 lowest-level terminal comparison."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/audit_chanlun_lesson035_trend_terminal_asof.py"
spec = importlib.util.spec_from_file_location("lesson35_terminal", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Lesson35TerminalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = m.read(m.CONTRACT)
        cls.fixtures = m.read(m.FIXTURES)
        cls.evidence = m.read(m.EVIDENCE)
        cls.inventory = m.read(m.INVENTORY)
        cls.pins = m.original_pins()

    def check(self, contract=None, evidence=None, pins=None):
        m.validate_contract(
            self.contract if contract is None else contract,
            self.evidence if evidence is None else evidence,
            self.inventory, self.pins if pins is None else pins)

    def example(self, key):
        return copy.deepcopy(next(x for x in self.fixtures["cases"] if x["id"] == key)["input"])

    def test_original_source_and_four_author_conditional_rules(self):
        self.check()
        self.assertEqual(self.contract["original_pdf"]["physical_page"], 291)
        self.assertEqual(len(self.contract["author_conditional_rules"]), 4)
        self.assertEqual(self.contract["author_conditional_rules"][2]["relations"], ["EQUAL", "LOWER"])
        self.assertEqual(self.contract["author_conditional_rules"][3]["relations"], ["EQUAL", "HIGHER"])

    def test_exact_authored_claim_page_sha_and_role_reject_forgery(self):
        e = copy.deepcopy(self.evidence)
        c = next(x for x in e["claims"] if x["id"] == "CL35-SO-9")
        c["kind"] = "EDITORIAL"
        with self.assertRaisesRegex(ValueError, "SOURCE"):
            self.check(evidence=e)
        e = copy.deepcopy(self.evidence)
        c = next(x for x in e["claims"] if x["id"] == "CL35-SO-9")
        c["source_anchor"]["native_text_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SOURCE"):
            self.check(evidence=e)
        pins = dict(self.pins)
        pins[(2, 291)] = "0" * 64
        with self.assertRaisesRegex(ValueError, "original page fingerprint"):
            self.check(pins=pins)

    def test_all_twelve_cases_produce_exact_conditional_output_only(self):
        results = m.check_cases(self.fixtures, self.contract)
        self.assertEqual(results["status"], m.BLOCKED)
        self.assertEqual(results["symbolic_cases"], 12)
        self.assertEqual(results["outcomes"]["AUTHOR_TERMINAL_COMPARISON_TRIGGER_ONLY"], 5)
        self.assertEqual(results["open_legal_premises"], 5)
        self.assertEqual(results["actual_legal_completed_trends"], 0)
        self.assertFalse(results["confirmed_theorem38_uniqueness"])

    def test_initial_two_centers_cannot_end_trend_on_equal_price(self):
        row = self.example("two_centers_not_trend")
        self.assertEqual(m.evaluate(row, self.contract)["status"], "TWO_CENTER_TREND_NOT_QUALIFIED")
        self.assertEqual(m.evaluate(row, self.contract)["terminal_ordinal"], None)

    def test_third_equal_ends_comparison_in_both_directions(self):
        for id_ in ("up_equal_third", "down_equal_third"):
            with self.subTest(id=id_):
                result = m.evaluate(self.example(id_), self.contract)
                self.assertEqual(result["status"], "AUTHOR_TERMINAL_COMPARISON_TRIGGER_ONLY")
                self.assertEqual(result["terminal_ordinal"], 3)
                self.assertFalse(result["legally_completed"])

    def test_third_reverse_relationship_triggers_in_both_directions(self):
        for id_ in ("up_lower_third", "down_higher_third"):
            with self.subTest(id=id_):
                self.assertEqual(m.evaluate(self.example(id_), self.contract)["terminal_ordinal"], 3)

    def test_future_center_never_revises_asof_result(self):
        row = self.example("future_fourth_cannot_leak")
        unchanged = m.evaluate(row, self.contract)
        self.assertEqual(unchanged["status"], "CONTINUATION_ONLY_NO_TERMINATION_CONFIRMATION")
        self.assertEqual(unchanged["used"], 3)
        row["events"][3]["relation_to_previous"] = "EQUAL"
        self.assertEqual(m.evaluate(row, self.contract), unchanged)

    def test_unconfirmed_center_stays_pending(self):
        row = self.example("third_not_confirmed")
        self.assertEqual(m.evaluate(row, self.contract)["status"], "PENDING_CENTER_CONFIRMATION")
        row["as_of"] = "2007-03-09T09:26:00+00:00"
        self.assertEqual(m.evaluate(row, self.contract)["status"],
                         "AUTHOR_TERMINAL_COMPARISON_TRIGGER_ONLY")

    def test_unverified_relation_never_silently_becomes_equal_or_higher(self):
        self.assertEqual(m.evaluate(self.example("third_unverified_relative_height"),
                                    self.contract)["status"], "CENTER_RELATIVE_HEIGHT_UNRESOLVED")

    def test_visible_mixed_rule_version_does_not_generate_signal(self):
        row = self.example("up_equal_third")
        row["events"][2]["rule_version"] = "LATER_UNVERIFIED_VERSION"
        self.assertEqual(m.evaluate(row, self.contract)["status"], "RULE_VERSION_MISMATCH")

    def test_forged_complete_center_or_market_fields_fail_closed(self):
        row = self.example("up_equal_third")
        row["events"][2]["center_kind"] = "ACTUAL_COMPLETED_CENTER_CERTIFIED"
        with self.assertRaisesRegex(ValueError, "promote"):
            m.evaluate(row, self.contract)
        row = self.example("up_equal_third")
        row["market_data"] = "not_allowed"
        with self.assertRaisesRegex(ValueError, "Unexpected proof"):
            m.evaluate(row, self.contract)

    def test_unverified_price_semantics_or_complete_parser_flag_rejected(self):
        contract = copy.deepcopy(self.contract)
        contract["complete_lowest_level_parser"] = True
        with self.assertRaisesRegex(ValueError, "False theorem"):
            self.check(contract=contract)
        contract = copy.deepcopy(self.contract)
        contract["required_unverified"].remove("author_center_relative_height_semantics")
        with self.assertRaisesRegex(ValueError, "Unverified"):
            self.check(contract=contract)

    def test_n_greater_than_two_and_equality_cannot_be_deleted(self):
        contract = copy.deepcopy(self.contract)
        contract["author_conditional_rules"][1]["min_ordinal"] = 2
        with self.assertRaisesRegex(ValueError, "threshold changed"):
            self.check(contract=contract)
        contract = copy.deepcopy(self.contract)
        contract["author_conditional_rules"][2]["relations"] = ["LOWER"]
        with self.assertRaisesRegex(ValueError, "equality condition changed"):
            self.check(contract=contract)

    def test_historical_asof_requires_timezone_and_ordered_clocks(self):
        row = self.example("up_equal_third")
        row["as_of"] = "2007-03-09T09:10:00"
        with self.assertRaisesRegex(ValueError, "Timezone-naive"):
            m.evaluate(row, self.contract)
        row = self.example("up_equal_third")
        row["events"][1]["confirmed_at"] = "2007-03-09T08:55:00+00:00"
        with self.assertRaisesRegex(ValueError, "cannot precede"):
            m.evaluate(row, self.contract)

    def test_public_report_and_index_preserve_not_proven_limits(self):
        article = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/23_第35课最低级别趋势延续与结束的条件判定.md"
        body = article.read_text(encoding="utf-8")
        for word in ("CL35-SO-9", "N＞2", "卷二p.291",
                     "AUTHOR_TERMINAL_COMPARISON_TRIGGER_ONLY", "等于", "未确认",
                     "OB38-ASOF", "TEXT_FIRST_NO_IMAGE", "NOT_RUN"):
            self.assertIn(word, body)
        for path in (ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/README.md",
                     ROOT / "deliverables/chanlun_108_acceptance/README.md"):
            self.assertIn(article.name, path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
