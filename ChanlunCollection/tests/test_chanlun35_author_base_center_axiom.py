"""Lesson35 p291 original lowest-level center is a conditional sufficient definition."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location(
    "author_axiom", ROOT/"tools/audit_chanlun35_author_base_center_axiom.py")
m=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class AuthorMinimumCenterAxiomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=m.lifecycle_tool()
        cls.primitive=cls.ledger.original_primitive()
        cls.doc=m.read(m.CONTRACT)
        cls.fixtures=m.read(m.CASES)
        cls.cards={n:m.read(ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json")
                   for n in (18,20,35)}

    def case(self,name):
        return copy.deepcopy(next(x["input"] for x in self.fixtures["cases"]
                                  if x["id"]==name))

    def check(self,doc=None,cards=None):
        return m.validate_contract(self.doc if doc is None else doc,
                                   self.ledger,self.primitive,
                                   self.cards if cards is None else cards)

    def test_author_page_291_source_says_constitutes_not_just_necessary(self):
        self.check()
        self.assertEqual(
            self.doc["author_original_base_axiom"],
            "THREE_CONSECUTIVE_IDENTICAL_PRICE_TRADES_CONSTITUTE_LOWEST_LEVEL_CENTER")
        self.assertEqual(self.doc["native_text_sha256"],m.PAGE_SHA)
        self.assertEqual(self.doc["author_text_claim_id"],"CL35-SO-2")

    def test_direct_three_events_generate_provenance_pinned_definitional_instance(self):
        c=m.produce(self.case("first_three_equal"),self.doc,self.ledger)
        self.assertEqual(c["status"],"AUTHOR_BASE_CENTER_AXIOM_APPLIES_IN_SYNTHETIC_STREAM")
        self.assertEqual(len(c["instances"]),1)
        i=c["instances"][0]
        self.assertEqual(i["first_three_trade_ids"],[1,2,3])
        self.assertEqual(i["first_observed_at"],"2026-11-08T09:02:00+00:00")
        self.assertEqual(i["source_claim_id"],"CL35-SO-2")
        self.assertEqual(i["certificate_kind"],m.CERT)
        self.assertTrue(i["conditional_base_center_exists_in_assumed_trades"])
        self.assertFalse(i["parent_trajectory_completed"])
        self.assertFalse(i["independent_real_trade_provenance_verified"])
        self.assertTrue(m.verify_receipt(self.case("first_three_equal"),c,self.doc,self.ledger))

    def test_two_events_or_asof_before_events_no_axiom_instance(self):
        for label in ("before_third","asof_before_first_event"):
            with self.subTest(label=label):
                p=m.produce(self.case(label),self.doc,self.ledger)
                self.assertEqual(p["instances"],[])
                self.assertEqual(p["status"],
                                 "NO_AUTHORED_BASE_CENTER_INSTANCE_IN_VISIBLE_PREFIX")

    def test_price_change_closes_only_raw_run_and_preserves_definitional_instance(self):
        r=m.produce(self.case("first_price_break_closes_only_raw_run"),self.doc,self.ledger)
        self.assertEqual(len(r["instances"]),1)
        x=r["instances"][0]
        self.assertTrue(x["raw_run_closed_only"])
        self.assertEqual(x["raw_run_closed_by_trade_id"],4)
        self.assertFalse(x["parent_trajectory_completed"])
        self.assertFalse(x["eligible_as_completed_child_type"])

    def test_same_price_extension_does_not_create_new_base_center_instance(self):
        first=m.produce(self.case("first_three_equal"),self.doc,self.ledger)
        later=m.produce(self.case("extend_equal_fourth"),self.doc,self.ledger)
        self.assertEqual(len(later["instances"]),1)
        self.assertEqual(first["instances"][0]["first_three_source_event_sha256"],
                         later["instances"][0]["first_three_source_event_sha256"])
        self.assertEqual(first["instances"][0]["first_observed_at"],
                         later["instances"][0]["first_observed_at"])

    def test_two_raw_runs_separated_by_other_price_create_two_distinct_instances(self):
        r=m.produce(self.case("two_equal_runs_separated"),self.doc,self.ledger)
        self.assertEqual([x["first_three_trade_ids"] for x in r["instances"]],
                         [[1,2,3],[5,6,7]])
        self.assertEqual([x["raw_run_closed_only"] for x in r["instances"]],
                         [True,False])
        self.assertFalse(r["real_market_authenticated"])

    def test_future_price_change_does_not_alter_asof_axiom_proof(self):
        a=m.produce(self.case("first_three_equal"),self.doc,self.ledger)
        b=m.produce(self.case("future_change_not_asof_visible"),self.doc,self.ledger)
        self.assertEqual(a,b)

    def test_decimal_equivalent_prices_produce_canonical_value(self):
        x=m.produce(self.case("exact_decimal_canonical_equal"),self.doc,self.ledger)
        self.assertEqual(x["instances"][0]["price_exact_decimal"],"2")

    def test_mixed_visible_rule_versions_invalidate_author_axiom(self):
        x=m.produce(self.case("observed_mixed_version_blocks"),self.doc,self.ledger)
        self.assertEqual(x["instances"],[])
        self.assertEqual(x["status"],"RULE_VERSION_INCOMPATIBLE_NO_AUTHORED_BASE_INSTANCE")

    def test_tampering_proof_rejected_without_full_recomputation(self):
        row=self.case("first_three_equal")
        proof=m.produce(row,self.doc,self.ledger)
        altered=copy.deepcopy(proof)
        altered["instances"][0]["first_three_trade_ids"]=[1,2,4]
        with self.assertRaisesRegex(ValueError,"Receipt altered"):
            m.verify_receipt(row,altered,self.doc,self.ledger)
        altered=copy.deepcopy(proof)
        altered["instances"][0]["parent_trajectory_completed"]=True
        with self.assertRaisesRegex(ValueError,"Receipt altered"):
            m.verify_receipt(row,altered,self.doc,self.ledger)
        altered=copy.deepcopy(proof)
        altered["instances"][0]["native_text_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"Receipt altered"):
            m.verify_receipt(row,altered,self.doc,self.ledger)

    def test_corrupt_original_pdf_source_card_cannot_create_axiom(self):
        cards=copy.deepcopy(self.cards)
        row=next(x for x in cards[35]["claims"] if x["id"]=="CL35-SO-2")
        row["kind"]="EDITORIAL"
        with self.assertRaisesRegex(ValueError,"verifiable author"):
            self.check(cards=cards)
        doc=copy.deepcopy(self.doc)
        doc["native_text_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"Exact authored original"):
            self.check(doc=doc)

    def test_an_author_base_center_is_not_an_actual_ended_trajectory(self):
        doc=copy.deepcopy(self.doc)
        doc["actual_center_completed"]=True
        with self.assertRaisesRegex(ValueError,"unsupported proof"):
            self.check(doc=doc)
        doc=copy.deepcopy(self.doc)
        doc["can_feed_higher_level_constructor"]=True
        with self.assertRaisesRegex(ValueError,"unsupported proof"):
            self.check(doc=doc)

    def test_conditional_center_cannot_be_passed_to_higher_center_constructor(self):
        obj=m.produce(self.case("first_three_equal"),self.doc,self.ledger)
        p=ROOT/"tools/audit_chanlun_recursive_source_eligibility.py"
        modspec=importlib.util.spec_from_file_location("recursive_conditional_geometry",p)
        mod=importlib.util.module_from_spec(modspec)
        modspec.loader.exec_module(mod)
        with self.assertRaisesRegex(ValueError,"Unexpected source/market or claim fields"):
            mod.interval_result(obj)

    def test_all_ten_synthetic_cases_and_eight_base_instances(self):
        x=m.fixtures_check(self.fixtures,self.doc,self.ledger)
        self.assertEqual(x["cases"],10)
        self.assertEqual(x["conditional_instances"],8)
        self.assertEqual(x["actual_completed_parent_types"],0)
        self.assertFalse(x["market_data_accessed"])
        self.assertFalse(x["proved_38_or_99"])

    def test_article_readme_and_prior_two_guides_include_source_correction(self):
        filename="27_第35课三笔同价构成最低级别中枢的定义性证据.md"
        page=ROOT/"deliverables/chanlun_108_acceptance/04_AI_GUIDE"/filename
        body=page.read_text(encoding="utf-8")
        for fragment in ("CL35-SO-2","卷二p.291","构成最低级别的中枢",
                         "必要条件", "充分条件", "AUTHOR_LOWEST_CENTER_AXIOM_IN_ASSUMED_EVENT_STREAM",
                         "独立验证", "OB38-UNIQUE", "NOT_RUN"):
            self.assertIn(fragment,body)
        for doc in ("25_第35课三笔同价交易的原始事件证据与未完成边界.md",
                    "26_同价成交段的生命周期与中枢完成证据隔离.md",
                    "README.md"):
            self.assertIn(filename,(page.parent/doc).read_text(encoding="utf-8"))
        self.assertIn(filename,(ROOT/"deliverables/chanlun_108_acceptance/README.md")
                      .read_text(encoding="utf-8"))


if __name__=="__main__":
    unittest.main()
