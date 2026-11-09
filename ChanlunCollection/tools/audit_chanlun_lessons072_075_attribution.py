#!/usr/bin/env python3
"""Role-based provenance: author, later commentary and editorial dispute remain distinct."""
from dataclasses import dataclass
ROLES={"AUTHOR_ORIGINAL","LATER_MARKET_POST","EDITORIAL_NOTE","FIRST_PERSON_ANECDOTE"}
@dataclass(frozen=True)
class ClaimSource:
    lesson:int
    pdf_page:int
    role:str
    original_post_date:str
    independent_evidence:bool=False
    def __post_init__(self):
        if self.role not in ROLES:raise ValueError("unknown source role")
def attribute(c):
    if c.role=="FIRST_PERSON_ANECDOTE" and not c.independent_evidence:
        return "UNVERIFIED_NARRATIVE"
    if c.role=="EDITORIAL_NOTE":
        return "EDITORIAL_ARGUMENT_NOT_ORIGINAL_AUTHOR"
    if c.role=="LATER_MARKET_POST":
        return "SEPARATE_DATED_POST"
    return "SOURCE_STATED_NOT_INDEPENDENTLY_VALIDATED" if not c.independent_evidence else "INDEPENDENT_EVIDENCE_PRESENT"
def example():
    a=ClaimSource(72,85,"EDITORIAL_NOTE","2007-08-21")
    b=ClaimSource(72,88,"LATER_MARKET_POST","2007-08-21 15:59:25")
    c=ClaimSource(75,121,"FIRST_PERSON_ANECDOTE","2007-08-29")
    return {"editor":attribute(a),"later":attribute(b),"anecdote":attribute(c),
            "regulatory_finding_inferred":False,"market_data_used":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),ensure_ascii=False,indent=2))
