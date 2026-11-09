#!/usr/bin/env python3
"""Derive the *first observed* 3-equal-price witness from synthetic trades.

Unlike interval declaration tools, this reads raw sequential event inputs and
derives price-run membership and the third-trade causal timestamp. An author
base-rule match is NOT a legally completed center, type, or live trade signal.
"""
from __future__ import annotations

import importlib.util
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "catalog/chanlun_lowest_trade_prefix_v1.json"
CASES = ROOT / "tests/fixtures/chanlun_lowest_trade_prefix_cases_v1.json"
INV = ROOT / "reports/source_inventory/chanlun_20261107_verified.json"
PINS1 = ROOT / "reports/source_inventory/chanlun_center_order_completion_native_text_sha256.json"
PINS2 = ROOT / "tools/inspect_chanlun_original_proof_text_readonly.py"
ID = "CL35-PRIMITIVE-TRADE-THREE-EQUAL-PREFIX-V1"
BASE_RULE = "CL35_PRIMITIVE_LOCAL_SYNTHETIC_V1"
DOC_SHA = {
    1: "0a402e19bbcabc24a5d031b047aeebcf96cdb7f777d2462cc7e5b28ed121b865",
    2: "af49aecbd363286baacbea02d3778b436df4dad797523ce0eb83846118827a66",
}
SOURCE = (
    ("CL35-SO-2", 35, 2, 291, "1a2c291cff189ea4de5bef2ecf152e9888773d1194b0ed4e7218f4cd0f3b846b",
     "AUTHOR_SOURCE_IN_COMPILATION", "THREE_CONSECUTIVE_SAME_PRICE_TRADES_LOWEST_BASE"),
    ("CL018-S07", 18, 1, 235, "d4f06d4d8395748f7b38307ccdc83436fdf9480a729fad413c45f772ae7023d4",
     "AUTHOR_SOURCE_IN_COMPILATION_WITH_EDITORIAL_INSERTS", "CAN_FINISH_NOT_MUST_FINISH"),
    ("CL020-S01", 20, 1, 245, "b699993c6d57238640eb94844f53d5391fcb1572659cae08fb2248139ca74ea3",
     "AUTHOR_SOURCE_IN_COMPILATION_WITH_EDITORIAL_INSERTS",
     "INDEFINITE_SAME_PRICE_ACTIVITY_DOES_NOT_FORCE_HIGHER_CENTER"),
)
OPEN = (
    "real_execution_trade_provenance", "unambiguous_author_lowest_level_time_base",
    "transaction_timestamp_observability",
    "nonidentical_price_run_separation_vs_complete_zen_center_rule",
    "independent_historical_rule_version",
    "finished_lowest_center_and_higher_type_eligibility",
)
EVENT_KEYS = {"trade_id", "observed_at", "price", "rule_version"}
CASE_KEYS = {"kind", "as_of", "events"}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def verified_original_pins():
    spec = importlib.util.spec_from_file_location("original_35_native_source", PINS2)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    newest = read(PINS1)
    require(newest["reader"] == "pymupdf_1.26.7_get_text_sort_true"
            and newest["source_pdf_sha256"] == DOC_SHA[1],
            "Previously verified volume1 source reader drift")
    return {(2, 291): module.EXPECTED_TEXT_SHA256[(2, 291)],
            (1, 235): newest["page_native_text_sha256"]["235"],
            (1, 245): newest["page_native_text_sha256"]["245"]}


def verify_contract(contract, inventory, pins, cards):
    require(contract.get("schema_version") == 1 and contract.get("contract_id") == ID
            and contract.get("scope") ==
                "AUTHOR_NATIVE_TEXT_CONDITIONAL_BASE_PATTERN_NOT_COMPLETED_CENTER",
            "Source gate identity/partial scope drift")
    require(contract.get("source_volumes") == {str(k): v for k,v in DOC_SHA.items()},
            "Original PDF SHA list changed")
    canonical = {int(Path(v["path"]).stem.split("卷")[-1]): v["sha256"]
                 for v in inventory["volumes"]}
    require(all(canonical[k] == sha for k,sha in DOC_SHA.items()),
            "Original PDF volume fingerprint drift")
    found = contract.get("author_source_links")
    require(isinstance(found, list) and len(found) == len(SOURCE),
            "Missing original base/extension source evidence")
    for doc, (id_, lesson, vol, page, sha, role, scope) in zip(found, SOURCE):
        require((doc.get("id"),doc.get("lesson"),doc.get("volume"),doc.get("page"),
                 doc.get("sha"),doc.get("role"),doc.get("scope")) ==
                (id_,lesson,vol,page,sha,role,scope), "Original author source link altered")
        require(pins.get((vol,page)) == sha, "Verified original native-text page SHA drift")
        card = cards[lesson]
        matching = [x for x in card["claims"] if x["id"] == id_]
        require(len(matching) == 1 and matching[0]["kind"] == "SOURCE"
                and page in matching[0]["pdf_pages"]
                and page in card["source"]["pdf_pages"]
                and card["source"]["sha256"] == DOC_SHA[vol],
                "Source card not a verifiable author main-text claim")
        if id_ == "CL018-S07":
            require(matching[0]["source_anchor"]["inline_editorial_markers_present"] is True
                    and matching[0]["source_anchor"]["independent_first_publication_verified"] is False,
                    "Editorial or first-publication status falsely upgraded")
    require(contract.get("author_condition") ==
            "THREE_CONSECUTIVE_TRADE_EVENTS_WITH_NUMERICALLY_IDENTICAL_PRICE"
            and contract.get("computation_qualifier") ==
            "SYNTHETIC_TRADE_EVENT_PREFIX_ONLY_WITH_EXACT_DECIMAL"
            and contract.get("observed_first_threshold") ==
            "THIRD_OBSERVED_TRADE_IN_CONTIGUOUS_SAME_PRICE_RUN"
            and contract.get("observed_extension") ==
            "ADDITIONAL_EQUAL_TRADES_MAY_EXTEND_SAME_RUN_NO_HIGHER_CENTER_PROOF",
            "Not the original conditional base witness rule")
    require(contract.get("unverified") == list(OPEN),
            "Undischarged legal proof conditions may not be erased")
    require(contract.get("output_certificate") ==
            "BASE_PATTERN_WITNESS_ONLY_NOT_ACTUAL_COMPLETED_CENTER"
            and contract.get("historical_first_publication_authenticated") is False
            and contract.get("market_data_read") is False
            and contract.get("actual_center_completed") is False
            and contract.get("higher_level_center_created") is False
            and contract.get("proof_38_or_99") is False
            and contract.get("market_backtest") == "NOT_RUN",
            "Fake actual center, higher structure, market or theorem certificate")


