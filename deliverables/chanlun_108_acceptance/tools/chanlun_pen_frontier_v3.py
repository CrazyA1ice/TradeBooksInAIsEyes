#!/usr/bin/env python3
"""V3 synthetic-only deterministic pen *frontier* over V1/V2 causal evidence.

This is NOT a full Chanlun pen/segment implementation. Every projected feature
is UNDETERMINED: the V2 strict-member segment gate must reject it.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from chanlun_event_lab_v1 import ClosedBar, dt, fractals, normalize, pair_gates, replay
from chanlun_incremental_events_v2 import (
    KIND, _append, digest, event_history as v2_event_history, require,
    validate_ledger, feature_containment,
)

ROOT=Path(__file__).resolve().parents[1]
SCOPE="provisional_alternating_pen_frontier_not_proven_complete_pen_or_segment"

def fractal_identity(f, merged, context):
    center=merged[f.center]
    return "F-"+digest({"symbol":context["symbol"],"timeframe":context["timeframe"],
                        "source_revision_sha256":context["source_revision_sha256"],
                        "direction":context["direction"],"center_raw_keys":center.keys,
                        "kind":f.kind})[:24]

def necessary_pair(left,right,merged,mode):
    return pair_gates((left,right),merged,mode)[0]["status"]

def _candidate(left,right,merged,context,rule_version):
    old_id=fractal_identity(left,merged,context)
    new_id=fractal_identity(right,merged,context)
    cid="P3-"+digest({"from":old_id,"to":new_id,"version":rule_version})[:24]
    return cid, {"object_kind":"PROVISIONAL_PEN_FRONTIER","rule_version_id":rule_version,
                 "left_fractal_id":old_id,"right_fractal_id":new_id,
                 "direction":"UP" if left.kind=="BOTTOM" else "DOWN",
                 "from_kind":left.kind,"to_kind":right.kind,
                 "left_center_raw_keys":list(merged[left.center].keys),
                 "right_center_raw_keys":list(merged[right.center].keys),
                 "left_extreme":str(left.extreme),"right_extreme":str(right.extreme),
                 "evidence_known_at":right.available_at.isoformat(),
                 "status":"LOCAL_READY_NECESSARY_ONLY",
                 "complete_pen":False,"complete_segment":False,
                 "trade_signal":False,
                 "feature_projection":{"role":"UNDETERMINED",
                    "low":str(min(left.extreme,right.extreme)),
                    "high":str(max(left.extreme,right.extreme)),
                    "source":"provisional_pen_not_certified",
                    "known_at":right.available_at.isoformat()}}

def pen_frontier(fracs,merged,*,mode,rule_version,context):
    """Deterministic chronological *research policy*, not a theorem of unique pens.

    Opposite fractal: accept ONLY if local necessary conditions passed.
    Same kind: replace most extreme terminal if strictly more extreme.
    Ties: block the unresolved continuation instead of breaking ties using future.
    After a stronger same-kind endpoint, recheck the last pair from its prior
    anchor; never silently keep a superseded endpoint's prior pen candidate.
    """
    require(mode in ("old","revised"),"Explicit old/revised pen mode required")
    require(isinstance(rule_version,str) and bool(rule_version),"Version identity missing")
    if not fracs:
        return {"objects":{}, "decisions":[], "blocked_tie":False}
    anchor=fracs[0]
    pairs=[]
    decisions=[]
    tie=None
    for f in fracs[1:]:
        if f.kind==anchor.kind:
            if f.extreme==anchor.extreme:
                tie=(anchor,f)
                decisions.append({"decision":"TIE_BLOCKED","left_center":anchor.center,"right_center":f.center})
                break
            better=(f.extreme>anchor.extreme if f.kind=="TOP" else f.extreme<anchor.extreme)
            if better:
                if pairs and pairs[-1][1]==anchor:
                    old_left=pairs[-1][0]
                    status=necessary_pair(old_left,f,merged,mode)
                    pairs.pop()
                    decisions.append({"decision":"TERMINAL_EXTREME_REPLACED_RECHECKED",
                                      "gate":status,"new_center":f.center})
                    if status=="LOCAL_ELIGIBLE_NECESSARY_ONLY":
                        pairs.append((old_left,f))
                else:
                    decisions.append({"decision":"MORE_EXTREME_SAME_KIND","new_center":f.center})
                anchor=f
            else:
                decisions.append({"decision":"LESS_EXTREME_IGNORED","ignored_center":f.center})
            continue
        status=necessary_pair(anchor,f,merged,mode)
        if status=="LOCAL_ELIGIBLE_NECESSARY_ONLY":
            pairs.append((anchor,f))
            anchor=f
            decisions.append({"decision":"PROVISIONAL_PAIR_ADDED","from_center":pairs[-1][0].center,
                              "to_center":f.center,"gate":status})
        else:
            decisions.append({"decision":"OPPOSITE_LOCAL_GATE_NOT_PASSED","from_center":anchor.center,
                              "to_center":f.center,"gate":status})
    objects={}
    for a,b in pairs:
        cid,payload=_candidate(a,b,merged,context,rule_version)
        objects[cid]=payload
    if tie is not None:
        a,b=tie
        fid_a,fid_b=fractal_identity(a,merged,context),fractal_identity(b,merged,context)
        tie_id="T3-"+digest({"left":fid_a,"right":fid_b,"version":rule_version})[:24]
        objects[tie_id]={"object_kind":"PEN_FRONTIER_CONFLICT","status":"TIE_PENDING",
                         "left_fractal_id":fid_a,"right_fractal_id":fid_b,
                         "evidence_known_at":b.available_at.isoformat(),
                         "rule_version_id":rule_version,"complete_pen":False,
                         "trade_signal":False}
    return {"objects":objects,"decisions":decisions,"blocked_tie":tie is not None}

def replay_pen_frontier(raw_bars, *, data_kind, direction, rule_pin, stop_at=None):
    """Append-only versioned pen candidate deltas, extending V2 validated input."""
    require(data_kind==KIND,"Only synthetic fixtures accepted")
    v2=v2_event_history(raw_bars,data_kind=data_kind,direction=direction,
                        rule_pin=rule_pin,stop_at=stop_at)
    parsed=[ClosedBar.parse(x) for x in raw_bars]
    events=[]
    last={}
    active={}
    prefixes=[]
    for prefix in v2["prefixes"]:
        n=prefix["visible_closed_bars"]
        clock=dt(prefix["observed_at"])
        snap=replay(raw_bars[:n],data_kind=data_kind,market_asof=clock,
                    direction=direction,rule_pin=rule_pin)
        rule=snap["rule"]
        if rule["state"]=="RESEARCH_RULE_PINNED":
            merged=normalize(parsed[:n],direction)
            fracs=fractals(merged)
            context={"symbol":snap["symbol"],"timeframe":snap["timeframe"],
                     "source_revision_sha256":snap["source_revision_sha256"],
                     "direction":direction}
            result=pen_frontier(fracs,merged,mode=rule["mode"],
                                rule_version=rule["version_id"],context=context)
            present=result["objects"]
            decisions=result["decisions"]
        else:
            present={}
            decisions=[{"decision":"PEN_RULE_UNAVAILABLE","state":rule["state"]}]
        clock_sha=prefix["visible_prefix_digest_sha256"]
        for obj_id in sorted(active.keys()-present.keys()):
            _append(events,last,obj_id,"RETRACT",active[obj_id],clock,clock_sha,
                    reason="NO_LONGER_SELECTED_BY_CURRENT_PREFIX")
        for obj_id in sorted(present):
            payload=present[obj_id]
            if obj_id not in last:
                action="OPEN"
            elif last[obj_id]["action"]=="RETRACT":
                action="REOPEN"
            elif last[obj_id]["payload"]!=payload:
                action="REVISE"
            else:
                continue
            _append(events,last,obj_id,action,payload,clock,clock_sha)
        active=present
        prefixes.append({"observed_at":prefix["observed_at"],"visible_closed_bars":n,
                         "visible_prefix_digest_sha256":clock_sha,
                         "provisional_pen_count":sum(x["object_kind"]=="PROVISIONAL_PEN_FRONTIER"
                                                     for x in present.values()),
                         "conflict_count":sum(x["object_kind"]=="PEN_FRONTIER_CONFLICT"
                                             for x in present.values()),
                         "research_decisions":decisions})
    report={"schema_version":3,"data_kind":KIND,"scope":SCOPE,
            "source_revision_sha256":v2["source_revision_sha256"],
            "source_v2_event_sha256":digest(v2["events"]),
            "symbol":v2["symbol"],"timeframe":v2["timeframe"],
            "direction_experiment":direction,
            "events":events,"prefixes":prefixes,
            "active_objects":[{"id":key,"payload":val} for key,val in sorted(active.items())],
            "complete_pen_parser":False,"complete_segment_parser":False,
            "segment_inputs_certified":False,"orders_sent":False,"real_market_backtest":False}
    validate_ledger(report)
    return report

def provisional_feature_audit(pen_payloads):
    """No provisional pen can become a STRICT feature without a separate proof."""
    require(isinstance(pen_payloads,list),"List of provisional pen payloads required")
    projections=[]
    for item in pen_payloads:
        require(item.get("object_kind")=="PROVISIONAL_PEN_FRONTIER" and
                item.get("feature_projection",{}).get("role")=="UNDETERMINED" and
                item.get("complete_pen") is False,
                "Only unconfirmed provisional pen projections allowed")
        projections.append({"role":"UNDETERMINED","low":item["feature_projection"]["low"],
                            "high":item["feature_projection"]["high"],
                            "source_version":item["rule_version_id"],
                            "evidence_known_at":item["evidence_known_at"]})
    return {"role":"UNDETERMINED","count":len(projections),"features":projections,
            "admitted_as_STRICT_segment_features":False,"full_segment_parser":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fixture",default="experiments/fixtures/chanlun_pen_frontier_synthetic_v3.json")
    p.add_argument("--direction",choices=("UP","DOWN"),default="UP")
    p.add_argument("--rule",choices=("pen_077_exposition","pen_081_later_dated_post"),
                   default="pen_077_exposition")
    p.add_argument("--attested-known-at",default="2007-09-19T09:00:00+08:00")
    p.add_argument("--proof-ref",default="synthetic-research-availability")
    p.add_argument("--stop-at")
    args=p.parse_args()
    fixture=json.loads((ROOT/args.fixture).read_text(encoding="utf8"))
    pin={"version_id":args.rule,"attested_known_at":args.attested_known_at,
         "proof_ref":args.proof_ref,"proof_kind":"synthetic_fixture"}
    out=replay_pen_frontier(fixture["bars"],data_kind=fixture["kind"],direction=args.direction,
                            rule_pin=pin,stop_at=args.stop_at)
    selected=[x["payload"] for x in out["active_objects"]
              if x["payload"]["object_kind"]=="PROVISIONAL_PEN_FRONTIER"]
    features=provisional_feature_audit(selected)
    summary={"status":"PASS_V3_SYNTHETIC_PROVISIONAL_PEN_FRONTIER",
             "prefixes":len(out["prefixes"]),"events":len(out["events"]),
             "event_action_counts":{k:sum(e["action"]==k for e in out["events"])
                                    for k in ("OPEN","REVISE","RETRACT","REOPEN")},
             "active_provisional_pen_candidates":len(selected),
             "active_undetermined_features":features["count"],
             "ledger_sha256":digest(out["events"]),
             "segment_features_certified":False,
             "complete_pen_parser":False,"complete_segment_parser":False,
             "orders_sent":False,"real_market_backtest":False}
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True))
if __name__=="__main__":
    main()
