#!/usr/bin/env python3
"""Protect physical analogy's author/date role and mechanical operation's evidence stages."""
from dataclasses import dataclass
@dataclass(frozen=True)
class SourceAssertion:
    role:str
    first_published_at:str
    claim_kind:str
    def __post_init__(self):
        if self.role not in ("ORIGINAL_AUTHOR","LATER_EDITOR"):raise ValueError("unknown provenance")
def theoretical_physics_gate(src,observable_unit=None,independent_measurement=False):
    if src.claim_kind!="MARKET_GEOMETRY_PHYSICS_ANALOGY":raise ValueError("not physics analogy")
    if src.role!="ORIGINAL_AUTHOR" or src.first_published_at!="2008-03-26 15:47:42":
        return "SEPARATE_LATER_EDITORIAL_CLAIM"
    if observable_unit is None or not independent_measurement:return "ANALOGY_ONLY_UNVERIFIED"
    return "OPERATIONAL_PROXY_READY_NOT_PHYSICAL_LAW"
def mechanical_gate(rule_locked,signal_confirmed_at,asof,risk_approved,fill_proved):
    if not rule_locked:return "RULE_UNSPECIFIED"
    if signal_confirmed_at is None or signal_confirmed_at>asof:return "NO_ACTION_PENDING"
    if not risk_approved:return "RISK_REJECTED"
    if not fill_proved:return "ELIGIBLE_NOT_FILLED"
    return "FILL_EVIDENCE_PRESENT_PNL_UNPROVEN"
def example():
    author=SourceAssertion("ORIGINAL_AUTHOR","2008-03-26 15:47:42","MARKET_GEOMETRY_PHYSICS_ANALOGY")
    editor=SourceAssertion("LATER_EDITOR","2010-07-02 11:34:50","MARKET_GEOMETRY_PHYSICS_ANALOGY")
    return {"analogy":theoretical_physics_gate(author),
            "editor_not_author":theoretical_physics_gate(editor,"joule",True),
            "mechanical_without_fill":mechanical_gate(True,2,3,True,False),
            "real_market_test":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
