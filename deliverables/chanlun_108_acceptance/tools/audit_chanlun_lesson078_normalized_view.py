#!/usr/bin/env python3
"""Immutable raw segment and derived high-level extremum projection."""
from dataclasses import dataclass
@dataclass(frozen=True)
class RawSegment:
    id:str
    direction:str
    points:tuple
    confirmed_at:int
    def __post_init__(self):
        if self.direction not in ("UP","DOWN") or len(self.points)<3:raise ValueError("invalid segment")
        times=[p[0] for p in self.points]
        if any(times[i]>=times[i+1] for i in range(len(times)-1)):raise ValueError("timestamps not increasing")
        if self.confirmed_at<times[-1]:raise ValueError("confirmation before last observed point")
def normalize(raw):
    price=[p[1] for p in raw.points]
    return {"id":raw.id+"::derived_high_level","source_id":raw.id,
            "direction":raw.direction,"range_low":min(price),"range_high":max(price),
            "display_start":min(price) if raw.direction=="UP" else max(price),
            "display_end":max(price) if raw.direction=="UP" else min(price),
            "original_endpoint":raw.points[-1][1],
            "original_points":raw.points,"confirmed_at":raw.confirmed_at,"derived_only":True}
def example():
    raw=RawSegment("segment-1","UP",((1,10),(2,15),(3,12)),4)
    before=raw.points
    result=normalize(raw)
    assert raw.points==before
    return {"raw_endpoint":raw.points[-1][1],"derived_endpoint":result["display_end"],
            "raw_unchanged":raw.points==before,"derived":result,
            "full_segment_parser":False,"market_data":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
