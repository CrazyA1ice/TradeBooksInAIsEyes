"""Source-first synthetic tape replay and F01 contradiction tests (not market)."""
from __future__ import annotations
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location(
    "kx_raw_tape_v456",ROOT/"tools/audit_kaixiang_raw_tape_prefix_v456.py")
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)
PATH=ROOT/"tests/fixtures/kaixiang_raw_tape_v456.json"


class KaixiangTapeFirstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads(PATH.read_text(encoding="utf-8"))

    def tape(self):
        return copy.deepcopy(self.doc)

    def test_full_fixture_audit_really_invokes_v455_graph(self):
        r=m.audit_fixture(PATH)
        self.assertTrue(r["source_digest_valid"])
        self.assertEqual(r["raw_trades"],27)
        self.assertEqual(r["f01_graph_nodes"],43)
        self.assertEqual(r["checked_prefixes"],8)
        self.assertFalse(r["real_market_verified"])
        self.assertFalse(r["actual_movement_completion_certified"])

    def test_local_pattern_and_unverified_exit_have_distinct_clocks(self):
        x=[m.replay_at(self.doc,t) for t in self.doc["checkpoints"]]
        self.assertEqual([r["local_pattern_count"] for r in x],[0,1,1,1,2,2,3,3])
        self.assertEqual([r["declared_exit_receipt_count"] for r in x],[0,0,1,1,1,2,2,3])
        self.assertEqual(x[1]["local_three_center_patterns"][0]["direction_from_raw"],"DOWN")
        self.assertFalse(x[1]["completed_movement_independently_certified"])

    def test_earlier_prefix_is_unchanged_when_future_price_changes(self):
        x=self.tape();early=m.replay_at(x,10)
        x["raw_prices"][20]="100"
        self.assertEqual(m.replay_at(x,10),early)

    def test_source_digest_detects_tampered_price(self):
        x=self.tape();x["raw_prices"][0]="15"
        with self.assertRaisesRegex(ValueError,"digest"):
            m.validate_full_tape(x)

    def test_digest_cannot_be_replaced_by_another_unverified_one(self):
        x=self.tape();x["raw_prices"][0]="15"
        x["raw_tape_sha256"]=m.digest(x["raw_prices"])
        with self.assertRaisesRegex(ValueError,"digest"):
            m.validate_full_tape(x)

    def test_deleted_or_inserted_trade_fails_full_tape(self):
        x=self.tape();x["raw_prices"].pop()
        with self.assertRaisesRegex(ValueError,"exactly 27"):
            m.validate_full_tape(x)
        x=self.tape();x["raw_prices"].insert(0,"14")
        with self.assertRaisesRegex(ValueError,"exactly 27"):
            m.validate_full_tape(x)

    def test_replay_rejects_broken_same_price_triple(self):
        x=self.tape();x["raw_prices"][2]="13"
        with self.assertRaisesRegex(ValueError,"three-equal-price"):
            m.replay_at(x,9)

    def test_replay_rejects_no_initial_direction(self):
        x=self.tape()
        x["raw_prices"][3:6]=["14"]*3
        with self.assertRaisesRegex(ValueError,"not identifiable"):
            m.replay_at(x,9)

    def test_replay_rejects_continuing_decline(self):
        x=self.tape()
        x["raw_prices"][6:9]=["6"]*3
        with self.assertRaisesRegex(ValueError,"still advances"):
            m.replay_at(x,9)

    def test_replay_rejects_noncanonical_nan_and_bool(self):
        for invalid in ("10.50","NaN","Infinity",True,0):
            x=self.tape();x["raw_prices"][0]=invalid
            with self.assertRaisesRegex(ValueError,"canonical|nonfinite|raw prices"):
                m.replay_at(x,1)

    def test_asof_must_be_int_and_nonnegative(self):
        for tick in (-1,True,2.5):
            with self.assertRaisesRegex(ValueError,"asof integer"):
                m.replay_at(self.doc,tick)

    def test_computed_direction_is_independent_of_old_declared_direction(self):
        x=self.tape();w=m.derive_graph(x)
        self.assertEqual(w["direction"],"DOWN")
        self.assertEqual(w["members"][0]["low"],7.0)
        self.assertEqual(w["members"][0]["high"],14.0)

    def test_old_case_identity_cannot_be_swapped(self):
        x=self.tape();x["source_answer_ids"]=["A007"]
        with self.assertRaisesRegex(ValueError,"A-index"):
            m.derive_graph(x)

    def test_no_graph_leaf_can_disagree_with_tape(self):
        x=self.tape();w=m.derive_graph(x)
        raw=next(v for v in w["graph"]["nodes"] if v["kind"]=="RAW_TRADE")
        raw["price"]="15"
        with self.assertRaisesRegex(ValueError,"leaf disagrees"):
            m.verify_graph_tape(w,x["raw_prices"])

    def test_f01_graph_rejects_forged_completion_truth(self):
        x=self.tape();w=m.derive_graph(x)
        row=next(z for z in w["graph"]["nodes"] if z["kind"]=="FINISHED_MOVEMENT")
        row["market_finish_authenticated"]=True
        with self.assertRaisesRegex(ValueError,"structure only"):
            m.previous.f01.check_graph(w["graph"])

    def test_altered_future_exit_is_not_an_authenticated_event(self):
        x=m.replay_at(self.doc,28)
        self.assertEqual(x["declared_exit_receipt_count"],3)
        self.assertFalse(x["completed_movement_independently_certified"])
        self.assertFalse(x["real_market_data"])


if __name__=="__main__":
    unittest.main()
