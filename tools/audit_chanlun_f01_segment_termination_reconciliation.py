#!/usr/bin/env python3
"""Integrate 67 local gap branches, 71 typed membership and 78 reversal requirement.

Deliberately a source-bounded evidence gate over synthetic PRE-STANDARDIZED
feature elements, not a full Chanlun segment/trend parser or source proof.
Import the independently audited earlier local classifiers to prevent
separate toy checks drifting out of alignment without noticing.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import audit_chanlun_lesson067_feature_gap as l67
import audit_chanlun_lesson071_typed_membership as l71
CONTRACT=ROOT/"catalog/chanlun_f01_segment_termination_reconciliation_v1.json"
FIXTURES=ROOT/"tests/fixtures/chanlun_f01_segment_termination_cases_v1.json"
ARTICLE=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_F01_SEGMENT_TERMINATION_67_71_78.md"
INDEX=ROOT/"catalog/chanlun_lesson_index.json"
HISTORY=ROOT/"catalog/chanlun_rule_history_v1.json"
UPSTREAM=ROOT/"catalog/chanlun_f01_typed_completion_obligations_v1.json"
IDENTITY="CHANLUN-F01-SEGMENT-TERMINATION-SOURCE-RECONCILIATION-V1"
SOURCE={(67,"CL67-SOURCE-1",388),(67,"CL67-SOURCE-2",388),
 (67,"CL67-SOURCE-3",388),(67,"CL67-SOURCE-4",389),
 (71,"CL71-SOURCE-1",71),(71,"CL71-SOURCE-2",71),
 (71,"CL71-SOURCE-3",71),(71,"CL71-SOURCE-4",72),
 (72,"CL72-SOURCE-4",87),(78,"CL78-SOURCE-1",174),
 (78,"CL78-SOURCE-2",175)}

def load(p):return json.loads(p.read_text(encoding="utf-8"))
def require(cond,msg):
    if not cond:raise ValueError(msg)

def audit_origins():
    c=load(CONTRACT)
    require(c.get("schema_version")==1 and c.get("id")==IDENTITY and
        c.get("scope")=="COMPILED_AUTHOR_SOURCE_LOCAL_67_71_78_ELIGIBILITY_NOT_FULL_SEGMENT_OR_LOWER_TREND_CERTIFICATE" and
        c.get("prior_contract")=="catalog/chanlun_f01_typed_completion_obligations_v1.json" and
        c.get("rule_history")=="catalog/chanlun_rule_history_v1.json",
        "Wrong original-scope contract")
    require(len(c.get("sources",[]))==len(SOURCE) and
        {(r["lesson"],r["claim_id"],r["physical_pdf_page"]) for r in c["sources"]}==SOURCE,
        "Unexpected source claims or physical pages")
    books={v["volume"]:v for v in load(INDEX)["volumes"]}
    for r in c["sources"]:
        n=r["lesson"];card=load(ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json")
        v=3 if n in (67,) else 4
        matches=[x for x in card["claims"] if x["id"]==r["claim_id"]]
        require(len(matches)==1 and matches[0]["kind"]=="SOURCE" and
          r["physical_pdf_page"] in matches[0]["pdf_pages"] and
          card["source"]["sha256"]==books[v]["sha256"] and
          card["source"]["path"]==books[v]["path"] and
          r["role"]=="SOURCE_IN_COMPILATION_NOT_INDEPENDENT_FIRST_PUBLICATION",
          "Original volume, SOURCE role or physical page disagrees")
    hist={e["id"]:e for e in load(HISTORY)["entries"]}
    for name in ("segment_067_feature_sequence","segment_067_editor_objection",
      "segment_071_typed_membership","segment_072_retrospective"):
        require(name in hist,"Unregistered original segment version")
    editor=hist["segment_067_editor_objection"]
    require(editor["source_displayed_at"] is None and
            editor["timestamp_basis"]=="unknown" and
            editor["role"]=="editor_later_undated",
            "Editor objection was improperly backdated as author source")
    require(load(UPSTREAM)["candidate_completion_certification_allowed"] is False,
            "Upstream type proof limitations erased")
    require(len(c["three_observation_gates"])==3 and
            {g["gate"] for g in c["three_observation_gates"]}==
            {"G1_STRICT_TYPED_FEATURES","G2_L67_TWO_BRANCH_END_CONDITION",
             "G3_L78_LEGAL_OPPOSITE_SEGMENT"} and
            len(c["unresolved_text_scope"])==4 and
            all(x["status"].startswith("OPEN_") for x in c["unresolved_text_scope"]),
            "Source gaps prematurely filled")
    for k in ("full_original_chart_visuals_verified",
      "unresolved_editorial_comments_backdated","complete_Rg_frozen",
      "proof_38_99_completed","actual_market_data_accessed"):
        require(c[k] is False,"Unsupported certification "+k)
    require(c["real_market_backtests"]=="NOT_RUN" and
            all(c["evaluation_roles"][k] is False for k in (
              "author_legal_segment_break_certified",
              "author_finished_lower_trend_certified","higher_level_center_eligible")),
            "A local pattern was promoted to author source/trading proof")
    return True

def gate(c):
    """Three separate gates; external reverse-segment truth cannot be forged."""
    need={"id","direction","sequence_id","as_of","features",
          "opposite_fractal","reverse_segment","source_version"}
    require(type(c) is dict and set(c)==need and
      c["direction"] in ("UP","DOWN") and c["source_version"]==
      "AUTHOR_2007_LOCAL_67_71_78_INTERPRETIVE_NOT_FULL_RULE" and
      type(c["as_of"]) is int and c["as_of"]>=0 and
      type(c["sequence_id"]) is str and c["sequence_id"],
      "Unfrozen synthetic segment research input")
    features=c["features"]
    require(type(features) is list and len(features)==3,
            "Three external pre-standardized feature descriptions required")
    for i,x in enumerate(features):
        require(type(x) is dict and set(x)=={"index","low","high",
          "sequence_id","role","confirmed_at"} and
          x["index"]==i+1 and type(x["confirmed_at"]) is int and
          x["confirmed_at"]>=x["index"] and
          x["role"] in ("STRICT","AUXILIARY","UNDETERMINED"),
          "Malformed pre-standardized feature")
        require(type(x["low"]) in (int,float) and type(x["high"]) in (int,float) and
                x["low"]<=x["high"],"Invalid synthetic range")
    for field in ("opposite_fractal","reverse_segment"):
        event=c[field]
        require(set(event)=={"externally_declared","confirmed_at"} and
          type(event["externally_declared"]) is bool and
          (event["confirmed_at"] is None or
            (type(event["confirmed_at"]) is int and event["confirmed_at"]>=0)) and
          (not event["externally_declared"] or event["confirmed_at"] is not None),
          "External evidence must remain a declared, dated assumption")
    base={"id":c["id"],"as_of":c["as_of"],
      "local_67_branch":None,"local_feature_condition_confirmed_at":None,
      "declared_reversal_seen_asof":False,
      "author_strict_segment_member_certified":False,
      "author_full_segment_end_certified":False,
      "author_finished_lower_trend_certified":False,
      "higher_center_eligible":False,"real_market":"NOT_RUN"}
    if any(x["confirmed_at"]>c["as_of"] for x in features):
        return {**base,"status":"PENDING_COMPLETED_FEATURES"}
    if any(x["sequence_id"]!=c["sequence_id"] or x["role"]!="STRICT" for x in features):
        return {**base,"status":"PENDING_STRICT_FEATURE_MEMBERSHIP"}
    for x in features:
        l71.Element(x["sequence_id"],x["role"],x["low"],x["high"],x["confirmed_at"])
    # Additional sequence typing is checked before any older 67 interval test.
    f=[l67.Feature(x["low"],x["high"],x["index"]) for x in features]
    expected="TOP" if c["direction"]=="UP" else "BOTTOM"
    local=l67.classify(f,expected)
    if local["status"] in ("NOT_EXPECTED_FRACTAL","PENDING_THREE_FEATURES"):
        return {**base,"status":"NO_SOURCE_67_LOCAL_FRACTAL_CANDIDATE"}
    require(local["status"] in ("LOCAL_END_CONDITION_NO_GAP","PENDING_OPPOSITE"),
            "Unexpected source 67 local state")
    gap=local["status"]=="PENDING_OPPOSITE"
    base["local_67_branch"]="GAP_NEEDS_OPPOSITE_FRACTAL" if gap else "NO_GAP_LOCAL_FRACTAL"
    if gap:
        opp=c["opposite_fractal"]
        if not opp["externally_declared"] or opp["confirmed_at"]>c["as_of"]:
            return {**base,"status":"PENDING_OPPOSITE_FRACTAL_ASOF"}
        require(opp["confirmed_at"]>features[-1]["index"] and
                opp["confirmed_at"]>=features[-1]["confirmed_at"],
                "Opposite fractal cannot be earlier than the local feature")
        local=l67.classify(f,expected,opposite_fractal_observed=True,
                opposite_index=opp["confirmed_at"])
    base["local_feature_condition_confirmed_at"]=local["confirmed_at"]
    reverse=c["reverse_segment"]
    if not reverse["externally_declared"] or reverse["confirmed_at"]>c["as_of"]:
        return {**base,"status":"LOCAL_67_CONDITION_ONLY_REVERSE_SEGMENT_NOT_YET_EVIDENCED"}
    require(reverse["confirmed_at"]>=local["confirmed_at"],
            "Reverse segment cannot predate the required local confirmation")
    base["declared_reversal_seen_asof"]=True
    return {**base,
      "status":"CONDITIONAL_78_REVERSE_SEGMENT_IF_EXTERNAL_LEGALITY_ACCEPTED_NOT_AUTHOR_CERTIFIED"}

def audit():
    audit_origins()
    fixtures=load(FIXTURES)
    require(fixtures["schema_version"]==1 and len(fixtures["cases"])==10,
            "Ten distinct 67/71/78 integrative cases expected")
    results=[]
    for row in fixtures["cases"]:
        x=gate(row["input"])
        require(x["status"]==row["expected_status"] and
                x["local_67_branch"]==row["expected_branch"] and
                x["local_feature_condition_confirmed_at"]==row["expected_local_at"],
                "Reconciliation countercase unexpectedly changed: "+row["input"]["id"])
        require(all(x[k] is False for k in (
             "author_full_segment_end_certified",
             "author_finished_lower_trend_certified",
             "higher_center_eligible")),
             "Synthetic local case illegally passed as completed Chanlun trend")
        results.append(x)
    s=ARTICLE.read_text(encoding="utf-8")
    require(len(s)>=8000 and
      all(t in s for t in ("第67课","第71课","第72课","第78课",
        "无缺口","有缺口","反向线段","严格成员","SOURCE",
        "EDITORIAL","未决","F01","NOT_RUN","不是完整线段解析器")),
      "Full source reconciliation argument not substantively written")
    return {"status":"L67_L71_L78_TYPED_SEGMENT_EVIDENCE_RECONCILED_F01_OPEN",
      "source_claims":len(SOURCE),"cases":len(results),
      "local_gaps":sum(x["local_67_branch"]=="GAP_NEEDS_OPPOSITE_FRACTAL" for x in results),
      "author_completed_segments":0,"author_completed_lower_trends":0,
      "unresolved_original_source_semantics":4,"market_data":"NOT_RUN"}

if __name__=="__main__":
    print(json.dumps(audit(),ensure_ascii=False,sort_keys=True))
