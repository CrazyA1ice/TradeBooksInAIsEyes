"""Author-pinned Zn extension condition is not a raw-trade center grouping proof."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"tools/audit_chanlun20_center_extension_membership_gate.py"
spec=importlib.util.spec_from_file_location("chanlun20_membership_gate",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class AuthorCenterMembershipGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=m.read(m.CONTRACT)
        cls.fixtures=m.read(m.FIXTURES)
        cls.pins=m.read(m.SOURCE_PINS)
        cls.inventory=m.read(m.SOURCE_INVENTORY)
        cls.cards={n:m.read(ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json")
                   for n in (18,20)}
        cls.rank=m.read(ROOT/"catalog/chanlun35_event_derived_center_price_order_v1.json")

    def original(self,doc=None,pins=None,cards=None,rank=None):
        m.validate_contract(self.doc if doc is None else doc,
                            self.pins if pins is None else pins,
                            self.inventory,
                            self.cards if cards is None else cards,
                            self.rank if rank is None else rank)

    def case(self,key):
        return copy.deepcopy(next(x["input"] for x in self.fixtures["cases"]
                                  if x["id"]==key))

    def test_source_volume_pdf_and_four_page_hashes(self):
        self.original()
        self.assertEqual(self.doc["volume1_pdf_sha256"],m.PDF_SHA)
        self.assertEqual(self.doc["native_pages_sha256"],m.PAGES)
        self.assertEqual(len(self.doc["original_sources"]),4)

    def test_source_role_or_native_text_hash_tampering_fails_closed(self):
        p=copy.deepcopy(self.pins)
        p["page_native_text_sha256"]["246"]="0"*64
        with self.assertRaisesRegex(ValueError,"provenance drift"):
            self.original(pins=p)
        cards=copy.deepcopy(self.cards)
        next(x for x in cards[20]["claims"] if x["id"]=="CL020-S02")["kind"]="EDITORIAL"
        with self.assertRaisesRegex(ValueError,"retyped"):
            self.original(cards=cards)

    def test_strict_disjointness_and_touch_open_cannot_be_rewritten_as_certified_extension(self):
        d=copy.deepcopy(self.doc)
        d["touch_policy"]="TOUCH_PROVES_EXTENSION"
        with self.assertRaisesRegex(ValueError,"formula or strict boundary"):
            self.original(doc=d)
        d=copy.deepcopy(self.doc)
        d["certificates"]["author_center_extension_certified"]=True
        with self.assertRaisesRegex(ValueError,"false completion proof"):
            self.original(doc=d)

    def test_raw_two_distinct_price_runs_still_have_no_author_Zn_membership(self):
        x=m.evaluate(self.case("raw_up_two_price_runs_not_independent_centers"),self.doc)
        self.assertEqual(x["raw_conditional_base_centers"],2)
        self.assertEqual(x["raw_price_condition"],"UP_INITIAL_PRICE_PAIR_ONLY")
        self.assertEqual(x["status"],"RAW_TRADE_RUN_CENTER_IDENTITY_UNRESOLVED_NO_ZN")
        self.assertFalse(x["author_independent_center_certified"])

    def test_raw_same_price_two_runs_still_not_author_extension_proof(self):
        x=m.evaluate(self.case("raw_equal_two_price_runs_not_extension_certificate"),self.doc)
        self.assertEqual(x["status"],"RAW_TRADE_RUN_CENTER_IDENTITY_UNRESOLVED_NO_ZN")
        self.assertEqual(x["raw_price_condition"],"INITIAL_EQUAL_CENTER_PRICES_UNRESOLVED")
        self.assertFalse(x["author_center_extension_certified"])

    def test_three_raw_centers_and_N_terminal_do_not_become_completed_trend(self):
        x=m.evaluate(self.case("raw_three_scalar_centers_do_not_imply_completed_trend"),self.doc)
        self.assertEqual(x["raw_conditional_base_centers"],3)
        self.assertEqual(x["raw_price_condition"],
                         "UP_AUTHOR_N_GT_2_TERMINAL_PRICE_TRIGGER_ONLY")
        self.assertFalse(x["trajectory_completed"])
        self.assertFalse(x["higher_center_can_be_constructed"])

    def test_author_declared_Zn_core_and_overlap_are_conditional_only(self):
        x=m.evaluate(self.case("zn_overlap_with_frozen_core"),self.doc)
        self.assertEqual(x["frozen_core"],{"ZD":"2","ZG":"5"})
        self.assertEqual(x["status"],"AUTHOR_ZN_EXTENSION_OVERLAP_CONDITION_ONLY")
        self.assertFalse(x["author_z_membership_verified"])
        self.assertFalse(x["author_center_extension_certified"])

    def test_author_Zn_disjointness_breaks_only_extension_interval_condition(self):
        x=m.evaluate(self.case("zn_disjoint_frozen_core"),self.doc)
        self.assertEqual(x["status"],
                         "AUTHOR_ZN_EXTENSION_STRICT_DISJOINTNESS_CONDITION_ONLY")
        self.assertEqual(x["first_strictly_disjoint_zn"],3)
        self.assertFalse(x["author_independent_center_certified"])

    def test_point_touch_is_a_distinct_unresolved_price_boundary(self):
        for key,status in (("zn_touch_boundary_kept_open","ZN_POINT_TOUCH_BOUNDARY_UNRESOLVED"),
                           ("zn_core_point_touch","CORE_POINT_TOUCH_BOUNDARY_UNRESOLVED")):
            with self.subTest(key=key):
                self.assertEqual(m.evaluate(self.case(key),self.doc)["status"],status)

    def test_nonoverlap_between_initial_core_members_is_not_a_center(self):
        x=m.evaluate(self.case("zn_core_empty"),self.doc)
        self.assertEqual(x["status"],"DECLARED_ZN_CORE_EMPTY")

    def test_future_disjoint_child_cannot_change_past_asof_decision(self):
        x=m.evaluate(self.case("zn_disjoint_later_not_visible"),self.doc)
        self.assertEqual(x["visible_zn"],2)
        self.assertEqual(x["status"],"NO_SUBSEQUENT_ZN_EXTENSION_EVENT")
        item=self.case("zn_disjoint_later_not_visible")
        item["members"][-1]["interval"]=["900","1000"]
        self.assertEqual(m.evaluate(item,self.doc),x)

    def test_unconfirmed_child_cannot_be_promoted_to_Zn_extension(self):
        x=m.evaluate(self.case("zn_missing_completion_cannot_be_used"),self.doc)
        self.assertEqual(x["status"],"UNCONFIRMED_ZN_NOT_EVALUATED")
        self.assertFalse(x["author_center_extension_certified"])

    def test_mixed_historical_versions_block_Zn_comparison(self):
        x=m.evaluate(self.case("zn_mixed_rules_not_comparable"),self.doc)
        self.assertEqual(x["status"],"DECLARED_ZN_RULE_VERSION_MISMATCH")
        self.assertEqual(x["frozen_core"],None)

    def test_arbitrary_manual_author_certificate_rejected_before_any_computation(self):
        data=self.case("zn_overlap_with_frozen_core")
        data["members"][2]["author_legal_Zn"]=True
        with self.assertRaisesRegex(ValueError,"legal certificate fields"):
            m.evaluate(data,self.doc)
        data=self.case("raw_up_two_price_runs_not_independent_centers")
        data["manual_center_grouping"]="TWO_INDEPENDENT"
        with self.assertRaisesRegex(ValueError,"Unexpected manual Zn"):
            m.evaluate(data,self.doc)

    def test_unordered_clocks_invalid_intervals_and_float_are_rejected(self):
        x=self.case("zn_overlap_with_frozen_core")
        x["members"][1]["seen_at"]=x["members"][0]["seen_at"]
        with self.assertRaisesRegex(ValueError,"strictly increasing"):
            m.evaluate(x,self.doc)
        x=self.case("zn_overlap_with_frozen_core")
        x["members"][2]["interval"]=["9","8"]
        with self.assertRaisesRegex(ValueError,"high below low"):
            m.evaluate(x,self.doc)
        x=self.case("zn_overlap_with_frozen_core")
        x["members"][2]["interval"][0]=3.0
        with self.assertRaisesRegex(ValueError,"exact positive decimal"):
            m.evaluate(x,self.doc)

    def test_extension_core_stays_frozen_to_first_two_declared_Zn(self):
        row=m.evaluate(self.case("zn_two_extra_overlapping_members"),self.doc)
        self.assertEqual(row["visible_zn"],4)
        self.assertEqual(row["frozen_core"],{"ZD":"2","ZG":"5"})
        self.assertEqual(row["status"],"AUTHOR_ZN_EXTENSION_OVERLAP_CONDITION_ONLY")

    def test_12_cases_and_no_certified_child_or_trade(self):
        report=m.fixtures_check(self.fixtures,self.doc)
        self.assertEqual(report["synthetic_cases"],12)
        self.assertEqual(report["unverified_premises"],7)
        self.assertEqual(report["genuine_independent_centers_certified"],0)
        self.assertEqual(report["genuine_completed_types_certified"],0)
        self.assertFalse(report["market_data_read"])

    def test_source_granularity_remains_closed_to_theorem38_and_theorem99(self):
        self.assertFalse(self.doc["certificates"]["lesson38_uniqueness_proven"])
        self.assertFalse(self.doc["certificates"]["lesson99_universal_center_proven"])
        self.assertFalse(self.doc["market_inputs_read"])
        self.assertEqual(self.doc["backtest_status"],"NOT_RUN")

    def test_article_and_index_require_identity_extension_separation(self):
        article=ROOT/"deliverables/chanlun_108_acceptance/04_AI_GUIDE/29_第20课中枢延伸与独立中枢的证据资格闸门.md"
        txt=article.read_text(encoding="utf-8")
        for word in ("CL020-S01","CL020-S02","卷一p.245","卷一p.246",
                     "RAW_TRADE_RUN_CENTER_IDENTITY_UNRESOLVED_NO_ZN",
                     "AUTHOR_ZN_EXTENSION_OVERLAP_CONDITION_ONLY",
                     "中枢延伸", "原始同价段","不能自动","OB38-UNIQUE","NOT_RUN"):
            self.assertIn(word,txt)
        for index in (article.parent/"README.md",
                      ROOT/"deliverables/chanlun_108_acceptance/README.md"):
            self.assertIn(article.name,index.read_text(encoding="utf-8"))


if __name__=="__main__":
    unittest.main()
