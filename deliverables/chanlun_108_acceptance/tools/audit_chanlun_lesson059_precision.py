#!/usr/bin/env python3
"""Exact decimal precision comparison of the author's two example levels, no market prices loaded."""
from decimal import Decimal,ROUND_DOWN,ROUND_HALF_UP
POLICIES={"TRUNCATE_TOWARD_ZERO":ROUND_DOWN,"ROUND_HALF_UP":ROUND_HALF_UP,"EXACT_CENTS":ROUND_DOWN}
def quantize(price,policy,quantum=None):
    if policy not in POLICIES:raise ValueError("PRECISION_POLICY_MISSING")
    if quantum is None:quantum=Decimal("0.01") if policy=="EXACT_CENTS" else Decimal("1")
    unit=Decimal(str(quantum))
    if unit<=0:raise ValueError("invalid quantum")
    x=Decimal(str(price))
    return (x/unit).to_integral_value(rounding=POLICIES[policy])*unit
def compare(a,b,policy):
    return {"policy":policy,"a":str(quantize(a,policy)),"b":str(quantize(b,policy)),
            "equal":quantize(a,policy)==quantize(b,policy)}
def example():
    a="3994.57";b="3994.21"
    out={p:compare(a,b,p) for p in POLICIES}
    assert out["TRUNCATE_TOWARD_ZERO"]["equal"]
    assert not out["ROUND_HALF_UP"]["equal"]
    assert not out["EXACT_CENTS"]["equal"]
    return {"author_numeric_inputs":[a,b],"cases":out,"real_market_data_used":False}
if __name__=="__main__":
    import json
    print(json.dumps(example(),ensure_ascii=False,indent=2))
