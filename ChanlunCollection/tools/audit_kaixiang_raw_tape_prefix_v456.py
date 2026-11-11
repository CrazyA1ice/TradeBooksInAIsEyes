#!/usr/bin/env python3
"""Frozen synthetic raw-price *prefix* replay into F01 necessary conditions.

v4.55 built its 27 raw leaves from predeclared bounds and direction. This tool
does the reverse for a deliberately tiny, closed 27-price SYNTHETIC tape:
  source prices -> consecutive equal-price triples -> initial center direction
  -> Nth center nonadvance -> local candidate -> compare to v4.55 receipt graph.
A local three-center candidate is visible on the ninth point. The v4.55
declared exit receipt is later (one tick), *without independent exit proof*.
Hashes pin a repository-controlled synthetic example, not exchange provenance.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ORIGIN="SYNTHETIC_SYMBOLS_NOT_MARKET"
PIN_SHA256="66c2a568a1ec4c0da664c5bbdeb5bd41e9ddcfccc5dbfbdaa961f916ae0f57eb"
EXPECTED_LENGTH=27
ID="KX-RAW-TAPE-PREFIX-DERIVED-THREE-CENTER-V456"


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError("v4.55 audited gate missing")
    m=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=m
    spec.loader.exec_module(m)
    return m


previous=load("kx_v456_preceding",ROOT/"tools/audit_kaixiang_f01_direction_three_centers.py")


def need(ok,reason):
    if not ok:
        raise ValueError("KX_TAPE: "+reason)


def price(value):
    need(type(value) is str and value, "raw prices must be canonical strings")
    try:
        d=Decimal(value)
    except (InvalidOperation,ValueError):
        raise ValueError("KX_TAPE: invalid decimal price") from None
    need(d.is_finite() and d>0 and str(d)==value,
         "nonpositive, nonfinite or noncanonical decimal price")
    return d


def digest(values):
    need(isinstance(values,list) and all(type(x) is str for x in values),
         "raw source must be list of strings")
    return hashlib.sha256(json.dumps(
        values,ensure_ascii=False,separators=(",",":")
    ).encode("utf-8")).hexdigest()


def validate_full_tape(fixture):
    need(fixture.get("schema_version")==1
         and fixture.get("id")==ID and fixture.get("origin")==ORIGIN,
         "frozen synthetic fixture identity")
    values=fixture.get("raw_prices")
    need(isinstance(values,list) and len(values)==EXPECTED_LENGTH,
         "frozen tape must contain exactly 27 synthetic prices")
    for p in values:price(p)
    actual=digest(values)
    need(fixture.get("raw_tape_sha256")==PIN_SHA256 and actual==PIN_SHA256,
         "synthetic tape digest does not match independent code pin")
    need(fixture.get("source_authentication")=="UNVERIFIED_REPOSITORY_SYNTHETIC",
         "no source-authentication promotion allowed")
    need(fixture.get("first_known_policy")=="PRICE_AT_ORDINAL_EXIT_DECLARATION_AT_NEXT_TICK",
         "synthetic time policy changed")
    return actual


def prefix_replay(values,asof_tick):
    """Read only prices available through asof_tick; never touch future items."""
    need(type(asof_tick) is int and asof_tick>=0,"asof integer tick required")
    need(isinstance(values,list),"raw price list required")
    seen=values[:min(len(values),asof_tick)]
    parsed=[price(x) for x in seen] # DO NOT read/validate future tape here.
    completed_groups=min(len(parsed)//9,3)
    rows=[]
    for i in range(completed_groups):
        g=parsed[9*i:9*i+9]
        need(all(g[3*j]==g[3*j+1]==g[3*j+2] for j in range(3)),
             "consecutive three-equal-price center violated")
        c1,c2,c3=g[0],g[3],g[6]
        need(c1!=c2,"initial up/down direction not identifiable")
        direction="DOWN" if c2<c1 else "UP"
        condition=(c3>=c2) if direction=="DOWN" else (c3<=c2)
        need(condition,"third center still advances trend; no local nonadvance")
        rows.append({
            "ordinal_member":i+1,"raw_ordinal_end":9*(i+1),
            "first_price_known_tick":9*(i+1),
            "direction_from_raw":direction,"first_center":str(c1),
            "second_center":str(c2),"third_center":str(c3),
            "range_low":str(min(c1,c2,c3)),"range_high":str(max(c1,c2,c3)),
            "local_nonadvance_price_test":True,
            "declared_exit_first_known_tick":9*(i+1)+1,
            "actual_exit_independently_proven":False,
        })
    return {
        "asof_tick":asof_tick,
        "observed_price_count":len(parsed),
        "local_three_center_patterns":rows,
        "local_pattern_count":len(rows),
        "declared_exit_receipt_count":sum(
            x["declared_exit_first_known_tick"]<=asof_tick for x in rows),
        "completed_movement_independently_certified":False,
        "real_market_data":False,
    }


def verify_graph_tape(witness, values):
    """Separate fail-closed source-to-graph root matching, with no market claim."""
    need(isinstance(witness,dict) and isinstance(witness.get("graph"),dict),
         "untrusted graph object required")
    need(isinstance(values,list) and len(values)==EXPECTED_LENGTH,
         "exactly 27 input prices required")
    raw=sorted(
        (x for x in witness["graph"]["nodes"] if x["kind"]=="RAW_TRADE"),
        key=lambda x:x["ordinal"])
    need(len(raw)==EXPECTED_LENGTH and
         [x["ordinal"] for x in raw]==list(range(1,EXPECTED_LENGTH+1)),
         "graph raw trade sequence has missing, repeated or extra ordinals")
    for ix,(rec,v) in enumerate(zip(raw,values),1):
        need(rec["price"]==v and rec["first_known_seq"]==ix
             and rec["historical_endpoint_seq"]==ix
             and rec["root_verified"] is False
             and rec["stream_id"]=="SYNTHETIC_UNVERIFIED_STREAM",
             "F01 graph leaf disagrees with full input tape and untrusted provenance")
    return True


def derive_graph(fixture):
    """Build *untrusted* F01 graph from tape-derived facts, not declared labels."""
    validate_full_tape(fixture)
    values=fixture["raw_prices"]
    completed=prefix_replay(values,EXPECTED_LENGTH)["local_three_center_patterns"]
    need(len(completed)==3, "all three synthetic member patterns required")
    labels={x["direction_from_raw"] for x in completed}
    need(len(labels)==1,"only single-direction 3-member demonstration supported")
    base=json.loads((ROOT/"tests/fixtures/kaixiang_f01_direction_three_centers_v455.json").read_text(encoding="utf-8"))
    need(fixture.get("source_case_id")==base["source_case_id"]
         and fixture.get("source_answer_ids")==base["source_answer_ids"]
         and fixture.get("policy_id")==base["policy_id"],
         "source case A-index or frozen policy mismatch")
    # These are OBSERVABLE comparison checks. The old labels are not a source.
    labels=labels.pop()
    inferred_bounds=[[x["range_low"],x["range_high"]] for x in completed]
    need(labels==base["direction"] and inferred_bounds==base["price_bounds"],
         "tape-derived answer contradicts previous declared research assumptions")
    args=dict(base)
    args["direction"]=labels
    args["price_bounds"]=inferred_bounds
    witness=previous.generate(args)
    # This checks the real audited graph-root-to-raw-array binding.
    verify_graph_tape(witness,values)
    return witness


def replay_at(fixture,asof_tick):
    """Only as-of source computation; whole-file pinning is separate offline."""
    return prefix_replay(fixture["raw_prices"],asof_tick)


def audit_fixture(path):
    fixture=json.loads(Path(path).read_text(encoding="utf-8"))
    validate_full_tape(fixture)
    witness=derive_graph(fixture)
    cand=json.loads((ROOT/"tests/fixtures/kaixiang_asof_symbolic_v452.json").read_text(encoding="utf-8"))
    candidate=next(x for x in cand["cases"] if x["id"]==fixture["source_case_id"])
    old=json.loads((ROOT/"tests/fixtures/kaixiang_center_asof_bridge_v453.json").read_text(encoding="utf-8"))
    center=next(x for x in old["bridge_cases"] if x["source_case_id"]==candidate["id"])
    ticks=fixture.get("checkpoints")
    need(ticks==[8,9,10,17,18,19,27,28],"fixed observation checkpoints changed")
    rows=[]
    for t in ticks:
        local=replay_at(fixture,t)
        graph=previous.evaluate(witness,candidate,center,t)
        need(len(graph["visible_members"])==local["declared_exit_receipt_count"],
             "graph completion claim not aligned with prefix local observations")
        need(graph["movement_completion_certified"] is False
             and graph["third_buy_certified"] is False
             and graph["market_data_used"] is False,
             "graph promoted self-declared completion to verified reality")
        rows.append(local)
    need([r["local_pattern_count"] for r in rows]==[0,1,1,1,2,2,3,3]
         and [r["declared_exit_receipt_count"] for r in rows]==[0,0,1,1,1,2,2,3],
         "pattern recognition and future declared exit were conflated")
    return {
        "status":"RAW_SYNTHETIC_TAPE_PREFIX_DERIVED_NOT_MARKET",
        "source_digest_valid":True,
        "raw_trades":len(fixture["raw_prices"]),
        "f01_graph_nodes":len(witness["graph"]["nodes"]),
        "checked_prefixes":len(rows),
        "local_pattern_counts":[r["local_pattern_count"] for r in rows],
        "unverified_exit_receipt_counts":[r["declared_exit_receipt_count"] for r in rows],
        "real_market_verified":False,
        "actual_movement_completion_certified":False,
        "third_buy_certified":False,
        "orders":0,
    }


if __name__=="__main__":
    print(json.dumps(audit_fixture(
        ROOT/"tests/fixtures/kaixiang_raw_tape_v456.json"),
        ensure_ascii=False,indent=2))
