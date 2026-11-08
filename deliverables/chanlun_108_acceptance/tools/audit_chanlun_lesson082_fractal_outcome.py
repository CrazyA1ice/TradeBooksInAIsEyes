#!/usr/bin/env python3
"""Append-only after-fractal outcome; cannot backdate future continuation or pen."""
from dataclasses import dataclass,field
@dataclass
class Candidate:
    created_at:int
    history:list=field(default_factory=list)
    state:str="UNOBSERVED"
    def event(self,ts,kind):
        if ts<self.created_at or (self.history and ts<=self.history[-1]["ts"]):
            raise ValueError("non-forward event time")
        transitions={"UNOBSERVED":{"FRACTAL_OBSERVED":"PENDING_OUTCOME"},
                     "PENDING_OUTCOME":{"PEN_COMPLETED":"EXTENDED_TO_PEN","CONTINUATION_CONFIRMED":"CONTINUATION"}}
        if kind not in transitions.get(self.state,{}):raise ValueError("invalid outcome transition")
        self.state=transitions[self.state][kind]
        self.history.append({"ts":ts,"kind":kind,"state":self.state})
        return self.state
def example():
    c=Candidate(1);c.event(2,"FRACTAL_OBSERVED");prior=c.history[0].copy()
    c.event(5,"PEN_COMPLETED")
    return {"first_event_immutable":c.history[0]==prior,
            "first_state":prior["state"],"final":c.state,"history":c.history,
            "full_pen_detector":False,"market_data":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
