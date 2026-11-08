#!/usr/bin/env python3
"""Strict feature-sequence membership gate and a deliberately local three-stroke boundary toy."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Element:
    sequence_id:str
    role:str
    low:float
    high:float
    completed_at:int
    def __post_init__(self):
        if self.role not in ("STRICT","AUXILIARY","UNDETERMINED") or self.low>self.high:
            raise ValueError("invalid feature element")
def containment_decision(a,b):
    if a.role!="STRICT" or b.role!="STRICT":
        return "NOT_ELIGIBLE_NONSTRICT"
    if not a.sequence_id or a.sequence_id!=b.sequence_id:
        return "NOT_ELIGIBLE_CROSS_SEQUENCE"
    a_contains_b=a.low<=b.low and a.high>=b.high
    b_contains_a=b.low<=a.low and b.high>=a.high
    return "ELIGIBLE_CONTAINMENT" if a_contains_b or b_contains_a else "NOT_CONTAINING"
def three_stroke_boundary(first_start,first_end,third_end,third_completed=False,third_confirmed_at=None):
    if first_start==first_end:raise ValueError("direction undefined")
    if not third_completed:return {"status":"PENDING_THIRD_STROKE","confirmed_at":None}
    if third_confirmed_at is None:raise ValueError("confirmation time required")
    direction=1 if first_end>first_start else -1
    if direction*(third_end-first_end)>0:state="LOCAL_NEW_SEGMENT"
    elif direction*(third_end-first_start)<0:state="LOCAL_OLD_SEGMENT_CONTINUES"
    else:state="PENDING_DIRECTION"
    return {"status":state,"confirmed_at":third_confirmed_at if state!="PENDING_DIRECTION" else None,
            "full_segment_parser":False}
def example():
    old=Element("old-up-segment","STRICT",3,9,10)
    same=Element("old-up-segment","STRICT",4,8,11)
    auxiliary=Element("old-up-segment","AUXILIARY",4,8,12)
    cross=Element("new-down-segment","STRICT",4,8,13)
    return {"same":containment_decision(old,same),"auxiliary":containment_decision(old,auxiliary),
            "cross":containment_decision(old,cross),
            "third_pending":three_stroke_boundary(10,8,7),
            "third_completed":three_stroke_boundary(10,8,7,True,14),
            "real_market_data_used":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),ensure_ascii=False,indent=2))
