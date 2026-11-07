#!/usr/bin/env python3
"""Append-only candidate revisions, and local center-branch events; no actual market parser."""
from dataclasses import dataclass,field
@dataclass
class EvidenceLog:
    events:list=field(default_factory=list)
    states:dict=field(default_factory=dict)
    def record(self,t,object_id,action,new_id=None):
        if self.events and t<=self.events[-1]["time"]:raise ValueError("time must advance")
        if action=="OPEN":
            if object_id in self.states:raise ValueError("id already exists")
            self.states[object_id]="PENDING"
        elif action in ("CONFIRM","INVALIDATE","REVISE"):
            if self.states.get(object_id)!="PENDING":raise ValueError("only pending object can change")
            if action=="REVISE" and (not new_id or new_id in self.states):
                raise ValueError("new version id required")
            self.states[object_id]={"CONFIRM":"CONFIRMED","INVALIDATE":"INVALIDATED","REVISE":"REVISED"}[action]
            if action=="REVISE":self.states[new_id]="PENDING"
        else:raise ValueError("invalid action")
        entry={"time":t,"object_id":object_id,"action":action,"new_id":new_id}
        self.events.append(entry)
        return entry.copy()
@dataclass
class CenterBranch:
    state:str="PENDING"
    def observe(self,event):
        states={"THIRD_BUY_CONFIRMED":"THIRD_BUY_UP","THIRD_SELL_CONFIRMED":"THIRD_SELL_DOWN","EXTENSION_CONFIRMED":"EXTENSION"}
        if event not in states:raise ValueError("unknown event")
        if self.state!="PENDING":raise ValueError("already decided this branch epoch")
        self.state=states[event]
        return self.state
def example():
    x=EvidenceLog()
    x.record(1,"monthly-fractal-1","OPEN")
    first=x.events[0].copy()
    x.record(2,"monthly-fractal-1","REVISE",new_id="monthly-fractal-2")
    x.record(3,"monthly-fractal-2","CONFIRM")
    center=CenterBranch()
    center.observe("EXTENSION_CONFIRMED")
    assert first==x.events[0]
    return {"immutable_history":x.events,"current_states":x.states,
            "center_branch":center.state,"real_orders_sent":False,"complete_market_parser":False}
if __name__=="__main__":
    import json
    print(json.dumps(example(),indent=2))
