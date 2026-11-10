#!/usr/bin/env python3
"""Finite illustrative witnesses for G01 / G05; NOT an implementation of Chanlun."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA="catalog/chanlun_g01_g05_conditional_witnesses_v1.json"
EXPECTED_IDS={*(f"G01-W{i:02d}" for i in range(1,6)),*(f"G05-W{i:02d}" for i in range(1,6))}

def decide(case: dict) -> str:
    a=case["assumptions"]
    if case["gate"]=="G01":
        assert a["member_completion_author_verified"] is False
        assert a["base_center"] is True
        cs=a["children"]
        if len(cs)<3:
            return "BASE_ONLY_NOT_PARENT_CENTER"
        assert len(cs)==3
        for c in cs:
            assert set(c)=={"low","high","complete","confirmed_at"}
            assert type(c["low"]) in (int,float) and type(c["high"]) in (int,float)
            assert c["low"]<=c["high"]
        overlap=max(c["low"] for c in cs)<=min(c["high"] for c in cs)
        if not overlap:
            return "NO_COMMON_OVERLAP"
        if not all(c["complete"] for c in cs):
            return "OVERLAP_WITH_UNCERTIFIED_CHILDREN"
        if not all(type(c["confirmed_at"]) is int and c["confirmed_at"]<=a["as_of"] for c in cs):
            return "ASOF_CHILD_PENDING"
        return "CONDITIONAL_PARENT_OVERLAP_NOT_AUTHOR_CERTIFIED"
    assert case["gate"]=="G05"
    assert a["associativity_asserted"] is True
    assert a["complete_input_assumed"] is True
    p=a["candidate_parses"]
    if not p:
        return "EXISTENCE_NOT_SHOWN"
    for q in p:
        assert set(q)=={"rule_id","cutpoints","assumed_legal"}
        assert q["assumed_legal"] is True
        assert all(type(x) is int and x>0 for x in q["cutpoints"])
        assert q["cutpoints"]==sorted(set(q["cutpoints"]))
    if any(q["rule_id"]!=a["rule_id"] for q in p):
        return "CROSS_RULE_COMPARISON_NOT_COUNTEREXAMPLE"
    if len({tuple(q["cutpoints"]) for q in p})>1:
        return "CONDITIONAL_NONUNIQUENESS_IF_BOTH_LEGAL"
    if len(p)>1:
        return "SAME_CUTPOINTS_NO_COUNTEREXAMPLE"
    return "ONE_ASSUMED_PARSE_NOT_UNIVERSAL_PROOF"

def audit(root=ROOT):
    d=json.loads((root/DATA).read_text(encoding="utf-8"))
    assert d["schema_version"]==1 and d["book"]=="chanlun"
    assert d["scope"]=="FINITE_SYNTHETIC_CONDITIONAL_WITNESSES_NOT_FULL_AUTHOR_RULE"
    assert d["role"]=="AI_TESTS_LOGICAL_NON_ENTAILMENT_NOT_AUTHOR_MARKET_VALIDATION"
    assert set(d["linked_gates"])=={"G01","G05"}
    assert d["proof_status"]=="OPEN"
    assert d["market_backtest"]==d["image_review"]=="NOT_RUN"
    assert len(d["cases"])==10
    assert {c["id"] for c in d["cases"]}==EXPECTED_IDS
    uses=0
    for gate, citations in d["source_evidence"].items():
        assert gate in {"G01","G05"} and len(citations)>=3
        for s in citations:
            assert set(s)=={"lesson","claim_id","pages"}
            n=s["lesson"]
            actual=json.loads((root/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8"))
            matches=[x for x in actual["claims"] if x.get("id")==s["claim_id"]]
            assert len(matches)==1 and matches[0]["kind"]=="SOURCE"
            assert matches[0]["pdf_pages"]==s["pages"]
            uses+=1
    decisions={}
    for c in d["cases"]:
        assert set(c)=={"id","gate","scenario","assumptions","expected","reason"}
        assert c["gate"] in {"G01","G05"}
        assert c["id"].startswith(c["gate"]+"-")
        assert isinstance(c["scenario"],str) and len(c["scenario"])>=12
        assert isinstance(c["reason"],str) and len(c["reason"])>=12
        status=decide(c)
        assert status==c["expected"],(c["id"],status,c["expected"])
        decisions[c["id"]]=status
    assert decisions["G01-W03"]=="CONDITIONAL_PARENT_OVERLAP_NOT_AUTHOR_CERTIFIED"
    assert decisions["G05-W01"]=="CONDITIONAL_NONUNIQUENESS_IF_BOTH_LEGAL"
    return {"status":"G01_G05_CONDITIONAL_WITNESS_AUDIT_PASSED","cases":10,"source_claim_uses":uses,"gates":2,"proof":"OPEN","market":"NOT_RUN"}

if __name__=="__main__":
    print("G01_G05_WITNESSES="+json.dumps(audit(),ensure_ascii=False,sort_keys=True))