def stamp(s):
    require(type(s) is str and s.strip(), "Empty synthetic event time")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError as exc:
        raise ValueError("Invalid synthetic event time") from exc
    require(dt.tzinfo is not None and dt.utcoffset() is not None,
            "Synthetic observation timestamps need UTC offsets")
    return dt


def number(s):
    require(type(s) is str and s.strip() and
            all(ch in "0123456789.+-" for ch in s), "Price must be an exact decimal string")
    try:
        val = Decimal(s)
    except InvalidOperation as exc:
        raise ValueError("Invalid decimal trade price") from exc
    require(val.is_finite() and val >= 0, "Invalid or negative synthetic price")
    return val


def inspect_prefix(case, contract):
    require(contract["contract_id"] == ID, "Wrong rule source contract")
    require(type(case) is dict and set(case) == CASE_KEYS,
            "Unexpected real-market/certification fields")
    require(case["kind"] == "SYNTHETIC_ORDERED_TRADES_NOT_REAL_MARKET",
            "Real market execution claims forbidden")
    asof = stamp(case["as_of"])
    events = case["events"]
    require(type(events) is list and 1 <= len(events) <= 1000,
            "Finite ordered synthetic event list required")
    all_events = []
    last = None
    for expected_id, event in enumerate(events,1):
        require(type(event) is dict and set(event) == EVENT_KEYS,
                "Event cannot carry claimed legal-center certification")
        require(type(event["trade_id"]) is int and event["trade_id"] == expected_id,
                "Missing, duplicated or out-of-order trade event")
        observed = stamp(event["observed_at"])
        require(last is None or observed > last,
                "Observation timestamp sequence must be strictly increasing")
        last = observed
        require(type(event["rule_version"]) is str and event["rule_version"].strip(),
                "Source rule version must be declared")
        all_events.append((event["trade_id"],observed,number(event["price"]),event["rule_version"]))
    prefix = [event for event in all_events if event[1] <= asof]
    if len({x[3] for x in prefix}) > 1 or any(x[3] != BASE_RULE for x in prefix):
        return {"status":"RULE_VERSION_INCOMPATIBLE_NOT_EVALUATED",
                "visible_trades":len(prefix),"witnesses":[],"actual_center_completed":False}
    witnesses = []
    run_start = None
    last_price = None
    count = 0
    for trade_id, observed, price, version in prefix:
        if last_price is None or price != last_price:
            run_start = trade_id
            count = 1
            last_price = price
        else:
            count += 1
        if count == 3:
            witnesses.append({
                "start_trade_id":run_start, "third_trade_id":trade_id,
                "last_visible_trade_id":trade_id, "price":str(price),
                "first_observable_at":observed.isoformat(),
                "observed_same_price_run_length":count,
                "legally_completed":False,
            })
        elif count > 3:
            witness = witnesses[-1]
            require(witness["start_trade_id"] == run_start,
                    "Run continuation witness identity mismatch")
            witness["last_visible_trade_id"] = trade_id
            witness["observed_same_price_run_length"] = count
    return {
        "status": ("BASE_PATTERN_WITNESSED_NOT_CENTER_CERTIFIED" if witnesses
                   else "NO_VISIBLE_BASE_TRIPLE"),
        "visible_trades":len(prefix), "witnesses":witnesses,
        "actual_center_completed":False,
    }


def run_fixtures(fixtures, contract):
    require(fixtures.get("schema_version") == 1
            and fixtures.get("contract_id") == ID and
            fixtures.get("synthetic_only") is True,
            "Source-labelled fixture scope changed")
    cases = fixtures.get("cases")
    require(type(cases) is list and len(cases) == 11
            and len({x["id"] for x in cases}) == len(cases),
            "Eleven primitive-event cases required")
    results = {}
    for test in cases:
        actual = inspect_prefix(test["input"], contract)
        require(actual == test["expected"], "Unexpected first observed triple: " + test["id"])
        results[actual["status"]] = results.get(actual["status"], 0)+1
    return {"status":"SOURCE_PINNED_PRIMITIVE_TRADE_PREFIX_WITNESS_ONLY",
            "author_source_links":len(SOURCE),"open_legal_premises":len(OPEN),
            "synthetic_prefix_cases":len(cases),
            "status_counts":results, "actual_completed_centers":0,
            "legal_child_trajectory_membership_confirmed":False,
            "market_data_accessed":False,"proof_38_or_99":False}


def main():
    doc = read(CONTRACT)
    verify_contract(doc, read(INV), verified_original_pins(),
                    {n:read(ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json")
                     for n in (18,20,35)})
    print(json.dumps(run_fixtures(read(CASES),doc),ensure_ascii=False))


if __name__ == "__main__":
    main()
