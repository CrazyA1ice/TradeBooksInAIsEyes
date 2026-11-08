#!/usr/bin/env python3
"""Synthetic necessary connector condition, NOT a complete center segmentation algorithm."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Segment:
    kind:str
    level:int
def validate_same_level_group(segments):
    if any(s.kind not in ("CENTER","LINK","HIGHER_LEVEL_EXTENSION") or s.level<0 for s in segments):
        raise ValueError("invalid synthetic token")
    centers=[(i,s) for i,s in enumerate(segments) if s.kind=="CENTER"]
    for (a,x),(b,y) in zip(centers,centers[1:]):
        if x.level==y.level:
            between=segments[a+1:b]
            if any(s.kind=="HIGHER_LEVEL_EXTENSION" for s in between):
                return {"status":"REQUIRES_DIFFERENT_HIGHER_LEVEL_ANALYSIS","full_parser_proven":False}
            if not any(s.kind=="LINK" and s.level<x.level for s in between):
                return {"status":"INVALID_SAME_LEVEL_ADJACENCY","full_parser_proven":False}
    return {"status":"LOCAL_CONNECTOR_CONDITION_SATISFIED","full_parser_proven":False}
def example():
    valid=validate_same_level_group([Segment("CENTER",1),Segment("LINK",0),Segment("CENTER",1)])
    invalid=validate_same_level_group([Segment("CENTER",1),Segment("CENTER",1)])
    assert valid["status"]=="LOCAL_CONNECTOR_CONDITION_SATISFIED"
    assert invalid["status"]=="INVALID_SAME_LEVEL_ADJACENCY"
    return {"with_connector":valid,"without_connector":invalid,"used_real_market_data":False}
if __name__=="__main__":
    import json
    print(json.dumps(example(),ensure_ascii=False,indent=2))
