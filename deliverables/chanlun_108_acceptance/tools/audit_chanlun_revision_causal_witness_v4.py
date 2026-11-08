#!/usr/bin/env python3
"""Reproduce before/after two synthetic correction events without retrospective signal leakage."""
import json
from pathlib import Path
from chanlun_revision_proof_gates_v4 import (
    BAR_PRICES, asof_restatement, make_synthetic_correction, pen_proof_obligations
)

ROOT=Path(__file__).resolve().parents[1]
bars=json.loads((ROOT/"experiments/fixtures/chanlun_pen_frontier_synthetic_v3.json").read_text("utf8"))["bars"]
pin={"version_id":"pen_077_exposition","attested_known_at":"2007-09-19T09:00:00+08:00",
     "proof_ref":"synthetic-research-only","proof_kind":"synthetic_fixture"}
raw=bars[5]
first={k:raw[k] for k in BAR_PRICES}
first.update(low="0.8",open="2.4",close="2.4")
a=make_synthetic_correction(1,raw,"2007-09-20T01:41:00+00:00",first,proof_ref="synthetic-row-revision-1")
updated={**raw,**first}
second={k:updated[k] for k in BAR_PRICES}
second.update(low="0.7",open="2.5",close="2.5")
b=make_synthetic_correction(2,updated,"2007-09-20T01:42:00+00:00",second,proof_ref="synthetic-row-revision-2")
def snap(events,t):
    return asof_restatement(bars,events,market_asof=t,rule_pin=pin)
original=snap([],"2007-09-20T01:40:50+00:00")
before=snap([a,b],"2007-09-20T01:40:50+00:00")
first_seen=snap([a,b],"2007-09-20T01:41:01+00:00")
first_only=snap([a],"2007-09-20T01:41:01+00:00")
second_seen=snap([a,b],"2007-09-20T01:42:01+00:00")
assert original==before, "Future correction contaminated past as-of response"
assert first_seen==first_only, "Second future correction contaminated first corrected snapshot"
assert [x["correction_count_applied"] for x in (original,first_seen,second_seen)]==[0,1,2]
assert len({x["effective_source_revision_sha256"] for x in (original,first_seen,second_seen)})==3
old_ids={x["id"] for x in original["active_provisional_pens"]}
new_ids={x["id"] for x in first_seen["active_provisional_pens"]}
assert old_ids and new_ids and old_ids.isdisjoint(new_ids), "Stale pen source-version ID retained"
stale=[pen_proof_obligations(first_seen,id) for id in old_ids]
assert all("NOT_ACTIVE_IN_THIS_SNAPSHOT" in x["blockers"] for x in stale)
untrusted={key:{"proof_ref":"caller-says-verified","reviewed_at":"2007-09-20T01:41:01+00:00"}
           for key in ("raw_extreme","direction_and_containment","rule_sufficiency",
                       "unique_decomposition","actual_market_availability","original_chart")}
for item in first_seen["active_provisional_pens"]:
    audit=pen_proof_obligations(first_seen,item["id"],untrusted)
    assert audit["status"]=="BLOCKED_NOT_CERTIFIED"
    assert audit["certifies_complete_pen"] is False
    assert len([b for b in audit["blockers"] if b.startswith("UNVERIFIED_EXTERNAL_")])==6
assert all(x["historic_replay_events_disclosed"] is False for x in (original,before,first_seen,second_seen))
print(json.dumps({
    "status":"PASS_V4_CORRECTION_CLOCK_AND_UNTRUSTED_PROOF_WITNESS",
    "source_kind":"synthetic_non_market_fixture",
    "corrections_by_cutoff":[x["correction_count_applied"] for x in (before,first_seen,second_seen)],
    "snapshots_distinct":True,"future_revision_isolated":True,
    "stale_candidate_ids_rejected":True,"self_reported_proofs_do_not_certify":True,
    "full_pen_certificates_issued":0,"strict_segment_members_issued":0,
    "historic_replay_events_exposed":False,"real_market_backtest":False,"orders_sent":False,
},sort_keys=True))
