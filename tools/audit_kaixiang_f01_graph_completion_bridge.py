#!/usr/bin/env python3
"""A *structural-only* F01 receipt graph binding for Kaixiang's synthetic center.

Consumes the repository's existing F01 check_graph (raw-point > primitive
base center > declared trend nonadvance > structurally declared finished
movement > higher center), and the v4.53 as-of overlap bridge. It NEVER
authenticates original prices, legal lower-level completion, a third buy,
or a real market result. All data/aliases are explicitly synthetic.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "SYNTHETIC_SYMBOLS_NOT_MARKET"
SCOPE = "SYNTHETIC_F01_GRAPH_ADMISSIBILITY_NOT_INDEPENDENT_COMPLETION"
ALIAS = "SYNTHETIC_LEVEL_ALIAS_NOT_CHART_TIMEFRAME"
STATUS = "F01_GRAPH_ADMISSIBLE_NOT_MARKET_AUTHENTICATED"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("missing source gate: "+str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


f01 = load("kaixiang_v454_f01", ROOT/"tools/audit_chanlun_f01_completion_receipts.py")
bridge = load("kaixiang_v454_v453", ROOT/"tools/audit_kaixiang_center_asof_bridge.py")


def need(ok, msg):
    if not ok:
        raise ValueError("KX_F01_BRIDGE: "+msg)


def build_synthetic_graph(case):
    """Builder solely for test witnesses; never a market parser or proof source."""
    need(case.get("origin") == ORIGIN, "only synthetic cases")
    need(case.get("scope") == SCOPE, "test mode fixed")
    need(case.get("level_alias_kind") == ALIAS, "explicit non-canonical level alias required")
    need(case.get("parent_level") == 1 and case.get("child_level") == 0,
         "only local F01 level0-to-level1 synthetic construction")
    policy = case["policy_id"]
    need(isinstance(policy, str) and len(policy) >= 8, "missing frozen policy")
    pairs = case["primitive_price_pairs"]
    keys = case["member_keys"]
    need(isinstance(pairs, list) and len(pairs) == 3
         and isinstance(keys, list) and len(keys) == 3
         and len(set(keys)) == 3, "three independently identifiable member inputs required")
    nodes, members, mapping = [], [], []
    ordinal = 0
    for i, (key, pair) in enumerate(zip(keys, pairs), 1):
        need(isinstance(key, str) and key.strip()
             and isinstance(pair, list) and len(pair) == 2,
             "one price pair per member")
        prices = [Decimal(str(p)) for p in pair]
        need(all(x.is_finite() and x >= 0 for x in prices) and prices[0] < prices[1],
             "ordered positive finite member price endpoints")
        centers = []
        for index, value in enumerate(prices):
            raw_ids = []
            for _ in range(3):
                ordinal += 1
                rid = f"{key}_raw_{ordinal}"
                nodes.append({
                    "id": rid, "kind": "RAW_TRADE", "level": 0,
                    "policy_id": policy, "first_known_seq": ordinal,
                    "historical_endpoint_seq": ordinal, "deps": [],
                    "root_verified": False, "stream_id": "UNTRUSTED_SYNTHETIC_TAPE",
                    "stream_digest": "unverified-source-identity-001",
                    "ordinal": ordinal, "price": str(value),
                })
                raw_ids.append(rid)
            cid = f"{key}_center_{index}"
            nodes.append({
                "id": cid, "kind": "F1_CENTER", "level": 0,
                "policy_id": policy, "first_known_seq": ordinal,
                "historical_endpoint_seq": ordinal, "deps": raw_ids,
                "low": str(value), "high": str(value),
                "center_ordinal": 2*i + index,
            })
            centers.append(cid)
        # DOWN + NOT_LOWER in this case is a declared, UNVERIFIED source
        # comparator. No real trend or actual exit is independently proved.
        exit_at = ordinal + 1
        eid = f"{key}_exit"
        nodes.append({
            "id": eid, "kind": "F1_TREND_NONADVANCE", "level": 0,
            "policy_id": policy, "first_known_seq": exit_at,
            "historical_endpoint_seq": ordinal, "deps": centers,
            "direction": "DOWN", "author_comparator_claim": "NOT_LOWER",
            "comparison_independently_verified": False,
        })
        mid = f"{key}_finished"
        nodes.append({
            "id": mid, "kind": "FINISHED_MOVEMENT", "level": 0,
            "policy_id": policy, "first_known_seq": exit_at,
            "historical_endpoint_seq": ordinal, "deps": [eid],
            "movement_ordinal": i, "low": str(prices[0]), "high": str(prices[1]),
            "market_finish_authenticated": False,
        })
        members.append({
            "key": key, "ordinal": i, "member_level": case["lower_level"],
            "member_status": bridge.MEMBER_ASSERTION,
            "completed_at_tick": ordinal, "first_known_tick": exit_at,
            "low": float(prices[0]), "high": float(prices[1]),
        })
        mapping.append({"member_key": key, "finished_receipt_id": mid})
        # Exit is an independently declared time step; source trade ordinals
        # remain consecutive within each F1 center despite the exit event.
    lower = max(Decimal(str(m["low"])) for m in members)
    upper = min(Decimal(str(m["high"])) for m in members)
    need(lower < upper, "demo three-member positive overlap required")
    center_id = "F2_SYNTHETIC_CENTER_A"
    nodes.append({
        "id": center_id, "kind": "F2_CENTER", "level": 1,
        "policy_id": policy,
        "first_known_seq": max(m["first_known_tick"] for m in members),
        "historical_endpoint_seq": max(m["completed_at_tick"] for m in members),
        "deps": [x["finished_receipt_id"] for x in mapping],
        "zone_low": str(lower), "zone_high": str(upper),
    })
    graph = {
        "schema_version": 1, "mode": "ABSTRACT_RECEIPTS_UNVERIFIED",
        "policy_id": policy, "nodes": nodes,
    }
    return {
        "origin": ORIGIN, "scope": SCOPE,
        "level_alias_kind": ALIAS, "parent_level": 1,
        "child_level": 0, "case_id": case["case_id"],
        "parent_center_receipt_id": center_id,
        "member_receipt_mapping": mapping,
        "graph": graph, "members": members,
    }


def evaluate(candidate_case, center_case, witness, asof_tick):
    """Validate graph plus exact price and time-to-member links; no certification."""
    bridge._tick(asof_tick, "asof_tick")
    need(witness.get("origin") == ORIGIN and witness.get("scope") == SCOPE,
         "synthetic source/proof scope missing")
    need(witness.get("level_alias_kind") == ALIAS
         and witness.get("child_level") == 0
         and witness.get("parent_level") == 1,
         "numeric-to-chart-level inference is forbidden")
    need(witness.get("case_id") == candidate_case.get("id")
         and center_case.get("source_case_id") == witness["case_id"],
         "cross-case provenance not allowed")
    graph = witness.get("graph")
    need(isinstance(graph, dict), "missing dependency graph")
    need(graph.get("policy_id") == center_case.get("policy"),
         "policy mismatched from frozen center case")
    verdict = f01.check_graph(graph)  # real reused F01 source-gate, no mocked check
    need(verdict["claim"] == "STRUCTURAL_CHECKED_NOT_MARKET_AUTHENTICATED"
         and verdict["market_status"] == "NOT_AUTHENTICATED",
         "F01 receipt gate tried to authenticate unverified data")
    nodes = {n["id"]: n for n in graph["nodes"]}
    parent_id = witness.get("parent_center_receipt_id")
    need(parent_id in nodes and nodes[parent_id]["kind"] == "F2_CENTER"
         and nodes[parent_id]["level"] == 1, "expected parent F2 center")
    parent = nodes[parent_id]
    entries = witness.get("member_receipt_mapping")
    members = witness.get("members")
    need(isinstance(entries, list) and len(entries) == 3
         and isinstance(members, list) and len(members) == 3,
         "three ordered movement receipts required")
    need([e["member_key"] for e in entries] == [m["key"] for m in members]
         and [e["finished_receipt_id"] for e in entries] == parent["deps"],
         "parent three dependencies must equal claimed member mapping")
    need(len({e["member_key"] for e in entries}) == 3, "duplicate member keys")
    need(center_case.get("lower_level") == members[0]["member_level"]
         and all(m["member_level"] == center_case["lower_level"] for m in members),
         "level alias must match unchanged original bridge scope")
    previous_ord = 0
    for m, entry in zip(members, entries):
        node = nodes[entry["finished_receipt_id"]]
        need(node["kind"] == "FINISHED_MOVEMENT" and node["level"] == 0,
             "must link graph's finished movement receipts")
        need(node["movement_ordinal"] == m["ordinal"]
             and node["movement_ordinal"] == previous_ord+1,
             "member numbering not consecutive")
        previous_ord = node["movement_ordinal"]
        need(node["first_known_seq"] == m["first_known_tick"]
             and node["historical_endpoint_seq"] == m["completed_at_tick"],
             "member completion or first-known timestamp differs from receipt")
        need(Decimal(str(m["low"])) == f01.money(node["low"])
             and Decimal(str(m["high"])) == f01.money(node["high"]),
             "member ranges disagree with graph's finished movement")
        # A structurally valid F01 finished movement may still claim made-up
        # low/high endpoints. Reconstruct extrema from SIX raw price leaves.
        exit_event = nodes[node["deps"][0]]
        leaf_nodes = [
            nodes[rid] for cid in exit_event["deps"]
            for rid in nodes[cid]["deps"]
        ]
        need(len(leaf_nodes) == 6
             and all(x["kind"] == "RAW_TRADE" for x in leaf_nodes),
             "must trace each member to six raw-price leaves")
        raw_prices = [f01.money(x["price"]) for x in leaf_nodes]
        need(min(raw_prices) == f01.money(node["low"])
             and max(raw_prices) == f01.money(node["high"]),
             "movement price extremes unsupported by six raw-price leaves")
    calculated_low = max(Decimal(str(m["low"])) for m in members)
    calculated_high = min(Decimal(str(m["high"])) for m in members)
    need(calculated_low == f01.money(parent["zone_low"])
         and calculated_high == f01.money(parent["zone_high"]),
         "parent overlap does not match linked child intervals")
    center = dict(center_case)
    center["members"] = members
    local = bridge.assess(candidate_case, center, asof_tick)
    graph_visible = [e["member_key"] for e,m in zip(entries,members)
                     if m["first_known_tick"] <= asof_tick]
    need(local["visible_member_ids"] == graph_visible, "future receipt disclosure")
    return {
        "result": STATUS if local["three_member_check"] == bridge.OVERLAP
                  else "F01_GRAPH_VALID_BUT_CENTER_ASOF_PENDING",
        "asof_tick": asof_tick,
        "source_case_id": witness["case_id"],
        "structurally_valid_f01_graph": True,
        "receipt_count": verdict["receipt_count"],
        "visible_finished_member_count": len(graph_visible),
        "three_member_check": local["three_member_check"],
        "intersection_if_all_visible": local["intersection_if_all_visible"],
        "candidate_states_unchanged": local["candidate_states_unchanged"],
        "candidate_remaining_unchanged": local["candidate_remaining_unchanged"],
        "f01_market_status": verdict["market_status"],
        "f01_author_complete_rule_status": verdict["author_complete_rule_status"],
        "legal_completed_lower_types_certified": False,
        "full_center_eligibility_certified": False,
        "third_buy_confirmed": False,
        "conclusive_final_hypothesis": False,
        "account_order_sent": False,
        "profit_evidence": False,
        "market_data": False,
    }


def audit_fixture(path):
    fixture = json.loads(Path(path).read_text(encoding="utf-8"))
    need(fixture["schema_version"] == 1 and fixture["origin"] == ORIGIN,
         "fixture provenance")
    candidate_fixture = json.loads(
        (ROOT/"tests/fixtures/kaixiang_asof_symbolic_v452.json").read_text(encoding="utf-8"))
    original_bridge = json.loads(
        (ROOT/"tests/fixtures/kaixiang_center_asof_bridge_v453.json").read_text(encoding="utf-8"))
    c = next(x for x in candidate_fixture["cases"] if x["id"] == fixture["case_id"])
    src = next(x for x in original_bridge["bridge_cases"]
               if x["source_case_id"] == fixture["case_id"])
    need(c["source_answer_ids"] == fixture["source_answer_ids"] == src["source_answer_ids"],
         "wrong original answer provenance")
    witness = build_synthetic_graph(fixture)
    need(witness["case_id"] == "KX-CASE-01", "only documented demonstration case")
    times = fixture["checkpoints"]
    need(times == [5, 7, 14, 21], "fixed research checkpoints")
    outputs = [evaluate(c, src, witness, t) for t in times]
    need([x["visible_finished_member_count"] for x in outputs] == [0,1,2,3],
         "first-known member prefix did not advance correctly")
    need(outputs[-1]["intersection_if_all_visible"] == [9.0,12.0],
         "third-member overlap result drift")
    need(all(x["legal_completed_lower_types_certified"] is False
             and x["full_center_eligibility_certified"] is False
             and x["account_order_sent"] is False
             and x["market_data"] is False for x in outputs),
         "source proof/market privileges illegally increased")
    return {
        "status": "SYNTHETIC_F01_GRAPH_AND_V453_ASOF_BRIDGE_CHECKED_NOT_MARKET",
        "source_answer_ids": fixture["source_answer_ids"],
        "f01_receipts": len(witness["graph"]["nodes"]),
        "checkpoints": len(outputs),
        "visible_members": [x["visible_finished_member_count"] for x in outputs],
        "final_intersection": outputs[-1]["intersection_if_all_visible"],
        "f01_authenticates_market": False,
        "lower_level_finished_movements_independently_proven": False,
        "real_market_data": False,
        "orders": 0,
    }


if __name__ == "__main__":
    print(json.dumps(audit_fixture(
        ROOT/"tests/fixtures/kaixiang_f01_graph_bridge_v454.json"),
        ensure_ascii=False, indent=2))
