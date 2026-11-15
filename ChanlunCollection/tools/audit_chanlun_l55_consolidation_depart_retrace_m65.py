#!/usr/bin/env python3
"""M65 source-only third-point admissibility gate; NOT a Chanlun parser or market signal."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"catalog/chanlun_l55_consolidation_depart_retrace_m65.json"
TYPES={"CONSOLIDATION","TREND","UNKNOWN"}
RELS={"OUTSIDE","NO_DEPARTURE","UNKNOWN"}
RET={"OUTSIDE","INSIDE","BOUNDARY_TOUCH","UNKNOWN"}
COMPLETIONS={"COMPLETE","INCOMPLETE","UNKNOWN"}

def audit(c):
    """All positive outcomes are research-only hypothetical candidate status."""
    if c.get("origin")!="SYNTHETIC_SOURCE_CONDITIONAL_NOT_MARKET":
        return "REJECT_SOURCE_GRADE"
    if c.get("market_verified") is not False or c.get("orders_sent") != 0:
        return "REJECT_FORGED_MARKET_CERTIFICATION"
    if c.get("child_type_departure") not in TYPES or c.get("child_type_retrace") not in TYPES:
        return "REJECT_INVALID_CHILD_TYPE"
    if c.get("departure_relation") not in RELS or c.get("retrace_relation") not in RET:
        return "REJECT_INVALID_RELATION"
    if c.get("child_completion_departure") not in COMPLETIONS or c.get("child_completion_retrace") not in COMPLETIONS:
        return "REJECT_INVALID_COMPLETION_GRADE"
    if c.get("original_center_legal") not in (True,False,None) or c.get("composition_legal") not in (True,False,None):
        return "REJECT_INVALID_STRUCTURAL_GRADE"
    if c.get("prior_completed_external_retrace") not in (True,False,None):
        return "REJECT_INVALID_FIRST_RETRACE_ROLE"
    if c.get("known_asof") not in (True,False):
        return "REJECT_INVALID_ASOF_FLAG"
    if c["departure_relation"]=="NO_DEPARTURE":
        return "REJECT_NO_DEPARTURE"
    if c["retrace_relation"]=="INSIDE":
        return "REJECT_INTERIOR_RETRACE_IS_OSCILLATION"
    if c["prior_completed_external_retrace"] is True:
        return "REJECT_NOT_FIRST_EXTERNAL_RETRACE"
    if c["retrace_relation"]=="BOUNDARY_TOUCH":
        return "PENDING_BOUNDARY_TOUCH_L20_L38"
    if c["original_center_legal"] is False or c["composition_legal"] is False:
        return "REJECT_INVALID_CENTER_OR_COMPOSITION"
    if c["child_completion_departure"]=="INCOMPLETE" or c["child_completion_retrace"]=="INCOMPLETE":
        return "PENDING_NOT_YET_COMPLETED"
    if (c["departure_relation"]=="UNKNOWN" or c["retrace_relation"]=="UNKNOWN"
        or c["child_type_departure"]=="UNKNOWN" or c["child_type_retrace"]=="UNKNOWN"
        or c["child_completion_departure"]=="UNKNOWN" or c["child_completion_retrace"]=="UNKNOWN"
        or c["original_center_legal"] is None or c["composition_legal"] is None
        or c["prior_completed_external_retrace"] is None or not c["known_asof"]):
        return "PENDING_REQUIRED_RECEIPT"
    # Price outcome and lower-market-root completion remain unverified in all scenarios.
    return "SOURCE_CONDITIONAL_CANDIDATE_ONLY"

def main():
    data=json.loads(DATA.read_text(encoding="utf-8"))
    for c in data["toy_cases"]:
        result=audit(c["input"])
        if result!=c["expected"]:
            raise SystemExit(f"M65_TEST_FAIL:{c['id']} expected={c['expected']} got={result}")
    print(json.dumps({"status":"M65_SOURCE_ONLY_SYNTHETIC_CONDITIONAL_GATE_PASS",
                      "cases":len(data["toy_cases"]),
                      "market_replay":"NOT_RUN","orders_sent":0},sort_keys=True))

if __name__=="__main__":
    main()
