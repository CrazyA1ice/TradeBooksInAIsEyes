#!/usr/bin/env python3
"""Evidence-conservation check between a closed synthetic trade tape and F01 exits.

The source-driven v4.56 program inferred local NONADVANCE from 9 raw prices
but v4.55 inserted a terminal *claim* at tick+1 without any independently
authenticated terminal event. A raw price at another member's timestamp is
not that member's legally completed trend. This gate rejects attempted
promotion and exposes the unsupported "one tick later" proof step.

Offline, synthetic and research-only. NEVER a market parser or trade engine.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ORIGIN="SYNTHETIC_SYMBOLS_NOT_MARKET"
ID="KX-UNVERIFIED-EXIT-EVIDENCE-CONSERVATION-V457"
KIND="SYNTHETIC_F01_DECLARATION_NOT_OBSERVED_EXIT"
UNKNOWN="NO_INDEPENDENT_COMPLETION_WITNESS"
SOURCE="UNVERIFIED_REPOSITORY_SYNTHETIC"


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError("missing pinned v4.56 source analyzer")
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module


prior=load("kaixiang_v457_source_first",ROOT/"tools/audit_kaixiang_raw_tape_prefix_v456.py")


def require(ok,msg):
    if not ok:
        raise ValueError("KX_EXIT_EVIDENCE: "+msg)


def validate_claims(claims,source):
    """A declaration's metadata is NOT a distinct observed market event."""
    require(isinstance(claims,dict) and claims.get("schema_version")==1
            and claims.get("id")==ID and claims.get("origin")==ORIGIN,
            "fixture identity or synthetic origin invalid")
    require(claims.get("source_authentication")==SOURCE,
            "untrusted source cannot become market-authenticated")
    require(claims.get("source_tape_id")==source["id"]
            and claims.get("source_tape_sha256")==source["raw_tape_sha256"]
            and claims.get("source_case_id")==source["source_case_id"]
            and claims.get("source_answer_ids")==source["source_answer_ids"]
            and claims.get("policy_id")==source["policy_id"],
            "source A-index, SHA, or policy mismatch")
    records=claims.get("exit_claims")
    require(isinstance(records,list) and len(records)==3,
            "exactly three research-label claims expected")
    required={"id","member_index","raw_member_end_tick","declared_first_known_tick",
              "claim_kind","market_event_id","independently_authenticated"}
    require(len({x["id"] for x in records if isinstance(x,dict) and "id" in x})==3,
            "duplicate or absent declaration IDs")
    for i,record in enumerate(records,1):
        require(isinstance(record,dict) and set(record)==required,
                "extra or missing claim evidence fields")
        require(record["id"]==f"synthetic-label-{i}"
                and type(record["member_index"]) is int and record["member_index"]==i,
                "synthetic label/member identity mismatch")
        require(type(record["raw_member_end_tick"]) is int
                and record["raw_member_end_tick"]==9*i
                and type(record["declared_first_known_tick"]) is int
                and record["declared_first_known_tick"]==9*i+1,
                "arbitrary first-known/completion clock claim rejected")
        require(record["claim_kind"]==KIND
                and record["market_event_id"] is None
                and record["independently_authenticated"] is False,
                "synthetic label cannot masquerade as independent exit evidence")
    return records


def examine_prefix(source,claims,at):
    """Only infer from source prices up to at; never certify a finished move."""
    require(type(at) is int and at>=0,"as-of must be a nonnegative integer")
    records=validate_claims(claims,source)
    state=prior.prefix_replay(source["raw_prices"],at)
    observed=state["observed_price_count"]
    received=[x for x in records if x["declared_first_known_tick"]<=at]
    require(len(received)==state["declared_exit_receipt_count"],
            "v4.56 declaration clock drift")
    seen_labels=[]
    for x in received:
        tick=x["declared_first_known_tick"]
        # At ticks 10 and 19 a new RAW_PRICE exists, but it is from
        # the NEXT pinned 9-trade block, not an independent terminal proof.
        # Tick 28 has no source price at all (27-point synthetic tape).
        if tick<=len(source["raw_prices"]):
            require((tick-1)//9+1==x["member_index"]+1,
                    "synthetic price position unexpectedly reused as an exit event")
            observed_at_claim="NEXT_MEMBER_RAW_PRICE_NOT_EXIT_EVENT"
        else:
            observed_at_claim="NO_RAW_PRICE_EVENT_AT_CLAIM_TICK"
        seen_labels.append({"member_index":x["member_index"],
                            "label_tick":tick,"raw_tape_at_tick":observed_at_claim,
                            "independent_exit_evidence":False})
    return {
        "asof_tick":at,
        "observed_raw_price_count":observed,
        "local_nonadvance_condition_count":state["local_pattern_count"],
        "synthetic_exit_label_count":len(received),
        "source_backed_exit_event_count":0,
        "independently_completed_movement_count":0,
        "label_provenance":seen_labels,
        "completion_status":UNKNOWN,
        "can_promote_to_verified_higher_center":False,
        "raw_source_authenticated_externally":False,
        "raw_tape_scope":"EXACT_REPOSITORY_SYNTHETIC_TAPE_NOT_EXCHANGE_COMPLETENESS",
        "market_data_accessed":False,
        "orders":0,
    }


