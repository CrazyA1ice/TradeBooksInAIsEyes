#!/usr/bin/env python3
"""Illustrative parent-context gate for a LOWER third sell; never issues orders."""
VALID=("CENTER_RISING","CENTER_FALLING","CENTER_OSCILLATING","UNKNOWN")
def contextualize(higher,lower,decision_at,higher_confirmed_at=None,lower_confirmed_at=None):
    if higher not in VALID or lower!="THIRD_SELL":raise ValueError("unknown context or lower event")
    if lower_confirmed_at is None or lower_confirmed_at>decision_at:
        return {"state":"LOWER_EVENT_PENDING","order":None}
    if higher=="UNKNOWN" or higher_confirmed_at is None or higher_confirmed_at>decision_at:
        return {"state":"HIGHER_CONTEXT_PENDING","order":None}
    outcome={"CENTER_RISING":"RISK_WARNING","CENTER_FALLING":"FALLING_CONTEXT",
             "CENTER_OSCILLATING":"OSCILLATION_BRANCH"}[higher]
    return {"state":outcome,"order":None}
def example():
    return {"rising":contextualize("CENTER_RISING","THIRD_SELL",20,10,15),
            "falling":contextualize("CENTER_FALLING","THIRD_SELL",20,10,15),
            "oscillating":contextualize("CENTER_OSCILLATING","THIRD_SELL",20,10,15),
            "unknown":contextualize("UNKNOWN","THIRD_SELL",20,None,15),"real_market_data":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
