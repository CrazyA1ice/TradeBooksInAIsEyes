#!/usr/bin/env python3
"""Only local feature sequence top/bottom, first-two gap and external opposite-fractal wait."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Feature:
    low:float
    high:float
    index:int
    def __post_init__(self):
        if self.low>self.high:raise ValueError("invalid range")
def overlaps(a,b):return max(a.low,b.low)<=min(a.high,b.high)
def classify(features,expected="TOP",opposite_fractal_observed=False,opposite_index=None):
    if expected not in ("TOP","BOTTOM"):raise ValueError("invalid sequence kind")
    if len(features)<3:return {"status":"PENDING_THREE_FEATURES","confirmed_at":None}
    if len(features)!=3:raise ValueError("requires three consecutive standardized features")
    a,b,c=features
    if not a.index<b.index<c.index:raise ValueError("indices must strictly increase")
    top=b.low>a.low and b.low>c.low and b.high>a.high and b.high>c.high
    bottom=b.low<a.low and b.low<c.low and b.high<a.high and b.high<c.high
    if not (top if expected=="TOP" else bottom):
        return {"status":"NOT_EXPECTED_FRACTAL","confirmed_at":None}
    gap=not overlaps(a,b)
    if gap and not opposite_fractal_observed:
        return {"status":"PENDING_OPPOSITE","candidate_extremum_index":b.index,"confirmed_at":None,"gap_first_second":True}
    if gap:
        if opposite_index is None or opposite_index<=c.index:raise ValueError("opposite evidence must arrive later")
        confirmed_at=opposite_index
    else:confirmed_at=c.index
    return {"status":"LOCAL_END_CONDITION_WITH_GAP" if gap else "LOCAL_END_CONDITION_NO_GAP",
            "candidate_extremum_index":b.index,"confirmed_at":confirmed_at,"gap_first_second":gap,
            "full_segment_algorithm_implemented":False}
def example():
    x=[Feature(0,2,0),Feature(1,3,1),Feature(.5,2,2)]
    y=[Feature(0,1,0),Feature(2,3,1),Feature(1,2,2)]
    return {"no_gap":classify(x),"with_gap_pending":classify(y),
            "with_gap_after_opposite":classify(y,opposite_fractal_observed=True,opposite_index=5),
            "real_market_data_used":False}
if __name__=="__main__":
    import json
    print(json.dumps(example(),indent=2))
