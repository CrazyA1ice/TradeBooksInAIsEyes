#!/usr/bin/env python3
"""Synthetic-only append-only structure events and *local* feature-sequence gates.

V2 extends the V1 read-only closed-bar/known-at semantics. No full pen or
segment parser, orders, returns, or claims of real-market validation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from decimal import Decimal

from chanlun_event_lab_v1 import ClosedBar, dec, dt, replay, normalize, fractals, pair_gates, included

ROOT=Path(__file__).resolve().parents[1]
KIND="synthetic_non_market_fixture"
RESEARCH_SCOPE="prefix_local_revisable_structures_and_feature_necessary_gates_only"
VALID_EVENTS={"OPEN","REVISE","RETRACT","REOPEN"}

def canonical(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(",",":"))

def digest(x):
    return hashlib.sha256(canonical(x).encode("utf-8")).hexdigest()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def _fractal_candidates(bars, direction, version_id):
    """An identity is tied to raw center provenance, not shifting merged index."""
    merged=normalize(bars,direction)
    fs=fractals(merged)
    out={}
    for f in fs:
        center=merged[f.center]
        witness=merged[f.center-1:f.center+2]
        object_id="F-"+digest({"symbol":bars[0].symbol,"timeframe":bars[0].timeframe,
                              "source_revision_sha256":bars[0].source_revision_sha256,
                              "direction":direction,"center_raw_keys":center.keys,"kind":f.kind})[:24]
        out[object_id]={"object_kind":"FRACTAL_CANDIDATE","kind":f.kind,
                        "center_raw_keys":list(center.keys),"center_normalized_index":f.center,
                        "extreme":str(f.extreme),
                        "extremum_known_at":center.known_at.isoformat(),
                        "evidence_known_at":f.available_at.isoformat(),
                        "witness_raw_keys":[list(m.keys) for m in witness],
                        "witness_intervals":[[str(m.low),str(m.high)] for m in witness],
                        "status":"PREFIX_LOCAL_REVISABLE"}
    # Pen pairs depend on the identities of their two local fractal candidates,
    # never on an assumed finalized pen extraction.
    p={}
    if version_id is None:
        return out
    identifiers={tuple(merged[f.center].keys):"F-"+digest({
        "symbol":bars[0].symbol,"timeframe":bars[0].timeframe,
        "source_revision_sha256":bars[0].source_revision_sha256,
        "direction":direction,"center_raw_keys":merged[f.center].keys,"kind":f.kind})[:24] for f in fs}
    candidates=pair_gates(fs,merged,version_id["mode"])
    for index, pair in enumerate(candidates):
        left,right=fs[index:index+2]
        left_id=identifiers[tuple(merged[left.center].keys)]
        right_id=identifiers[tuple(merged[right.center].keys)]
        object_id="P-"+digest({"left":left_id,"right":right_id,"rule_version":version_id["version_id"]})[:24]
        p[object_id]={"object_kind":"PEN_NECESSARY_GATE","left_fractal_id":left_id,
                      "right_fractal_id":right_id,"status":pair["status"],
                      "rule_version_id":version_id["version_id"],"rule_mode":version_id["mode"],
                      "evidence_known_at":max(left.available_at,right.available_at).isoformat(),
                      "trade_signal":False,"complete_pen":False}
    out.update(p)
    return out

def event_history(raw_bars, *, data_kind, direction, rule_pin=None, registry=None, stop_at=None):
    """Recompute each CLOSED contiguous prefix; emit immutable deltas.

    Future suffixes are not read into earlier prefix snapshots. Availability
    must be monotone; pending/incomplete suffix is never skipped.
    """
    require(data_kind==KIND,"Only explicitly synthetic input allowed")
    require(direction in ("UP","DOWN"),"Fixed direction required")
    require(isinstance(raw_bars,list) and bool(raw_bars),"Nonempty market bar list")
    until=dt(stop_at) if stop_at is not None else None
    parsed=[ClosedBar.parse(b) for b in raw_bars]
    # Preserve V1's whole-stream validation (duplicate keys, gaps, mixed source,
    # overlapping bars, and nonmonotone known-at).
    # V1 replay is allowed to see syntactic future data but its visible results
    # only use contiguous already completed+known source prefixes.
    replay(raw_bars,data_kind=data_kind,market_asof=parsed[0].known,
           direction=direction,rule_pin=rule_pin,registry=registry)
    events=[]
    previous_active={}
    last_event={}
    prefixes=[]
    for index, bar in enumerate(parsed):
        if not bar.is_closed:
            break
        asof=max(bar.end,bar.known)
        if until is not None and asof>until:
            break
        # Validate the full prefix for every step. No later raw bars contribute.
        old_snapshot=replay(raw_bars[:index+1],data_kind=data_kind,
                            market_asof=asof,direction=direction,
                            rule_pin=rule_pin,registry=registry)
        require(old_snapshot["visible_closed_bars"]==index+1,
                "Internal market prefix failed to close")
        pin=old_snapshot["rule"]
        if pin["state"]=="RESEARCH_RULE_PINNED":
            pin_version={"mode":pin["mode"],"version_id":pin["version_id"]}
        else:
            pin_version=None
        present=_fractal_candidates(parsed[:index+1],direction,pin_version)
        # Freeze observation order; all retractions are emitted at their actual
        # new observation time, without changing earlier event entries.
        for ident in sorted(previous_active.keys()-present.keys()):
            prior=last_event[ident]
            payload=previous_active[ident]
            _append(events,last_event,ident,"RETRACT",payload,asof,old_snapshot["visible_prefix_digest_sha256"],
                    reason="NO_LONGER_PRESENT_IN_OBSERVED_PREFIX")
        for ident in sorted(present):
            payload=present[ident]
            if ident not in last_event:
                action="OPEN"
            elif last_event[ident]["action"]=="RETRACT":
                action="REOPEN"
            elif last_event[ident]["payload"]!=payload:
                action="REVISE"
            else:
                continue
            _append(events,last_event,ident,action,payload,asof,old_snapshot["visible_prefix_digest_sha256"])
        previous_active=present
        prefixes.append({"observed_at":asof.isoformat(),"visible_closed_bars":index+1,
                         "visible_prefix_digest_sha256":old_snapshot["visible_prefix_digest_sha256"],
                         "active_fractals":sum(x["object_kind"]=="FRACTAL_CANDIDATE" for x in present.values()),
                         "active_pen_necessary_gates":sum(x["object_kind"]=="PEN_NECESSARY_GATE" for x in present.values())})
    if until is not None:
        # We do not synthesize extra events at stop_at; most recent known state
        # remains unchanged between completed/observable inputs.
        pass
    report={"schema_version":2,"data_kind":KIND,"direction_experiment":direction,
            "source_revision_sha256":parsed[0].source_revision_sha256,
            "symbol":parsed[0].symbol,"timeframe":parsed[0].timeframe,
            "scope":RESEARCH_SCOPE,"events":events,"prefixes":prefixes,
            "active_objects":[{"id":ident,"payload":payload} for ident,payload in sorted(previous_active.items())],
            "full_pen_parser":False,"full_segment_parser":False,
            "full_center_parser":False,"orders_sent":False,"real_market_backtest":False}
    validate_ledger(report)
    return report

def _append(events,last,ident,action,payload,clock,prefix_hash,reason=None):
    old=last.get(ident)
    n=1 if old is None else old["revision"]+1
    entry={"ordinal":len(events)+1,"object_id":ident,"object_kind":payload["object_kind"],
           "action":action,"revision":n,"supersedes_event_id":old["event_id"] if old else None,
           "observed_at":clock.isoformat(),"prefix_digest_sha256":prefix_hash,
           "payload":json.loads(canonical(payload))}
    if reason:
        entry["reason"]=reason
    entry["event_id"]="EV-"+digest(entry)
    events.append(entry)
    last[ident]=entry

def validate_ledger(report):
    previous_clock=None
    latest={}
    active={}
    for e in report["events"]:
        require(e["action"] in VALID_EVENTS,"Unknown event action")
        require(e["ordinal"]==len(latest.get("_ordinals",[]))+1 if False else e["ordinal"]>=1,
                "Invalid ordinal")  # exact sequential check below
    for ordinal,e in enumerate(report["events"],1):
        require(e["ordinal"]==ordinal,"Nonsequential event ordinal")
        require(e["event_id"]=="EV-"+digest({k:v for k,v in e.items() if k!="event_id"}),
                "Event digest tampering")
        clock=dt(e["observed_at"])
        require(previous_clock is None or clock>=previous_clock,"Event time went backwards")
        previous_clock=clock
        old=latest.get(e["object_id"])
        require(e["revision"]==(1 if old is None else old["revision"]+1),"Revision discontinuity")
        require(e["supersedes_event_id"]==(None if old is None else old["event_id"]),
                "Event chain broken")
        if e["action"]=="OPEN":
            require(old is None,"Duplicate OPEN instead of REOPEN/REVISE")
        elif e["action"]=="REOPEN":
            require(old is not None and old["action"]=="RETRACT","REOPEN without prior retract")
        elif e["action"]=="REVISE":
            require(old is not None and old["action"] in ("OPEN","REOPEN","REVISE"),
                    "REVISE without active object")
            require(old["payload"]!=e["payload"],"Non-substantive revision")
        elif e["action"]=="RETRACT":
            require(old is not None and old["action"] in ("OPEN","REOPEN","REVISE"),
                    "RETRACT without active object")
        require(dt(e["payload"]["evidence_known_at"])<=clock,
                "Structure evidence from future used in ledger")
        latest[e["object_id"]]=e
        if e["action"]=="RETRACT":
            active.pop(e["object_id"],None)
        else:
            active[e["object_id"]]=e["payload"]
    require(report["active_objects"]==[{"id":k,"payload":v} for k,v in sorted(active.items())],
            "Final active snapshot not reproducible from immutable ledger")
    return True

def feature_record(raw):
    required={"key","sequence_id","role","index","low","high","completed_at"}
    require(isinstance(raw,dict) and set(raw)==required,"Strict typed feature fields required")
    require(raw["role"] in ("STRICT","AUXILIARY","UNDETERMINED"),"Bad membership role")
    require(isinstance(raw["sequence_id"],str) and raw["sequence_id"].strip(),"Bad sequence identity")
    require(isinstance(raw["key"],str) and raw["key"].strip(),"Bad feature identity")
    require(type(raw["index"]) is int and raw["index"]>=0,"Bad feature index")
    low,high=dec(raw["low"]),dec(raw["high"])
    require(low<=high,"Invalid feature bounds")
    return {"key":raw["key"],"sequence_id":raw["sequence_id"],"role":raw["role"],
            "index":raw["index"],"low":low,"high":high,"completed_at":dt(raw["completed_at"])}

def feature_containment(a,b):
    x,y=feature_record(a),feature_record(b)
    if x["role"]!="STRICT" or y["role"]!="STRICT":
        return "BLOCKED_NON_STRICT_MEMBERSHIP"
    if x["sequence_id"]!=y["sequence_id"]:
        return "BLOCKED_CROSS_SEQUENCE"
    return "LOCAL_CONTAINMENT_ELIGIBLE" if (
        (x["low"]<=y["low"] and x["high"]>=y["high"]) or
        (y["low"]<=x["low"] and y["high"]>=x["high"])) else "NOT_CONTAINING"

def feature_three_gate(main_three, *, expected, asof, opposite_three=None):
    """Typed necessary feature-fractal gate, no inferred pen or segment stream.

    All feature inputs must be independently verified synthetic completed
    elements. For gap case require THREE complete opposite STRICT elements with
    the opposite fractal, not caller-supplied boolean confirmation.
    """
    now=dt(asof)
    require(expected in ("TOP","BOTTOM"),"Expected feature fractal must be TOP/BOTTOM")
    require(isinstance(main_three,list) and len(main_three)==3,"Exactly three main features required")
    a,b,c=[feature_record(x) for x in main_three]
    keys=[x["key"] for x in (a,b,c)]
    require(len(set(keys))==3,"Duplicate feature key")
    require(a["index"]<b["index"]<c["index"],"Feature indices not in order")
    require(a["completed_at"]<=b["completed_at"]<=c["completed_at"],"Feature completion time not ordered")
    require(len({x["sequence_id"] for x in (a,b,c)})==1,"Mixed feature sequence")
    if any(x["role"]!="STRICT" for x in (a,b,c)):
        return {"status":"BLOCKED_NON_STRICT_MEMBERSHIP","confirmed_at":None,
                "full_segment_parser":False,"orders_sent":False}
    if c["completed_at"]>now:
        return {"status":"PENDING_THIRD_COMPLETED_FEATURE","confirmed_at":None,
                "full_segment_parser":False,"orders_sent":False}
    top=b["low"]>a["low"] and b["low"]>c["low"] and b["high"]>a["high"] and b["high"]>c["high"]
    bottom=b["low"]<a["low"] and b["low"]<c["low"] and b["high"]<a["high"] and b["high"]<c["high"]
    if not (top if expected=="TOP" else bottom):
        return {"status":"NOT_EXPECTED_STRICT_FRACTAL","confirmed_at":None,
                "full_segment_parser":False,"orders_sent":False}
    gap=max(a["low"],b["low"])>min(a["high"],b["high"])
    result={"status":"LOCAL_NO_GAP_CONDITION_PASSED_NECESSARY_ONLY" if not gap else "PENDING_OPPOSITE_THREE_FEATURES",
            "candidate_extremum_key":b["key"],"candidate_extremum_completed_at":b["completed_at"].isoformat(),
            "gap_first_second":gap,"confirmed_at":c["completed_at"].isoformat() if not gap else None,
            "full_segment_parser":False,"orders_sent":False}
    if not gap or opposite_three is None:
        return result
    require(isinstance(opposite_three,list) and len(opposite_three)==3,"Opposite proof requires three features")
    x,y,z=[feature_record(item) for item in opposite_three]
    require(len({p["key"] for p in (x,y,z)})==3 and not set(keys)&{x["key"],y["key"],z["key"]},
            "Opposite witness not independent")
    require(x["index"]<y["index"]<z["index"] and x["completed_at"]<=y["completed_at"]<=z["completed_at"],
            "Opposite sequence order invalid")
    require(len({p["sequence_id"] for p in (x,y,z)})==1 and x["sequence_id"]!=a["sequence_id"],
            "Opposite sequence must be distinct")
    require(all(p["role"]=="STRICT" for p in (x,y,z)),"Opposite proof includes auxiliary feature")
    require(x["completed_at"]>c["completed_at"],"Opposite proof not later than main three")
    if z["completed_at"]>now:
        return result
    opposite_top=y["low"]>x["low"] and y["low"]>z["low"] and y["high"]>x["high"] and y["high"]>z["high"]
    opposite_bottom=y["low"]<x["low"] and y["low"]<z["low"] and y["high"]<x["high"] and y["high"]<z["high"]
    if not (opposite_bottom if expected=="TOP" else opposite_top):
        return result
    result.update(status="LOCAL_GAP_CONDITION_PASSED_NECESSARY_ONLY",confirmed_at=z["completed_at"].isoformat(),
                  opposite_witness_keys=[x["key"],y["key"],z["key"]])
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fixture",default="experiments/fixtures/chanlun_prefix_synthetic_v1.json")
    p.add_argument("--direction",choices=("UP","DOWN"),default="UP")
    p.add_argument("--rule",choices=("pen_077_exposition","pen_081_later_dated_post"))
    p.add_argument("--attested-known-at")
    p.add_argument("--proof-ref")
    p.add_argument("--stop-at",help="Explicit offset-aware timestamp")
    args=p.parse_args()
    require(bool(args.rule)==(args.attested_known_at is not None and args.proof_ref is not None),
            "Provide all or none of rule and availability proof")
    fixture=json.loads((ROOT/args.fixture).read_text(encoding="utf8"))
    pin={"version_id":args.rule,"attested_known_at":args.attested_known_at,
         "proof_ref":args.proof_ref,"proof_kind":"synthetic_fixture"} if args.rule else None
    result=event_history(fixture["bars"],data_kind=fixture["kind"],direction=args.direction,
                         rule_pin=pin,stop_at=args.stop_at)
    summary={"status":"PASS_SYNTHETIC_IMMUTABLE_EVENTS",
             "processed_closed_prefixes":len(result["prefixes"]),
             "events":len(result["events"]),
             "event_action_counts":{action:sum(e["action"]==action for e in result["events"])
                                    for action in sorted(VALID_EVENTS)},
             "last_active_objects":len(result["active_objects"]),
             "ledger_sha256":digest(result["events"]),
             "full_pen_parser":False,"full_segment_parser":False,"orders_sent":False}
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True))
if __name__=="__main__":main()
