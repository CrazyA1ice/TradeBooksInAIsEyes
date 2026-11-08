#!/usr/bin/env python3
"""Ordered interval containment and 3-bar fractal toy examples; no live or historical stock data."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Bar:
    low:float
    high:float
    source_indices:tuple=()
    def __post_init__(self):
        if self.low>self.high:raise ValueError("invalid bar")
def containment(a,b):
    return (a.low<=b.low and a.high>=b.high) or (b.low<=a.low and b.high>=a.high)
def merge(a,b,direction):
    if direction not in ("UP","DOWN"):raise ValueError("direction must be fixed")
    if not containment(a,b):raise ValueError("non-containing pair")
    lows=(a.low,b.low);highs=(a.high,b.high)
    return Bar(max(lows) if direction=="UP" else min(lows),
               max(highs) if direction=="UP" else min(highs),
               a.source_indices+b.source_indices)
def ordered_reduce(values,direction):
    if direction not in ("UP","DOWN"):raise ValueError("direction not preset")
    output=[]
    for i,pair in enumerate(values):
        b=Bar(pair[0],pair[1],(i,))
        if output and containment(output[-1],b):
            output[-1]=merge(output[-1],b,direction)
        else:output.append(b)
    return output
def fractal_complete(triple):
    if len(triple)<3:return {"status":"PENDING_THIRD_COMPLETED_BAR","kind":None}
    if len(triple)!=3:raise ValueError("three consecutive merged bars required")
    a,b,c=triple
    if b.high>a.high and b.high>c.high and b.low>a.low and b.low>c.low:kind="TOP"
    elif b.high<a.high and b.high<c.high and b.low<a.low and b.low<c.low:kind="BOTTOM"
    else:kind="UNDETERMINED"
    return {"status":"CONFIRMED_3_BARS","kind":kind,
            "confirm_source_index":max(c.source_indices or (2,))}
def example():
    A=Bar(0,6,(0,));B=Bar(0,10,(1,));C=Bar(4,10,(2,))
    assert containment(A,B) and containment(B,C) and not containment(A,C)
    out=ordered_reduce([(0,6),(0,10),(4,10)],"UP")
    top=fractal_complete([Bar(1,3,(0,)),Bar(3,5,(1,)),Bar(2,4,(2,))])
    return {"nontransitive":{"A_B":True,"B_C":True,"A_C":False},
            "ordered_up":[{"low":x.low,"high":x.high,"source_indices":x.source_indices} for x in out],
            "top":top,"pending":fractal_complete([Bar(1,3,(0,)),Bar(3,5,(1,))]),
            "real_market_data_used":False,"full_chanlun_parser_implemented":False}
if __name__=="__main__":
    import json
    print(json.dumps(example(),ensure_ascii=False,indent=2))
