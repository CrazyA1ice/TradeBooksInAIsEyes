#!/usr/bin/env python3
"""Second buy gate: source explicitly allows second-below-first; no OHLC parsing."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Input:
    first_buy_price:float
    second_buy_price:float
    first_confirmed_at:int
    up_leg_completed_at:int|None
    down_retest_completed_at:int|None
    asof:int
    third_buy_confirmed_at:int|None=None
    coincident_price_time:bool=False
def classify(x):
    if x.first_confirmed_at>x.asof or x.up_leg_completed_at is None or x.down_retest_completed_at is None:
        return {"state":"SECOND_BUY_PENDING"}
    if not(x.first_confirmed_at<x.up_leg_completed_at<x.down_retest_completed_at<=x.asof):
        return {"state":"SECOND_BUY_PENDING"}
    relation=("BELOW" if x.second_buy_price<x.first_buy_price else
              "ABOVE" if x.second_buy_price>x.first_buy_price else "EQUAL")
    overlap=(x.third_buy_confirmed_at is not None and x.third_buy_confirmed_at<=x.asof and x.coincident_price_time)
    return {"state":"SECOND_THIRD_COINCIDE" if overlap else "SECOND_BUY_ELIGIBLE_LOCAL",
            "price_relation":relation,"real_market_proof":False}
def example():
    return {"weak":classify(Input(10,9,1,2,4,4)),
            "strong":classify(Input(10,12,1,2,4,5,5,True)),
            "incomplete":classify(Input(10,9,1,2,4,3))}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
