#!/usr/bin/env python3
"""Synthetic portfolio snapshot, accounting cash recovery is not zero economic exposure."""
from decimal import Decimal
def snapshot(initial_external,withdrawn,shares,price,earlier_price=None):
    init=Decimal(str(initial_external));w=Decimal(str(withdrawn));p=Decimal(str(price))
    if init<0 or w<0 or p<0 or not isinstance(shares,int) or shares<0:
        raise ValueError("bad portfolio inputs")
    now=shares*p;past=shares*Decimal(str(earlier_price)) if earlier_price is not None else None
    if past is not None and past<0:raise ValueError("negative old value")
    return {"initial_cash_recovered":w>=init,"remaining_value":str(now),
            "change_from_prior_mark":str(now-past) if past is not None else None,
            "risk_exposure_still_positive":now>0,"no_guaranteed_wealth":True}
def example():
    return {"s":snapshot(100,100,10,2,10),"orders_sent":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
