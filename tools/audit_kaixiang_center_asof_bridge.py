#!/usr/bin/env python3
"""One synthetic three-member interval witness next to Kaixiang's as-of candidate ledger.

BRIDGE ONLY. Not a lower-level completed-trend parser, market-data reader,
buy-point detector, Chanlun universal proof, trading engine, or performance test.
The input's completed-member status is a caller's SYMBOLIC ASSERTION, not proof.
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "SYNTHETIC_SYMBOLS_NOT_MARKET"
MEMBER_ASSERTION = "COMPLETED_LOWER_LEVEL_TYPE_ASSERTED_SYNTHETIC"
OVERLAP = "THREE_ASSERTED_COMPLETE_MEMBERS_POSITIVE_OVERLAP_ONLY"
PENDING_KNOWLEDGE = "PENDING_THIRD_MEMBER_FIRST_KNOWABLE_TIME"
PENDING_MEMBER = "PENDING_THREE_MEMBERS"
NO_OVERLAP = "NO_POSITIVE_THREE_MEMBER_OVERLAP"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("missing audited upstream helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# Reuse the repository's exact lesson-99 three-completed-member interval gate.
l99 = _load("kaixiang_bridge_l99", ROOT/"tools/audit_chanlun_lesson099_resegmentation.py")
candidate_gate = _load("kaixiang_bridge_candidates", ROOT/"tools/audit_kaixiang_asof_candidates.py")


def require(value, reason: str):
    if not value:
        raise ValueError(reason)


def _tick(v, field: str) -> int:
    require(type(v) is int and v >= 0, field + " must be a nonnegative integer")
    return v


def _number(v, field: str):
    require(type(v) in (float, int) and math.isfinite(v),
            field + " must be a finite nonboolean number")
    return v


def assess(candidate_case: dict, center_case: dict, asof_tick: int) -> dict:
    """Check symbolic member overlap; NEVER upgrade the candidate's final labels."""
    _tick(asof_tick, "asof_tick")
    require(isinstance(candidate_case, dict) and isinstance(center_case, dict),
            "cases must be objects")
    require(center_case.get("origin") == ORIGIN,
            "synthetic provenance required")
    require(center_case.get("source_case_id") == candidate_case.get("id"),
            "source case identity mismatch")
    scope = candidate_case.get("scope")
    require(center_case.get("scope") == scope, "cross-scope structural proof forbidden")
    fields = ("target_level", "policy", "segment_instance")
    require(all(isinstance(center_case.get(f), str) and center_case[f].strip()
                and "|" not in center_case[f] for f in fields),
            "target level, policy, segment identity must be frozen")
    require(scope == "|".join(center_case[f] for f in fields),
            "scope must freeze level, policy and segment instance")
    lower = center_case.get("lower_level")
    require(isinstance(lower, str) and lower.strip() and lower != center_case["target_level"],
            "distinct lower-level member identity required")
    require(center_case.get("candidate") in candidate_case.get("candidates", []),
            "linked hypothesis must be declared in the original ledger")
    parts = center_case.get("members")
    require(isinstance(parts, list) and len(parts) in (2, 3),
            "exactly 2 or 3 consecutive asserted members expected")
    seen = set()
    last_completed = -1
    validated = []
    for n, p in enumerate(parts, 1):
        require(isinstance(p, dict) and set(p) == {
            "key", "ordinal", "member_level", "member_status",
            "completed_at_tick", "first_known_tick", "low", "high"},
            "member schema must remain explicit")
        require(type(p["ordinal"]) is int and p["ordinal"] == n,
                "member ordinal must be consecutive and ordered")
        require(isinstance(p["key"], str) and p["key"].strip() and p["key"] not in seen,
                "unique member identity required")
        seen.add(p["key"])
        require(p["member_level"] == lower and p["member_status"] == MEMBER_ASSERTION,
                "only asserted completed members of specified lower level accepted")
        completed = _tick(p["completed_at_tick"], "completed_at_tick")
        known = _tick(p["first_known_tick"], "first_known_tick")
        require(completed >= last_completed and known >= completed,
                "completed members must be chronological and knowable no earlier than completion")
        last_completed = completed
        low = _number(p["low"], "low")
        high = _number(p["high"], "high")
        require(low < high, "positive member interval required")
        validated.append(p)

    # Use FIRST KNOWABLE time, not historical completion time, as the
    # existing lesson-99 gate's 'complete_at' input. Thus late disclosures
    # cannot rewrite a previously frozen market-information prefix.
    helper_members = [
        l99.Segment(p["key"], p["first_known_tick"], p["low"], p["high"])
        for p in validated
    ]
    base = l99.center_asof(helper_members, asof_tick)
    if base["state"] == "CENTER_PENDING":
        state = PENDING_MEMBER if len(parts) < 3 else PENDING_KNOWLEDGE
    elif base["state"] == "CENTER_CONFIRMED":
        state = OVERLAP
    else:
        require(base["state"] == "NO_POSITIVE_OVERLAP", "unknown source center gate result")
        state = NO_OVERLAP
    current = candidate_gate.assess(candidate_case, asof_tick)
    # Never disclose future member keys/intervals to the as-of output.
    known = [p["key"] for p in validated if p["first_known_tick"] <= asof_tick]
    intersection = list(base["intersection"]) if state == OVERLAP else None
    return {
        "source_case_id": candidate_case["id"],
        "asof_tick": asof_tick,
        "scope": scope,
        "linked_candidate": center_case["candidate"],
        "three_member_check": state,
        "visible_member_ids": known,
        "intersection_if_all_visible": intersection,
        "positive_overlap_first_knowable_tick":
            max(p["first_known_tick"] for p in validated) if state == OVERLAP else None,
        "upstream_lesson99_function": "center_asof",
        "upstream_candidate_function": "assess",
        "candidate_states_unchanged": current["candidate_states"],
        "candidate_remaining_unchanged": current["remaining_hypotheses"],
        "candidate_risk_exit_unchanged": current["risk_exit_asserted"],
        "center_sufficient_for_complete_chanlun_center": False,
        "completed_lower_level_types_independently_proven": False,
        "segmentation_policy_eligibility_proven": False,
        "third_buy_or_center_extension_proven": False,
        "candidate_set_exhaustiveness_proven": False,
        "trade_or_fill_asserted": False,
        "real_market_data_used": False,
        "research_only": True,
    }


