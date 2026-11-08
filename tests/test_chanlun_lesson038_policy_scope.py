"""Source-locked asymmetric lesson38 partial semantics and anti-false-counterexample gates."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "tools/audit_chanlun_lesson038_policy_scope.py"
spec = importlib.util.spec_from_file_location("chanlun38_rules", CODE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Lesson38PartialRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = m.read(m.CONTRACT_FILE)
        cls.fixtures = m.read(m.FIXTURES_FILE)
        cls.evidence = m.read(m.EVIDENCE)
        cls.inventory = m.read(m.INVENTORY)
        cls.pins = m.locked_original_pins()

    def check(self, contract=None, evidence=None, pins=None):
        m.verify_contract(
            self.contract if contract is None else contract,
            self.evidence if evidence is None else evidence,
            self.inventory,
            self.pins if pins is None else pins,
        )

    def test_original_source_and_all_seven_policy_clauses_verified(self):
        self.check()
        self.assertEqual(len(self.contract["clauses"]), 7)
        self.assertEqual(self.contract["page_text_sha256"], m.PAGE_HASH)

    def test_338_and_339_are_both_in_canonical_claim(self):
        record = next(x for x in self.evidence["claims"] if x["id"] == "CL38-SOURCE-2")
        self.assertEqual(record["pdf_pages"], [338, 339])
        self.assertEqual(record["source_anchor_details"]["physical_pdf_pages_native_text_sha256"], m.PAGE_HASH)
        self.assertFalse(record["source_anchor_details"]["original_publication_provenance_independently_checked"])

    def test_never_relabel_undefined_extension_as_market_impossibility(self):
        c = copy.deepcopy(self.contract)
        c["clauses"][1]["policy"] = "PROHIBITED_EVERYWHERE"
        with self.assertRaisesRegex(ValueError, "Original clause identity/value/source altered"):
            self.check(contract=c)
        case = self.fixtures["cases"][4]
        self.assertEqual(m.compare(case["left"], case["right"], self.contract),
                         "UNDEFINED_POLICY_DOES_NOT_PROVE_IMPOSSIBILITY")

    def test_original_fingerprint_and_role_mismatch_are_fail_closed(self):
        c = copy.deepcopy(self.contract)
        c["clauses"][2]["native_text_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Original clause"):
            self.check(contract=c)
        c = copy.deepcopy(self.contract)
        c["clauses"][2]["role"] = "EDITORIAL"
        with self.assertRaisesRegex(ValueError, "Original clause"):
            self.check(contract=c)
        pins = dict(self.pins)
        pins[(2, 339)] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Previously verified"):
            self.check(pins=pins)

    def test_incomplete_new_rule_or_missing_open_fields_never_certified(self):
        c = copy.deepcopy(self.contract)
        c["completed_R_g"] = True
        with self.assertRaisesRegex(ValueError, "Invented completeness"):
            self.check(contract=c)
        c = copy.deepcopy(self.contract)
        c["open_fields"].remove("equal_price_tiebreak")
        with self.assertRaisesRegex(ValueError, "Missing unresolved"):
            self.check(contract=c)

    def test_all_seven_examples_have_expected_provisional_results(self):
        out = m.verify_cases(self.fixtures, self.contract)
        self.assertEqual(out["original_policy_clauses_checked"], 7)
        self.assertEqual(out["symbolic_scenarios"], 7)
        self.assertFalse(out["counterexample_to_complete_chanlun"])
        self.assertFalse(out["mathematical_uniqueness_proven"])
        self.assertFalse(out["complete_parser"])
        self.assertEqual(out["verdict_counts"]["COMPETING_CUTS_UNRESOLVED_NOT_CHANLUN_COUNTEREXAMPLE"], 1)

    def test_cross_level_and_rule_versions_are_not_competing_under_one_Rg(self):
        for idx in (2, 6):
            case = self.fixtures["cases"][idx]
            self.assertEqual(m.compare(case["left"], case["right"], self.contract),
                             "NOT_SAME_FROZEN_RULE_DOMAIN")

    def test_below_level_pan_pair_declared_policy_rejected_without_parser_claim(self):
        case = self.fixtures["cases"][1]
        self.assertEqual(m.compare(case["left"], case["right"], self.contract),
                         "DECLARED_POLICY_CONFLICT_NOT_FULL_PARSE_VERDICT")

    def test_injected_market_inputs_and_forged_boundaries_fail(self):
        c = copy.deepcopy(self.fixtures["cases"][0]["left"])
        c["kind"] = "REAL_A_STOCK_MARKET"
        with self.assertRaisesRegex(ValueError, "Market data forbidden"):
            m.assess(c)
        c = copy.deepcopy(self.fixtures["cases"][0]["left"])
        c["cuts"] = [0, 2, 2, 6]
        with self.assertRaisesRegex(ValueError, "Candidate bounds do not partition"):
            m.assess(c)

    def test_article_and_index_present_without_theorem_upgrade(self):
        page = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/21_第38课部分规则与竞争切点的判定界限.md"
        body = page.read_text(encoding="utf-8")
        for needle in ("CL38-SOURCE-2", "卷二p.339", "不定义", "不允许",
                       "允许", "OB38-UNIQUE", "COMPETING_CUTS_UNRESOLVED",
                       "不是缠论反例", "TEXT_FIRST_NO_IMAGE", "NOT_RUN"):
            self.assertIn(needle, body)
        for index in (
            "deliverables/chanlun_108_acceptance/04_AI_GUIDE/README.md",
            "deliverables/chanlun_108_acceptance/README.md",
        ):
            self.assertIn(page.name, (ROOT / index).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
