#!/usr/bin/env python3
"""Check synthetic finite nested intervals and confirmation timing. Not a market backtest."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Candidate:
    lower: float
    upper: float
    occurrence_time: int
    confirmation_time: int
    def __post_init__(self):
        if self.lower>self.upper:raise ValueError("invalid interval")
        if self.confirmation_time<self.occurrence_time:raise ValueError("future information used before occurrence")
def check_chain(items,earliest_trade_time=None):
    if not items:raise ValueError("empty chain")
    for prev,cur in zip(items,items[1:]):
        if not (prev.lower<=cur.lower and cur.upper<=prev.upper):
            return {"status":"not_nested","narrowest":None,"unique_point":False}
        if cur.confirmation_time<prev.confirmation_time:
            raise ValueError("child confirmed before parent without independent evidence")
    last=items[-1]
    if earliest_trade_time is not None and earliest_trade_time<max(x.confirmation_time for x in items):
        return {"status":"not_yet_tradable","narrowest":None,"unique_point":False}
    return {"status":"nested","narrowest":[last.lower,last.upper],"unique_point":last.lower==last.upper}
def demo():
    seq=[Candidate(0,10,0,3),Candidate(2,8,1,5),Candidate(3,7,2,7)]
    return {"valid":check_chain(seq,8),"premature":check_chain(seq,6),
            "invalid":check_chain([seq[0],Candidate(8,12,1,6)],8),
            "real_market_backtest":False}
if __name__=="__main__":
    import json
    print(json.dumps(demo(),ensure_ascii=False,indent=2))
