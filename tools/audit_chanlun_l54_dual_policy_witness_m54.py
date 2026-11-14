#!/usr/bin/env python3
"""M54 Lesson 54 exact source-symbolic witness topology, not an OHLC/Chanlun parser."""
import copy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"catalog/chanlun_l54_dual_policy_witness_m54.json"
ID="CHANLUN-L54-TWO-R-THREE-GROUP-SOURCE-WITNESS-M54"
EXPECTED={
 "R_A":{"groups":[["d1g1","g1d2","d2g2"],["g2d3","d3g3","g3d4"],["d4g4","g4d5","d5g5"]],"connector":["g0d1"],"formed":"g5","price":["d2","g5"]},
 "R_B":{"groups":[["d2g2","g2d3","d3g3"],["g3d4","d4g4","g4d5"],["d5g5","g5d6","d6g6"]],"connector":["g0d1","d1g1","g1d2"],"formed":"g6","price":["d3","g5"]}
}
NODE_ORDER=["g0","d1","g1","d2","g2","d3","g3","d4","g4","d5","g5","d6","g6"]
NODES=set(NODE_ORDER)

def endpoints(segment):
    found=[(a,b) for a in NODES for b in NODES if segment==a+b]
    if len(found)!=1:
        raise ValueError("unknown or ambiguous endpoint token "+segment)
    return found[0]

def valid_chain(segments):
    if not segments:
        return False
    try:
        e=[endpoints(s) for s in segments]
    except ValueError:
        return False
    return all(e[i][1]==e[i+1][0] for i in range(len(e)-1))

def inspect_policy(p):
    policy_id=p.get("id")
    if policy_id not in EXPECTED:
        return {"status":"UNKNOWN_POLICY"}
    e=EXPECTED[policy_id]
    if p.get("groups")!=e["groups"] or p.get("prefix_connector")!=e["connector"]:
        return {"status":"AUTHOR_GROUP_TOKEN_MISMATCH"}
    if p.get("author_attested_higher_at")!=e["formed"] or p.get("higher_price_interval_symbolic")!=e["price"]:
        return {"status":"AUTHOR_ATTESTATION_OR_PRICE_SYMBOL_MISMATCH"}
    groups=p["groups"]
    if len(groups)!=3 or any(len(g)!=3 for g in groups):
        return {"status":"NOT_THREE_BY_THREE"}
    if not all(valid_chain(g) for g in groups):
        return {"status":"SEGMENT_CHAIN_BREAK"}
    sequence=p["prefix_connector"]+[s for g in groups for s in g]
    if not valid_chain(sequence):
        return {"status":"GROUP_BOUNDARY_DISCONTINUITY"}
    if endpoints(sequence[-1])[1]!=p["author_attested_higher_at"]:
        return {"status":"FORMATION_MILESTONE_NOT_LAST_ENDPOINT"}
    return {"status":"AUTHOR_TEXT_GROUPING_WITNESS_ONLY",
            "policy":policy_id,"group_count":3,
            "member_count":9,"end_symbol":e["formed"],"interval_symbols":e["price"],
            "independently_verified_completed_g_movements":False,
            "first_known_actual_market_time":None,
            "phi20_authenticated":False,
            "real_market_ohlc_used":False}

def checkpoint(doc,milestone):
    policy_out={p["id"]:inspect_policy(p) for p in doc["policies"]}
    if any(r["status"]!="AUTHOR_TEXT_GROUPING_WITNESS_ONLY" for r in policy_out.values()):
        raise ValueError("invalid source symbol groups")
    if milestone not in ("g5","g6"):
        return {"status":"UNKNOWN_CHECKPOINT"}
    desired={x["id"]:x for x in doc["checkpoints"]}[milestone]
    known={pid:NODE_ORDER.index(milestone)>=NODE_ORDER.index(v["end_symbol"]) for pid,v in policy_out.items()}
    if known!=desired["author_attested_by_policy"]:
        raise AssertionError("source checkpoint changed")
    return {"status":"AUTHOR_ATTESTATION_CHECKPOINT_ONLY","milestone":milestone,
            "by_policy":known,"exists_r":any(known.values()),"forall_r":all(known.values()),
            "no_real_market_first_known_claim":True}

def topology(kind,independent_connector,doc):
    if kind=="TWO_SAME_LEVEL_CENTERS" and not independent_connector:
        return "REJECT_SAMELEVEL_MISSING_CONNECTOR"
    if kind=="THREE_CHILD_CENTERS_FOR_PARENT" and not independent_connector:
        return "ALLOWED_AUTHOR_TOPOLOGY_NOT_COMPLETION_PROOF"
    return "NEEDS_OTHER_STRUCTURAL_ELIGIBILITY_PROOF"

def audit(doc):
    if doc.get("id")!=ID or doc.get("schema_version")!=1:
        raise ValueError("contract identity mismatch")
    policies={p["id"]:inspect_policy(p) for p in doc["policies"]}
    if set(policies)!=set(EXPECTED) or any(p["status"]!="AUTHOR_TEXT_GROUPING_WITNESS_ONLY" for p in policies.values()):
        raise AssertionError("M54 canonical source witness changed")
    a,b=checkpoint(doc,"g5"),checkpoint(doc,"g6")
    if (a["exists_r"],a["forall_r"],b["exists_r"],b["forall_r"])!=(True,False,True,True):
        raise AssertionError("author policy-quantifier distinction changed")
    t=doc["structural_topologies"]
    if topology("TWO_SAME_LEVEL_CENTERS",False,doc)!="REJECT_SAMELEVEL_MISSING_CONNECTOR" or topology("THREE_CHILD_CENTERS_FOR_PARENT",False,doc)!="ALLOWED_AUTHOR_TOPOLOGY_NOT_COMPLETION_PROOF":
        raise AssertionError("topology type fence failed")
    return {"contract":ID,"source_policy_groups":2,"author_symbolic_members":18,
            "g5_exists_but_not_forall":True,"g6_exists_and_forall":True,
            "verified_market":False,"phi20_open":True,"status":"AUTHOR_TEXT_SYMBOLS_ONLY"}

if __name__=="__main__":
    print(json.dumps(audit(json.loads(CONTRACT.read_text(encoding="utf-8"))),ensure_ascii=False,indent=2))
