#!/usr/bin/env python3
"""Conditional author-defined lowest-level center existence, NOT its completion.

Recomputes PR55 raw trade witnesses and PR56 event provenance. Author lesson35
p291 defines 3 consecutive same-price trades AS the smallest center. This
script corrects earlier 'necessary-only' language without claiming fake real
executions, end times, completed lower types, or a full Chanlun grammar.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"catalog/chanlun35_author_base_center_axiom_v1.json"
CASES=ROOT/"tests/fixtures/chanlun35_author_base_center_axiom_cases_v1.json"
LIFECYCLE_SCRIPT=ROOT/"tools/audit_chanlun_primitive_run_lifecycle.py"
DOC_ID="CL35-AUTHOR-LOWEST-CENTER-DEFINITIONAL-INSTANCE-V1"
PDF_SHA="af49aecbd363286baacbea02d3778b436df4dad797523ce0eb83846118827a66"
PAGE_SHA="1a2c291cff189ea4de5bef2ecf152e9888773d1194b0ed4e7218f4cd0f3b846b"
CERT="AUTHOR_LOWEST_CENTER_AXIOM_IN_ASSUMED_EVENT_STREAM"
SIX_GAPS=(
 "independent_trade_origin_and_order","market_timestamp_observability",
 "author_applicable_primitive_level","historical_version_at_observation",
 "center_termination_evidence",
 "finished_lower_trajectory_and_higher_center_eligibility",
)
BLOCKED=(
 "ASSUMED_EVENT_IS_REAL_EXECUTION",
 "SAME_PRICE_RUN_CLOSURE_IS_CENTER_COMPLETION",
 "ONE_CENTER_IN_PREFIX_IS_FINISHED_CONSOLIDATION",
 "THREE_BASE_CENTERS_ARE_THREE_FINISHED_LOWER_TRAJECTORIES",
 "SOURCE_PUBLICATION_DATE_IS_LIVE_KNOWABILITY",
)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok, reason):
    if not ok: raise ValueError(reason)


def lifecycle_tool():
    spec=importlib.util.spec_from_file_location("author_base_existing_raw_ledger",LIFECYCLE_SCRIPT)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def validate_contract(doc, lifecycle, primitive, cards):
    source=read(primitive.CONTRACT)
    primitive.verify_contract(source,read(primitive.INV),
                              primitive.verified_original_pins(),cards)
    lifecycle.verify_contract(read(lifecycle.CONTRACT),primitive,source,
                              read(lifecycle.RECURSION_CONTRACT))
    require(doc.get("schema_version")==1 and doc.get("id")==DOC_ID
            and doc.get("scope")==
            "SOURCE_AUTHORED_BASE_CENTER_CONDITIONAL_ON_SYNTHETIC_TRADES_NOT_COMPLETED_TREND",
            "Authored base axiom source/scope changed")
    require((doc.get("author_text_claim_id"),doc.get("original_pdf_path"),
             doc.get("original_pdf_sha256"),doc.get("physical_pdf_page"),
             doc.get("native_text_sha256")) ==
            ("CL35-SO-2","ChineseBooks/缠论/缠论_卷2.pdf",PDF_SHA,291,PAGE_SHA),
            "Exact authored original PDF claim changed")
    claim=[x for x in cards[35]["claims"] if x["id"]=="CL35-SO-2"]
    require(len(claim)==1 and claim[0]["kind"]=="SOURCE" and
            291 in claim[0]["pdf_pages"] and
            cards[35]["source"]["sha256"]==PDF_SHA,
            "Author source evidence cannot be promoted or attributed to editorial")
    require(primitive.verified_original_pins()[(2,291)]==PAGE_SHA,
            "Authored base wording page checksum drift")
    require(doc.get("author_original_base_axiom")==
            "THREE_CONSECUTIVE_IDENTICAL_PRICE_TRADES_CONSTITUTE_LOWEST_LEVEL_CENTER"
            and doc.get("new_source_interpretation")==
            "AUTHOR_DEFINITION_IS_SUFFICIENT_WITHIN_A_VALIDATED_PRIMITIVE_TRADE_MODEL"
            and doc.get("important_contrast")==
            "CENTER_EXISTS_CONDITIONALLY_DOES_NOT_MEAN_CENTER_ENDS_OR_PARENT_TREND_COMPLETES",
            "Author sufficient primitive base axiom or qualification erased")
    require(doc.get("source_links")==[x[0] for x in primitive.SOURCE] and
            doc.get("derived_from")==lifecycle.CONTRACT_ID and
            doc.get("assumed_data_kind")=="SYNTHETIC_ORDERED_TRADES_NOT_REAL_MARKET" and
            doc.get("proof_certificate")==CERT and
            doc.get("lifecycle_receipt_trusted_only_when_recomputed") is True,
            "Source lineage / recomputed proof requirement altered")
    require(doc.get("blocked_promotions")==list(BLOCKED) and
            doc.get("validation_required")==list(SIX_GAPS) and
            doc.get("original_rule_version_scope")==
            "AUTHOR_TEXT_AT_VOLUME2_PAGE291_NO_LATER_PEN_OR_SEGMENT_REVISIONS",
            "Undefined high-level promotion or rule-version change")
    for key in ("independent_market_trade_authentication",
                "historical_first_publication_authenticated","actual_center_completed",
                "actual_consolidation_trend_completed","can_feed_higher_level_constructor",
                "market_data_read","pdf_images_read","original_proofs38_99_completed"):
        require(doc.get(key) is False,"Attempted unsupported proof/market promotion: "+key)
    require(doc.get("market_backtests")=="NOT_RUN","Undisclosed market research")


def sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,
                                    separators=(",",":")).encode("utf-8")).hexdigest()


def produce(case, doc, lifecycle=None):
    require(doc["id"]==DOC_ID,"Wrong source axiom")
    lifecycle=lifecycle or lifecycle_tool()
    primitive=lifecycle.original_primitive()
    base=primitive.inspect_prefix(case,read(primitive.CONTRACT))
    raw=lifecycle.audit(case,read(lifecycle.CONTRACT),primitive)
    require(base["visible_trades"]==raw["visible_trades"] and
            base["actual_center_completed"] is False and
            raw["legal_center_completed"] is False and
            raw["may_enter_recursive_center_constructor"] is False,
            "Original raw input evidence changed unexpectedly")
    if raw["status"]=="RULE_VERSION_INCOMPATIBLE_NOT_EVALUATED":
        require(base["witnesses"]==[],"Mixed version still returned a witness")
        return {"status":"RULE_VERSION_INCOMPATIBLE_NO_AUTHORED_BASE_INSTANCE",
                "visible_prefix_sha256":raw["visible_prefix_sha256"],
                "source_axiom_id":DOC_ID,"instances":[],
                "real_market_authenticated":False,"parent_trajectory_completed":False}
    visible=case["events"][:raw["visible_trades"]]
    cases=[]
    for r in raw["raw_price_runs"]:
        if r["third_trade_id"] is None:
            continue
        tid=r["third_trade_id"]
        start=r["start_trade_id"]
        triplet=visible[start-1:tid]
        require(len(triplet)==3 and [x["trade_id"] for x in triplet]==
                list(range(start,tid+1)),"Noncontiguous synthetic witness forbidden")
        val=primitive.number(triplet[0]["price"])
        require(all(primitive.number(x["price"])==val for x in triplet),
                "Source-base price equality is not established")
        require(primitive.stamp(triplet[-1]["observed_at"]).isoformat()==r["third_observed_at"],
                "Third event observation clock changed")
        cases.append({
            "certificate_kind":CERT,"source_claim_id":"CL35-SO-2",
            "pdf_volume":2,"physical_page":291,
            "native_text_sha256":PAGE_SHA,"source_version":primitive.BASE_RULE,
            "first_three_trade_ids":[x["trade_id"] for x in triplet],
            "first_three_source_event_sha256":sha(triplet),
            "price_exact_decimal":format(val.normalize(), "f"),
            "first_observed_at":r["third_observed_at"],
            "visible_prefix_sha256":raw["visible_prefix_sha256"],
            "conditional_base_center_exists_in_assumed_trades":True,
            "raw_run_closed_only":r["raw_price_run_closed"],
            "raw_run_closed_by_trade_id":r["closed_by_trade_id"],
            "independent_real_trade_provenance_verified":False,
            "parent_trajectory_completed":False,
            "eligible_as_completed_child_type":False,
        })
    require(len(cases)==len(base["witnesses"]),
            "Authored definition instance count disagrees with prior exact event recognizer")
    return {"status":("AUTHOR_BASE_CENTER_AXIOM_APPLIES_IN_SYNTHETIC_STREAM"
                      if cases else "NO_AUTHORED_BASE_CENTER_INSTANCE_IN_VISIBLE_PREFIX"),
            "visible_prefix_sha256":raw["visible_prefix_sha256"],
            "source_axiom_id":DOC_ID,"instances":cases,
            "real_market_authenticated":False,"parent_trajectory_completed":False}


def verify_receipt(input_case, submitted, doc, lifecycle=None):
    require(type(submitted) is dict and
            submitted==produce(input_case,doc,lifecycle),
            "Receipt altered, source not reproducible, or certificate was upgraded")
    return True


def fixtures_check(testcases, doc, lifecycle):
    require(testcases.get("schema_version")==1 and
            testcases.get("contract_id")==DOC_ID and
            testcases.get("synthetic_only") is True,
            "Source/fixture version mismatch")
    rows=testcases.get("cases")
    require(type(rows) is list and len(rows)==10 and
            len({r["id"] for r in rows})==len(rows),
            "Ten distinct authored-base definition cases required")
    counts={}
    for row in rows:
        actual=produce(row["input"],doc,lifecycle)
        require(actual["status"]==row["expected_status"] and
                len(actual["instances"])==row["expected_instance_count"] and
                [x["raw_run_closed_only"] for x in actual["instances"]]==
                    row["expected_raw_close_flags"],
                "Actual definitional-author base proof deviates from fixture: "+row["id"])
        verify_receipt(row["input"],actual,doc,lifecycle)
        require(all(x["conditional_base_center_exists_in_assumed_trades"]
                    and not x["parent_trajectory_completed"] and
                    not x["independent_real_trade_provenance_verified"]
                    for x in actual["instances"]),
                "Real-market or higher-level completion fabricated")
        counts[actual["status"]]=counts.get(actual["status"],0)+1
    return {"status":"AUTHOR_BASE_DEFINITION_INSTANCES_REPRODUCED_NOT_COMPLETED_REAL_CENTERS",
            "original_source_claim":"CL35-SO-2","cases":len(rows),
            "conditional_instances":sum(row["expected_instance_count"] for row in rows),
            "verdict_counts":counts,"unverified_external_premises":len(SIX_GAPS),
            "actual_completed_parent_types":0,
            "market_data_accessed":False,"proved_38_or_99":False}


def main():
    lifecycle=lifecycle_tool()
    primitive=lifecycle.original_primitive()
    contract=read(CONTRACT)
    cards={n:read(ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json")
           for n in (18,20,35)}
    validate_contract(contract,lifecycle,primitive,cards)
    print(json.dumps(fixtures_check(read(CASES),contract,lifecycle),ensure_ascii=False))


if __name__=="__main__":
    main()
