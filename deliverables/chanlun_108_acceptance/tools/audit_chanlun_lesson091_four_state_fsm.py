#!/usr/bin/env python3
"""Author's four-state transition grammar; unknown OHLC belongs OUTSIDE this toy FSM."""
from dataclasses import dataclass
NEXT={(1,1):{(1,0)},(-1,1):{(-1,0)},(1,0):{(1,1),(-1,1)},(-1,0):{(-1,1),(1,1)}}
@dataclass(frozen=True)
class PenState:
    direction:int
    phase:int
    def __post_init__(self):
        if (self.direction,self.phase) not in NEXT:raise ValueError("noncanonical state")
def next_allowed(a,b):
    if not isinstance(a,PenState) or not isinstance(b,PenState):raise ValueError("requires canonical PenState")
    return (b.direction,b.phase) in NEXT[(a.direction,a.phase)]
def replay(states):
    if not states:return "UNKNOWN_NO_CONFIRMED_INPUT"
    if not all(isinstance(s,PenState) for s in states):return "UNKNOWN_NONCANONICAL_INPUT"
    if not all(next_allowed(a,b) for a,b in zip(states,states[1:])):return "INVALID_TRANSITION"
    return "CANONICAL_GRAMMAR_ACCEPTED_NOT_MARKET_PROOF"
def example():
    up=PenState(1,1);candidate=PenState(1,0);down=PenState(-1,1)
    return {"valid":replay([up,candidate,down]),"invalid":replay([up,down]),
            "no_input":replay([]),"canonical_states":len(NEXT),
            "whole_market_coverage_proven":False,"real_market_data":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),ensure_ascii=False,indent=2))
