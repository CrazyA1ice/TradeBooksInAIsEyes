#!/usr/bin/env python3
"""M66 segment endpoint-vs-confirmation as-of gate; source-only and toy-only.

Reuses prior REAL in-repository F01 and M65 verification; never analyzes stock data,
does not authenticate historical Sina bytes and does not send orders.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.audit_chanlun_f01_root_pan_frontier_v476 import audit as f01_audit
from tools.audit_chanlun_l55_consolidation_depart_retrace_m65 import audit as m65_audit
CATALOG=ROOT/"catalog/chanlun_july11_segment_confirmation_m66.json"

def classify(case: dict) -> str:
    if case.get("source_grade")!="TOY_ARCHIVED_REPLY_TEST_ONLY":
        return "REJECT_SOURCE_GRADE"
    if case.get("market_authentication") is not False or case.get("orders_sent")!=0:
        return "REJECT_MARKET_GRADE"
    if case.get("role")!="LOWEST_LEVEL_SEGMENT":
        return "REJECT_HIGHER_LEVEL_SEGMENT_METAPHOR"
    values=[case.get(key) for key in ("endpoint_seq","preview_seq","segment_break_confirm_seq","asof_seq")]
    if any(type(v) is not int or v<0 for v in values):
        return "REJECT_CLOCK_VALUES"
    endpoint,preview,confirm,now=values
    if not endpoint<=preview<=confirm:
        return "REJECT_CLOCK_ORDER"
    if case.get("macd_used_as_formal_confirmation") is not False:
        return "REJECT_MACD_AS_FORMAL_CONFIRMATION"
    if case.get("claims_root_pan_exit") is not False:
        return "REJECT_F01_ROOT_PAN_EXIT_NOT_CERTIFIED"
    if case.get("claims_higher_movement_finished") is not False:
        return "REJECT_SEGMENT_END_IMPLIES_MOVEMENT_END"
    if now<endpoint:
        return "PENDING_EVENT_NOT_IN_PREFIX"
    if now<preview:
        return "HISTORICAL_ENDPOINT_NOT_YET_CONFIRMATION"
    if now<confirm:
        return "PREVIEW_ONLY_SEGMENT_UNCONFIRMED"
    if case.get("has_next_segment_break_receipt") is not True:
        return "PENDING_SEGMENT_BREAK_RECEIPT"
    return "HYPOTHETICAL_SEGMENT_CONFIRMED_MOVEMENT_OPEN"

def audit(doc: dict|None=None) -> dict:
    d=doc or json.loads(CATALOG.read_text(encoding="utf-8"))
    if d.get("schema_version")!=1 or d.get("id")!="CHANLUN-M66-20070711-REAL-HOST-COMMENT-PREVIEW-VS-SEGMENT-CONFIRMATION":
        raise ValueError("M66_SOURCE_SCHEMA_ID")
    h=d["author_host"]
    if h["url"]!="https://chzhshch.blog/stocks/3850points/" or h["host_article_published_at"]!="2007-07-11T15:41:38" or "NOT_LESSON64" not in h["role"]:
        raise ValueError("M66_SOURCE_HOST")
    rows=d["replies"]
    if len(rows)!=8 or len({x["id"] for x in rows})!=8:
        raise ValueError("M66_REPLY_COUNT")
    for x in rows:
        if x["host_url"]!=h["url"] or x["role"]!="ARCHIVED_AUTHOR_REPLY_WITH_QUESTION" or x["original_sina_comment_bytes_authenticated"] is not False or not h["host_article_published_at"] < x["reply_at"] or not x["question_at"] < x["reply_at"]:
            raise ValueError("M66_SOURCE_REPLY_IDENTITY")
    if {x["id"]:x["reply_at"][11:] for x in rows} != {
       "J11_155314":"15:53:14", "J11_155925":"15:59:25", "J11_160145":"16:01:45",
       "J11_160823":"16:08:23", "J11_161026":"16:10:26", "J11_161353":"16:13:53",
       "J11_163332":"16:33:32", "J11_163627":"16:36:27"}:
        raise ValueError("M66_SOURCE_CLOCKS")
    s=d["evidence_frontier"]
    if not (s["source_replies_found"]==8 and s["F01"]=="OPEN" and s["OB38"]=="OPEN" and s["OB99"]=="OPEN"
         and s["Phi20"]=="OPEN" and s["A087_second_center_formula"]=="UNKNOWN"
         and s["L54_600151_2007_minute"]=="NOT_ACQUIRED" and s["market_experiments"]=="NOT_RUN"
         and s["orders"]==0 and s["independent_original_sina_authenticated"] is False):
        raise ValueError("M66_FORGED_PROOF")
    checks=d["toy_cases"]
    if len(checks)!=18 or len({c["id"] for c in checks})!=18:
        raise ValueError("M66_TOY_COUNT")
    for c in checks:
        got=classify(c["input"])
        if got!=c["expected"]:
            raise ValueError(f"M66_TOY_FAILURE {c['id']} expected={c['expected']} got={got}")
    f=f01_audit()
    if f["status"]!="ROOT_PAN_EXIT_STILL_OPEN_NEGATIVE_REGRESSIONS_PASS" or f["root_pan_exit_certified"] is not False or f["negative_cases_rejected"]!=6:
        raise ValueError("M66_F01_UPGRADE_NOT_ALLOWED")
    last=json.loads((ROOT/d["prior_research"]["third_point_catalog"]).read_text(encoding="utf-8"))
    positive=next(x for x in last["toy_cases"] if x["id"]=="allowed_toy_consolidation_combo")
    if m65_audit(positive["input"])!="SOURCE_CONDITIONAL_CANDIDATE_ONLY":
        raise ValueError("M66_M65_SOURCE_ONLY_STRENGTH")
    return {
      "status":"M66_ARCHIVED_REPLY_SOURCE_AND_ASOF_BOUNDARY_PASS",
      "archive_replies":len(rows),"toy_cases":len(checks),
      "f01_prior_negative_cases_retained":f["negative_cases_rejected"],
      "m65_market_third_sell_certified":False,
      "root_pan_exit":"OPEN","market":"NOT_RUN","orders":0
    }

if __name__=="__main__":
    print(json.dumps(audit(),ensure_ascii=False,sort_keys=True))