def audit_fixture(path: Path):
    fixture = json.loads(Path(path).read_text(encoding="utf-8"))
    require(fixture.get("origin") == ORIGIN and fixture.get("schema_version") == 1,
            "unrecognized bridge fixture")
    source = json.loads(
        (ROOT/"tests/fixtures/kaixiang_asof_symbolic_v452.json").read_text(encoding="utf-8"))
    previous = {x["id"]: x for x in source["cases"]}
    cases = fixture.get("bridge_cases")
    require(isinstance(cases, list) and len(cases) == 5,
            "five distinct documented bridge scenarios required")
    require(len({x["source_case_id"] for x in cases}) == 5,
            "one bridge case per source scenario required")
    checked = 0
    for case in cases:
        c = previous.get(case["source_case_id"])
        require(c is not None and case.get("source_answer_ids") == c["source_answer_ids"],
                "source answer IDs must match previous authenticated case index")
        for checkpoint in case["checkpoints"]:
            got = assess(c, case, checkpoint["asof_tick"])
            require(got["three_member_check"] == checkpoint["state"]
                    and got["intersection_if_all_visible"] == checkpoint["intersection"]
                    and got["visible_member_ids"] == checkpoint["visible"]
                    and got["candidate_risk_exit_unchanged"] is checkpoint["risk_exit"],
                    "symbolic bridge checkpoint failed")
            require(got["center_sufficient_for_complete_chanlun_center"] is False
                    and got["third_buy_or_center_extension_proven"] is False
                    and got["trade_or_fill_asserted"] is False,
                    "synthetic overlap illegally promoted to trade or fully qualified center")
            checked += 1
    return {
        "status": "SYMBOLIC_THREE_MEMBER_BRIDGE_VERIFIED_NOT_MARKET",
        "bridge_cases": len(cases),
        "prefix_checks": checked,
        "used_existing_lesson99_center_asof": True,
        "candidate_states_mutated": False,
        "genuine_lower_level_completion_verified": False,
        "third_buy_detected": False,
        "market_data": False,
        "orders_sent": 0,
    }


if __name__ == "__main__":
    print(json.dumps(audit_fixture(
        ROOT/"tests/fixtures/kaixiang_center_asof_bridge_v453.json"),
        ensure_ascii=False, indent=2))
