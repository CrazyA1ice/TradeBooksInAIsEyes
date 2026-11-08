#!/usr/bin/env python3
"""Synthetic decision provenance gates. No investment order or mind-reading."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Decision:
    reason:str
    signal_known_at:int|None
    decision_at:int
    prior_loss:bool=False
    approved_budget:bool=False
def inspect(d):
    if d.reason not in {"PERSONAL_CONSUMPTION_ANCHOR","PRECOMMITTED_RISK_RULE","KNOWN_MARKET_SIGNAL"}:
        raise ValueError("unsupported reason")
    if d.signal_known_at is not None and d.signal_known_at>d.decision_at:
        return "FUTURE_DATA_REJECTED"
    if d.reason=="PERSONAL_CONSUMPTION_ANCHOR":
        return "ANCHOR_ONLY_NOT_MARKET_SIGNAL"
    if d.reason=="KNOWN_MARKET_SIGNAL" and d.signal_known_at is None:
        return "SIGNAL_UNCONFIRMED"
    return "AUDITABLE_DECISION_NO_PROFIT_GUARANTEE"
def capital_addition(d):
    return "REJECT_UNBUDGETED_TOPUP" if not d.approved_budget else "BUDGET_REVIEW_REQUIRED"
def example():
    return {"anchor":inspect(Decision("PERSONAL_CONSUMPTION_ANCHOR",None,10)),
            "future":inspect(Decision("KNOWN_MARKET_SIGNAL",11,10)),
            "loss_topup":capital_addition(Decision("PRECOMMITTED_RISK_RULE",None,10,True,False)),
            "market_tested":False,"orders_sent":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
