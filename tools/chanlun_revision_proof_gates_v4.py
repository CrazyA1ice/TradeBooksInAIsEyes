#!/usr/bin/env python3
"""Synthetic-only V4 revision journal, as-of snapshots, and pen proof obligations.

A corrected old bar is a RESTATEMENT, not evidence that its corrected price was
known at the historical bar close. No source here can issue a complete-pen
certificate or elevate V3 provisional features to STRICT segment members.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from chanlun_event_lab_v1 import ClosedBar, dt, replay
from chanlun_incremental_events_v2 import KIND, digest, require
from chanlun_pen_frontier_v3 import replay_pen_frontier

ROOT = Path(__file__).resolve().parents[1]
BAR_PRICES=("open","high","low","close","volume")
EVENT_KEYS={"ordinal","bar_key","received_at","expected_old_digest",
            "replacement_ohlcv","source_proof_kind","source_proof_ref","event_id"}
OBLIGATIONS=("raw_extreme","direction_and_containment","rule_sufficiency",
             "unique_decomposition","actual_market_availability","original_chart")

def _verify_source(bars):
    require(isinstance(bars,list) and bool(bars),"Nonempty source required")
    parsed=[ClosedBar.parse(row) for row in bars]
    replay(bars,data_kind=KIND,market_asof=parsed[0].known,direction="UP")
    return parsed

def bar_digest(raw):
    """Hash exact raw source row, not float-cast values or JSON whitespace."""
    return digest(raw)

def make_synthetic_correction(ordinal, raw_before, received_at, replacement_ohlcv, *, proof_ref):
    """Test fixture builder. Output still checked exactly like user-supplied journal."""
    require(type(ordinal) is int and ordinal>0,"positive ordinal required")
    event={"ordinal":ordinal,"bar_key":raw_before["key"],"received_at":dt(received_at).isoformat(),
           "expected_old_digest":bar_digest(raw_before),
           "replacement_ohlcv":replacement_ohlcv,
           "source_proof_kind":"synthetic_fixture","source_proof_ref":proof_ref}
    event["event_id"]="CORR4-"+digest(event)
    return event

def validate_journal(bars, corrections):
    """Validate *all* journal events and prior-hash chain, without market writes."""
    parsed=_verify_source(bars)
    require(isinstance(corrections,list),"Correction journal must be a list")
    current={x["key"]:copy.deepcopy(x) for x in bars}
    known={x.key:x.known for x in parsed}
    prior_clock=None
    snapshots=[]
    for n,event in enumerate(corrections,1):
        require(isinstance(event,dict) and set(event)==EVENT_KEYS,
                "Correction event has missing or unexpected fields")
        require(type(event["ordinal"]) is int and event["ordinal"]==n,
                "Correction ordinal must be contiguous")
        require(event["bar_key"] in current,"Correction references unknown bar")
        require(event["source_proof_kind"]=="synthetic_fixture" and
                isinstance(event["source_proof_ref"],str) and event["source_proof_ref"].strip(),
                "External correction evidence is not supported in synthetic phase")
        clock=dt(event["received_at"])
        require(prior_clock is None or clock>prior_clock,"Correction received_at must strictly increase")
        require(clock>known[event["bar_key"]],"Correction cannot predate original bar availability")
        prior_clock=clock
        require(event["event_id"]=="CORR4-"+digest({k:v for k,v in event.items() if k!="event_id"}),
                "Correction event digest does not match immutable content")
        require(event["expected_old_digest"]==bar_digest(current[event["bar_key"]]),
                "Correction prior row digest mismatch: stale or reordered journal")
        changes=event["replacement_ohlcv"]
        require(isinstance(changes,dict) and set(changes)==set(BAR_PRICES) and
                all(isinstance(changes[k],str) for k in BAR_PRICES),
                "Replacement OHLCV requires exactly five decimal strings")
        new={**current[event["bar_key"]],**changes}
        require(new!=current[event["bar_key"]],"No-op correction is forbidden")
        ClosedBar.parse(new)  # Prices, times, symbolic key, and fixed SHA still checked.
        current[event["bar_key"]]=new
        snapshots.append({"ordinal":n,"received_at":clock.isoformat(),
                          "event_id":event["event_id"],"bar_key":event["bar_key"],
                          "new_bar_digest_sha256":bar_digest(new)})
    return snapshots

def asof_restatement(bars, corrections, *, market_asof, rule_pin, direction="UP"):
    """Keep original and restated views separated by *correction received_at*.

    V3's historical prefix-event log is NOT surfaced for a correction restatement,
    because its early synthetic timestamps would be backdated relative to when
    corrected prices were actually received. Only currently restated candidates
    are described, explicitly tagged not historical-asof trading observations.
    """
    require(direction in ("UP","DOWN"),"Explicit frozen containment direction required")
    parsed=_verify_source(bars)
    history=validate_journal(bars,corrections)
    clock=dt(market_asof)
    observed=[e for e in corrections if dt(e["received_at"])<=clock]
    raw=copy.deepcopy(bars)
    index={b["key"]:i for i,b in enumerate(raw)}
    for event in observed:
        raw[index[event["bar_key"]]].update(event["replacement_ohlcv"])
    source_version=digest({"original_source_revision_sha256":parsed[0].source_revision_sha256,
                           "applied_correction_events":[e["event_id"] for e in observed]})
    for b in raw:
        b["source_revision_sha256"]=source_version
    # Explicitly bind this response to the cut-off: do not include future
    # correction event metadata, payload, counts or the unfiltered journal SHA.
    view=replay_pen_frontier(raw,data_kind=KIND,direction=direction,rule_pin=rule_pin,
                             stop_at=clock.isoformat())
    candidates=[{"id":x["id"],"payload":x["payload"]} for x in view["active_objects"]
                if x["payload"]["object_kind"]=="PROVISIONAL_PEN_FRONTIER"]
    proof_data={"source_revision_sha256":source_version,
                "original_source_revision_sha256":parsed[0].source_revision_sha256,
                "correction_event_ids":[e["event_id"] for e in observed],
                "market_asof":clock.isoformat(),
                "direction_experiment":direction,
                "rule_version_id":rule_pin["version_id"] if rule_pin is not None else None}
    return {"schema_version":4,"source_kind":KIND,
            "representation":"ASOF_OBSERVED_SOURCE_VERSION_WITH_RESTATEMENT_WARNING",
            "market_asof":clock.isoformat(),"correction_count_applied":len(observed),
            "applied_corrections":[{"ordinal":e["ordinal"],"bar_key":e["bar_key"],
                                    "received_at":dt(e["received_at"]).isoformat(),
                                    "event_id":e["event_id"]} for e in observed],
            "snapshot_sha256":digest(proof_data),
            "effective_source_revision_sha256":source_version,
            "base_source_revision_sha256":parsed[0].source_revision_sha256,
            "visible_prefix_count":len(view["prefixes"]),
            "active_provisional_pens":candidates,
            "active_provisional_pen_count":len(candidates),
            "historic_replay_events_disclosed":False,
            "historic_replay_events_may_not_be_claimed_live":True,
            "corrected_bar_original_known_at_unchanged_not_corrected_known_at":True,
            "full_pen_certified":False,"segment_features_certified":False,
            "orders_sent":False,"real_market_data_used":False}

def pen_proof_obligations(snapshot, candidate_id, proof_claims=None):
    """Source/evidence gate. Self-reported proof refs are never certification.

    A future real-market verifier must independently verify actual files,
    visible rule publication, OHLC extremum provenance, unique decomposition,
    chart geometry, and time-resolved data availability.
    """
    require(isinstance(snapshot,dict) and snapshot.get("schema_version")==4 and
            snapshot.get("source_kind")==KIND,"A V4 synthetic snapshot is required")
    require(isinstance(candidate_id,str) and bool(candidate_id),"Candidate id required")
    require(proof_claims is None or isinstance(proof_claims,dict),"Proof claims must be a dictionary")
    claims=proof_claims if proof_claims is not None else {}
    require(set(claims).issubset(OBLIGATIONS),"Unknown proof obligation field")
    candidate=next((x for x in snapshot["active_provisional_pens"] if x["id"]==candidate_id),None)
    blockers=[]
    if candidate is None:
        blockers.append("NOT_ACTIVE_IN_THIS_SNAPSHOT")
    else:
        p=candidate["payload"]
        require(p.get("object_kind")=="PROVISIONAL_PEN_FRONTIER" and
                p.get("complete_pen") is False and
                p.get("feature_projection",{}).get("role")=="UNDETERMINED",
                "Provisional candidate has unsupported certified state")
    for requirement in OBLIGATIONS:
        item=claims.get(requirement)
        if item is None:
            blockers.append("MISSING_"+requirement.upper())
            continue
        require(isinstance(item,dict) and set(item)=={"proof_ref","reviewed_at"} and
                isinstance(item["proof_ref"],str) and bool(item["proof_ref"].strip()),
                "Proof claims must include nonempty reference and reviewed_at")
        reviewed=dt(item["reviewed_at"])
        if reviewed>dt(snapshot["market_asof"]):
            blockers.append("FUTURE_PROOF_"+requirement.upper())
        # Even a valid ref is only caller-supplied: never an independent proof.
        blockers.append("UNVERIFIED_EXTERNAL_"+requirement.upper())
    blockers.extend(("SYNTHETIC_SOURCE_NOT_REAL_BAR_ATTESTATION",
                     "NO_COMPLETE_FORMAL_PEN_UNIQUENESS_PROOF",
                     "NO_INDEPENDENT_VERIFIER_REGISTERED"))
    return {"status":"BLOCKED_NOT_CERTIFIED","candidate_id":candidate_id,
            "bound_source_snapshot_sha256":snapshot["snapshot_sha256"],
            "asof":snapshot["market_asof"],
            "blockers":blockers,"proof_claims_count":len(claims),
            "source_revisions_applied":snapshot["correction_count_applied"],
            "certifies_complete_pen":False,"segment_role":"UNDETERMINED",
            "orders_sent":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fixture",default="experiments/fixtures/chanlun_pen_frontier_synthetic_v3.json")
    p.add_argument("--asof",default="2007-09-20T02:00:00+00:00")
    p.add_argument("--direction",choices=("UP","DOWN"),default="UP")
    p.add_argument("--rule",choices=("pen_077_exposition","pen_081_later_dated_post"),
                   default="pen_077_exposition")
    args=p.parse_args()
    fixture=json.loads((ROOT/args.fixture).read_text(encoding="utf8"))
    require(fixture.get("kind")==KIND,"Synthetic fixture only")
    row=fixture["bars"][5]
    new={k:row[k] for k in BAR_PRICES}
    new.update(low="0.8",open="2.4",close="2.4")
    corr=make_synthetic_correction(1,row,"2007-09-20T01:41:00+00:00",new,proof_ref="synthetic-batch-1")
    pin={"version_id":args.rule,"attested_known_at":"2007-09-19T09:00:00+08:00",
         "proof_ref":"synthetic-rule-study","proof_kind":"synthetic_fixture"}
    v=asof_restatement(fixture["bars"],[corr],market_asof=args.asof,
                       rule_pin=pin,direction=args.direction)
    checks=[pen_proof_obligations(v,x["id"]) for x in v["active_provisional_pens"]]
    assert all(x["status"]=="BLOCKED_NOT_CERTIFIED" for x in checks)
    print(json.dumps({"status":"PASS_V4_SYNTHETIC_REVISION_AND_CERTIFICATION_GATES",
                      "market_asof":v["market_asof"],
                      "corrections_applied":v["correction_count_applied"],
                      "snapshot_sha256":v["snapshot_sha256"],
                      "active_provisional_pens":v["active_provisional_pen_count"],
                      "complete_pens_certified":0,"strict_segment_features":0,
                      "orders_sent":False,"real_market_backtest":False},
                     ensure_ascii=False,sort_keys=True))
if __name__=="__main__":
    main()
