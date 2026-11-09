#!/usr/bin/env python3
"""Provenance labels only; no operational market-manipulation content."""
from dataclasses import dataclass
ROLES={"AUTHOR_STORY","SELF_ASSERTED_LEGALITY","EDITORIAL_NOTE","DATED_LATER_POST","EXTERNAL_REGULATORY_FINDING"}
@dataclass(frozen=True)
class Record:
    role:str
    page:int
    date:str
    independent_document:bool=False
    def __post_init__(self):
        if self.role not in ROLES or self.page<1:raise ValueError("invalid source role/page")
def classify(record):
    if record.role=="DATED_LATER_POST":return "SEPARATE_DATED_SOURCE"
    if record.role=="EDITORIAL_NOTE":return "EDITORIAL_NOT_AUTHOR"
    if record.role=="SELF_ASSERTED_LEGALITY":return "LEGALITY_NOT_INDEPENDENTLY_ESTABLISHED"
    if record.role=="AUTHOR_STORY":return "UNVERIFIED_FIRST_PERSON"
    return "CITABLE_EXTERNAL_FINDING" if record.independent_document else "UNVERIFIED_EXTERNAL_REFERENCE"
def example():
    return {"legal":classify(Record("SELF_ASSERTED_LEGALITY",338,"2007-10-22")),
            "story":classify(Record("AUTHOR_STORY",338,"2007-10-22")),
            "next_day":classify(Record("DATED_LATER_POST",340,"2007-10-23")),
            "orders_sent":False,"legal_verdict_inferred":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
