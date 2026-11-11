#!/usr/bin/env python3
"""Source-bounded F01 initial-direction and Nth-nonadvance witness guard.

Fixes a *local false-positive class* in the preceding v4.54 research
bridge: its two supplied F1 centers were the N-1 and N comparison pair;
they did not prove the earlier direction defining the purported trend.
We add a three-center, nine-raw-point witness for each synthetic
movement. The existing F01 check_graph remains authoritative for
syntactic dependency checks; this extra guard checks SINGLE-PRICE
directions and comparator values. Not a Chanlun parser, source
authentication, market completion certification, or trading system.
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import json

from audit_kaixiang_f01_graph_completion_bridge import f01, bridge, ORIGIN
from audit_kaixiang_f01_graph_completion_bridge import SCOPE, ALIAS

ROOT=Path(__file__).resolve().parents[1]
IDENTITY="KX-F01-SYNTHETIC-INITIAL-DIRECTION-THREE-CENTER-V455"
STRUCTURE="THREE_CENTER_LOCAL_DIRECTION_AND_NONADVANCE_CHECKED_NOT_MARKET"
PROVENANCE="SYNTHETIC_SOURCE_ASSERTIONS_NOT_AUTHENTICATED"


def require(ok, why):
    if not ok:
        raise ValueError("KX_DIRECTION: "+why)


def generate(spec):
    """Generate a 43-node DAG, where each of 3 children has 3 base centers."""
    require(spec.get("id")==IDENTITY and spec.get("origin")==ORIGIN
            and spec.get("provenance")==PROVENANCE
            and spec.get("scope")==SCOPE
            and spec.get("level_alias_kind")==ALIAS
            and spec.get("parent_level")==1 and spec.get("child_level")==0,
            "invalid synthetic identity or level alias")
    direction=spec.get("direction")
    require(direction in ("DOWN","UP"),"explicit direction needed")
    pairs=spec.get("price_bounds")
    keys=spec.get("member_keys")
    require(isinstance(pairs,list) and len(pairs)==3
            and isinstance(keys,list) and len(keys)==3
            and len(set(keys))==3 and all(isinstance(k,str) and k for k in keys),
            "three stable source member IDs required")
    policy=spec.get("policy_id")
    require(isinstance(policy,str) and len(policy)>=8,"frozen policy ID missing")
    nodes=[];members=[];certificates=[];ordn=0; deps=[]
    for i,(key,bounds) in enumerate(zip(keys,pairs)):
        require(isinstance(bounds,list) and len(bounds)==2,"member price endpoints")
        low,high=[f01.money(v) for v in bounds]
        require(low>=0 and high>low,"positive finite nonnegative pair required")
        middle=(low+high)/Decimal(2)
        # Center 1->2 proves an initial trend direction. Center 3 no
        # longer advances that original direction, and is the exit
        # comparison's Nth (N=3) center. All are SINGLE-PRICE centers.
        seq=(high,low,middle) if direction=="DOWN" else (low,high,middle)
        cs=[]
        for j,price in enumerate(seq):
            leaves=[]
            for k in range(3):
                ordn+=1
                rid=f"{key}_raw_{ordn}"
                nodes.append({"id":rid,"kind":"RAW_TRADE","level":0,
                    "policy_id":policy,"first_known_seq":ordn,
                    "historical_endpoint_seq":ordn,"deps":[],
                    "root_verified":False,"stream_id":"SYNTHETIC_UNVERIFIED_STREAM",
                    "stream_digest":"synthetic-untrusted-root-20261111",
                    "ordinal":ordn,"price":str(price)})
                leaves.append(rid)
            cid=f"{key}_c{j+1}"
            nodes.append({"id":cid,"kind":"F1_CENTER","level":0,
                "policy_id":policy,"first_known_seq":ordn,
                "historical_endpoint_seq":ordn,"deps":leaves,
                "low":str(price),"high":str(price),
                "center_ordinal":3*i+j+1})
            cs.append(cid)
        exit_tick=ordn+1
        eid=f"{key}_claimed_exit"
        nodes.append({"id":eid,"kind":"F1_TREND_NONADVANCE",
            "level":0,"policy_id":policy,"first_known_seq":exit_tick,
            "historical_endpoint_seq":ordn,"deps":cs[-2:],
            "direction":direction,
            "author_comparator_claim":"NOT_LOWER" if direction=="DOWN" else "NOT_HIGHER",
            "comparison_independently_verified":False})
        mid=f"{key}_claimed_finished"
        nodes.append({"id":mid,"kind":"FINISHED_MOVEMENT",
            "level":0,"policy_id":policy,"first_known_seq":exit_tick,
            "historical_endpoint_seq":ordn,"deps":[eid],
            "movement_ordinal":i+1,"low":str(low),"high":str(high),
            "market_finish_authenticated":False})
        certificates.append({"member_key":key,
            "initial_center_id":cs[0],"second_center_id":cs[1],
            "nth_center_id":cs[2],"exit_id":eid,"movement_id":mid,
            "declared_direction":direction})
        members.append({"key":key,"ordinal":i+1,
            "member_level":spec.get("lower_level"),
            "member_status":bridge.MEMBER_ASSERTION,
            "completed_at_tick":ordn,"first_known_tick":exit_tick,
            "low":float(low),"high":float(high)})
        deps.append(mid)
    zlo=max(f01.money(str(m["low"])) for m in members)
    zhi=min(f01.money(str(m["high"])) for m in members)
    require(zlo<zhi,"fixture requires positive member overlap")
    nodes.append({"id":"synthetic_parent_center",
        "kind":"F2_CENTER","level":1,"policy_id":policy,
        "first_known_seq":members[-1]["first_known_tick"],
        "historical_endpoint_seq":members[-1]["completed_at_tick"],
        "deps":deps,"zone_low":str(zlo),"zone_high":str(zhi)})
    return {"id":IDENTITY,"origin":ORIGIN,"scope":SCOPE,"direction":direction,
        "policy_id":policy,"source_case_id":spec["source_case_id"],
        "source_answer_ids":spec["source_answer_ids"],"certificates":certificates,
        "members":members,"parent_center_id":"synthetic_parent_center",
        "graph":{"schema_version":1,"mode":"ABSTRACT_RECEIPTS_UNVERIFIED",
                 "policy_id":policy,"nodes":nodes}}


def evaluate(witness,candidate_case,center_case,asof_tick):
    require(witness.get("id")==IDENTITY and witness.get("origin")==ORIGIN
            and witness.get("scope")==SCOPE,"unsupported witness provenance")
    require(witness.get("source_case_id")==candidate_case.get("id")
            and witness.get("source_case_id")==center_case.get("source_case_id")
            and witness.get("source_answer_ids")==candidate_case.get("source_answer_ids")
            and witness.get("source_answer_ids")==center_case.get("source_answer_ids"),
            "A-index source/provenance mismatch")
    require(witness.get("policy_id")==center_case.get("policy"),"frozen policy mismatch")
    verdict=f01.check_graph(witness["graph"])
    require(verdict["claim"]=="STRUCTURAL_CHECKED_NOT_MARKET_AUTHENTICATED",
            "unexpected F01 certification")
    nodes={n["id"]:n for n in witness["graph"]["nodes"]}
    certs=witness.get("certificates")
    members=witness.get("members")
    require(isinstance(certs,list) and isinstance(members,list)
            and len(certs)==3 and len(members)==3,"three qualified members required")
    parent=nodes[witness["parent_center_id"]]
    require(parent["kind"]=="F2_CENTER" and parent["level"]==1
            and parent["deps"]==[q["movement_id"] for q in certs],
            "parent must depend on exactly these 3 movements")
    for n,(q,m) in enumerate(zip(certs,members),1):
        require(q["member_key"]==m["key"] and m["ordinal"]==n,
                "member certificate mapping changed")
        ids=[q["initial_center_id"],q["second_center_id"],q["nth_center_id"]]
        require(len(set(ids))==3 and all(x in nodes for x in ids),
                "three distinct base centers required; cannot silently skip initial direction")
        cs=[nodes[x] for x in ids]
        require(all(x["kind"]=="F1_CENTER" and x["level"]==0 for x in cs),
                "direction must derive from base-center events")
        require([x["center_ordinal"] for x in cs]==list(
            range(3*(n-1)+1,3*n+1)),"three centers must be sequential")
        prices=[];ordinals=[];raw_ids=[]
        for cent in cs:
            src=[nodes[x] for x in cent["deps"]]
            require(len(src)==3 and all(x["kind"]=="RAW_TRADE" for x in src),
                    "base center source leaves missing")
            require(len({x["stream_id"] for x in src})==1
                    and len({x["stream_digest"] for x in src})==1,
                    "base sources must be from same declared tape")
            v=[f01.money(x["price"]) for x in src]
            require(v[0]==v[1]==v[2]==f01.money(cent["low"])==f01.money(cent["high"]),
                    "center value not backed by three raw-price leaves")
            prices.append(v[0])
            ordinals.extend(x["ordinal"] for x in src)
            raw_ids.extend(src)
        require(ordinals==list(range(ordinals[0],ordinals[0]+9)),
                "three centers must use chronological consecutive raw price leaves")
        require(len({x["stream_id"] for x in raw_ids})==1
                and len({x["stream_digest"] for x in raw_ids})==1,
                "cross-center raw tape identity mismatch")
        exit_node=nodes[q["exit_id"]]
        move=nodes[q["movement_id"]]
        require(exit_node["kind"]=="F1_TREND_NONADVANCE"
                and exit_node["deps"]==ids[-2:]
                and move["kind"]=="FINISHED_MOVEMENT" and move["deps"]==[q["exit_id"]],
                "exit must use the last two of three successive centers")
        direction=q["declared_direction"]
        require(direction==witness["direction"]==exit_node["direction"],
                "direction label mismatch")
        if direction=="DOWN":
            require(prices[1]<prices[0],
                    "INITIAL_DIRECTION_UNPROVEN: prior center must be strictly higher")
            require(prices[2]>=prices[1],
                    "NONADVANCE_FALSE: Nth center moved lower, trend did not stop")
            require(exit_node["author_comparator_claim"]=="NOT_LOWER",
                    "down comparator label")
        elif direction=="UP":
            require(prices[1]>prices[0],
                    "INITIAL_DIRECTION_UNPROVEN: prior center must be strictly lower")
            require(prices[2]<=prices[1],
                    "NONADVANCE_FALSE: Nth center moved higher, trend did not stop")
            require(exit_node["author_comparator_claim"]=="NOT_HIGHER",
                    "up comparator label")
        else:
            raise ValueError("KX_DIRECTION: unsupported direction")
        require(f01.money(move["low"])==min(prices)
                and f01.money(move["high"])==max(prices),
                "finished-movement extrema disagree with 9 raw leaves")
        require(m["completed_at_tick"]==cs[-1]["historical_endpoint_seq"]
                and m["first_known_tick"]==exit_node["first_known_seq"]
                and move["first_known_seq"]==exit_node["first_known_seq"]
                and move["historical_endpoint_seq"]==m["completed_at_tick"],
                "first known/completion clocks do not align")
        require(f01.money(str(m["low"]))==f01.money(move["low"])
                and f01.money(str(m["high"]))==f01.money(move["high"]),
                "member interval disagrees with raw-backed movement receipt")
    center=dict(center_case)
    center["members"]=members
    local=bridge.assess(candidate_case,center,asof_tick)
    require(local["candidate_set_exhaustiveness_proven"] is False
            and local["center_sufficient_for_complete_chanlun_center"] is False,
            "local overlap was improperly promoted")
    visible=[m["key"] for m in members if m["first_known_tick"]<=asof_tick]
    require(local["visible_member_ids"]==visible,"future receipt leaked")
    return {
        "status":STRUCTURE if local["three_member_check"]==bridge.OVERLAP
                 else "THREE_CENTER_GRAPH_VALID_ASOF_PENDING",
        "asof_tick":asof_tick,"source_answer_ids":witness["source_answer_ids"],
        "graph_node_count":verdict["receipt_count"],
        "initial_direction_prices_checked":True,
        "nth_nonadvance_prices_checked":True,
        "visible_members":visible,
        "overlap_if_visible":local["intersection_if_all_visible"],
        "candidate_states_unchanged":local["candidate_states_unchanged"],
        "candidate_remaining_unchanged":local["candidate_remaining_unchanged"],
        "independent_original_trade_authentication":False,
        "lowest_level_nonadvance_rule_fully_formalized":False,
        "universal_level_policy_and_segmentation_proven":False,
        "movement_completion_certified":False,
        "third_buy_certified":False,
        "market_data_used":False,"orders_sent":0,
    }


def fixture_audit(path):
    spec=json.loads(Path(path).read_text(encoding="utf-8"))
    older=json.loads((ROOT/"tests/fixtures/kaixiang_asof_symbolic_v452.json").read_text(encoding="utf-8"))
    c=next(x for x in older["cases"] if x["id"]==spec["source_case_id"])
    b=json.loads((ROOT/"tests/fixtures/kaixiang_center_asof_bridge_v453.json").read_text(encoding="utf-8"))
    center=next(x for x in b["bridge_cases"] if x["source_case_id"]==c["id"])
    require(spec["source_answer_ids"]==c["source_answer_ids"]==center["source_answer_ids"],
            "source identity mismatch")
    w=generate(spec)
    ticks=spec["checkpoints"]
    require(ticks==[9,10,19,28],"fixed synthetic validation moments")
    results=[evaluate(w,c,center,t) for t in ticks]
    require([len(x["visible_members"]) for x in results]==[0,1,2,3],
            "first-known clocks were altered")
    require(results[-1]["overlap_if_visible"]==[9.0,12.0],
            "positive interval mismatch")
    require(all(x["movement_completion_certified"] is False
                and x["market_data_used"] is False and x["orders_sent"]==0
                for x in results),"forbidden market/trade claim")
    return {"status":"THREE_CENTER_PRICE_RELATIONS_CHECKED_SYNTHETIC_ONLY",
        "graph_nodes":len(w["graph"]["nodes"]),
        "checked_times":len(results),
        "visible_members":[len(x["visible_members"]) for x in results],
        "end_intersection":results[-1]["overlap_if_visible"],
        "market_data":False,"independently_finished_movements":0,
        "real_trades_authenticated":0,"orders":0}


if __name__=="__main__":
    print(json.dumps(fixture_audit(
        ROOT/"tests/fixtures/kaixiang_f01_direction_three_centers_v455.json"
    ),ensure_ascii=False,indent=2))
