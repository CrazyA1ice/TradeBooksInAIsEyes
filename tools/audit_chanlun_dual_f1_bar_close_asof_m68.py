#!/usr/bin/env python3
"""M68: derive two F1 predicates from identical synthetic raw tape AT AS-OF.

Substantive new gate: unit bars MUST have separate observed close receipts; a
partially observed bar's eventual high/low is NEVER read into an earlier as-of.
Strict trades do NOT require bar closure. A later operational segment is a
distinct third model and has no source-backed segment completion here.
Never licenses a real center, movement exit, trading signal or an order.
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.audit_chanlun_f1_init_non_equivalence import decimal, evaluate_trace
from tools.audit_chanlun_base_pan_cutoff_dual import SPEC as DUAL_SPEC, REPORT as DUAL_REPORT, audit as prior_dual
from tools.audit_chanlun_f01_root_pan_frontier_v476 import audit as prior_f01
from tools.audit_chanlun_confucius61_pan_end_root_cut_m67 import audit as prior_m67

SPEC=ROOT/"catalog/chanlun_dual_f1_bar_close_asof_m68.json"
OLD=ROOT/"catalog/chanlun_f1_unitbar_trade_non_equivalence_v1.json"
METHODS=("L17_UNIT_BAR","L35_TICK_STRICT","L60_PRACTICAL_SEGMENT")
TRUE_STATE="CENTER_FORMATION_PREDICATE_VISIBLE_ONLY"
FALSE_STATE="NOT_ESTABLISHED_IN_PREFIX"

def require(ok, reason):
    if not ok:
        raise ValueError("M68_ASOF_REJECTED: "+reason)

def witnesses():
    data=json.loads(OLD.read_text(encoding="utf-8"))
    return {w["id"]:w for w in data["witnesses"]}

def inspect(witness,bar_close_first_known,asof,source_grade="EXISTING_V434_SYNTHETIC_ONLY",
            claims_market=False,claims_pan_finished=False,claims_f2_child_finished=False):
    require(source_grade=="EXISTING_V434_SYNTHETIC_ONLY","source must be prior artificial witness")
    require(claims_market is False and claims_pan_finished is False and claims_f2_child_finished is False,
            "cannot forge real market, root exit or finished child")
    require(type(asof) is int and asof>=0,"asof must be a nonnegative observation index")
    require(isinstance(witness,dict) and witness.get("id") in witnesses(),"known original witness identity")
    original=witnesses()[witness["id"]]
    require(witness==original,"cannot replace prior source price or bar partition")
    prices=witness["prices"]
    bar_ids=witness["bar_ids"]
    require(isinstance(bar_close_first_known,list)
            and len(bar_close_first_known)==bar_ids[-1]+1
            and all(type(t) is int and t>=0 for t in bar_close_first_known),
            "full typed sequence of bar-close receipt clocks")
    # Trade observation ordinal i has first-known i+1. A completed bar must
    # be certified strictly AFTER its last observed synthetic trade.
    for b,close_known in enumerate(bar_close_first_known):
        last=max(i+1 for i,v in enumerate(bar_ids) if v==b)
        require(close_known>last,"bar-close receipt cannot predate its final trade")
    require(all(a<b for a,b in zip(bar_close_first_known,bar_close_first_known[1:])),
            "bar-close receipt times must be strictly ordered in this synthetic simulator")
    seen=[i for i in range(len(prices)) if i+1<=asof]
    trade_prices=[Decimal(prices[i]) for i in seen]
    strict=any(trade_prices[i]==trade_prices[i+1]==trade_prices[i+2]
               for i in range(max(0,len(trade_prices)-2)))
    # This is a prefix of FULLY CLOSED bars. We never inspect a future bar
    # high/low or use a trade from a not-yet-closed bar for the Kline predicate.
    num_closed=0
    for b,known in enumerate(bar_close_first_known):
        if known<=asof:
            num_closed+=1
        else:
            break
    groups=[]
    for b in range(num_closed):
        source=[Decimal(prices[i]) for i,pbar in enumerate(bar_ids) if pbar==b]
        require(source and all(i+1<=asof for i,pbar in enumerate(bar_ids) if pbar==b),
                "bar close received before all its trades")
        groups.append((min(source),max(source)))
    overlap=False
    for j in range(max(0,len(groups)-2)):
        lo=max(g[0] for g in groups[j:j+3])
        hi=min(g[1] for g in groups[j:j+3])
        if lo<=hi:
            overlap=True
            break
    return {
      "states":{"L17_UNIT_BAR":TRUE_STATE if overlap else FALSE_STATE,
                "L35_TICK_STRICT":TRUE_STATE if strict else FALSE_STATE,
                "L60_PRACTICAL_SEGMENT":"NO_SEGMENT_EVIDENCE"},
      "asof":asof,"witness_id":witness["id"],
      "closed_bars":num_closed,"visible_trades":len(seen),
      "source_authenticated":False,"actual_market":False,
      "base_pan_exit":"OPEN","f2_completed_child":False,"orders_sent":0
    }

def first_known(witness,closes):
    # Full toy sequence only lets us audit old prefixes one by one. No future
    # event is used by inspect() before its own asof.
    end=max([len(witness["prices"]),*closes])
    out={m:None for m in METHODS}
    for t in range(end+1):
        result=inspect(witness,closes,t)["states"]
        for m in METHODS:
            if out[m] is None and result[m]==TRUE_STATE:
                out[m]=t
    return out

def audit(contract=None):
    doc=contract or json.loads(SPEC.read_text(encoding="utf-8"))
    require(doc.get("schema_version")==1 and
            doc.get("id")=="M68-THREE-F1-DOMAINS-ASOF-BAR-CLOSE-RECEIPT-AND-NO-CROSS-PROMOTION",
            "source contract identity")
    prev=doc["precedents"]
    require(prev["existing_toy_catalog"]==OLD.relative_to(ROOT).as_posix(),
            "must directly reuse original v434 synthetic evidence")
    require(set(doc["distinction"]["methods"])==set(METHODS)
            and doc["distinction"]["practical_segment_is_not_a_unit_bar"] is True
            and doc["distinction"]["bar_complete_must_have_a_separate_close_receipt"] is True,
            "cannot conflate three lowest representations")
    front=doc["status"]
    require(front["F01"]==front["OB38"]==front["OB99"]==front["Phi20"]=="OPEN"
            and front["A087_second_formula"]=="UNKNOWN"
            and front["E1_E4"]=="NOT_RUN" and front["orders"]==0
            and front["actual_close_receipt_from_provider"] is False,
            "must not promote proof or market")
    original=witnesses()
    cases=doc["cases"]
    require(len(cases)==9 and len({c["id"] for c in cases})==9,
            "nine as-of comparison cases")
    for c in cases:
        require(c["witness"] in original,"witness identity")
        result=inspect(original[c["witness"]],c["bar_close_first_known"],c["asof"])
        require(result["states"]==c["expected"],"case "+c["id"])
        require(result["base_pan_exit"]=="OPEN" and result["orders_sent"]==0,
                "cannot turn this into a trade")
    for k,expected in doc["expected_asof_first_known"].items():
        related=[c for c in cases if c["witness"]==k and c["id"]!="LATE_CLOSE_RECEIPT_NOT_IN_PREFIX" and c["id"]!="LATE_CLOSE_RECEIPT_ARRIVED"]
        require(bool(related),"missing original witness")
        earliest=first_known(original[k],related[0]["bar_close_first_known"])
        require(earliest==expected,"prefix first-known discrepancy: "+k)
    # Reuse prior source-bound actual implementations instead of repeating
    # their conclusions in a new unexecuted table.
    prior=json.loads(DUAL_SPEC.read_text(encoding="utf-8"))
    a=prior_dual(prior,DUAL_REPORT.read_text(encoding="utf-8"))
    require(a["author_total_bottom_exit_proven"] is False,"dual-f1 old no-go changed")
    strict=prior_f01()
    require(strict["root_pan_exit_certified"] is False and strict["negative_cases_rejected"]==6,
            "prior actual F01 six rejected proofs not retained")
    m67=prior_m67()
    require(m67["root_pan_exit"]=="OPEN" and m67["market"]=="NOT_RUN",
            "prior g0 pan exit still unresolved")
    return {"status":"M68_TWO_F1_ASOF_CLOSED_BAR_SOURCE_GATE_PASS",
            "source_witnesses":len(original),"cases":len(cases),
            "f01_negatives_reexecuted":strict["negative_cases_rejected"],
            "practical_segment_evidence":False,"market":"NOT_RUN",
            "F01":"OPEN","orders":0}

if __name__=="__main__":
    print(json.dumps(audit(),ensure_ascii=False,sort_keys=True))
