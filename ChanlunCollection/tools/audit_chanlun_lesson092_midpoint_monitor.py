#!/usr/bin/env python3
"""Simple center and suboscillation interval midpoints, not a third-point parser."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Interval:
    low:float
    high:float
    completed_at:int
    def __post_init__(self):
        if self.low>self.high:raise ValueError("invalid price interval")
    @property
    def midpoint(self):return (self.low+self.high)/2
def monitor(center,sub,asof,third_point_confirmed=False):
    if not isinstance(center,Interval) or not isinstance(sub,Interval):raise ValueError("typed intervals required")
    if center.completed_at>asof or sub.completed_at>asof:
        return {"warning":"PENDING_COMPLETION","structural":"NOT_ASOF_CONFIRMED"}
    z=center.midpoint;zn=sub.midpoint
    label="MIDPOINT_ABOVE" if zn>z else "MIDPOINT_BELOW" if zn<z else "MIDPOINT_EQUAL"
    outside=zn<center.low or zn>center.high
    return {"center_midpoint":z,"sub_midpoint":zn,"strength":label,
            "warning":"OUTSIDE_WARNING" if outside else "INSIDE_MONITOR",
            "structural":"THIRD_POINT_INDEPENDENTLY_CONFIRMED" if third_point_confirmed else "THIRD_POINT_NOT_CONFIRMED",
            "third_point_not_inferred_from_midpoint":True}
def example():
    c=Interval(10,20,2);s=Interval(19,25,3)
    return {"outside_unconfirmed":monitor(c,s,3),"premature":monitor(c,s,2),"market_data":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
