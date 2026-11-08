#!/usr/bin/env python3
"""Append-only transition with explicit center-component/movement-type separation."""
from dataclasses import dataclass,field
@dataclass
class Transition:
    history:list=field(default_factory=list)
    state:str="OLD_CONTEXT_ACTIVE"
    def record(self,t,action):
        if self.history and t<=self.history[-1][0]:raise ValueError("non-monotonic time")
        allowed={"OLD_CONTEXT_ACTIVE":{"OLD_END_CANDIDATE":"TRANSITION_PENDING"},
                 "TRANSITION_PENDING":{"NEW_STRUCTURE_CONFIRMED":"NEW_CONTEXT_CONFIRMED"}}
        if action not in allowed.get(self.state,{}):raise ValueError("invalid transition")
        self.state=allowed[self.state][action]
        self.history.append((t,action,self.state))
        return self.state
def classify_geometry(center_count,complete):
    if not isinstance(center_count,int) or center_count<0:raise ValueError("center count")
    if not complete:return "MOVEMENT_PENDING"
    if center_count==1:return "CONSOLIDATION_MOVEMENT"
    if center_count>=2:return "MULTICENTER_MOVEMENT_CANDIDATE"
    return "NO_COMPLETED_CENTER"
def example():
    s=Transition();s.record(10,"OLD_END_CANDIDATE")
    snapshot=s.history[0]
    s.record(20,"NEW_STRUCTURE_CONFIRMED")
    return {"first_event_unchanged":s.history[0]==snapshot,"state":s.state,
            "transition_history":s.history,"one_center":classify_geometry(1,True),
            "unconfirmed":classify_geometry(1,False),
            "center_is_component_not_movement":True,"full_geometry_parser":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
