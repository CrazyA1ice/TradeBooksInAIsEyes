"""Synthetic F01 receipt DAG must not promote claimed finishes to real author proof."""
from __future__ import annotations
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location(
    "kaixiang_f01_graph_bridge",ROOT/"tools/audit_kaixiang_f01_graph_completion_bridge.py")
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)
BASE=ROOT/"tests/fixtures/kaixiang_f01_graph_bridge_v454.json"


class KaixiangF01GraphBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fx=json.loads(BASE.read_text(encoding="utf-8"))
        old=json.loads((ROOT/"tests/fixtures/kaixiang_asof_symbolic_v452.json").read_text(encoding="utf-8"))
        ctr=json.loads((ROOT/"tests/fixtures/kaixiang_center_asof_bridge_v453.json").read_text(encoding="utf-8"))
        cls.c=next(x for x in old["cases"] if x["id"]==cls.fx["case_id"])
        cls.src=next(x for x in ctr["bridge_cases"] if x["source_case_id"]==cls.fx["case_id"])

    def witness(self):
        return mod.build_synthetic_graph(self.fx)

    def run_witness(self,w,t=21):
        return mod.evaluate(self.c,self.src,w,t)

    def test_exact_prior_case_source_identity_and_full_fixture(self):
        self.assertEqual(self.fx["source_answer_ids"],self.c["source_answer_ids"])
        self.assertEqual(self.fx["source_answer_ids"],self.src["source_answer_ids"])
        result=mod.audit_fixture(BASE)
        self.assertEqual(result["f01_receipts"],31)
        self.assertEqual(result["visible_members"],[0,1,2,3])
        self.assertEqual(result["final_intersection"],[9.0,12.0])
        self.assertFalse(result["lower_level_finished_movements_independently_proven"])

    def test_graph_is_real_upstream_checker_not_a_dummy_flag(self):
        w=self.witness()
        verdict=mod.f01.check_graph(w["graph"])
        self.assertEqual(verdict["claim"],"STRUCTURAL_CHECKED_NOT_MARKET_AUTHENTICATED")
        self.assertEqual(verdict["receipt_count"],31)
        self.assertEqual(self.run_witness(w)["result"],mod.STATUS)

    def test_at_first_known_time_no_future_completion_leakage(self):
        w=self.witness()
        for t,count in ((5,0),(7,1),(14,2),(21,3)):
            x=self.run_witness(w,t)
            self.assertEqual(x["visible_finished_member_count"],count)
            self.assertFalse(x["legal_completed_lower_types_certified"])
            self.assertFalse(x["third_buy_confirmed"])
            self.assertFalse(x["account_order_sent"])
        self.assertIsNone(self.run_witness(w,14)["intersection_if_all_visible"])
        self.assertEqual(self.run_witness(w,21)["intersection_if_all_visible"],[9,12])

    def test_no_source_price_authentication_promotion(self):
        w=self.witness()
        x=self.run_witness(w)
        self.assertEqual(x["f01_market_status"],"NOT_AUTHENTICATED")
        self.assertEqual(x["f01_author_complete_rule_status"],"OPEN")
        self.assertFalse(x["full_center_eligibility_certified"])
        self.assertFalse(x["profit_evidence"])

    def test_reject_wrong_parent_center_or_reordered_members(self):
        w=self.witness()
        w["member_receipt_mapping"][0],w["member_receipt_mapping"][1]=(
            w["member_receipt_mapping"][1],w["member_receipt_mapping"][0])
        with self.assertRaisesRegex(ValueError,"parent three dependencies|child movements consecutive"):
            self.run_witness(w)
        w=self.witness()
        w["graph"]["nodes"][-1]["deps"].reverse()
        with self.assertRaisesRegex(ValueError,"parent three dependencies|child movements consecutive"):
            self.run_witness(w)

    def test_reject_mismatched_move_price_intervals(self):
        w=self.witness()
        w["members"][0]["low"]=8
        with self.assertRaisesRegex(ValueError,"ranges disagree"):
            self.run_witness(w)
        w=self.witness()
        mid=w["member_receipt_mapping"][0]["finished_receipt_id"]
        next(n for n in w["graph"]["nodes"] if n["id"]==mid)["low"]="6"
        with self.assertRaisesRegex(ValueError,"ranges disagree"):
            self.run_witness(w)

    def test_leaf_prices_must_support_claimed_movement_extrema(self):
        w=self.witness()
        raw=next(n for n in w["graph"]["nodes"] if n["kind"]=="RAW_TRADE")
        raw["price"]="9"
        with self.assertRaisesRegex(ValueError,"three CONSECUTIVE|same-price primitive"):
            self.run_witness(w)
        w=self.witness()
        raws=[n for n in w["graph"]["nodes"] if n["kind"]=="RAW_TRADE"]
        for n in raws[:3]:n["price"]="6"
        center=next(n for n in w["graph"]["nodes"] if n["kind"]=="F1_CENTER")
        center["low"]=center["high"]="6"
        with self.assertRaisesRegex(ValueError,"unsupported by six raw-price"):
            self.run_witness(w)

    def test_reject_fabricated_finished_market_authentication(self):
        w=self.witness()
        x=next(n for n in w["graph"]["nodes"] if n["kind"]=="FINISHED_MOVEMENT")
        x["market_finish_authenticated"]=True
        with self.assertRaisesRegex(ValueError,"structure only"):
            self.run_witness(w)

    def test_reject_unverified_raw_claimed_verified(self):
        w=self.witness()
        x=next(n for n in w["graph"]["nodes"] if n["kind"]=="RAW_TRADE")
        x["root_verified"]=True
        with self.assertRaisesRegex(ValueError,"raw source not authenticated"):
            self.run_witness(w)

    def test_reject_forward_dependency_time(self):
        w=self.witness()
        mid=w["member_receipt_mapping"][0]["finished_receipt_id"]
        node=next(n for n in w["graph"]["nodes"] if n["id"]==mid)
        node["first_known_seq"]=1
        with self.assertRaisesRegex(ValueError,"cannot know historical endpoint before observation|timestamp is before dependency"):
            self.run_witness(w)

    def test_reject_member_first_known_backdating(self):
        w=self.witness()
        w["members"][2]["first_known_tick"]=18
        with self.assertRaisesRegex(ValueError,"timestamp differs"):
            self.run_witness(w)

    def test_reject_cycle_and_unauthorized_evidence_type(self):
        w=self.witness()
        node=next(n for n in w["graph"]["nodes"] if n["kind"]=="RAW_TRADE")
        node["deps"]=[w["member_receipt_mapping"][0]["finished_receipt_id"]]
        with self.assertRaisesRegex(ValueError,"circular|first-known timestamp"):
            self.run_witness(w)
        w=self.witness()
        node=next(n for n in w["graph"]["nodes"] if n["kind"]=="F1_TREND_NONADVANCE")
        node["kind"]="SEGMENT_END"
        with self.assertRaisesRegex(ValueError,"source reference needed|wrong evidence types|segment"):
            self.run_witness(w)

    def test_reject_wrong_policy_and_real_market_mode(self):
        w=self.witness()
        w["graph"]["policy_id"]="not_the_frozen_policy"
        with self.assertRaisesRegex(ValueError,"policy mismatched"):
            self.run_witness(w)
        w=self.witness()
        w["graph"]["mode"]="AUTHENTICATED_MARKET"
        with self.assertRaisesRegex(ValueError,"never accept certified market mode"):
            self.run_witness(w)

    def test_original_bridge_member_values_are_not_mutated(self):
        a=copy.deepcopy(self.c)
        b=copy.deepcopy(self.src)
        w=self.witness()
        mod.evaluate(self.c,self.src,w,14)
        self.assertEqual(self.c,a)
        self.assertEqual(self.src,b)

    def test_no_real_data_side_effects_or_trade(self):
        w=self.witness()
        t=self.run_witness(w,21)
        self.assertFalse(t["market_data"])
        self.assertFalse(t["account_order_sent"])
        self.assertFalse(t["conclusive_final_hypothesis"])
        self.assertFalse(t["third_buy_confirmed"])


if __name__=="__main__":
    unittest.main()
