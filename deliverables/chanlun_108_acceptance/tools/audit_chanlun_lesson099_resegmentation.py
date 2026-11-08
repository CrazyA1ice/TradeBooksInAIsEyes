#!/usr/bin/env python3
"""Synthetic ordered source segments and a separate, immutable derived regrouping view."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Segment:
    key:str
    complete_at:int
    low:float
    high:float
    def __post_init__(self):
        if self.low>self.high:raise ValueError("invalid interval")
def center_asof(parts,asof):
    if len(parts)<3:return {"state":"CENTER_PENDING","reason":"NEEDS_THREE_COMPLETE_COMPONENTS"}
    if any(x.complete_at>asof for x in parts):return {"state":"CENTER_PENDING","reason":"FUTURE_COMPONENT"}
    low=max(x.low for x in parts);high=min(x.high for x in parts)
    return {"state":"CENTER_CONFIRMED" if low<high else "NO_POSITIVE_OVERLAP",
            "intersection":(low,high),"source_parts":tuple(x.key for x in parts)}
def regroup(parts,groups,asof):
    source=tuple(parts)
    flat=[name for group in groups for name in group]
    if len(set(flat))!=len(flat) or sorted(flat)!=sorted(x.key for x in source):
        raise ValueError("groups must partition original immutable segment IDs")
    if any(p.complete_at>asof for p in source):
        return {"state":"DERIVED_VIEW_PENDING","source_unchanged":source==tuple(parts)}
    return {"state":"DERIVED_VIEW_READY","groups":tuple(tuple(g) for g in groups),
            "source_unchanged":source==tuple(parts),"original_order":tuple(x.key for x in source)}
def example():
    a=[Segment("a",1,8,14),Segment("b",2,9,13),Segment("c",4,10,12)]
    return {"early":center_asof(a,3),"later":center_asof(a,4),
            "derived":regroup(a,[["a"],["b","c"]],4),
            "market_data":False,"full_chanlun_parser":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
