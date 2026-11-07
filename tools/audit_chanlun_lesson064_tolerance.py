#!/usr/bin/env python3
"""Decimal close-within-epsilon relation is symmetric, reflexive, NOT transitive."""
from decimal import Decimal
def near(a,b,epsilon="0.5"):
    aa=Decimal(str(a));bb=Decimal(str(b));eps=Decimal(str(epsilon))
    if eps<0:raise ValueError("negative tolerance")
    return abs(aa-bb)<=eps
def example():
    a,b,c="0.00","0.49","0.98"
    result={"a":a,"b":b,"c":c,"epsilon":"0.5",
            "a_b":near(a,b),"b_c":near(b,c),"a_c":near(a,c),
            "full_price_clustering_implemented":False,"real_market_data_used":False}
    assert result["a_b"] and result["b_c"] and not result["a_c"]
    return result
if __name__=="__main__":
    import json
    print(json.dumps(example(),ensure_ascii=False,indent=2))
