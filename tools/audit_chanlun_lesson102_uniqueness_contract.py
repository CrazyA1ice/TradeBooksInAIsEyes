#!/usr/bin/env python3
"""Proof-obligation example. NOT a counterexample to a fully specified Chanlun parser."""
def uniqueness_gate(candidate_partitions,definition_complete):
    normalized={tuple(tuple(group) for group in partition) for partition in candidate_partitions}
    if not definition_complete:return "NEEDS_COMPLETE_FORMAL_SPEC"
    if not normalized:return "NO_LEGAL_PARSE"
    if len(normalized)>1:return "MULTIPLE_CANDIDATES_REQUIRE_TIEBREAK_PROOF"
    return "UNIQUE_WITHIN_PROVIDED_CANDIDATES_ONLY"
def example():
    p1=[["a","b"],["c","d"]]
    p2=[["a"],["b","c","d"]]
    return {"underspecified":uniqueness_gate([p1,p2],False),
            "two_candidates":uniqueness_gate([p1,p2],True),
            "one_candidate":uniqueness_gate([p1],True),
            "valid_chanlun_parse_tested":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
