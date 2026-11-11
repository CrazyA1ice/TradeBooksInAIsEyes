"""A source-bounded initial-direction proof guard over the pre-existing F01 graph."""
from __future__ import annotations
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location("kx_v455",ROOT/"tools/audit_kaixiang_f01_direction_three_centers.py")
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)
FIXTURE=ROOT/"tests/fixtures/kaixiang_f01_direction_three_centers_v455.json"


class KaixiangDirectionReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=json.loads(FIXTURE.read_text(encoding="utf-8"))
        prior=json.loads((ROOT/"tests/fixtures/kaixiang_asof_symbolic_v452.json").read_text(encoding="utf-8"))
        cls.c=next(x for x in prior["cases"] if x["id"]==cls.spec["source_case_id"])
        p=json.loads((ROOT/"tests/fixtures/kaixiang_center_asof_bridge_v453.json").read_text(encoding="utf-8"))
        cls.b=next(x for x in p["bridge_cases"] if x["source_case_id"]==cls.c["id"])

    def witness(self):
        return mod.generate(self.spec)

    def check(self,w,at=28):
        return mod.evaluate(w,self.c,self.b,at)

    def change_center(self,w,member_index,center_index,price):
        q=w["certificates"][member_index]
        cid=[q["initial_center_id"],q["second_center_id"],q["nth_center_id"]][center_index]
        nodes={n["id"]:n for n in w["graph"]["nodes"]}
        center=nodes[cid]
        center["low"]=center["high"]=str(price)
        for rid in center["deps"]:
            nodes[rid]["price"]=str(price)

    def test_all_fixture_checkpoints(self):
        r=mod.fixture_audit(FIXTURE)
        self.assertEqual(r["graph_nodes"],43)
        self.assertEqual(r["checked_times"],4)
        self.assertEqual(r["visible_members"],[0,1,2,3])
        self.assertEqual(r["end_intersection"],[9.0,12.0])
        self.assertEqual(r["independently_finished_movements"],0)

    def test_real_upstream_f01_graph_is_invoked(self):
        w=self.witness()
        base=mod.f01.check_graph(w["graph"])
        self.assertEqual(base["audit"],"PASS_STRUCTURE_ONLY")
        out=self.check(w)
        self.assertEqual(out["status"],mod.STRUCTURE)
        self.assertTrue(out["initial_direction_prices_checked"])
        self.assertTrue(out["nth_nonadvance_prices_checked"])
        self.assertFalse(out["movement_completion_certified"])

    def test_old_v454_graph_lacks_required_initial_center_witness(self):
        old=json.loads((ROOT/"tests/fixtures/kaixiang_f01_graph_bridge_v454.json").read_text(encoding="utf-8"))
        witness=mod.bridge.candidate_gate if False else None
        # Older bridge emits only the N-1/N comparison pair, not the
        # earlier trend-forming center. Old graph still passes F01.
        old_module=mod.load("kx_old_v454",ROOT/"tools/audit_kaixiang_f01_graph_completion_bridge.py")
        old_w=old_module.build_synthetic_graph(old)
        self.assertEqual(mod.f01.check_graph(old_w["graph"])["audit"],"PASS_STRUCTURE_ONLY")
        old_w["id"]=mod.IDENTITY
        old_w["source_case_id"]=self.c["id"]
        old_w["source_answer_ids"]=self.c["source_answer_ids"]
        with self.assertRaisesRegex(ValueError,"three qualified members|three distinct base centers"):
            self.check(old_w)

    def test_f01_false_positive_initial_direction_now_rejected(self):
        w=self.witness()
        self.change_center(w,0,0,"6")  # c1=6 < c2=7; DOWN was never established
        self.assertEqual(mod.f01.check_graph(w["graph"])["audit"],"PASS_STRUCTURE_ONLY")
        with self.assertRaisesRegex(ValueError,"INITIAL_DIRECTION_UNPROVEN"):
            self.check(w)

    def test_f01_false_positive_continuing_decline_now_rejected(self):
        w=self.witness()
        self.change_center(w,0,2,"6")  # c3=6 < c2=7, so DOWN is advancing
        self.assertEqual(mod.f01.check_graph(w["graph"])["audit"],"PASS_STRUCTURE_ONLY")
        with self.assertRaisesRegex(ValueError,"NONADVANCE_FALSE"):
            self.check(w)

    def test_nth_equal_second_center_is_valid_local_nonadvance(self):
        w=self.witness()
        self.change_center(w,0,2,"7")
        out=self.check(w)
        self.assertTrue(out["nth_nonadvance_prices_checked"])

    def test_upward_variant_has_symmetric_center_order(self):
        x=copy.deepcopy(self.spec)
        x["direction"]="UP"
        w=mod.generate(x)
        r=self.check(w)
        self.assertTrue(r["initial_direction_prices_checked"])
        self.change_center(w,0,2,"15")  # 3rd center higher than second
        with self.assertRaisesRegex(ValueError,"NONADVANCE_FALSE"):
            self.check(w)

    def test_up_direction_label_alone_cannot_rewrite_down_prices(self):
        w=self.witness()
        w["direction"]="UP"
        for q in w["certificates"]:
            q["declared_direction"]="UP"
            target=next(n for n in w["graph"]["nodes"] if n["id"]==q["exit_id"])
            target["direction"]="UP"
            target["author_comparator_claim"]="NOT_HIGHER"
        self.assertEqual(mod.f01.check_graph(w["graph"])["audit"],"PASS_STRUCTURE_ONLY")
        with self.assertRaisesRegex(ValueError,"INITIAL_DIRECTION_UNPROVEN"):
            self.check(w)

    def test_last_member_not_known_until_after_nine_raws(self):
        w=self.witness()
        for at,count in ((9,0),(10,1),(19,2),(28,3)):
            self.assertEqual(len(self.check(w,at)["visible_members"]),count)
        self.assertIsNone(self.check(w,19)["overlap_if_visible"])

    def test_first_known_timestamp_cannot_be_retroactively_moved(self):
        w=self.witness()
        w["members"][2]["first_known_tick"]=27
        with self.assertRaisesRegex(ValueError,"first known/completion clocks"):
            self.check(w)

    def test_cross_stream_price_witness_rejected(self):
        w=self.witness()
        first=w["certificates"][0]["initial_center_id"]
        node=next(x for x in w["graph"]["nodes"] if x["id"]==first)
        rid=node["deps"][0]
        next(x for x in w["graph"]["nodes"] if x["id"]==rid)["stream_id"]="different"
        with self.assertRaisesRegex(ValueError,"same raw tape"):
            self.check(w)

    def test_missing_center_or_wrong_order_fails_closed(self):
        w=self.witness()
        w["certificates"][0]["initial_center_id"]=w["certificates"][0]["second_center_id"]
        with self.assertRaisesRegex(ValueError,"three distinct base centers"):
            self.check(w)
        w=self.witness()
        a=w["certificates"][0]
        a["initial_center_id"],a["second_center_id"]=a["second_center_id"],a["initial_center_id"]
        with self.assertRaisesRegex(ValueError,"sequential"):
            self.check(w)

    def test_forged_market_proof_flags_are_still_denied(self):
        w=self.witness()
        n=next(x for x in w["graph"]["nodes"] if x["kind"]=="RAW_TRADE")
        n["root_verified"]=True
        with self.assertRaisesRegex(ValueError,"raw source not authenticated"):
            self.check(w)
        w=self.witness()
        n=next(x for x in w["graph"]["nodes"] if x["kind"]=="F1_TREND_NONADVANCE")
        n["comparison_independently_verified"]=True
        with self.assertRaisesRegex(ValueError,"comparator"):
            self.check(w)

    def test_cannot_substitute_segment_end_for_finished_type(self):
        w=self.witness()
        n=next(x for x in w["graph"]["nodes"] if x["kind"]=="FINISHED_MOVEMENT")
        n["kind"]="SEGMENT_END"
        with self.assertRaisesRegex(ValueError,"wrong evidence types|segment"):
            self.check(w)

    def test_source_and_policy_scope_immutable(self):
        w=self.witness()
        w["policy_id"]="malicious"
        with self.assertRaisesRegex(ValueError,"frozen policy mismatch"):
            self.check(w)
        w=self.witness()
        w["source_answer_ids"]=["A007"]
        with self.assertRaisesRegex(ValueError,"A-index source"):
            self.check(w)

    def test_overlap_does_not_resurrect_candidate_or_promote_profit(self):
        w=self.witness()
        x=self.check(w)
        self.assertEqual(x["overlap_if_visible"],[9,12])
        self.assertEqual(x["candidate_states_unchanged"]["third_buy_extension"],"INVALIDATED")
        self.assertFalse(x["movement_completion_certified"])
        self.assertFalse(x["third_buy_certified"])
        self.assertFalse(x["market_data_used"])
        self.assertEqual(x["orders_sent"],0)


if __name__=="__main__":
    unittest.main()
