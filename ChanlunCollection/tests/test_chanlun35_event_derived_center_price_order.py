"""Source-limited event-derived lowest-center ordering; no fake completed trend."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"tools/audit_chanlun35_event_center_price_order.py"
spec=importlib.util.spec_from_file_location("chanlun35_event_price_order",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class EventDerivedCenterOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=m.original()
        cls.lifecycle=cls.base.lifecycle_tool()
        cls.primitive=cls.lifecycle.original_primitive()
        cls.doc=m.read(m.CONTRACT)
        cls.fixtures=m.read(m.FIXTURES)
        cls.card={n:m.read(ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json")
                  for n in (18,20,35)}
        cls.terminal=m.read(m.SOURCE_TERMINAL)

    def sample(self,name):
        return copy.deepcopy(next(x["input"] for x in self.fixtures["cases"] if x["id"]==name))

    def check(self,doc=None,cards=None,terminal=None):
        return m.validate_contract(self.doc if doc is None else doc,
                                   self.base,self.primitive,
                                   self.card if cards is None else cards,
                                   self.terminal if terminal is None else terminal)

    def test_original_author_p291_source_and_n_gt_two_terminal_are_locked(self):
        self.check()
        self.assertEqual(self.doc["original_physical_page"],291)
        self.assertEqual(self.doc["native_text_sha256"],m.PAGE_SHA)
        self.assertEqual(self.doc["author_claims"],["CL35-SO-2","CL35-SO-9","CL018-S07"])

    def test_all_14_synthetic_event_stories_repeatably_classified(self):
        receipt=m.verify_fixtures(self.fixtures,self.doc,self.base)
        self.assertEqual(receipt["synthetic_raw_event_cases"],14)
        self.assertEqual(receipt["source_author_claims"],3)
        self.assertEqual(receipt["unverified_membership_and_completion_slots"],6)
        self.assertEqual(receipt["actual_completed_trajectories"],0)
        self.assertFalse(receipt["market_data_accessed"])

    def test_relative_price_is_derived_from_raw_trades_not_submitted_label(self):
        x=m.inspect(self.sample("up_two"),self.doc,self.base)
        self.assertEqual([r["price_exact_decimal"] for r in x["center_price_relations"]],
                         ["1","2"])
        self.assertEqual([r["relative_to_prior"] for r in x["center_price_relations"]],
                         ["BASE","HIGHER"])
        self.assertEqual(x["center_price_relations"][1]["first_three_trade_ids"],
                         [5,6,7])
        self.assertEqual(len(x["center_price_relations"][1]["original_three_trade_sha256"]),64)
        self.assertFalse(x["center_identity_author_certified"])

    def test_second_same_price_is_left_unresolved_not_called_down(self):
        x=m.inspect(self.sample("initial_equal"),self.doc,self.base)
        self.assertEqual(x["status"],"INITIAL_EQUAL_CENTER_PRICES_UNRESOLVED")
        self.assertEqual(x["first_terminal_center_ordinal"],None)
        self.assertFalse(x["trend_actually_completed"])

    def test_one_center_not_certified_finished_consolidation(self):
        x=m.inspect(self.sample("one_center"),self.doc,self.base)
        self.assertEqual(x["status"],"ONE_CENTER_POSSIBLE_CONSOLIDATION_NOT_COMPLETED")
        self.assertEqual(x["center_count"],1)
        self.assertFalse(x["trend_actually_completed"])

    def test_up_and_down_two_center_strictly_ordered_conditions(self):
        self.assertEqual(m.inspect(self.sample("up_two"),self.doc,self.base)["status"],
                         "UP_INITIAL_PRICE_PAIR_ONLY")
        self.assertEqual(m.inspect(self.sample("down_two"),self.doc,self.base)["status"],
                         "DOWN_INITIAL_PRICE_PAIR_ONLY")

    def test_third_center_equal_or_reversing_triggers_only_price_condition(self):
        for name,sign in (("up_terminal_equal_third","UP"),
                          ("up_terminal_lower_third","UP"),
                          ("down_terminal_equal_third","DOWN"),
                          ("down_terminal_higher_third","DOWN")):
            with self.subTest(name=name):
                x=m.inspect(self.sample(name),self.doc,self.base)
                self.assertEqual(x["status"],sign+"_AUTHOR_N_GT_2_TERMINAL_PRICE_TRIGGER_ONLY")
                self.assertEqual(x["first_terminal_center_ordinal"],3)
                self.assertFalse(x["trend_actually_completed"])

    def test_earliest_trigger_does_not_move_when_later_price_rises_again(self):
        x=m.inspect(self.sample("earliest_fourth_trigger"),self.doc,self.base)
        self.assertEqual(x["first_terminal_center_ordinal"],4)
        self.assertEqual(x["center_count"],5)
        self.assertEqual(x["center_price_relations"][-1]["relative_to_prior"],"HIGHER")

    def test_visible_asof_prefix_excludes_future_third_center(self):
        x=m.inspect(self.sample("future_third_excluded"),self.doc,self.base)
        y=m.inspect(self.sample("up_two"),self.doc,self.base)
        self.assertEqual([i["price_exact_decimal"] for i in x["center_price_relations"]],
                         [i["price_exact_decimal"] for i in y["center_price_relations"]])
        self.assertEqual(x["status"],"UP_INITIAL_PRICE_PAIR_ONLY")
        self.assertEqual(x["center_count"],2)

    def test_mixed_visible_version_blocks_inferred_center_price_order(self):
        x=m.inspect(self.sample("mixed_visible_rule"),self.doc,self.base)
        self.assertEqual(x["status"],"VERSION_MISMATCH_NO_ORDER")
        self.assertEqual(x["center_price_relations"],[])

    def test_declared_manual_relation_or_pretended_completed_type_is_rejected(self):
        sample=self.sample("up_two")
        sample["events"][0]["manual_relation_to_previous"]="HIGHER"
        with self.assertRaisesRegex(ValueError,"certification"):
            m.inspect(sample,self.doc,self.base)
        sample=self.sample("up_two")
        sample["legal_trajectory_completed"]=True
        with self.assertRaisesRegex(ValueError,"certification"):
            m.inspect(sample,self.doc,self.base)

    def test_n_gt_two_source_equality_cannot_be_removed(self):
        t=copy.deepcopy(self.terminal)
        t["author_conditional_rules"][2]["relations"]=["LOWER"]
        with self.assertRaisesRegex(ValueError,"terminal equality"):
            self.check(terminal=t)
        c=copy.deepcopy(self.doc)
        c["rule_clause"]["from_third"]["up_terminal"]="LATER_PRICE_LT_PRIOR_PRICE"
        with self.assertRaisesRegex(ValueError,"invented"):
            self.check(doc=c)

    def test_source_claim_misattribution_or_fake_center_completion_fail_closed(self):
        card=copy.deepcopy(self.card)
        source=next(x for x in card[35]["claims"] if x["id"]=="CL35-SO-9")
        source["kind"]="EDITORIAL"
        with self.assertRaisesRegex(ValueError,"non-author claim"):
            self.check(cards=card)
        d=copy.deepcopy(self.doc)
        d["valid_completed_trajectories"]=1
        with self.assertRaisesRegex(ValueError,"False completed trend"):
            self.check(doc=d)

    def test_raw_runs_are_not_necessarily_distinct_author_centers(self):
        x=m.inspect(self.sample("up_continuation"),self.doc,self.base)
        self.assertEqual(x["status"],"UP_DIRECTIONAL_PRICE_CONTINUATION_ONLY")
        self.assertTrue(all(not r["distinct_author_center_identity_verified"]
                            for r in x["center_price_relations"]))
        self.assertFalse(x["trend_actually_completed"])
        self.assertFalse(self.doc["can_feed_higher_level_recursive_constructor"])

    def test_no_market_data_and_no_unauthorized_source_extension(self):
        self.assertFalse(self.doc["actual_trade_provenance_authenticated"])
        self.assertFalse(self.doc["lowest_level_trend_termination_proven"])
        self.assertFalse(self.doc["proof38_unique"])
        self.assertFalse(self.doc["proof99_universal"])
        self.assertEqual(self.doc["market_backtests"],"NOT_RUN")

    def test_guide_article_and_both_readmes_link_to_this_advance(self):
        article=ROOT/"deliverables/chanlun_108_acceptance/04_AI_GUIDE/28_第35课从原始交易中枢价格到趋势条件推导.md"
        txt=article.read_text(encoding="utf-8")
        for word in ("CL35-SO-2","CL35-SO-9","卷二p.291","相等",
                     "INITIAL_EQUAL_CENTER_PRICES_UNRESOLVED",
                     "UP_AUTHOR_N_GT_2_TERMINAL_PRICE_TRIGGER_ONLY",
                     "不同原始同价段","完成","OB38-UNIQUE","NOT_RUN"):
            self.assertIn(word,txt)
        for parent in (article.parent/"README.md",
                       ROOT/"deliverables/chanlun_108_acceptance/README.md"):
            self.assertIn(article.name,parent.read_text(encoding="utf-8"))


if __name__=="__main__":
    unittest.main()
