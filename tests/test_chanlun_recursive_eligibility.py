"""Conditional center recursion: source-role integrity, exact decimal logic, no fake parser."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "tools/audit_chanlun_recursive_source_eligibility.py"
spec = importlib.util.spec_from_file_location("recursive_eligibility", CODE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RecursiveEligibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = m.read(m.CONTRACT_FILE)
        cls.fixtures = m.read(m.FIXTURES_FILE)
        cls.inventory = m.read(m.INVENTORY)
        cls.pins = m.original_pins()
        cls.evidence = {
            lesson: m.read(ROOT / f"knowledge/evidence/chanlun_lesson{lesson:03d}.json")
            for lesson in (17, 35, 38)
        }

    def check(self, contract=None, evidence=None, pins=None):
        m.validate_contract(self.contract if contract is None else contract, self.inventory,
                            self.pins if pins is None else pins,
                            self.evidence if evidence is None else evidence)

    def test_all_six_original_author_claims_sha_locked(self):
        self.check()
        self.assertEqual(len(self.contract["original_author_claims"]), 6)
        self.assertEqual(set(self.contract["author_verified_original_pdf_sha256"]), {"1", "2"})

    def test_six_unresolved_external_legality_premises_not_self_certified(self):
        self.assertEqual(len(self.contract["premise_slots"]), 6)
        self.assertTrue(all(p["status"] == "EXTERNAL_NOT_VERIFIED"
                            for p in self.contract["premise_slots"]))
        x = copy.deepcopy(self.contract)
        x["premise_slots"][0]["status"] = "VERIFIED"
        with self.assertRaisesRegex(ValueError, "self-certified"):
            self.check(contract=x)

    def test_wrong_original_page_sha_or_wrong_evidence_role_fail(self):
        x = copy.deepcopy(self.contract)
        x["original_author_claims"][0]["native_text_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            self.check(contract=x)
        x = copy.deepcopy(self.contract)
        x["original_author_claims"][0]["claim_id"] = "CL017-I05"
        with self.assertRaisesRegex(ValueError, "original-claim identity"):
            self.check(contract=x)
        x = copy.deepcopy(self.contract)
        x["original_author_claims"][0]["source_role"] = "EDITORIAL"
        with self.assertRaisesRegex(ValueError, "original-claim identity"):
            self.check(contract=x)

    def test_author_date_and_theorem_cannot_be_invented(self):
        for name, fake in (("original_publication_independently_checked", True),
                           ("complete_rule_R_g_available", True),
                           ("lesson38_uniqueness_proven", True),
                           ("lesson99_eventual_center_proven", True)):
            with self.subTest(name=name):
                x = copy.deepcopy(self.contract)
                x[name] = fake
                with self.assertRaises(ValueError):
                    self.check(contract=x)

    def test_eight_interval_cases_and_two_base_cases(self):
        x = m.check_examples(self.fixtures, self.contract)
        self.assertEqual(x["status"], "SOURCE_PINNED_CONDITIONAL_RECURSIVE_GEOMETRY_ONLY")
        self.assertEqual(x["symbolic_geometry_cases"], 8)
        self.assertEqual(x["symbolic_base_cases"], 2)
        self.assertEqual(x["open_independent_premises"], 6)
        for field in ("actual_lower_type_legality_certified", "actual_higher_center_certified",
                      "theorem38_proven", "theorem99_proven", "real_market_data_accessed"):
            self.assertIs(x[field], False)

    def test_pairwise_intersections_are_not_triple_intersection(self):
        self.assertEqual(
            m.interval_result(self.fixtures["fixtures"][2]["case"]),
            "NO_THREE_WAY_OVERLAP")

    def test_touch_point_is_not_silently_classed_as_width(self):
        self.assertEqual(m.interval_result(self.fixtures["fixtures"][1]["case"]),
                         "GEOMETRY_POINT_TOUCH_ONLY_UNRESOLVED_SOURCE_EQUALITY")

    def test_only_closed_exact_decimal_synthetic_strings(self):
        self.assertEqual(m.price("0.1") + m.price("0.2"), m.price("0.3"))
        with self.assertRaisesRegex(ValueError, "synthetic decimal"):
            m.price(1.0)
        with self.assertRaisesRegex(ValueError, "synthetic decimal"):
            m.price("NaN")
        with self.assertRaisesRegex(ValueError, "Malformed price interval"):
            x = copy.deepcopy(self.fixtures["fixtures"][0]["case"])
            x["intervals"][0] = ["5", "1"]
            m.interval_result(x)

    def test_out_of_order_undone_and_mixed_versions_are_not_confirmed(self):
        for i, expected in ((3, "PENDING_UNFINISHED_SUBTYPE"),
                            (4, "NOT_THREE_CONSECUTIVE_SUBTYPES"),
                            (5, "CROSS_LEVEL_NOT_SAME_SUBTYPE"),
                            (6, "RULE_VERSION_MISMATCH")):
            self.assertEqual(m.interval_result(self.fixtures["fixtures"][i]["case"]), expected)

    def test_self_declared_canonical_type_certificate_is_rejected(self):
        x = copy.deepcopy(self.fixtures["fixtures"][0]["case"])
        x["legal_type_certified"] = True
        with self.assertRaisesRegex(ValueError, "Unexpected source/market or claim fields"):
            m.interval_result(x)

    def test_base_equal_three_is_only_synthetic_predicate(self):
        self.assertEqual(m.lowest_equal_three(["2", "2.00", "2.0"]),
                         "SYMBOLIC_THREE_IDENTICAL_TRADE_PRICES_ONLY")
        self.assertEqual(m.lowest_equal_three(["2", "2.01", "2"]),
                         "SYMBOLIC_BASE_CONDITION_NOT_MET")

    def test_new_article_is_linked_and_does_not_claim_complete_parser(self):
        page = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/22_第17与35课递归中枢条件的来源可核判断.md"
        txt = page.read_text(encoding="utf-8")
        for needle in ("CL017-S02", "CL35-SO-2", "CL35-SO-3", "CL38-SOURCE-2",
                       "六项", "区间交集", "点接触", "SOURCE_PINNED_CONDITIONAL_RECURSIVE_GEOMETRY_ONLY",
                       "OB38-UNIQUE", "OB99-EXIST", "TEXT_FIRST_NO_IMAGE", "NOT_RUN"):
            self.assertIn(needle, txt)
        for idx in (ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/README.md",
                    ROOT / "deliverables/chanlun_108_acceptance/README.md"):
            self.assertIn(page.name, idx.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
