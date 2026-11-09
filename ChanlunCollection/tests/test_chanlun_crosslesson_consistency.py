"""Cross-lesson logic consistency: proof scopes, provenance and toy implications."""
import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
MODULE_PATH=ROOT/"tools/audit_chanlun_crosslesson_consistency.py"
spec=importlib.util.spec_from_file_location("cl108_consistency",MODULE_PATH)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class WholeBookTheoryConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract=m.load(m.LEDGER)
        cls.manuscript=m.MANUSCRIPT.read_text(encoding="utf-8")

    def test_all_16_tensions_source_and_rule_history_are_checked(self):
        receipt=m.audit()
        self.assertEqual(receipt["tensions"],16)
        self.assertGreaterEqual(receipt["distinct_canonical_SOURCE_claims"],30)
        self.assertGreaterEqual(receipt["coexisting_rule_versions"],8)
        self.assertFalse(receipt["author_theory_contradiction_proven"])
        self.assertFalse(receipt["author_theory_consistency_proven"])

    def test_all_five_evidence_scope_classes_are_present(self):
        self.assertEqual(set(x["status"] for x in self.contract["entries"]),m.CATEGORIES)
        self.assertEqual(set(self.contract["case_types"]),m.CATEGORIES)

    def test_each_source_claim_exists_and_retains_source_pdf(self):
        index=m.load(m.INDEX)
        vols={x["lesson"]:vol for vol in index["volumes"] for x in vol["lessons"]}
        for case in self.contract["entries"]:
            for x in case["source_claims"]:
                with self.subTest(case=case["id"],source=x):
                    c=m.load(ROOT/f"knowledge/evidence/chanlun_lesson{x['lesson']:03d}.json")
                    source=next(z for z in c["claims"] if z["id"]==x["claim_id"])
                    self.assertEqual(source["kind"],"SOURCE")
                    self.assertEqual(c["source"]["sha256"],vols[x["lesson"]]["sha256"])
                    self.assertTrue(source["pdf_pages"])

    def test_no_type_claim_stated_as_theorem_proof(self):
        for k in m.NO_FORMAL_PROOF:
            self.assertIs(self.contract[k],False)
        for e in self.contract["entries"]:
            self.assertFalse(e["counterexample_proves_original_author_wrong"])
            self.assertFalse(e["authorial_intent_inferred"])
            self.assertFalse(e["actual_trade_verified"])
        self.assertEqual(self.contract["financial_backtests"],"NOT_RUN")

    def test_all_13_finite_models_show_only_abstract_nonimplications(self):
        computed={}
        for entry in self.contract["entries"]:
            label=entry["abstract_model"]
            if label in {"NO_FORMAL_COUNTERMODEL_TO_RG","RULE_REVISION_NOT_RETROACTIVE","REGISTRY_NO_GLOBAL_SUPERSESSION"}:
                continue
            left,right=m.witness(label)
            computed[entry["id"]]=(left,right)
            self.assertIs(left,True)
            self.assertIs(right,False)
        self.assertEqual(len(computed),13)
        self.assertNotIn("C07",computed)
        self.assertNotIn("C09",computed)
        self.assertNotIn("C16",computed)

    def test_completed_center_does_not_follow_merely_from_minimal_author_axiom(self):
        self.assertEqual(m.witness("BASE_CENTER_EXISTS_NOT_ENDED"),(True,False))
        self.assertIn("构成不推出当下结束",self.manuscript)

    def test_source_three_buy_may_be_followed_by_other_structure(self):
        self.assertEqual(m.witness("THIRD_BUY_NOT_FUTURE_TREND"),(True,False))
        self.assertIn("第三类买点后",self.manuscript)
        self.assertIn("高级别盘整",self.manuscript)

    def test_covering_buy_points_does_not_entail_execution_profit(self):
        self.assertEqual(m.witness("COVERAGE_NOT_PROFIT"),(True,False))
        self.assertIn("U_buy",self.manuscript)
        self.assertIn("B1∪B2∪B3",self.manuscript)

    def test_nonsufficient_third_point_necessary_for_specific_large_reversal(self):
        self.assertEqual(m.witness("NECESSARY_NOT_SUFFICIENT"),(True,False))
        self.assertIn("L⇒T",self.manuscript)
        self.assertIn("T⇒L",self.manuscript)

    def test_associativity_is_not_a_unique_parse_theorem(self):
        self.assertEqual(m.witness("ASSOCIATIVITY_NOT_UNIQUE_PARSE"),(True,False))
        self.assertIn("[ab]",self.manuscript)
        self.assertIn("[a][b]",self.manuscript)

    def test_existential_future_does_not_prove_universal_termination(self):
        self.assertEqual(m.witness("EXISTS_NOT_FORALL"),(True,False))
        self.assertIn("∀ future, ∃ finite t",self.manuscript)
        self.assertIn("不能将这个玩具集合当作对第99课原文的真实反例",self.manuscript)

    def test_recursion_f1_f2_not_automorphism(self):
        self.assertEqual(m.witness("RECURSIVE_GRAMMAR_NOT_BIJECTION"),(True,False))
        self.assertIn("f1_a",self.manuscript)
        self.assertIn("双射",self.manuscript)

    def test_editor_and_unknown_appendix_appear_with_null_dating(self):
        reg=m.load(m.VERSIONS)
        entries={x["id"]:x for x in reg["entries"]}
        for k in ("pen_062_appended_candidate","segment_067_editor_objection"):
            self.assertIsNone(entries[k]["source_displayed_at"])
            self.assertEqual(entries[k]["timestamp_basis"],"unknown")
        self.assertIsNotNone(entries["pen_081_later_dated_post"]["source_displayed_at"])

    def test_33_multi_meaning_and_38_uniqueness_kept_scoped_unresolved(self):
        row=next(x for x in self.contract["entries"] if x["id"]=="C07")
        self.assertEqual(row["status"],"CONDITIONAL_SCOPE_RECONCILIATION")
        self.assertIn("待核",self.manuscript)
        self.assertIn("R_g",self.manuscript)
        self.assertFalse(row["counterexample_proves_original_author_wrong"])

    def test_bottom_types_fractal_and_trend_not_conflated(self):
        self.assertEqual(m.witness("FRACTAL_BOTTOM_NOT_STRUCTURAL_BOTTOM"),(True,False))
        row=next(x for x in self.contract["entries"] if x["id"]=="C14")
        self.assertEqual(row["status"],"TYPE_DOMAIN_RESTRICTION")
        self.assertIn("2008年10月",self.manuscript)

    def test_new_integrated_manuscript_is_linked_and_has_crosswalk(self):
        self.assertGreaterEqual(len(self.manuscript),12000)
        readme=(ROOT/"deliverables/chanlun_108_acceptance/README.md").read_text(encoding="utf-8")
        self.assertIn(m.MANUSCRIPT.name,readme)
        for case in self.contract["entries"]:
            self.assertIn(case["id"],self.manuscript)


if __name__=="__main__":
    unittest.main()
