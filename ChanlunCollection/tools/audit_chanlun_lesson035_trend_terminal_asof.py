#!/usr/bin/env python3
"""Verify lesson35 lowest-level trend TERMINATION COMPARISONS, not real completion.

Externally declared symbolic center-order relations and confirmation times are
not legal center certificates. This tool never infers center order from price
zones, retroactively confirms an unseen event, or proves lesson38 uniqueness.
"""
from __future__ import annotations

import importlib.util
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "catalog/chanlun_lesson035_terminal_comparison_v1.json"
FIXTURES = ROOT / "tests/fixtures/chanlun35_terminal_asof_cases_v1.json"
EVIDENCE = ROOT / "knowledge/evidence/chanlun_lesson035.json"
INVENTORY = ROOT / "reports/source_inventory/chanlun_20261107_verified.json"
PDF_PINS = ROOT / "tools/inspect_chanlun_original_proof_text_readonly.py"
CONTRACT_ID = "CL35-LOWEST-LEVEL-TREND-TERMINAL-CONDITIONAL-V1"
PAGE_SHA = "1a2c291cff189ea4de5bef2ecf152e9888773d1194b0ed4e7218f4cd0f3b846b"
PDF_SHA = "af49aecbd363286baacbea02d3778b436df4dad797523ce0eb83846118827a66"
OPEN = ("source_legal_lowest_level_centers",
        "author_center_relative_height_semantics",
        "center_completion_confirmation_time",
        "continuous_non_overlapping_center_membership",
        "same_frozen_historical_rule_version")
RULES = (("initial_trend_pair", "min_centers", 2, ("HIGHER", "LOWER")),
         ("continuation_from_third", "min_ordinal", 3, ("HIGHER", "LOWER")),
         ("up_terminal_from_third", "min_ordinal", 3, ("EQUAL", "LOWER")),
         ("down_terminal_from_third", "min_ordinal", 3, ("EQUAL", "HIGHER")))
EVENT_KEYS = {"ordinal", "center_kind", "relation_to_previous",
              "seen_at", "confirmed_at", "rule_version"}
