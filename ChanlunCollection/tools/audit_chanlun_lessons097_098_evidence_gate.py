#!/usr/bin/env python3
"""Three-layer conditional signal + plan + actual fill, using strictly as-of observations."""
def observed_branch(asof,continuation_at=None,retest_at=None):
    if continuation_at is not None and continuation_at>asof:continuation_at=None
    if retest_at is not None and retest_at>asof:retest_at=None
    if continuation_at is None and retest_at is None:return "WAIT_FOR_EVIDENCE"
    if continuation_at is not None and retest_at is not None:return "CONFLICT_REVIEW"
    return "CONTINUATION_CONFIRMED" if continuation_at is not None else "RETEST_CONFIRMED"
def execution_gate(signal,plan_approved,settled_shares,requested_sale,filled=None):
    if any(not isinstance(x,int) or x<0 for x in (settled_shares,requested_sale)):
        raise ValueError("bad holding")
    if filled is not None and (not isinstance(filled,int) or filled<0 or filled>requested_sale):
        raise ValueError("invalid fill")
    if signal not in ("CONTINUATION_CONFIRMED","RETEST_CONFIRMED"):
        return "WAIT_FOR_SIGNAL"
    if not plan_approved:return "PLAN_NOT_APPROVED"
    if requested_sale>settled_shares:return "EXECUTION_BLOCKED_TPLUS1_OR_INELIGIBLE"
    if filled is None:return "ELIGIBLE_NOT_PROVEN_FILLED"
    return "FILLED" if filled==requested_sale else "PARTIAL_OR_UNFILLED"
def example():
    return {"future_unknown":observed_branch(10,continuation_at=11),
            "retest":observed_branch(10,retest_at=9),
            "tplus1_block":execution_gate("RETEST_CONFIRMED",True,0,100),
            "unfilled":execution_gate("CONTINUATION_CONFIRMED",True,100,100),
            "live_market_orders":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
