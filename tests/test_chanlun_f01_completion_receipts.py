"""Only invented receipt-graph fixtures: NEVER historical OHLC or backtest claims."""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from tools.audit_chanlun_f01_completion_receipts import (
    ROOT, SPEC, PREVIOUS, REPORT, check_graph, validate_contract
)

POLICY = "F1_TICK_F2_AUTHOR_RG_FROZEN_TEST_ONLY"


def fictitious_graph() -> dict:
    """A graph invented to test necessary conditions; NOT one real-market observation."""
    b = {"schema_version": 1, "mode": "ABSTRACT_RECEIPTS_UNVERIFIED",
         "policy_id": POLICY, "nodes": []}
    d = b["nodes"]

    def put(id, kind, level, known, deps, **attrs):
        d.append({"id": id, "kind": kind, "level": level, "first_known_seq": known,
                  "historical_endpoint_seq": known, "policy_id": POLICY, "deps": deps, **attrs})
        return id

    # Three complete lower claims for a parent center, then departure/retrace.
    # All evidence is FICTIONAL and declared unauthenticated.
    price_triplets = [
        ("8", "10", "10"), ("8", "10", "10"), ("8", "10", "10"),
        ("10", "12", "12"), ("10", "11", "11"),
    ]
    times = 0
    for m, prices in enumerate(price_triplets):
        center_ids = []
        for c, price in enumerate(prices):
            raw_ids = []
            for _ in range(3):
                i = times
                raw_ids.append(put(
                    f"T{i}", "RAW_TRADE", 0, i, [],
                    stream_id="NONEXISTENT_TEST_TAPE",
                    stream_digest="fictional-test-digest-only-00000000",
                    ordinal=i, price=price, root_verified=False,
                ))
                times += 1
            center_ids.append(put(
                f"C{m}-{c}", "F1_CENTER", 0, times - 1, raw_ids,
                low=price, high=price, center_ordinal=m * 3 + c + 1,
            ))
        exit_id = put(
            f"E{m}", "F1_TREND_NONADVANCE", 0, times - 1, center_ids[1:],
            direction="UP", author_comparator_claim="NOT_HIGHER",
            comparison_independently_verified=False,
        )
        lo, hi = min(map(int, prices)), max(map(int, prices))
        put(f"M{m}", "FINISHED_MOVEMENT", 0, times - 1, [exit_id],
            movement_ordinal=m, low=str(lo), high=str(hi),
            market_finish_authenticated=False)

    f2 = put("Z1", "F2_CENTER", 1, 26, ["M0", "M1", "M2"],
             zone_low="8", zone_high="10")
    third = put("P1", "THIRD_POINT", 1, 44, [f2, "M3", "M4"],
                side="BUY", first_retrace_claim_independently_proven=False)
    pan = put("X1", "PAN_EXIT", 1, 44, [f2, third],
              historical_exit_authenticated=False)
    next(x for x in d if x["id"] == "X1")["historical_endpoint_seq"] = 40
    return b


class TestF01Receipts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")

    def reject(self, edit):
        d = fictitious_graph()
        edit(d)
        with self.assertRaises(ValueError):
            check_graph(d)

    @staticmethod
    def node(d, id):
        return next(x for x in d["nodes"] if x["id"] == id)

    def test_contract_source_claims_and_open_limits(self):
        validate_contract(self.spec, self.previous, self.report)

    def test_fictitious_graph_is_only_structural_admissible(self):
        r = check_graph(fictitious_graph())
        self.assertEqual(r["audit"], "PASS_STRUCTURE_ONLY")
        self.assertEqual(r["market_status"], "NOT_AUTHENTICATED")
        self.assertEqual(r["author_complete_rule_status"], "OPEN")

    def test_igual_boundary_retrace_low_equals_upper_ZG_permitted(self):
        d = fictitious_graph()
        self.assertEqual(self.node(d, "Z1")["zone_high"], self.node(d, "M4")["low"])
        self.assertEqual(check_graph(d)["audit"], "PASS_STRUCTURE_ONLY")

    def test_strictly_broken_ZG_rejected(self):
        self.reject(lambda d: self.node(d, "M4").update(low="9"))

    def test_missing_one_of_three_primitive_trades_rejected(self):
        self.reject(lambda d: self.node(d, "C0-0")["deps"].pop())

    def test_skipped_trade_ordinal_rejected(self):
        self.reject(lambda d: self.node(d, "T1").update(ordinal=1000))

    def test_mismatched_primitive_price_rejected(self):
        self.reject(lambda d: self.node(d, "T1").update(price="123"))

    def test_fake_raw_authentication_rejected(self):
        self.reject(lambda d: self.node(d, "T1").update(root_verified=True))

    def test_wrong_f1_uptrend_predicate_rejected(self):
        self.reject(lambda d: self.node(d, "E0").update(author_comparator_claim="NOT_LOWER"))

    def test_f1_comparator_not_fake_verified(self):
        self.reject(lambda d: self.node(d, "E0").update(comparison_independently_verified=True))

    def test_base_pan_cannot_be_completed_from_base_center_alone(self):
        self.reject(lambda d: self.node(d, "M0").update(deps=["C0-2"]))

    def test_wrong_f2_child_level_rejected(self):
        self.reject(lambda d: self.node(d, "M0").update(level=1))

    def test_f2_intersection_wrong_rejected(self):
        self.reject(lambda d: self.node(d, "Z1").update(zone_high="11"))

    def test_nonconsecutive_finished_child_ordinals_rejected(self):
        self.reject(lambda d: self.node(d, "M1").update(movement_ordinal=7))

    def test_third_point_needs_full_completed_retrace_type(self):
        self.reject(lambda d: self.node(d, "P1").update(deps=["Z1", "M3", "C4-2"]))

    def test_no_circular_completion(self):
        self.reject(lambda d: self.node(d, "Z1").update(deps=["X1", "M1", "M2"]))

    def test_no_backwards_asof_knowledge(self):
        self.reject(lambda d: self.node(d, "P1").update(first_known_seq=27))

    def test_keep_historical_endpoint_distinct_from_confirmation(self):
        d = fictitious_graph()
        node = self.node(d, "X1")
        self.assertLess(node["historical_endpoint_seq"], node["first_known_seq"])
        self.assertEqual(check_graph(d)["audit"], "PASS_STRUCTURE_ONLY")

    def test_no_policy_mix(self):
        self.reject(lambda d: self.node(d, "M2").update(policy_id="OTHER_F1_AND_RG"))

    def test_no_fabricated_real_market_mode(self):
        self.reject(lambda d: d.update(mode="REAL_MARKET_FULLY_AUTHENTICATED"))

    def test_cannot_turn_segment_end_into_finished_trend(self):
        def edit(d):
            d["nodes"].append({"id": "S1", "kind": "SEGMENT_END", "level": 0,
                               "first_known_seq": 44, "historical_endpoint_seq": 43,
                               "policy_id": POLICY, "deps": [],
                               "segment_rule_authenticated": False, "source_note": "L67"})
            self.node(d, "M4")["deps"] = ["S1"]
        self.reject(edit)

    def test_unimplemented_trend_backtest_cannot_be_claimed(self):
        self.reject(lambda d: self.node(d, "X1").update(kind="TREND_EXIT"))


if __name__ == "__main__":
    unittest.main()
