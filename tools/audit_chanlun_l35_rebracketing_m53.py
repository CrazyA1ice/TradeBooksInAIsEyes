#!/usr/bin/env python3
"""M53 source-anchored a+B+b rebracketing: arithmetic only, NOT real Chanlun authentication."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"catalog/chanlun_l35_rebracketing_monotonicity_m53.json"
ID="CL35-A-B-B-REBRACKETED-RANGE-MONOTONICITY-M53"
ORDER=("a","B1","B2","B3","b")

def overlap(a,b):
    if a is None or b is None:
        return None
    lo,hi=max(a[0],b[0]),min(a[1],b[1])
    return [lo,hi] if lo<=hi else None

def envelope(a,b):
    return [min(a[0],b[0]),max(a[1],b[1])]

def subset(a,b):
    if a is None:
        return True
    return b is not None and b[0]<=a[0] and a[1]<=b[1]

def assess(case):
    parts=case["parts"]
    if len(parts)!=5 or tuple(p["id"] for p in parts)!=ORDER:
        return {"status":"PART_ID_INVALID_OR_DUPLICATE"}
    if tuple(p["ordinal"] for p in parts)!=tuple(range(5)):
        return {"status":"PART_ORDER_INVALID"}
    if len({p["source"] for p in parts})!=1:
        return {"status":"SOURCE_ID_MISMATCH"}
    if len({p["rule"] for p in parts})!=1:
        return {"status":"R_POLICY_MISMATCH"}
    if any(p["known_at"]>case["asof"] for p in parts):
        return {"status":"PENDING_FIRST_KNOWN_NO_FUTURE_LEAK"}
    if any(not p["external_complete_declared"] for p in parts):
        return {"status":"COMPONENT_COMPLETION_NOT_EVEN_DECLARED"}
    if any(p["low"]>p["high"] for p in parts):
        return {"status":"INVALID_CLOSED_INTERVAL"}
    a,b1,b2,b3,b=([p["low"],p["high"]] for p in parts)
    raw=overlap(overlap(b1,b2),b3)
    g1,g2,g3=envelope(a,b1),b2,envelope(b3,b)
    grouped=overlap(overlap(g1,g2),g3)
    if not subset(raw,grouped):
        raise AssertionError("Raw triple must be a subset of rebracketed triple")
    return {
        "status":"ARITHMETIC_ONLY_GROUP_MEMBERS_UNVERIFIED",
        "raw_intersection":raw,
        "grouped_intersection":grouped,
        "strictly_wider":grouped!=raw,
        "group_ranges":[g1,g2,g3],
        "author_level_movement_completed":False,
        "L20_two_center_Phi_authenticated":False,
        "higher_center_authenticated":False,
        "real_market_used":False,
    }

def audit(doc):
    if doc.get("schema_version")!=1 or doc.get("id")!=ID:
        raise ValueError("M53 contract identity mismatch")
    rows=[]
    for c in doc["cases"]:
        out=assess(c)
        for k,v in c["expected"].items():
            if out.get(k)!=v:
                raise AssertionError(f'{c["id"]} {k}: {out.get(k)!r} != {v!r}')
        if any(out.get(k) for k in ("author_level_movement_completed","L20_two_center_Phi_authenticated","higher_center_authenticated","real_market_used")):
            raise AssertionError(f'{c["id"]}: prohibited certification')
        rows.append({"case":c["id"],"status":out["status"]})
    return {"id":ID,"cases":len(rows),"verified":True,"data_kind":"SYNTHETIC_RANGE_MATH","results":rows}

if __name__=="__main__":
    print(json.dumps(audit(json.loads(CATALOG.read_text(encoding="utf-8"))),ensure_ascii=False,indent=2))