CASE_KEYS = {"kind", "direction", "as_of", "events"}
RELATIONS = {"BASE", "HIGHER", "LOWER", "EQUAL", "UNKNOWN"}
BLOCKED = "CONDITIONAL_TREND_COMPARISON_ONLY_NOT_COMPLETED_TREND"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def original_pins() -> dict:
    spec = importlib.util.spec_from_file_location("original_chanlun_native_text", PDF_PINS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.EXPECTED_TEXT_SHA256


def validate_contract(doc: dict, evidence: dict, inventory: dict, pins: dict) -> None:
    require(doc.get("schema_version") == 1 and doc.get("id") == CONTRACT_ID,
            "Unexpected original author rule contract")
    require(doc.get("scope") ==
            "AUTHOR_MAIN_IN_COMPILATION_TEXT_CONDITIONAL_ONLY_NOT_A_COMPLETE_CENTER_PARSER",
            "Partial source qualification removed")
    p = doc["original_pdf"]
    require(p == {"path": "ChineseBooks/缠论/缠论_卷2.pdf", "sha256": PDF_SHA,
                  "physical_page": 291, "native_text_sha256": PAGE_SHA,
                  "claim_id": "CL35-SO-9",
                  "historical_first_publication_verified": False},
            "Original PDF page or publication attribution changed")
    volume = next(v for v in inventory["volumes"] if v["path"] == p["path"])
    require(volume["sha256"] == PDF_SHA and pins[(2, 291)] == PAGE_SHA,
            "Previously verified original page fingerprint changed")
    matches = [v for v in evidence["claims"] if v["id"] == "CL35-SO-9"]
    require(len(matches) == 1, "Missing authored terminal-rule claim")
    claim = matches[0]
    require(claim["kind"] == "SOURCE" and claim["pdf_pages"] == [291] and
            claim["source_anchor"]["native_text_sha256"] == PAGE_SHA and
            claim["source_anchor"]["pdf_volume_sha256"] == PDF_SHA and
            claim["source_anchor"]["role"] == "AUTHOR_MAIN_IN_COMPILATION" and
            claim["source_anchor"]["comparison_of_center_price_intervals_not_fully_specified_here"] is True,
            "Authored SOURCE or unspecified center ordering semantics were altered")
    rules = doc.get("author_conditional_rules")
    require(isinstance(rules, list) and len(rules) == 4,
            "Four conditional author clauses required")
    for rule, (id_, key, n, expected) in zip(rules, RULES):
        require(rule.get("id") == id_ and rule.get(key) == n,
                "Author N>2 / initial two-center threshold changed")
        if key == "min_centers" or id_ == "continuation_from_third":
            observed = (rule.get("up_relation"), rule.get("down_relation"))
        else:
            observed = tuple(rule.get("relations", ()))
        require(observed == expected, "Author direction or equality condition changed")
    require(doc.get("comparison_meaning") ==
            "SYMBOLIC_CENTER_RANK_RELATION_GIVEN_EXTERNALLY_NOT_DERIVED_FROM_ZONE_PRICE" and
            doc.get("asof_semantics") ==
            "AI_CAUSAL_GUARD_ON_SYNTHETIC_CONFIRMATION_TIMES_NOT_ORIGINAL_REALTIME_PROOF",
            "Synthetic comparison or clock misrepresented as original data")
    require(doc.get("required_unverified") == list(OPEN),
            "Unverified center/price-comparison premises removed")
    for key in ("complete_lowest_level_parser", "legal_trend_completed_certified",
                "may_feed_verified_higher_center", "author_uniqueness_proven",
                "real_market_data_accessed"):
        require(doc.get(key) is False, "False theorem or legality promotion: " + key)
    require(doc.get("market_backtest") == "NOT_RUN", "Market backtest claim changed")


def timestamp(value: str) -> datetime:
    require(type(value) is str and bool(value.strip()), "Missing synthetic time")
    try:
        dt = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Invalid synthetic timestamp") from exc
    require(dt.tzinfo is not None and dt.utcoffset() is not None,
            "Timezone-naive source clocks are not allowed")
    return dt


def verdict(status: str, used: int, terminal=None) -> dict:
    return {"status": status, "used": used, "terminal_ordinal": terminal,
            "legally_completed": False}


def evaluate(row: dict, contract: dict) -> dict:
    require(contract["id"] == CONTRACT_ID, "Wrong rule contract")
    require(type(row) is dict and set(row) == CASE_KEYS,
            "Unexpected proof or market source fields")
    require(row["kind"] == "SYNTHETIC_DECLARED_LOWEST_CENTERS_NOT_MARKET",
            "Market data, real centers, or attributed prices are not supported")
    require(row["direction"] in ("UP", "DOWN"), "Only UP/DOWN author relations")
    asof = timestamp(row["as_of"])
    items = row["events"]
    require(isinstance(items, list) and 1 <= len(items) <= 25, "Invalid hypothetical center series")
    observed = []
    last_seen = last_confirm = None
    pending = False
    for ordinal, item in enumerate(items, 1):
        require(type(item) is dict and set(item) == EVENT_KEYS,
                "Center schema may not contain self-issued legal certificates")
        require(type(item["ordinal"]) is int and item["ordinal"] == ordinal,
                "Center ordinals must be consecutive and ordered")
        require(item["center_kind"] == "SYMBOLIC_CENTER_NOT_SOURCE_CERTIFIED",
                "Attempt to promote an abstract center into a legal one")
        require(item["relation_to_previous"] in RELATIONS and
                (item["relation_to_previous"] == "BASE") == (ordinal == 1),
                "Relative-center rank missing or invalid")
        require(type(item["rule_version"]) is str and item["rule_version"].strip(),
                "Frozen center-rule version missing")
        seen = timestamp(item["seen_at"])
        confirmed = (timestamp(item["confirmed_at"])
                     if item["confirmed_at"] is not None else None)
        require(last_seen is None or seen > last_seen,
                "Synthetic observation clocks must increase")
        last_seen = seen
        if confirmed is not None:
            require(confirmed >= seen and
                    (last_confirm is None or confirmed > last_confirm),
                    "Synthetic confirmation cannot precede observations")
            last_confirm = confirmed
        if seen > asof:
            break  # Future centers MUST NOT influence a past as-of result.
        if confirmed is None or confirmed > asof:
            pending = True
            break
        observed.append(item)
    if len({e["rule_version"] for e in observed}) > 1:
        return verdict("RULE_VERSION_MISMATCH", len(observed))
    if pending:
        return verdict("PENDING_CENTER_CONFIRMATION", len(observed))
    if len(observed) < 2:
        return verdict("INSUFFICIENT_VISIBLE_CENTERS", len(observed))
    direction = row["direction"]
    extend = "HIGHER" if direction == "UP" else "LOWER"
    reverse = "LOWER" if direction == "UP" else "HIGHER"
    second = observed[1]["relation_to_previous"]
    if second == "UNKNOWN":
        return verdict("CENTER_RELATIVE_HEIGHT_UNRESOLVED", len(observed))
    if second != extend:
        return verdict("TWO_CENTER_TREND_NOT_QUALIFIED", len(observed))
    for ordinal, center in enumerate(observed[2:], 3):
        relation = center["relation_to_previous"]
        if relation == "UNKNOWN":
            return verdict("CENTER_RELATIVE_HEIGHT_UNRESOLVED", len(observed))
        if relation in ("EQUAL", reverse):
            return verdict("AUTHOR_TERMINAL_COMPARISON_TRIGGER_ONLY", len(observed), ordinal)
        require(relation == extend, "Unknown directional center order")
    return verdict("CONTINUATION_ONLY_NO_TERMINATION_CONFIRMATION", len(observed))


def check_cases(fixtures: dict, contract: dict) -> dict:
    require(fixtures.get("schema_version") == 1 and
            fixtures.get("contract_id") == CONTRACT_ID and
            fixtures.get("synthetic_only") is True,
            "Test fixture source and purpose changed")
    cases = fixtures["cases"]
    require(isinstance(cases, list) and len(cases) == 12 and
            len({c["id"] for c in cases}) == len(cases),
            "Twelve distinct source logic cases are required")
    counts = {}
    for c in cases:
        result = evaluate(c["input"], contract)
        require(result == c["expected"], "Conditional result drift: " + c["id"])
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    require(counts.get("AUTHOR_TERMINAL_COMPARISON_TRIGGER_ONLY") == 5,
            "Directional terminal condition coverage changed")
    return {"status": BLOCKED, "verified_claim_id": "CL35-SO-9",
            "original_page": 291, "open_legal_premises": len(OPEN),
            "symbolic_cases": len(cases), "outcomes": counts,
            "actual_legal_completed_trends": 0, "real_market_data": False,
            "confirmed_theorem38_uniqueness": False, "market_backtests": 0}


def main() -> None:
    contract = read(CONTRACT)
    validate_contract(contract, read(EVIDENCE), read(INVENTORY), original_pins())
    print(json.dumps(check_cases(read(FIXTURES), contract), ensure_ascii=False))


if __name__ == "__main__":
    main()
