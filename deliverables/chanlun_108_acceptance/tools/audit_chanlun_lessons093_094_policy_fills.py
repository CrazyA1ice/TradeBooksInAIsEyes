#!/usr/bin/env python3
"""Separate market signal, risk policy, and T+1 eligible settled holdings."""
POLICIES={"CONSERVATIVE":"PARTIAL_EXIT_PLAN","OSCILLATION_SKILLED":"OBSERVE_OSCILLATION_PLAN","NO_TRADE":"WAIT"}
def plan(state,confirmed_at,asof,profile):
    if profile not in POLICIES:raise ValueError("unknown policy")
    if confirmed_at is None or confirmed_at>asof:return "SIGNAL_PENDING"
    if state!=(1,0):return "STATE_NOT_TARGETED"
    return POLICIES[profile]
def sell_gate(total_owned,settled_shares,requested_sell,filled_shares=0):
    if any(not isinstance(x,int) or x<0 for x in (total_owned,settled_shares,requested_sell,filled_shares)):
        raise ValueError("bad share counts")
    if settled_shares>total_owned or requested_sell>total_owned:raise ValueError("impossible holdings")
    if requested_sell>settled_shares:return "RESTRICTED_TPLUS1"
    if filled_shares>requested_sell:raise ValueError("overfill")
    if filled_shares<requested_sell:return "UNFILLED_OR_PARTIAL"
    return "FILLED" if filled_shares>0 else "NO_ORDER"
def example():
    return {"conservative":plan((1,0),10,11,"CONSERVATIVE"),
            "oscillation":plan((1,0),10,11,"OSCILLATION_SKILLED"),
            "new_shares_blocked":sell_gate(100,0,100),
            "older_settled_unfilled":sell_gate(100,100,50),
            "real_orders":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
