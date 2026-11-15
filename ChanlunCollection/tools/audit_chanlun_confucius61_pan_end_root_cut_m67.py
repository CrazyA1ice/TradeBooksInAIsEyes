#!/usr/bin/env python3
"""M67: archived 2007-04-03 author replies, scoped pan end vs unproved root exit.

This module deliberately DOES NOT identify actual market segment/movement ends.
Positive results are synthetic author-condition classifications only.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.audit_chanlun_f01_root_pan_frontier_v476 import audit as prior_f01
from tools.audit_chanlun_july11_segment_confirmation_m66 import audit as prior_m66

CATALOG=ROOT/"catalog/chanlun_confucius61_pan_end_root_cut_m67.json"

def classify(event: dict) -> str:
    if event.get("origin")!="SYNTHETIC_PAN_END_POLICY_TEST_ONLY":
        return "REJECT_SOURCE_GRADE"
    if event.get("market_verified") is not False or type(event.get("orders")) is not int or event["orders"]!=0:
        return "REJECT_FORGED_MARKET"
    if type(event.get("level")) is not int or event["level"]<0:
        return "REJECT_INVALID_LEVEL"
    if any(type(event.get(k)) is not int or event[k]<0 for k in ("known_at_seq","asof_seq")):
        return "REJECT_INVALID_CLOCK"
    for k in ("center_formed","center_terminated","child_completion_certified"):
        if event.get(k) not in (True,False,None):
            return "REJECT_INVALID_CERTIFICATE_TYPE"
    for k in ("policy_frozen","pan_divergence_only_promoted","root_third_point_without_child","claims_no_pan_any_level"):
        if type(event.get(k)) is not bool:
            return "REJECT_INVALID_POLICY_FLAG"
    if event["claims_no_pan_any_level"]:
        return "REJECT_GLOBAL_NO_PAN_PROMOTION"
    if event["pan_divergence_only_promoted"]:
        return "REJECT_PAN_DIVERGENCE_AS_SUFFICIENT"
    if event["level"]==0 and event["root_third_point_without_child"]:
        return "REJECT_ROOT_THIRD_POINT_WITHOUT_CHILD_GRAMMAR"
    if event["center_formed"] is False:
        return "REJECT_CENTER_NOT_FORMED"
    if event["center_formed"] is None:
        return "PENDING_CENTER_FORMATION_WITNESS"
    if not event["policy_frozen"]:
        return "PENDING_POLICY_FREEZE"
    if event["center_terminated"] is False:
        return "PENDING_CENTER_CONTINUES"
    if event["center_terminated"] is None:
        return "PENDING_CENTER_TERMINATION_WITNESS"
    if event["asof_seq"]<event["known_at_seq"]:
        return "PENDING_ASOF_CONFIRMATION"
    if event["level"]==0:
        return "PENDING_STRICT_ROOT_PAN_EXIT_RULE"
    if event["child_completion_certified"] is not True:
        return "PENDING_CHILD_COMPLETION"
    return "AUTHOR_CONDITIONAL_LOCAL_PAN_END_ONLY"

def audit(doc:dict|None=None)->dict:
    d=doc if doc is not None else json.loads(CATALOG.read_text(encoding="utf-8"))
    if d.get("schema_version")!=1 or d.get("id")!="CHANLUN-M67-CONFUCIUS61-PAN-END-LEVEL-SCOPE-STRICT-ROOT-CUT":
        raise ValueError("M67_BAD_CONTRACT_ID")
    host=d["source_host"]
    if host["article"]!="论语详解61" or host["original_post_at"]!="2007-04-03T15:27:02" or host["url"]!="https://chzhshch.blog/confucius/61/" or host["original_2007_sina_bytes_authenticated"] is not False:
        raise ValueError("M67_WRONG_ORIGINAL_HOST")
    replies={s["id"]:s for s in d["source_replies"]}
    if len(replies)!=2 or replies["CONFUCIUS61_155118"]["reply_at"]!="2007-04-03T15:51:18" or replies["CONFUCIUS61_155451"]["reply_at"]!="2007-04-03T15:54:51":
        raise ValueError("M67_BAD_COMMENT_CLOCK_ID")
    if (replies["CONFUCIUS61_155118"]["question_author"]!="你的样子"
        or replies["CONFUCIUS61_155451"]["question_author"]!="hehe2"):
        raise ValueError("M67_BAD_QUESTION_AUTHOR")
    for s in replies.values():
        if s["role"]!="ARCHIVED_AUTHOR_REPLY" or not host["original_post_at"]<s["reply_at"] or not s["question_at"]<s["reply_at"]:
            raise ValueError("M67_BAD_QUESTION_REPLY_ROLE")
    if d["missing_independent_witness"]["source_available"] is not False or d["missing_independent_witness"]["formal_global_impossibility_claim"] is not False:
        raise ValueError("M67_ROOT_PROOF_FABRICATED")
    status=d["status"]
    if any(status.get(k)!="OPEN" for k in ("F01","OB38","OB99","Phi20")) or status["market_experiments"]!="NOT_RUN" or status["orders"]!=0:
        raise ValueError("M67_WRONG_EVIDENCE_BOUNDARY")
    tests=d["synthetic_cases"]
    if len(tests)!=23 or len({c["id"] for c in tests})!=23:
        raise ValueError("M67_TEST_COUNT")
    for c in tests:
        if classify(c["input"])!=c["expected"]:
            raise ValueError("M67_CASE:"+c["id"]+" got "+classify(c["input"]))
    old=prior_f01()
    if old["negative_cases_rejected"]!=6 or old["root_pan_exit_certified"] is not False:
        raise ValueError("M67_PRIOR_F01_FAIL")
    m66=prior_m66()
    if m66["root_pan_exit"]!="OPEN" or m66["market"]!="NOT_RUN":
        raise ValueError("M67_M66_COMPLETION_PROMOTION")
    return {"result":"M67_SCOPED_PAN_END_SOURCE_CONTRACT_PASS",
            "author_reply_count":len(replies),"synthetic_cases":len(tests),
            "prior_f01_negative_rejections":old["negative_cases_rejected"],
            "root_pan_exit":"OPEN","market":"NOT_RUN","orders":0}

if __name__=="__main__":
    print(json.dumps(audit(),ensure_ascii=False,sort_keys=True))
