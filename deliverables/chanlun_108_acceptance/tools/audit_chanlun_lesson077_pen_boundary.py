#!/usr/bin/env python3
"""Synthetic top/bottom candidates; necessary pen conditions, no full price parser."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Fractal:
    kind:str
    center:int
    extreme:float
    def __post_init__(self):
        if self.kind not in ("TOP","BOTTOM") or self.center<1:raise ValueError("invalid fractal")
def same_kind_filter(a,b):
    if a.kind!=b.kind or b.center<=a.center:raise ValueError("same kind and later timestamp required")
    if a.extreme==b.extreme:return {"state":"TIE_PENDING","candidate_centers":[a.center,b.center]}
    better=b.extreme>a.extreme if a.kind=="TOP" else b.extreme<a.extreme
    return {"state":"PREFER_MORE_EXTREME","candidate_centers":[b.center if better else a.center]}
def pen_candidates(a,b):
    if a.kind==b.kind:return "NOT_OPPOSITE_FRACTALS"
    if b.center<=a.center:return "BAD_TIME_ORDER"
    if b.center-a.center<4:return "NO_INDEPENDENT_KLINE"
    top=a.extreme if a.kind=="TOP" else b.extreme
    bottom=b.extreme if b.kind=="BOTTOM" else a.extreme
    if top<=bottom:return "INVALID_PRICE_ORDER"
    return "LOCAL_ELIGIBLE_PEN_CANDIDATE"
def example():
    return {"equal_tops":same_kind_filter(Fractal("TOP",3,10),Fractal("TOP",5,10)),
            "higher_top":same_kind_filter(Fractal("TOP",3,10),Fractal("TOP",5,11)),
            "pen":pen_candidates(Fractal("TOP",3,12),Fractal("BOTTOM",7,5)),
            "not_full_chanlun_parser":True,"real_market_data":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
