#!/usr/bin/env python3
"""Pure synthetic pen necessary-gate versioning. Not a Chanlun OHLC pen parser."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Conditions:
    shared_kline:bool
    old_independent_after_containment:bool
    raw_middle_kline_count:int
    def __post_init__(self):
        if self.raw_middle_kline_count<0:raise ValueError("negative bars")
def old_rule(c):
    return "LOCAL_REJECT" if c.shared_kline or not c.old_independent_after_containment else "LOCAL_ELIGIBLE"
def proposed_new_rule(c):
    return "LOCAL_REJECT" if c.shared_kline or c.raw_middle_kline_count<3 else "LOCAL_ELIGIBLE"
def compare(c,decision_asof):
    proposal_first_post="2007-09-18 22:53:57"
    if not isinstance(decision_asof,str):raise ValueError("date string required")
    can_use_new=decision_asof>=proposal_first_post
    return {"old":old_rule(c),"new_proposal":proposed_new_rule(c),
            "new_known_at_decision":can_use_new,"new_rule_posted_at":proposal_first_post,
            "full_pen_parser":False,"real_market_data":False}
def example():
    c=Conditions(False,False,3)
    return {"historical":compare(c,"2007-09-17 12:00:00"),
            "after_proposal":compare(c,"2007-09-19 09:30:00")}
if __name__=="__main__":
 import json
 print(json.dumps(example(),ensure_ascii=False,indent=2))
