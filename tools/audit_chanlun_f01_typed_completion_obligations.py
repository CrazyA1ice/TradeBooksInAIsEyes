#!/usr/bin/env python3
"""Source-pinned F01 typed completion proof obligations; not a Chanlun parser.

Actual complete lower trajectories are NEVER inferred from primitive centers,
pen/segment observations, or user-declared completion. A minimal syntax witness
computes only conditional candidate overlap when three synthetic declared
children are present; legal finished-child certificates remain OPEN.
"""
from __future__ import annotations
import json
from pathlib import Path
from decimal import Decimal, InvalidOperation
from datetime import datetime

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"catalog/chanlun_f01_typed_completion_obligations_v1.json"
FORMAL=ROOT/"reports/source_inventory/chanlun_formal_proof_readiness_v1.json"
VERSION=ROOT/"catalog/chanlun_rule_history_v1.json"
INDEX=ROOT/"catalog/chanlun_lesson_index.json"
THIRD=ROOT/"catalog/chanlun_f01_f02_third_point_boundary_v1.json"
ARTICLE=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_F01_COMPLETION_PROOF_OBLIGATIONS.md"
ID="CHANLUN-F01-TYPED-COMPLETION-OBLIGATION-CHAIN-V1"
EXPECTED={
  (17,"CL017-S02",197),(18,"CL018-S01",234),
  (18,"CL018-S07",235),(35,"CL35-SO-2",291),
  (35,"CL35-SO-3",291),(38,"CL38-SOURCE-1",338),
  (62,"CL62-SOURCE-3",293),(67,"CL67-SOURCE-3",388),
  (71,"CL71-SOURCE-1",71),(71,"CL71-SOURCE-4",72),
  (78,"CL78-SOURCE-1",174),(78,"CL78-SOURCE-2",175),
  (81,"CL81-SOURCE-4",241)
}
EXPECTED_TYPES={"PRIMITIVE_TRADES","BASE_CENTER_INSTANCE","PEN_CONSTRUCTED",
  "FEATURE_FRACTAL_OBSERVED","REVERSE_PEN_ONLY",
  "LEGAL_OPPOSITE_SEGMENT_ASSUMED","FINISHED_LOWER_TREND_ASSUMED",
  "AUTHOR_AUTHENTICATED_FINISHED_CHILD","THREE_CONSECUTIVE_FINISHED_CHILDREN"}
STOP_FLAGS=("candidate_completion_certification_allowed",
    "source_roles_independently_authenticated","all_canonical_pdf_images_reviewed",
    "historical_asof_knowability_proven","full_Rg_frozen",
    "OB38_unique_proven","OB99_future_proven","actual_market_data_accessed")

def read(path):return json.loads(path.read_text(encoding="utf-8"))
def require(value,message):
    if not value:raise ValueError(message)