def different_future_same_prefix(source):
    """Counterfactual *price* extensions; not legal Chanlun trend trajectories."""
    a=source["raw_prices"][:9]
    require(len(a)==9,"nine-point prefix required")
    p=prior.prefix_replay(a,9)
    require(p["local_pattern_count"]==1,"expected v4.56 first local price condition")
    low=a+["6","6","6"]
    high=a+["16","16","16"]
    require(low[:9]==high[:9]==a,"history was changed by counterfactual")
    return {"shared_raw_prefix":9,
            "price_at_future_fourth_center_low":low[9],
            "price_at_future_fourth_center_high":high[9],
            "different_price_futures_possible":low[9]!=high[9],
            "original_prefix_condition_identical":True,
            "futures_are_legal_finished_chanlun_types_proven":False,
            "prediction_or_profit_established":False}


def audit_fixture(path):
    claims=json.loads(Path(path).read_text(encoding="utf-8"))
    source=json.loads((ROOT/"tests/fixtures/kaixiang_raw_tape_v456.json").read_text(encoding="utf-8"))
    prior.validate_full_tape(source)
    validate_claims(claims,source)
    # This still runs the previous F01 DAG; all source claims remain untrusted.
    witness=prior.derive_graph(source)
    nodes=witness["graph"]["nodes"]
    prior.previous.f01.check_graph(witness["graph"])
    require(sum(x["kind"]=="F1_TREND_NONADVANCE" for x in nodes)==3
            and all(x.get("comparison_independently_verified") is False
                    for x in nodes if x["kind"]=="F1_TREND_NONADVANCE"),
            "an unverified F01 comparison was improperly authenticated")
    require(sum(x["kind"]=="FINISHED_MOVEMENT" for x in nodes)==3
            and all(x.get("market_finish_authenticated") is False
                    for x in nodes if x["kind"]=="FINISHED_MOVEMENT"),
            "market finished movement forged")
    ticks=claims.get("checkpoints")
    require(ticks==[8,9,10,17,18,19,27,28],
            "as-of checkpoints must remain fixed")
    rows=[examine_prefix(source,claims,t) for t in ticks]
    local=[r["local_nonadvance_condition_count"] for r in rows]
    labels=[r["synthetic_exit_label_count"] for r in rows]
    require(local==[0,1,1,1,2,2,3,3]
            and labels==[0,0,1,1,1,2,2,3],
            "prefix inference failed")
    require(rows[-1]["label_provenance"][-1]["raw_tape_at_tick"]==
            "NO_RAW_PRICE_EVENT_AT_CLAIM_TICK",
            "tick28 has no independently observed event")
    require(all(r["independently_completed_movement_count"]==0
                and r["can_promote_to_verified_higher_center"] is False
                and r["orders"]==0 for r in rows),
            "completion or order was illegally upgraded")
    future=different_future_same_prefix(source)
    require(future["different_price_futures_possible"],
            "counterfactual future ambiguity missing")
    return {
        "status":"SYNTHETIC_EXIT_PROOF_GAP_EXPLICIT_NOT_MARKET",
        "pinned_raw_prices":len(source["raw_prices"]),
        "f01_graph_nodes":len(nodes),
        "observed_prefixes":len(rows),
        "local_nonadvance_counts":local,
        "synthetic_exit_labels":labels,
        "independently_authenticated_exit_count":0,
        "unobserved_last_claim_tick":28,
        "source_last_trade_ordinal":len(source["raw_prices"]),
        "same_prefix_divergent_future_prices":True,
        "real_market_data":False,
        "orders":0,
    }


if __name__=="__main__":
    print(json.dumps(audit_fixture(
        ROOT/"tests/fixtures/kaixiang_exit_evidence_v457.json"),
        ensure_ascii=False,indent=2))
