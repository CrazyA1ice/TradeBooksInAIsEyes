#!/usr/bin/env python3
"""Synthetic immutable prospective pen endpoint replacement and type-fence witness."""
import copy
import json
from pathlib import Path
from chanlun_pen_frontier_v3 import replay_pen_frontier, provisional_feature_audit
from chanlun_incremental_events_v2 import digest, feature_containment, validate_ledger

ROOT=Path(__file__).resolve().parents[1]
dataset=json.loads((ROOT/"experiments/fixtures/chanlun_pen_frontier_synthetic_v3.json").read_text("utf8"))
assert dataset["kind"]=="synthetic_non_market_fixture"
bars=dataset["bars"]
def make_pin(version):
    return {"version_id":version,"attested_known_at":"2007-09-19T09:00:00+08:00",
            "proof_ref":"synthetic-research-availability","proof_kind":"synthetic_fixture"}
def run(rows,pin,stop=None):
    report=replay_pen_frontier(rows,data_kind=dataset["kind"],direction="UP",
                               rule_pin=pin,stop_at=stop)
    assert validate_ledger(report)
    return report
def opened(z):
    return {e["object_id"] for e in z["events"]
            if e["object_kind"]=="PROVISIONAL_PEN_FRONTIER" and e["action"]=="OPEN"}

old,new=(make_pin("pen_077_exposition"),make_pin("pen_081_later_dated_post"))
first_old=run(bars[:7],old)
first_new=run(bars[:7],new)
assert opened(first_old) and opened(first_new)
assert opened(first_old).isdisjoint(opened(first_new))
assert [p["visible_prefix_digest_sha256"] for p in first_old["prefixes"]]==[
    p["visible_prefix_digest_sha256"] for p in first_new["prefixes"]]
changed=copy.deepcopy(bars)
changed[7].update(low="0.5",high="3",open="2",close="2")
revised=run(changed[:9],old)
retracted={e["object_id"] for e in revised["events"] if e["action"]=="RETRACT"}
assert opened(first_old).issubset(retracted)
assert first_old["events"]==revised["events"][:len(first_old["events"])]
past=run(changed,old,"2007-09-20T01:37:01+00:00")
assert past["events"]==first_old["events"]
provisional=[x["payload"] for x in first_old["active_objects"]
             if x["payload"]["object_kind"]=="PROVISIONAL_PEN_FRONTIER"]
projection=provisional_feature_audit(provisional)
assert projection["features"] and projection["role"]=="UNDETERMINED"
f=projection["features"][0]
source={"key":"trial1","index":1,"sequence_id":"fiction","role":f["role"],
        "low":f["low"],"high":f["high"],"completed_at":f["evidence_known_at"]}
another={**source,"key":"trial2","index":2}
assert feature_containment(source,another)=="BLOCKED_NON_STRICT_MEMBERSHIP"
result={"status":"PASS_SYNTHETIC_V3_PROVISIONAL_FRONTIER",
        "old_version_eligible_candidates":len(opened(first_old)),
        "revised_version_eligible_candidates":len(opened(first_new)),
        "different_rule_candidate_id_sets":True,
        "later_stronger_extreme_retracts_previous":True,
        "historical_event_prefix_identical":True,
        "future_suffix_isolated":True,
        "v3_changed_history_sha256":digest(revised["events"]),
        "provisional_features_strict_membership":"BLOCKED_NON_STRICT_MEMBERSHIP",
        "complete_pen_parser":False,"complete_segment_parser":False,
        "market_backtest":False,"orders_sent":False}
print(json.dumps(result,ensure_ascii=False,sort_keys=True))
