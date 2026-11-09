#!/usr/bin/env python3
"""Executable pure-synthetic witness suite for v2 immutable amendments and segment gates."""
from __future__ import annotations
import copy
import json
from pathlib import Path

from chanlun_incremental_events_v2 import event_history, feature_three_gate, feature_containment, validate_ledger, digest

ROOT=Path(__file__).resolve().parents[1]
fixture=json.loads((ROOT/"experiments/fixtures/chanlun_prefix_synthetic_v1.json").read_text("utf8"))
bars=fixture["bars"]

def history(changed):
    z=event_history(changed,data_kind="synthetic_non_market_fixture",direction="UP")
    assert validate_ledger(z)
    return z

def actions(z):
    return [x["action"] for x in z["events"] if x["object_kind"]=="FRACTAL_CANDIDATE"]

base=history(bars[:3])
same_center=copy.deepcopy(bars[:4])
same_center[3].update(low="4",high="6",open="5",close="5")
revision=history(same_center)
new_peak=copy.deepcopy(bars[:4])
new_peak[3].update(low="3",high="8",open="4",close="6")
retraction=history(new_peak)
assert actions(base)==["OPEN"]
assert actions(revision)==["OPEN","REVISE"]
assert actions(retraction)==["OPEN","RETRACT"]
assert base["events"][0]==revision["events"][0]==retraction["events"][0], "Immutable origin event changed"
assert len(retraction["active_objects"])==0

def feature(key,seq,index,lo,hi,hour_min,role="STRICT"):
    return {"key":key,"sequence_id":seq,"role":role,"index":index,
            "low":str(lo),"high":str(hi),
            "completed_at":"2007-09-20T"+hour_min+":00+00:00"}
main=[feature("a1","old",1,0,1,"01:30"),
      feature("a2","old",2,2,4,"01:31"),
      feature("a3","old",3,1,3,"01:32")]
opposite=[feature("b1","new",4,8,10,"01:33"),
          feature("b2","new",5,6,8,"01:34"),
          feature("b3","new",6,7,9,"01:35")]
pending=feature_three_gate(main,expected="TOP",asof="2007-09-20T01:34:30+00:00",
                           opposite_three=opposite)
confirmed=feature_three_gate(main,expected="TOP",asof="2007-09-20T01:35:00+00:00",
                             opposite_three=opposite)
no_gap=copy.deepcopy(main);no_gap[0]["high"]="3"
no_gap_result=feature_three_gate(no_gap,expected="TOP",asof="2007-09-20T01:35:00+00:00")
aux=copy.deepcopy(main);aux[2]["role"]="AUXILIARY"
nonmember=feature_three_gate(aux,expected="TOP",asof="2007-09-20T01:35:00+00:00")
cross=copy.deepcopy(main[1]);cross["sequence_id"]="new"
containment=feature_containment(main[1],cross)
assert pending["status"]=="PENDING_OPPOSITE_THREE_FEATURES"
assert confirmed["status"]=="LOCAL_GAP_CONDITION_PASSED_NECESSARY_ONLY"
assert no_gap_result["status"]=="LOCAL_NO_GAP_CONDITION_PASSED_NECESSARY_ONLY"
assert nonmember["status"]=="BLOCKED_NON_STRICT_MEMBERSHIP"
assert containment=="BLOCKED_CROSS_SEQUENCE"

report={"status":"PASS_SYNTHETIC_V2_EVENT_AND_SEGMENT_WITNESSES",
        "source_data":"synthetic_non_market_fixture",
        "fractal_event_chains":{"initial":actions(base),"witness_revised":actions(revision),
                                "witness_retracted":actions(retraction),
                                "initial_event_immutable":True},
        "segment_local_necessary_cases":{"gap_pending":pending["status"],
                                         "gap_after_later_opposite":confirmed["status"],
                                         "overlapping_no_gap":no_gap_result["status"],
                                         "auxiliary_blocked":nonmember["status"],
                                         "cross_sequence_containment":containment},
        "final_source_hashes":{"revised_history":digest(revision["events"]),
                               "retracted_history":digest(retraction["events"])},
        "full_pen_or_segment_parser":False,"orders_sent":False,"market_backtest":False}
print(json.dumps(report,ensure_ascii=False,sort_keys=True))