def audit_sources(doc):
    require(doc.get("schema_version")==1 and doc.get("id")==ID and
        doc.get("scope")==
        "SOURCE_PINNED_TYPE_TRANSITION_CONSTRAINTS_AND_PREFIX_NONIDENTIFIABILITY_NOT_A_COMPLETE_CHANLUN_PARSER" and
        doc.get("formal_readiness")=="reports/source_inventory/chanlun_formal_proof_readiness_v1.json" and
        doc.get("version_register")=="catalog/chanlun_rule_history_v1.json" and
        doc.get("upstream_third_point_contract")=="catalog/chanlun_f01_f02_third_point_boundary_v1.json" and
        doc.get("canonical_pdf_index")=="catalog/chanlun_lesson_index.json",
        "F01 source/proof contract changed")
    require(all(doc.get(f) is False for f in STOP_FLAGS) and
            doc.get("backtests")=="NOT_RUN",
            "False author completion proof or actual market access")
    source=doc.get("source_claims",[])
    require(len(source)==len(EXPECTED) and
            {(x["lesson"],x["claim_id"],x["physical_pdf_page"]) for x in source}==EXPECTED,
            "Source evidence set changed or duplicates")
    volumes={n:v for v in read(INDEX)["volumes"] for n in [v["volume"]]}
    for row in source:
        n,claim,page=row["lesson"],row["claim_id"],row["physical_pdf_page"]
        c=read(ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json")
        v=1 if n in (17,18) else 2 if n in (35,38) else 3 if n in (62,67) else 4
        require(c["source"]["path"]==volumes[v]["path"] and
                c["source"]["sha256"]==volumes[v]["sha256"] and
                1<=page<=volumes[v]["pdf_page_count"] and
                row["role"]=="SOURCE_IN_COMPILATION_NOT_INDEPENDENT_FIRST_PUBLICATION",
                "PDF volume/role/source attribution mismatch")
        claimed=[x for x in c["claims"] if x["id"]==claim]
        require(len(claimed)==1 and claimed[0]["kind"]=="SOURCE" and
                page in claimed[0]["pdf_pages"],
                "Claim not in original volume source-card page")
    names={x["id"] for x in doc.get("types",[])}
    require(len(doc["types"])==len(EXPECTED_TYPES) and names==EXPECTED_TYPES and
            all(x["not_enough_for"] and x["may_create"] for x in doc["types"]),
            "Original construction and termination types were merged")
    edges=doc.get("nonimplications",[])
    require(len(edges)==8 and
            all(len(x["support"])>=1 for x in edges) and
            len({(x["from"],x["to"]) for x in edges})==len(edges),
            "A source nonimplication was removed")
    source_ids={c["claim_id"] for c in source}
    require(all(set(x["support"])<=source_ids for x in edges),
            "Nonimplication refers to uncited source")
    require("PARENT_TREND_FINISHED_NOW" in [x["to"] for x in edges] and
            ("THREE_TRADES_BASE_CENTER","FINISHED_LOWER_TREND") in
            [(x["from"],x["to"]) for x in edges],
            "Fundamental not-completed-vs-can-complete guard lost")
    p=doc["prefix_argument"]
    require(p["author_source"]=="CL018-S07" and
            p["not_a_market_counterexample"] is True and
            p["not_proof_of_author_theory_inconsistency"] is True and
            p["formal_consequence"]==
            "CURRENT_PREFIX_MEETING_MINIMAL_CENTER_THRESHOLD_ALONE_DOES_NOT_DETERMINE_UNIVERSAL_ACTUAL_END_TIMESTAMP",
            "Prefix nonidentification argument overstated")
    v=read(VERSION)["entries"]
    ids={x["id"] for x in v}
    for name in ["pen_062_original","pen_062_appended_candidate",
                 "segment_067_feature_sequence","segment_071_typed_membership",
                 "pen_081_later_dated_post"]:
        require(name in ids,"Missing original historical rule source version")
    appendix=next(x for x in v if x["id"]=="pen_062_appended_candidate")
    require(appendix["source_displayed_at"] is None and
            appendix["timestamp_basis"]=="unknown",
            "Undated editor backdated as original")
    f=read(FORMAL)
    require(f["certifies_theorem"] is False and
            f["complete_frozen_rule_ref"] is None and
            {g["id"] for g in f["goals"]}==
            {"OB38-EXIST","OB38-UNIQUE","OB38-ASOF","OB99-EXIST","OB99-LOCATION"} and
            all(g["status"]=="BLOCKED_NOT_CERTIFIED" for g in f["goals"]),
            "F01 research illegally certifies unresolved OB38/OB99")
    third=read(THIRD)
    require(third["author_center_destroyed_certified"] is False,
            "Prior third point boundary limitations erased")
    return True

def atom(x):
    require(type(x) is str and x.strip(),"Interval endpoint must be decimal string")
    try:v=Decimal(x)
    except InvalidOperation as e:raise ValueError("Invalid decimal") from e
    require(v.is_finite(),"Nonfinite price")
    return v

def conditional_three_child_intersection(packet):
    """Keep source-declared lower trajectories out of author-certified union."""
    require(type(packet) is dict and set(packet)=={"as_of","level","rule_version",
          "children","declaration_origin"} and
          packet["declaration_origin"]=="SYNTHETIC_EXTERNAL_COMPLETION_ASSERTIONS_NOT_SOURCE_PROOF" and
          type(packet["level"]) is int and packet["level"]>=1 and
          type(packet["rule_version"]) is str and bool(packet["rule_version"]),
          "A synthetic declared completion must not pose as author proof")
    asof=datetime.fromisoformat(packet["as_of"])
    require(asof.tzinfo is not None and asof.utcoffset() is not None,
            "As-of must include timezone")
    children=packet["children"]
    require(type(children) is list and len(children)==3 and
            len({x["id"] for x in children})==3 and
            all(x["seq"]==i for i,x in enumerate(children,1)),
            "Three distinct ordered child declarations required")
    result={"status":"PENDING_DECLARED_CHILD_COMPLETION",
            "declared_intersection":None,"source_author_finished_children":0,
            "actual_author_center_certified":False,"parent_completed":False,
            "proof38_or_99":False,"market_data_used":False}
    ranges=[]
    for ch in children:
        require(set(ch)=={"id","seq","low","high","level","declared_completed_at",
                         "rule_version","source_certification"},
                "Illegal child evidence shape")
        require(ch["level"]==packet["level"]-1 and
                ch["rule_version"]==packet["rule_version"] and
                ch["source_certification"]=="NOT_AUTHOR_AUTHENTICATED",
                "Child's rule level/version/source certificate mismatched")
        x=datetime.fromisoformat(ch["declared_completed_at"])
        require(x.tzinfo is not None and x.utcoffset() is not None,
                "Child declared completion needs timezone")
        if x>asof:return result
        lo,hi=atom(ch["low"]),atom(ch["high"])
        require(lo<=hi,"Invalid child range")
        ranges.append((lo,hi))
    low=max(x for x,_ in ranges);high=min(x for _,x in ranges)
    result["status"]="CONDITIONAL_THREE_DECLARED_CHILD_INTERVAL_OVERLAP_ONLY" if low<=high else "DECLARED_CHILD_INTERVALS_DO_NOT_OVERLAP"
    if low<=high:result["declared_intersection"]=[str(low),str(high)]
    return result

def audit():
    doc=read(CONTRACT);audit_sources(doc)
    article=ARTICLE.read_text(encoding="utf-8")
    require(len(article)>8500 and
            all(t in article for t in ("F01","第18课","第78课","第81课",
               "第35课","第38课","条件性不可判定","源码","已完成次级走势",
               "NOT_RUN","前缀","反向线段","正式结论")),
            "Long-form whole-book bridge and findings missing")
    return {"status":"F01_TYPED_AUTHOR_COMPLETION_OBLIGATIONS_AUDITED_STILL_OPEN",
            "author_source_claims":len(doc["source_claims"]),
            "distinct_observation_types":len(doc["types"]),
            "nonimplication_barriers":len(doc["nonimplications"]),
            "actual_finished_lower_trajectories_certified":0,
            "parent_centers_author_certified":0,
            "universal_prefix_completion_proven":False,
            "real_market":"NOT_RUN"}

if __name__=="__main__":
    print(json.dumps(audit(),ensure_ascii=False,sort_keys=True))
