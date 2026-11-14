#!/usr/bin/env python3
"""M52 finite closed-interval logic; synthetic declarations only, no full Chanlun parser."""
import json
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / "catalog/chanlun_l20_l35_finite_z_envelope_bridge_m52.json"
ID = "CL20-L35-FINITE-Z-ENVELOPE-M52"

def overlap(a,b):
    lo,hi=max(a[0],b[0]),min(a[1],b[1])
    return [lo,hi] if lo<=hi else None

def hull(z):
    return [min(a["lo"] for a in z),max(a["hi"] for a in z)]

def check(case):
    a,b,t=case["left"],case["right"],case["asof"]
    if a["id"]==b["id"]:return {"status":"DUPLICATE_CENTER_ID"}
    if a["rule"]!=b["rule"]:return {"status":"RULE_MISMATCH"}
    for c in (a,b):
        z=c["z"]
        if len(z)<2 or any(x["lo"]>x["hi"] for x in z):return {"status":"INVALID_INTERVAL"}
        if any(x["known_at"]>t for x in z):return {"status":"PENDING_ASOF"}
        if overlap([z[0]["lo"],z[0]["hi"]],[z[1]["lo"],z[1]["hi"]])!=c["core"]:
            return {"status":"BAD_SEED_CORE"}
        if any(overlap([x["lo"],x["hi"]],c["core"]) is None for x in z[2:]):
            return {"status":"INVALID_EXTENSION_MEMBER"}
    outer=overlap(hull(a["z"]),hull(b["z"]))
    pair=any(overlap([x["lo"],x["hi"]],[y["lo"],y["hi"]]) is not None
             for x in a["z"] for y in b["z"])
    if (outer is not None)!=pair:raise AssertionError("Qualified finite union lemma violated")
    return {"status":"MATH_ONLY","left_hull":hull(a["z"]),"right_hull":hull(b["z"]),
            "overlap":outer,"has_pair":pair,"higher_center_authenticated":False,
            "completed_higher_movements_authenticated":False,"market_data":False}

def audit(doc):
    if doc["id"]!=ID:raise ValueError("source contract changed")
    for c in doc["cases"]:
        result=check(c)
        for k,v in c["expected"].items():
            if result.get(k)!=v:raise AssertionError(f'{c["id"]}: {k} {result.get(k)} != {v}')
        if result.get("higher_center_authenticated"):raise AssertionError("Unauthorized center claim")
    return {"id":ID,"cases":len(doc["cases"]),"all_passed":True,"market_data":False}

if __name__=="__main__":
    print(json.dumps(audit(json.loads(CATALOG.read_text(encoding="utf-8"))),indent=2))
