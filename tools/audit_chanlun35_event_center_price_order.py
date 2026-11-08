#!/usr/bin/env python3
"""Event-derived *conditional* lowest-center price order from lesson35 p291.

Every price derives from the PR57 author-axiom receipt's three original events;
the ranking is not an input annotation. Distinct raw runs are NOT independently
certified distinct author centers. A price-order terminal condition is not a
completed trend or live market observation.
"""
from __future__ import annotations

import importlib.util
import json
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"catalog/chanlun35_event_derived_center_price_order_v1.json"
FIXTURES=ROOT/"tests/fixtures/chanlun35_event_derived_center_price_order_cases_v1.json"
UPSTREAM=ROOT/"tools/audit_chanlun35_author_base_center_axiom.py"
SOURCE_TERMINAL=ROOT/"catalog/chanlun_lesson035_terminal_comparison_v1.json"
ID="CL35-EVENT-DERIVED-LOWEST-CENTER-PRICE-ORDER-V1"
PDF_SHA="af49aecbd363286baacbea02d3778b436df4dad797523ce0eb83846118827a66"
PAGE_SHA="1a2c291cff189ea4de5bef2ecf152e9888773d1194b0ed4e7218f4cd0f3b846b"
GAPS=(
 "author_validated_independent_center_grouping",
 "actual_market_trade_origin",
 "author_primitive_level_applicability",
 "actual_center_and_trajectory_completion_clock",
 "equal_price_initial_pair_ambiguity",
 "higher_level_eligible_finished_child_membership",
)
CLAUSE={
 "initial_pair":{"up":"CENTER_2_PRICE_GT_CENTER_1_PRICE",
                 "down":"CENTER_2_PRICE_LT_CENTER_1_PRICE",
                 "equal":"DO_NOT_CLASSIFY_TREND_WITHOUT_ADDITIONAL_AUTHOR_EQUALITY_ADJUDICATION"},
 "from_third":{"up_continue":"LATER_PRICE_GT_PRIOR_PRICE",
               "down_continue":"LATER_PRICE_LT_PRIOR_PRICE",
               "up_terminal":"LATER_PRICE_LE_PRIOR_PRICE",
               "down_terminal":"LATER_PRICE_GE_PRIOR_PRICE"},
 "single_center":"ONE_CENTER_IS_ONLY_POTENTIAL_CONSOLIDATION_NOT_FINISHED_CONSOLIDATION",
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def ensure(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def original():
    spec=importlib.util.spec_from_file_location("base_axiom_source_import",UPSTREAM)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def validate_contract(doc,base,primitive,card,terminal):
    ensure(doc.get("schema_version")==1 and doc.get("id")==ID and
           doc.get("scope")==
           "AUTHOR_LOWEST_CENTER_PRICE_ORDER_CONDITIONAL_ON_DISTINCT_SYNTHETIC_RUNS_NOT_COMPLETED_TRENDS",
           "Scope/version of event-derived center ordering changed")
    ensure(doc.get("base_axiom_contract")==base.DOC_ID and
           doc.get("source_sha256")==PDF_SHA and
           doc.get("original_physical_page")==291 and
           doc.get("native_text_sha256")==PAGE_SHA and
           primitive.verified_original_pins()[(2,291)]==PAGE_SHA,
           "Authored source PDF or base axiom provenance changed")
    ensure(doc.get("author_claims")==["CL35-SO-2","CL35-SO-9","CL018-S07"],
           "Author source-chain identities changed")
    for name,lesson in (("CL35-SO-2",35),("CL35-SO-9",35),("CL018-S07",18)):
        rows=[x for x in card[lesson]["claims"] if x["id"]==name]
        ensure(len(rows)==1 and rows[0]["kind"]=="SOURCE",
               "Source chain includes missing or non-author claim")
    s9=next(x for x in card[35]["claims"] if x["id"]=="CL35-SO-9")
    ensure(s9["pdf_pages"]==[291] and
           s9["source_anchor"]["native_text_sha256"]==PAGE_SHA and
           s9["source_anchor"]["role"]=="AUTHOR_MAIN_IN_COMPILATION" and
           card[35]["source"]["sha256"]==PDF_SHA,
           "Terminal-price source cannot silently change original page/role")
    ensure(terminal["id"]=="CL35-LOWEST-LEVEL-TREND-TERMINAL-CONDITIONAL-V1" and
           terminal["author_conditional_rules"][2]["relations"]==["EQUAL","LOWER"] and
           terminal["author_conditional_rules"][3]["relations"]==["EQUAL","HIGHER"],
           "N>2 terminal equality author rule drift")
    ensure(doc.get("rule_clause")==CLAUSE and
           doc.get("raw_run_distinctness_status")==
           "DIFFERENT_PRICE_RUNS_ARE_NOT_AUTHOR_VERIFIED_DISTINCT_CENTERS" and
           doc.get("source_height_comparison")==
           "POINT_PRICE_COMPARISON_ONLY_UNDER_AUTHOR_STRICT_TRADE_LOWEST_LEVEL_AXIOM" and
           doc.get("event_clock")==
           "CAUSAL_SYNTHETIC_PREFIX_ASOF_NOT_REAL_TRADE_AUTHENTICATION",
           "Center identity, clock, initial equality or comparison rule was silently invented")
    ensure(doc.get("open_proof_slots")==list(GAPS),"External legal source premises removed")
    for key,value in (
        ("valid_completed_trajectories",0),
        ("actual_trade_provenance_authenticated",False),
        ("lowest_level_trend_termination_proven",False),
        ("can_feed_higher_level_recursive_constructor",False),
        ("proof38_unique",False),
        ("proof99_universal",False),
        ("market_backtests","NOT_RUN"),
    ):
        ensure(doc.get(key)==value,"False completed trend, market or theorem claim: "+key)


def relation(current, previous):
    if current>previous:
        return "HIGHER"
    if current<previous:
        return "LOWER"
    return "EQUAL"


def inspect(case,doc,base=None):
    ensure(doc["id"]==ID,"Unexpected rule contract in evaluator")
    base=base or original()
    receipt=base.produce(case,read(base.CONTRACT))
    ensure(base.verify_receipt(case,receipt,read(base.CONTRACT)),
           "Failed to reproduce source event receipt")
    if receipt["status"]=="RULE_VERSION_INCOMPATIBLE_NO_AUTHORED_BASE_INSTANCE":
        return {"status":"VERSION_MISMATCH_NO_ORDER",
                "visible_prefix_sha256":receipt["visible_prefix_sha256"],
                "center_count":0,"center_price_relations":[],
                "first_terminal_center_ordinal":None,
                "center_identity_author_certified":False,
                "trend_actually_completed":False}
    entries=receipt["instances"]
    centers=[]
    for n,x in enumerate(entries,1):
        ensure(x["certificate_kind"]==base.CERT and
               x["source_claim_id"]=="CL35-SO-2" and
               x["conditional_base_center_exists_in_assumed_trades"] is True and
               x["native_text_sha256"]==PAGE_SHA and
               x["source_version"]==base.lifecycle_tool().original_primitive().BASE_RULE and
               x["eligible_as_completed_child_type"] is False,
               "Conditional base center source-chain tampered or upgraded")
        price=Decimal(x["price_exact_decimal"])
        prior=Decimal(entries[n-2]["price_exact_decimal"]) if n>1 else None
        centers.append({"ordinal":n,"first_three_trade_ids":x["first_three_trade_ids"],
                        "price_exact_decimal":x["price_exact_decimal"],
                        "relative_to_prior":relation(price,prior) if n>1 else "BASE",
                        "observed_at":x["first_observed_at"],
                        "original_three_trade_sha256":x["first_three_source_event_sha256"],
                        "raw_run_closed_only":x["raw_run_closed_only"],
                        "distinct_author_center_identity_verified":False})
    total=len(centers)
    terminal=None
    if total==0:
        status="NO_VISIBLE_LOWEST_CENTER_INSTANCE"
    elif total==1:
        status="ONE_CENTER_POSSIBLE_CONSOLIDATION_NOT_COMPLETED"
    else:
        first=centers[1]["relative_to_prior"]
        if first=="EQUAL":
            status="INITIAL_EQUAL_CENTER_PRICES_UNRESOLVED"
        else:
            direction="UP" if first=="HIGHER" else "DOWN"
            status="UP_INITIAL_PRICE_PAIR_ONLY" if direction=="UP" else "DOWN_INITIAL_PRICE_PAIR_ONLY"
            for row in centers[2:]:
                same="HIGHER" if direction=="UP" else "LOWER"
                if row["relative_to_prior"]!=same:
                    terminal=row["ordinal"]
                    status=("UP_AUTHOR_N_GT_2_TERMINAL_PRICE_TRIGGER_ONLY"
                            if direction=="UP" else
                            "DOWN_AUTHOR_N_GT_2_TERMINAL_PRICE_TRIGGER_ONLY")
                    break
                status=("UP_DIRECTIONAL_PRICE_CONTINUATION_ONLY"
                        if direction=="UP" else "DOWN_DIRECTIONAL_PRICE_CONTINUATION_ONLY")
    return {"status":status,
            "visible_prefix_sha256":receipt["visible_prefix_sha256"],
            "center_count":total,"center_price_relations":centers,
            "first_terminal_center_ordinal":terminal,
            "center_identity_author_certified":False,
            "trend_actually_completed":False}


def verify_fixtures(cases,doc,base):
    ensure(cases.get("schema_version")==1 and cases.get("contract_id")==ID
           and cases.get("synthetic_only") is True,"Wrong synthetic fixture contract")
    rows=cases.get("cases")
    ensure(isinstance(rows,list) and len(rows)==14 and
           len({x["id"] for x in rows})==14,
           "14 distinct center-price proof cases required")
    counts={}
    for row in rows:
        result=inspect(row["input"],doc,base)
        want=row["expected"]
        ensure(result["status"]==want["status"] and
               result["center_count"]==want["center_count"] and
               result["first_terminal_center_ordinal"]==want["first_terminal_center_ordinal"] and
               [x["relative_to_prior"] for x in result["center_price_relations"]]==want["relations"],
               "Unexpected inferred center ranking: "+row["id"])
        ensure(result["center_identity_author_certified"] is False and
               result["trend_actually_completed"] is False,
               "Hypothetical distinct-run prices promoted into a certified trend")
        counts[result["status"]]=counts.get(result["status"],0)+1
    return {"status":"AUTHOR_LOWEST_CENTER_PRICE_ORDER_COMPUTED_WITH_UNPROVEN_DISTINCTNESS",
            "synthetic_raw_event_cases":len(rows),"source_author_claims":3,
            "unverified_membership_and_completion_slots":len(GAPS),
            "outcomes":counts,"actual_completed_trajectories":0,
            "market_data_accessed":False,"theorem38_unique_proven":False}


def main():
    base=original()
    lifecycle=base.lifecycle_tool()
    primitive=lifecycle.original_primitive()
    cards={n:read(ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json") for n in (18,20,35)}
    base.validate_contract(read(base.CONTRACT),lifecycle,primitive,cards)
    doc=read(CONTRACT)
    validate_contract(doc,base,primitive,cards,read(SOURCE_TERMINAL))
    print(json.dumps(verify_fixtures(read(FIXTURES),doc,base),ensure_ascii=False))


if __name__=="__main__":
    main()
