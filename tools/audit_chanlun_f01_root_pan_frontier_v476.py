#!/usr/bin/env python3
"""F01 v4.76: executable root-pan negative-frontier audit.

Reuses the repository's EXISTING, UNTRUSTED abstract receipt checker.
This file is a regression/diagnostic harness, not a tick parser, an
independent author-proof generator, market authentication, or strategy.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from tools.audit_chanlun_f01_completion_receipts import check_graph

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog/chanlun_f01_root_pan_frontier_v476.json"
REPORT = ROOT / ("deliverables/chanlun_108_acceptance/00_REVIEW/"
                 "CHANLUN_F01_ROOT_PAN_EXIT_REGRESSION_AND_MISSING_WITNESS_V476.md")
PREDECESSOR = ROOT / "tools/audit_chanlun_f01_completion_receipts.py"
POLICY = "STRICT_TICK_F1_FROZEN_V476_RESEARCH_ONLY"
SOURCE_CLAIMS = {
    (18, "CL018-S07", 235),
    (20, "CL020-S03", 247),
    (35, "CL35-SO-2", 291),
    (35, "CL35-SO-9", 291),
}
CASE_EXPECTATIONS = {
    "CENTER_ASSUMED_FINISHED": "no unfinished/segment-based or unsupported finish promotion",
    "BASE_PAN_EXIT_FROM_CENTER": "no automatic lowest-pan terminal predicate",
    "PAN_DIVERGENCE_ALERT_AS_FINISH": "unsupported or unimplemented evidence kind",
    "SEGMENT_END_ASSUMED_FINISHED": "no unfinished/segment-based or unsupported finish promotion",
    "ONE_CENTER_AS_NTH_TREND_EXIT": "Nth center must be beyond second",
    "SELF_JUSTIFYING_BOUNDARY": "circular completion evidence",
}


def require(flag: bool, explanation: str) -> None:
    if not flag:
        raise ValueError("ROOT_PAN_FRONTIER_INVALID: " + explanation)


def node(id: str, kind: str, deps: list[str], level: int = 0,
         seen: int = 2, **extra: object) -> dict:
    return {
        "id": id,
        "kind": kind,
        "level": level,
        "first_known_seq": seen,
        "historical_endpoint_seq": seen,
        "policy_id": POLICY,
        "deps": deps,
        **extra,
    }


def one_center_graph() -> dict:
    """Synthetic three-trade seed, NOT market data and NOT a complete pan."""
    rows = [
        node(f"T{i}", "RAW_TRADE", [], seen=i, stream_id="FICTION_ONLY",
             stream_digest="fictional-source-not-authenticated-v476",
             ordinal=i, price="10", root_verified=False)
        for i in range(3)
    ]
    rows.append(node("C0", "F1_CENTER", ["T0", "T1", "T2"],
                     low="10", high="10", center_ordinal=1))
    return {
        "schema_version": 1,
        "mode": "ABSTRACT_RECEIPTS_UNVERIFIED",
        "policy_id": POLICY,
        "nodes": rows,
    }


def make_candidate(case_id: str) -> dict:
    """Purely hypothetical invalid proof attempts, never actual trades."""
    require(case_id in CASE_EXPECTATIONS, "unknown candidate")
    data = one_center_graph()
    ns = data["nodes"]

    if case_id == "CENTER_ASSUMED_FINISHED":
        ns.append(node("M0", "FINISHED_MOVEMENT", ["C0"],
                       movement_ordinal=0, low="10", high="10",
                       market_finish_authenticated=False))
    elif case_id == "BASE_PAN_EXIT_FROM_CENTER":
        ns.append(node("X0", "PAN_EXIT", ["C0"],
                       historical_exit_authenticated=False))
    elif case_id == "PAN_DIVERGENCE_ALERT_AS_FINISH":
        ns.append(node("D0", "PAN_DIVERGENCE_ALERT", ["C0"]))
    elif case_id == "SEGMENT_END_ASSUMED_FINISHED":
        ns.append(node("S0", "SEGMENT_END", [],
                       segment_rule_authenticated=False,
                       source_note="L67_LOCAL_ONLY"))
        ns.append(node("M0", "FINISHED_MOVEMENT", ["S0"],
                       movement_ordinal=0, low="10", high="10",
                       market_finish_authenticated=False))
    elif case_id == "ONE_CENTER_AS_NTH_TREND_EXIT":
        # Fake "second" structural ID reuses the only 3 raw observations.
        # Even a locally admissible center witness is not a legal N>2 exit.
        ns.append(node("C1", "F1_CENTER", ["T0", "T1", "T2"],
                       low="10", high="10", center_ordinal=2))
        ns.append(node("E0", "F1_TREND_NONADVANCE", ["C0", "C1"],
                       direction="UP", author_comparator_claim="NOT_HIGHER",
                       comparison_independently_verified=False))
    elif case_id == "SELF_JUSTIFYING_BOUNDARY":
        # M1 finished because X1 happened, X1 because M1 finished.
        # All declared times match: as-of arithmetic alone does not detect it.
        ns.append(node("M1", "FINISHED_MOVEMENT", ["X1"],
                       level=1, movement_ordinal=1, low="10", high="10",
                       market_finish_authenticated=False))
        ns.append(node("X1", "PAN_EXIT", ["M1"], level=1,
                       historical_exit_authenticated=False))
    return data


def validate_sources(contract: dict, root: Path = ROOT) -> None:
    require(contract.get("schema_version") == 1 and
            contract.get("id") == "CHANLUN-F01-ROOT-PAN-FRONTIER-V476",
            "schema/id")
    require(contract.get("scope") ==
            "EXISTING_UNTRUSTED_RECEIPT_GRAMMAR_NEGATIVE_REGRESSION",
            "scope must stay negative")
    claims = contract.get("source_claims", [])
    require(isinstance(claims, list) and len(claims) == len(SOURCE_CLAIMS),
            "exact source claims")
    require({(x["lesson"], x["claim_id"], x["pdf_page"]) for x in claims}
            == SOURCE_CLAIMS, "source identity/pages")
    for s in claims:
        e = json.loads((root / f"knowledge/evidence/chanlun_lesson{s['lesson']:03d}.json")
                       .read_text(encoding="utf-8"))
        matches = [c for c in e["claims"] if c["id"] == s["claim_id"]]
        require(len(matches) == 1 and matches[0]["kind"] == "SOURCE" and
                s["pdf_page"] in matches[0]["pdf_pages"] and
                s["role"] == "AUTHOR_MAIN_SOURCE_CARD_IN_COMPILATION",
                "misattributed author source")
    cases = contract.get("negative_cases", [])
    require(isinstance(cases, list) and len(cases) == len(CASE_EXPECTATIONS),
            "six adverse cases")
    require({c["id"] for c in cases} == set(CASE_EXPECTATIONS),
            "missing/extra adverse case")
    require(all(c.get("expected_reason") == CASE_EXPECTATIONS[c["id"]] and
                c.get("claim_status") == "REJECTED_AS_COMPLETION_CERTIFICATE"
                for c in cases), "cannot upgrade negative case")
    flags = contract.get("proof_frontier", {})
    require(flags.get("strict_tick_root_center") == "CONSTRUCTIBLE_STRUCTURE_ONLY" and
            flags.get("strict_tick_root_pan_exit") == "OPEN" and
            flags.get("strict_tick_root_center_identity") == "OPEN" and
            flags.get("root_trend_nonadvance_comparator") ==
            "AUTHOR_CONDITION_WITH_UNDETERMINED_FULL_COMPARATOR" and
            flags.get("global_market_completion") == "NOT_CERTIFIED" and
            flags.get("market_backtest") == "NOT_RUN" and
            flags.get("trades_executed") == 0 and
            flags.get("author_full_grammar_recovered") is False,
            "proof frontier/market boundaries were wrongly promoted")
    require(contract.get("existing_checker") ==
            "tools/audit_chanlun_f01_completion_receipts.py",
            "prior executable checker")
    report_path = root / ("deliverables/chanlun_108_acceptance/00_REVIEW/"
                          "CHANLUN_F01_ROOT_PAN_EXIT_REGRESSION_AND_MISSING_WITNESS_V476.md")
    paragraph = report_path.read_text(encoding="utf-8")
    for key in ("v4.76", "第18课", "第20课", "第35课", "ROOT_PAN_EXIT",
                "不能证明", "F01", "OPEN", "NOT_RUN"):
        require(key in paragraph, "report missing boundary " + key)


def audit(contract: dict | None = None, root: Path = ROOT) -> dict:
    spec = contract if contract is not None else json.loads(
        (root / "catalog/chanlun_f01_root_pan_frontier_v476.json")
        .read_text(encoding="utf-8"))
    validate_sources(spec, root)
    valid = check_graph(one_center_graph())
    require(valid["audit"] == "PASS_STRUCTURE_ONLY" and
            valid["market_status"] == "NOT_AUTHENTICATED" and
            valid["author_complete_rule_status"] == "OPEN",
            "three same-price trades may certify center structure only")
    evidence = []
    for case_id in CASE_EXPECTATIONS:
        try:
            check_graph(make_candidate(case_id))
        except ValueError as ex:
            # Check the real preexisting validation reason, not just failure.
            message = str(ex)
            require(CASE_EXPECTATIONS[case_id] in message,
                    f"{case_id} failed for an unexpected reason: {message}")
            evidence.append({"candidate": case_id,
                             "result": "REJECTED_AS_COMPLETION_CERTIFICATE"})
        else:
            raise ValueError("ROOT_PAN_FRONTIER_INVALID: unsound acceptance "
                             + case_id)
    return {
        "status": "ROOT_PAN_EXIT_STILL_OPEN_NEGATIVE_REGRESSIONS_PASS",
        "one_center_constructible": True,
        "root_pan_exit_certified": False,
        "negative_cases_rejected": len(evidence),
        "cases": evidence,
        "market": "NOT_RUN",
        "proof": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, sort_keys=True))
