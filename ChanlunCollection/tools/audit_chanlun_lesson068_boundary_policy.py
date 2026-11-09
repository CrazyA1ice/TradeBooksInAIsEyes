#!/usr/bin/env python3
"""Pre-registered time-specific price boundary labels, no orders or market data."""
from dataclasses import dataclass
from decimal import Decimal
@dataclass(frozen=True)
class Boundary:
    price:Decimal
    frozen_at:int
    policy_version:str
def categorize(boundary,observed_price,observed_at):
    if observed_at<boundary.frozen_at:raise ValueError("future-defined boundary cannot label past data")
    p=Decimal(str(observed_price))
    if not p.is_finite() or not boundary.price.is_finite():raise ValueError("nonfinite price")
    if p<boundary.price:state="BELOW"
    elif p==boundary.price:state="EQUAL"
    else:state="ABOVE"
    return {"state":state,"asof":observed_at,"boundary_frozen_at":boundary.frozen_at,
            "policy_version":boundary.policy_version,"orders_sent":False}
def example():
    b=Boundary(Decimal("10.00"),5,"v1")
    return {"below":categorize(b,"9.99",6),"equal":categorize(b,"10.00",7),
            "above":categorize(b,"10.01",8),"real_market_data_used":False}
if __name__=="__main__":
    import json
    print(json.dumps(example(),ensure_ascii=False,indent=2))
