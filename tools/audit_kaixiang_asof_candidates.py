#!/usr/bin/env python3
"""Symbolic as-of gate for Kaixiang quote-linked scenarios; NOT a Chanlun parser.

No real prices, prediction, trades, live access, or proof of market completeness.
Events are caller assertions and this gate does not certify their market truth.
An eliminated branch is only locally eliminated under a frozen scope. A sole
survivor is NOT proof of its real-world occurrence or of a complete universe.
"""
from __future__ import annotations
import json
from pathlib import Path

KINDS = frozenset(("LOCAL_CONDITION", "CANDIDATE_INVALIDATED", "ACCOUNT_RISK_LIMIT"))
EVIDENCE = "SYNTHETIC_ASSERTION_NOT_INDEPENDENTLY_VALIDATED"
ORIGIN = "SYNTHETIC_SYMBOLS_NOT_MARKET"
NO_TRADE = "NO_AUTOMATED_TRADE_DECISION"
RISK = "RISK_EXIT_REVIEW_ONLY_NO_ORDER"


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def _tick(value, name):
    require(type(value) is int and value >= 0, name + " must be nonnegative integer ticks")
    return value


def assess(case: dict, asof_tick: int) -> dict:
    """Evaluate immutable symbolic candidate IDs at a known-information prefix.

    The time notion is a synthetic integer tick, not exchange time. A recorded
    fact is usable only after both occurrence AND information availability.
    Historical final-type inference, three-buy verification and fills are out of
    scope. Scope includes level, segmentation rule and segment-instance ID.
    """
    _tick(asof_tick, "asof_tick")
    require(isinstance(case, dict), "case must be an object")
    require(case.get("origin") == ORIGIN, "synthetic source declaration required")
    scope = case.get("scope")
    require(isinstance(scope, str) and scope.strip() and scope != "ACCOUNT",
            "frozen, non-account structural scope required")
    branches = case.get("candidates")
    require(isinstance(branches, list) and len(branches) >= 2,
            "at least two declared hypotheses required")
    require(all(isinstance(x, str) and x.strip() for x in branches)
            and len(set(branches)) == len(branches),
            "candidate IDs must be unique, nonempty and immutable")
    require(isinstance(case.get("source_answer_ids"), list)
            and bool(case["source_answer_ids"])
            and all(isinstance(x, str) and x.startswith("A") for x in case["source_answer_ids"]),
            "traceable original answer IDs required")
    events = case.get("events")
    require(isinstance(events, list), "event list required")
    ids = set()
    for item in events:
        require(isinstance(item, dict), "event must be object")
        require(set(item) == {"id", "kind", "occurred_tick", "known_tick",
                              "candidate", "scope", "evidence"},
                "event must contain exactly the fixed evidence fields")
        eid = item["id"]
        require(isinstance(eid, str) and eid.strip() and eid not in ids,
                "unique event ID required")
        ids.add(eid)
        require(item["kind"] in KINDS, "unsupported evidence kind")
        _tick(item["occurred_tick"], "occurred_tick")
        _tick(item["known_tick"], "known_tick")
        require(item["occurred_tick"] <= item["known_tick"],
                "information cannot be known before occurrence")
        require(item["evidence"] == EVIDENCE,
                "unverified synthetic evidence must retain its provenance")
        if item["kind"] == "ACCOUNT_RISK_LIMIT":
            require(item["scope"] == "ACCOUNT" and item["candidate"] is None,
                    "account-risk events cannot masquerade as technical labels")
        else:
            require(item["scope"] == scope,
                    "cross-level/cross-policy/cross-instance evidence not permitted")
            require(item["candidate"] in branches,
                    "event candidate not in frozen universe")
    states = {item: "PENDING" for item in branches}
    risk = False
    seen = []
    for item in sorted(events, key=lambda x: (x["known_tick"], x["occurred_tick"], x["id"])):
        if item["known_tick"] > asof_tick or item["occurred_tick"] > asof_tick:
            continue
        kind = item["kind"]
        if kind == "ACCOUNT_RISK_LIMIT":
            risk = True
        elif kind == "CANDIDATE_INVALIDATED":
            states[item["candidate"]] = "INVALIDATED"
        else:
            require(states[item["candidate"]] != "INVALIDATED",
                    "invalidated candidate ID cannot be resurrected within same scope")
            states[item["candidate"]] = "LOCAL_CONDITION_ONLY"
        seen.append(item["id"])
    remaining = [c for c in branches if states[c] != "INVALIDATED"]
    return {
        "case_id": case.get("id"),
        "asof_tick": asof_tick,
        "scope": scope,
        "source_answer_ids": list(case["source_answer_ids"]),
        "candidate_states": states,
        "remaining_hypotheses": remaining,
        "sole_survivor": remaining[0] if len(remaining) == 1 else None,
        "sole_survivor_confirmed_final": False,
        "candidate_universe_exhaustiveness_proven": False,
        "chanlun_structure_certified": False,
        "observed_event_ids": seen,
        "risk_exit_asserted": risk,
        "action": RISK if risk else NO_TRADE,
        "order_submitted": False,
        "fill_confirmed": False,
        "market_data_used": False,
        "research_only": True,
    }


def audit_fixture(path: Path) -> dict:
    j = json.loads(Path(path).read_text(encoding="utf-8"))
    require(j.get("schema_version") == 1 and j.get("origin") == ORIGIN,
            "fixture identity or origin invalid")
    cases = j.get("cases", [])
    require(len(cases) == 8 and len({x["id"] for x in cases}) == 8,
            "v4.51 must supply exactly eight distinct anchor cases")
    results = []
    for case in cases:
        for check in case["checkpoints"]:
            row = assess(case, check["tick"])
            require(row["remaining_hypotheses"] == check["remaining"]
                    and row["risk_exit_asserted"] is check["risk_exit"]
                    and row["observed_event_ids"] == check["seen"]
                    and row["sole_survivor_confirmed_final"] is False,
                    "symbolic checkpoint mismatch: " + case["id"])
            results.append(row)
    return {"status": "SYNTHETIC_ASOF_CONTRACT_CHECKED_NOT_MARKET",
            "cases": len(cases), "prefix_checks": len(results),
            "market_data": False, "real_trading_orders": 0,
            "unproven_closed_world": True}


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(json.dumps(audit_fixture(
        root / "tests/fixtures/kaixiang_asof_symbolic_v452.json"
    ), ensure_ascii=False, indent=2))
