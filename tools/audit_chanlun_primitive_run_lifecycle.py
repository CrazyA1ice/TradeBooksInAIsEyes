#!/usr/bin/env python3
"""Event-derived RAW PRICE RUN lifecycle; price-run closure != Chanlun center end.

Imports the already source-locked PR55 primitive three-trade detector. Every
visible event has an independently reconstructible state; no `completed`
field from users, no genuine trade data, no OCR/images and no downstream
recursive/legal-center certificate. The lifecycle is an AI audit convention.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "catalog/chanlun_primitive_run_lifecycle_v1.json"
FIXTURES = ROOT / "tests/fixtures/chanlun_primitive_run_lifecycle_cases_v1.json"
PRIMITIVE_SCRIPT = ROOT / "tools/audit_chanlun_primitive_trades_prefix.py"
SOURCE_CONTRACT = ROOT / "catalog/chanlun_lowest_trade_prefix_v1.json"
RECURSION_CONTRACT = ROOT / "catalog/chanlun_recursive_eligibility_bridge_v1.json"
CONTRACT_ID = "CL35-PRIMITIVE-RUN-LIFECYCLE-EVIDENCE-V1"
RULE_STATES = (
    ("RUN_START", "RAW_PRICE_RUN_STARTED", "first observed trade or changed decimal price"),
    ("BELOW_THIRD", "RAW_EQUAL_PREFIX_BELOW_THIRD",\n     "second observed equal-price trade; still below base witness"),
    ("WITNESS_AT_THIRD", "BASE_THIRD_TRADE_WITNESSED",
     "third consecutive observed equal-price trade"),
    ("SAME_PRICE_EXTENSION", "RAW_EQUAL_RUN_EXTENDED",
     "fourth or later observed equal-price trade"),
    ("CHANGE_PRICE_CLOSES_RAW_RUN", "PRICE_CHANGED_CLOSES_PREVIOUS_RAW_RUN_ONLY",
     "first observed non-equal-price trade; raw run closure only"),
)
OPEN = (
    "legal_lowest_level_center_qualification",
    "independent_ending_not_just_price_change",
    "author_same_level_child_type_legality",
    "three_continuous_completed_child_types",
    "fixed_level_and_historical_rule_version",
    "author_authorized_boundary_and_asof_semantics",
)
FINAL_CERT = "EVENT_DERIVED_RAW_RUN_PROVENANCE_ONLY_NOT_COMPLETED_CHANLUN_CENTER"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def original_primitive():
    spec = importlib.util.spec_from_file_location("verified_primitive_author_base", PRIMITIVE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_contract(contract, primitive, original, recursion):
    require(contract.get("schema_version") == 1 and contract.get("contract_id") == CONTRACT_ID
            and contract.get("scope") ==
                "DERIVED_RAW_TRADE_EVENT_LIFECYCLE_NOT_AUTHOR_CENTER_COMPLETION",
            "Source lifecycle version or source scope altered")
    require(contract.get("upstream_path") ==
            "catalog/chanlun_lowest_trade_prefix_v1.json"
            and contract.get("upstream_primitive_script") ==
            "tools/audit_chanlun_primitive_trades_prefix.py"
            and contract.get("upstream_source_contract") == primitive.ID
            and primitive.ID == original["contract_id"],
            "Original base-rule source lineage differs")
    require(contract.get("downstream_rule_contract") ==
            "CHANLUN-RECURSIVE-ELIGIBILITY-ONLY-V1"
            and contract.get("downstream_path") ==
            "catalog/chanlun_recursive_eligibility_bridge_v1.json"
            and recursion["contract_id"] == contract["downstream_rule_contract"],
            "Unreviewed or incompatible higher-level recursive rule")
    require(contract.get("source_claims") == [x[0] for x in primitive.SOURCE],
            "Source claim lineage drift")
    actual = contract.get("state_rules")
    require(isinstance(actual, list) and len(actual) == len(RULE_STATES),
            "Derived state machine incomplete")
    for row, (id_, status, when) in zip(actual, RULE_STATES):
        require(row == {"id": id_, "status": status, "when": when},
                "Price-run and author-center rules were conflated")
    require(contract.get("completion_semantics") ==
            {"raw_run_closed_is_center_completed": False,
             "third_trade_threshold_is_center_completed": False,
             "repeated_equal_trades_create_higher_center": False,
             "can_feed_recursive_three_completed_lower_types": False},
            "Attempt to turn raw price run into completed center")
    require(contract.get("required_upstream_to_downstream_evidence") == list(OPEN),
            "Missing independent center/type completion premises")
    require(contract.get("output_certificate") == FINAL_CERT
            and contract.get("market_records_read") is False
            and contract.get("pdf_images_read") is False
            and contract.get("original_historical_first_publication_verified") is False
            and contract.get("proof38_or_99_completed") is False
            and contract.get("market_backtest") == "NOT_RUN",
            "False legal/trading/source theorem certificate")
    require(original["output_certificate"] ==
            "BASE_PATTERN_WITNESS_ONLY_NOT_ACTUAL_COMPLETED_CENTER"
            and original["actual_center_completed"] is False
            and recursion["conditional_center_is_certified"] is False
            and recursion["complete_rule_R_g_available"] is False
            and recursion["premise_slots"][0] ==
            {"id": "three_completed_consecutive_eligible_subtypes",
             "status": "EXTERNAL_NOT_VERIFIED"},
            "Upstream or downstream completion proof was modified")


def audit(input_data, contract, primitive):
    require(contract["contract_id"] == CONTRACT_ID, "Wrong lifecycle contract")
    upstream = load(SOURCE_CONTRACT)
    # This validates the entire synthetic series before looking at its as-of prefix.
    base = primitive.inspect_prefix(input_data, upstream)
    seen_at = primitive.stamp(input_data["as_of"])
    visible = [event for event in input_data["events"]
               if primitive.stamp(event["observed_at"]) <= seen_at]
    digest = hashlib.sha256(json.dumps(visible, sort_keys=True, ensure_ascii=False,
                                      separators=(",", ":")).encode("utf-8")).hexdigest()
    empty = {"visible_trades": len(visible), "visible_prefix_sha256": digest,
             "raw_price_runs": [], "event_provenance": [],
             "eligible_base_witness_count": 0, "legal_center_completed": False,
             "may_enter_recursive_center_constructor": False}
    if base["status"] == "RULE_VERSION_INCOMPATIBLE_NOT_EVALUATED":
        return {"status": "RULE_VERSION_INCOMPATIBLE_NOT_EVALUATED", **empty}
    runs, trail = [], []
    for event in visible:
        tid = event["trade_id"]
        price = primitive.number(event["price"])
        at = primitive.stamp(event["observed_at"]).isoformat()
        closed_start = None
        if not runs or price != primitive.number(runs[-1]["price"]):
            if runs:
                prev = runs[-1]
                prev["closed_by_trade_id"] = tid
                prev["closed_observed_at"] = at
                prev["raw_price_run_closed"] = True
                closed_start = prev["start_trade_id"]
            runs.append({"start_trade_id": tid, "last_visible_trade_id": tid,
                         "price": str(price.normalize()),
                         "trade_count": 1, "third_trade_id": None,
                         "third_observed_at": None, "closed_by_trade_id": None,
                         "closed_observed_at": None, "raw_price_run_closed": False,
                         "legal_center_completed": False})
            event_type = ("PRICE_CHANGED_CLOSES_PREVIOUS_RAW_RUN_ONLY"
                          if closed_start is not None else "RAW_PRICE_RUN_STARTED")
        else:
            current = runs[-1]
            current["trade_count"] += 1
            current["last_visible_trade_id"] = tid
            if current["trade_count"] == 3:
                current["third_trade_id"] = tid
                current["third_observed_at"] = at
                event_type = "BASE_THIRD_TRADE_WITNESSED"
            else:
                event_type = ("RAW_EQUAL_RUN_EXTENDED" if current["trade_count"] > 3
                              else "RAW_EQUAL_PREFIX_BELOW_THIRD")
        current = runs[-1]
        trail.append({"trade_id": tid, "observed_at": at,
                      "event_state": event_type,
                      "raw_run_start_trade_id": current["start_trade_id"],
                      "closed_raw_run_start_trade_id": closed_start,
                      "candidate_third_trade_id": current["third_trade_id"],
                      "legal_center_completed": False})
    matched = [r for r in runs if r["third_trade_id"] is not None]
    require(len(matched) == len(base["witnesses"]),
            "Independent PR55 witness count inconsistent with raw event ledger")
    for raw, witness in zip(matched, base["witnesses"]):
        require(raw["start_trade_id"] == witness["start_trade_id"]
                and raw["third_trade_id"] == witness["third_trade_id"]
                and raw["last_visible_trade_id"] == witness["last_visible_trade_id"]
                and raw["trade_count"] == witness["observed_same_price_run_length"]
                and raw["third_observed_at"] == witness["first_observable_at"]
                and primitive.number(raw["price"]) == primitive.number(witness["price"]),
                "Independent PR55 three-trade witness disagrees with event ledger")
    if matched:
        status = ("OPEN_RAW_RUN_WITH_BASE_WITNESS_NOT_CENTER_COMPLETE"
                  if runs[-1]["third_trade_id"] is not None else
                  "PRIOR_RAW_RUN_WITNESSED_AND_CLOSED_NOT_CENTER_COMPLETE")
    else:
        status = "NO_VISIBLE_BASE_TRIPLE"
    return {"status": status, "visible_trades": len(visible),
            "visible_prefix_sha256": digest, "raw_price_runs": runs,
            "event_provenance": trail, "eligible_base_witness_count": len(matched),
            "legal_center_completed": False,
            "may_enter_recursive_center_constructor": False}


def run_fixtures(cases, contract, primitive):
    require(cases.get("schema_version") == 1 and cases.get("contract_id") == CONTRACT_ID
            and cases.get("synthetic_only") is True, "Wrong lifecycle fixture version")
    rows = cases.get("cases")
    require(isinstance(rows, list) and len(rows) == 8
            and len({x["id"] for x in rows}) == len(rows),
            "Eight distinct lifecycle proof scenarios required")
    counts = {}
    for item in rows:
        result = audit(item["input"], contract, primitive)
        expect = item["expected"]
        require(result["status"] == expect["status"] and
                result["eligible_base_witness_count"] == expect["witnesses"] and
                len(result["raw_price_runs"]) == expect["raw_runs"] and
                sum(bool(x["raw_price_run_closed"]) for x in result["raw_price_runs"]) ==
                    expect["closed_runs"] and
                [x["event_state"] for x in result["event_provenance"]] ==
                    expect["event_states"],
                "Lifecycle/correctness regression: " + item["id"])
        require(result["legal_center_completed"] is False and
                result["may_enter_recursive_center_constructor"] is False
                and all(x["legal_center_completed"] is False
                        for x in result["raw_price_runs"]),
                "An event witness was falsely promoted into legal type")
        counts[result["status"]] = counts.get(result["status"], 0)+1
    return {"status": FINAL_CERT, "original_author_links": len(primitive.SOURCE),
            "unverified_center_type_requirements": len(OPEN),
            "lifecycle_cases": len(rows), "results": counts,
            "actual_completed_centers": 0,
            "eligible_child_type_certificates": 0,
            "actual_market_events_read": False,
            "proof38_or_99": False}


def main():
    primitive = original_primitive()
    contract = load(CONTRACT)
    source = load(SOURCE_CONTRACT)
    recursion = load(RECURSION_CONTRACT)
    primitive.verify_contract(source, primitive.read(primitive.INV),
                              primitive.verified_original_pins(),
                              {n:primitive.read(ROOT /
                                  f"knowledge/evidence/chanlun_lesson{n:03d}.json")
                               for n in (18, 20, 35)})
    verify_contract(contract, primitive, source, recursion)
    print(json.dumps(run_fixtures(load(FIXTURES), contract, primitive),
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
