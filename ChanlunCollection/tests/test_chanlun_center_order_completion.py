"""Exact source-locked Chanlun 18/20 Zn interval math, NOT actual legal centers."""
import copy
import importlib.util
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/audit_chanlun_center_order_completion.py"
spec = importlib.util.spec_from_file_location("chanlun_center_source", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class CenterOrderCompletionSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = m.read(m.CONTRACT)
        cls.pins = m.read(m.PINS)
        cls.inventory = m.read(m.INVENTORY)
        cls.cards = {n: m.read(ROOT / f"knowledge/evidence/chanlun_lesson{n:03d}.json")
                     for n in (18, 20)}
        cls.examples = m.read(m.CASES)

    def check(self, contract=None, pins=None, cards=None):
        m.validate(contract or self.contract, pins or self.pins, self.inventory,
                   cards or self.cards)

    def case(self, name):
        return copy.deepcopy(next(x["input"] for x in self.examples["cases"] if x["id"] == name))

    def test_six_original_pdf_pins_and_three_source_claim_anchors(self):
        self.check()
        self.assertEqual(len(m.PROOF_PAGES), 6)
        self.assertEqual(len(self.contract["source_claims"]), 3)
        self.assertFalse(self.contract["complete_chanlun_parser"])

    def test_original_pdf_page_hash_or_editorial_role_changes_fail(self):
        p = copy.deepcopy(self.pins)
        p["page_native_text_sha256"]["246"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprints"):
            self.check(pins=p)
        c = copy.deepcopy(self.cards)
        note = next(x for x in c[20]["claims"] if x["id"] == "CL020-S08")
        note["kind"] = "EDITORIAL"
        with self.assertRaisesRegex(ValueError, "authored PDF page"):
            self.check(cards=c)
        c = copy.deepcopy(self.cards)
        note = next(x for x in c[18]["claims"] if x["id"] == "CL018-S07")
        note["source_anchor"]["inline_editorial_markers_present"] = False
        with self.assertRaisesRegex(ValueError, "Author/editor boundary"):
            self.check(cards=c)

    def test_strict_gg_dd_author_formulas_must_not_be_weakened_to_nonstrict(self):
        c = copy.deepcopy(self.contract)
        c["author_comparison_formulas"]["up"] = "later.DD >= earlier.GG"
        with self.assertRaisesRegex(ValueError, "strict comparison"):
            self.check(contract=c)
        self.assertEqual(m.evaluate(self.case("equal_up_boundary_is_not_strict_up"),
                                    self.contract),
                         "AUTHOR_EXPANSION_NUMERIC_CONDITION_ONLY")

    def test_exact_decimal_values_and_full_Zn_ranges(self):
        row = self.case("all_Zn_not_just_first_two_for_GG")
        first = m.parse_center(row["earlier"])
        self.assertEqual(first["GG"], Decimal("10"))
        self.assertEqual(first["ZG"], Decimal("3"))
        self.assertEqual(first["DD"], Decimal("1"))
        self.assertEqual(first["ZD"], Decimal("1.5"))
        self.assertEqual(m.evaluate(row, self.contract),
                         "AUTHOR_EXPANSION_NUMERIC_CONDITION_ONLY")
        self.assertEqual(m.decimal("0.1") + m.decimal("0.2"), m.decimal("0.3"))

    def test_directional_inequalities_are_condition_only(self):
        self.assertEqual(m.evaluate(self.case("up_strict_full_fluctuation_separation"),
                                    self.contract),"AUTHOR_STRICT_UP_NUMERIC_CONDITION_ONLY")
        self.assertEqual(m.evaluate(self.case("down_strict_full_fluctuation_separation"),
                                    self.contract),"AUTHOR_STRICT_DOWN_NUMERIC_CONDITION_ONLY")

    def test_three_declared_completed_children_do_not_certify_parent_ending(self):
        result = m.run_cases(self.examples,self.contract)
        self.assertEqual(result["status"], "AUTHOR_CENTER_FORMULAS_PINNED_CONDITIONAL_ONLY")
        self.assertEqual(result["symbolic_cases"],10)
        self.assertEqual(result["author_legal_center_certificates"],0)
        self.assertEqual(result["completed_actual_trends"],0)
        self.assertFalse(result["proof_38_or_99"])
        self.assertFalse(result["market_data_accessed"])

    def test_center_can_be_potentially_complete_yet_continue_unbounded(self):
        source = self.contract["author_completion_distinctions"]
        self.assertEqual(source["consolidation_after_threshold"],"may_finish_but_may_extend")
        self.assertEqual(source["trend_after_two_centers"],"may_finish_but_may_extend")
        c=copy.deepcopy(self.contract)
        c["author_completion_distinctions"]["consolidation_after_threshold"] = "must_be_finished"
        with self.assertRaisesRegex(ValueError,"Possible completion"):
            self.check(contract=c)

    def test_future_child_not_visible_and_incomplete_child_never_qualify(self):
        self.assertEqual(m.evaluate(self.case("future_child_completion_not_visible"),
                                    self.contract),"ASOF_LOWER_TYPE_NOT_YET_CONFIRMED")
        self.assertEqual(m.evaluate(self.case("one_unfinished_lower_type"),
                                    self.contract),"UNCOMPLETED_LOWER_TYPE_PENDING")

    def test_ambiguous_same_position_and_point_touch_stay_open(self):
        for key, expected in (("same_center_relative_position_not_classified",
                                "AUTHOR_NUMERIC_RELATION_UNRESOLVED"),
                              ("point_touch_core_not_auto_accepted",
                                "POINT_TOUCH_CORE_AUTHOR_SEMANTICS_UNRESOLVED"),
                              ("empty_center_core", "DECLARED_CENTER_CORE_EMPTY")):
            with self.subTest(key=key):
                self.assertEqual(m.evaluate(self.case(key), self.contract), expected)

    def test_forged_real_center_certificate_and_price_type_rejected(self):
        x=self.case("up_strict_full_fluctuation_separation")
        x["earlier"]["kind"]="REAL_VERIFIED_CENTER"
        with self.assertRaisesRegex(ValueError,"self-certified"):
            m.evaluate(x,self.contract)
        x=self.case("up_strict_full_fluctuation_separation")
        x["earlier"]["z_segments"][0][0]=1.0
        with self.assertRaisesRegex(ValueError,"decimal strings"):
            m.evaluate(x,self.contract)
        x=self.case("up_strict_full_fluctuation_separation")
        x["trade_history"]=True
        with self.assertRaisesRegex(ValueError,"Unexpected market"):
            m.evaluate(x,self.contract)

    def test_mixed_rule_versions_cannot_compare(self):
        x=self.case("up_strict_full_fluctuation_separation")
        x["later"]["rule_version"]="POSTDATED_UNKNOWN_RULE"
        self.assertEqual(m.evaluate(x,self.contract),
                         "DIFFERENT_RULE_VERSION_NO_COMPARISON")

    def test_illegal_first_three_and_naive_clock_fail(self):
        x=self.case("up_strict_full_fluctuation_separation")
        x["earlier"]["first_three_lower_confirmed_at"][0]="2026-11-08T09:01:00"
        with self.assertRaisesRegex(ValueError,"Timezone-naive"):
            m.evaluate(x,self.contract)
        x=self.case("up_strict_full_fluctuation_separation")
        x["earlier"]["first_three_lower_completed"][1]=False
        with self.assertRaisesRegex(ValueError,"Incomplete lower"):
            m.evaluate(x,self.contract)

    def test_later_center_must_actually_follow_prior_center_in_synthetic_clock(self):
        row = self.case("up_strict_full_fluctuation_separation")
        row["later"]["first_three_lower_confirmed_at"] = (
            row["earlier"]["first_three_lower_confirmed_at"][:])
        with self.assertRaisesRegex(ValueError, "confirmation order is not verified"):
            m.evaluate(row, self.contract)

    def test_evidence_scope_report_linked_from_both_indexes(self):
        article=ROOT/"deliverables/chanlun_108_acceptance/04_AI_GUIDE/24_第18与20课中枢比较及可完成性原文检验.md"
        text=article.read_text(encoding="utf-8")
        for key in ("CL018-S07","CL020-S08","GG","DD","ZG","ZD",
                    "AUTHOR_STRICT_UP_NUMERIC_CONDITION_ONLY",
                    "AUTHOR_EXPANSION_NUMERIC_CONDITION_ONLY",
                    "完成资格","不等于","未完成","第38课","第99课","NOT_RUN"):
            self.assertIn(key,text)
        for index in (ROOT/"deliverables/chanlun_108_acceptance/04_AI_GUIDE/README.md",
                      ROOT/"deliverables/chanlun_108_acceptance/README.md"):
            self.assertIn(article.name,index.read_text(encoding="utf-8"))


if __name__=="__main__":
    unittest.main()
