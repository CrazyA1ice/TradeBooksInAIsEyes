#!/usr/bin/env python3
"""Conservative evidence eligibility on synthetic inputs; never author-rule certification."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA="catalog/chanlun_g01_g05_evidence_eligibility_v1.json"

def evaluate(c):
    x=c["input"]
    if c["gate"]=="G01":
        assert x["rule_version"]=="AUTHOR_67_71_78_TEXT_SCOPE"
        fs=x["features"]
        assert len(fs)==3
        assert len({a["id"] for a in fs})==3
        assert all(a["role"] in ("STRICT","AUXILIARY") for a in fs)
        if any(a["role"]!="STRICT" or a["sequence_id"]!=x["sequence_id"] for a in fs):
            return "INVALID_STRICT_SEQUENCE"
        if any(a["confirmed_at"]>x["as_of"] for a in fs):
            return "FEATURE_NOT_YET_ASOF"
        rev=x["opposite_segment"]
        if rev is None:
            return "PENDING_REVERSE_SEGMENT_EVIDENCE"
        assert rev["externally_declared"] is True
        if rev["confirmed_at"]>x["as_of"] or not rev["construction_evidence"]:
            return "EXTERNAL_REVERSE_UNVERIFIED"
        return "LOCAL_REVERSE_EVIDENCE_NOT_AUTHOR_CERTIFIED"
    assert c["gate"]=="G05"
    assert x["rule_version"]=="R38_RESEARCH_FROZEN_PARTIAL"
    assert x["input_complete"] is True
    ss=x["segments"]
    assert ss and all(s["rule_version"]==x["rule_version"] for s in ss)
    assert all(s["cutpoints"]==sorted(set(s["cutpoints"])) for s in ss)
    if any(s["source_role"]=="AI_CONVENTION" for s in ss):
        return "AI_ONLY_PARSE_NOT_AUTHOR_ELIGIBLE"
    assert all(s["source_role"]=="EXTERNAL_ASSUMPTION" for s in ss)
    if any(not s["complete"] for s in ss):
        return "INCOMPLETE_CANDIDATE_PENDING"
    distinct={tuple(s["cutpoints"]) for s in ss}
    if len(distinct)==1:
        return "SAME_CUTPOINTS_NOT_UNIVERSAL_UNIQUENESS"
    assert len(distinct)>1
    if x["tie_status"]=="AI_LEXICOGRAPHIC":
        return "AI_SELECTION_NOT_AUTHOR_CONFLUENCE"
    assert x["tie_status"]=="UNRESOLVED"
    return "COMPETING_CUTPOINTS_RULE_UNPROVEN"

def audit(root=ROOT):
    d=json.loads((root/DATA).read_text(encoding="utf-8"))
    assert d["scope"]=="PARTIAL_TYPED_EVIDENCE_ELIGIBILITY_NOT_COMPLETE_AUTHOR_RULE"
    assert d["role"]=="AI_CONSERVATIVE_INTERPRETATION_NOT_AUTHOR_CERTIFICATION"
    assert d["proof_status"]=="OPEN" and d["market_backtest"]==d["image_review"]=="NOT_RUN"
    assert (root/d["prior_contract"]).is_file()
    assert len(d["cases"])==11
    assert len({c["id"] for c in d["cases"]})==11
    assert sum(c["gate"]=="G01" for c in d["cases"])==6
    assert sum(c["gate"]=="G05" for c in d["cases"])==5
    assert len(d["limitations"])>=3
    uses=0
    for gate,refs in d["source_evidence"].items():
        assert gate in ("G01","G05") and len(refs)>=4
        for r in refs:
            assert set(r)=={"lesson","claim_id","pages"}
            n=r["lesson"]
            obj=json.loads((root/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8"))
            matches=[v for v in obj["claims"] if v["id"]==r["claim_id"]]
            assert len(matches)==1 and matches[0]["kind"]=="SOURCE"
            assert matches[0]["pdf_pages"]==r["pages"]
            uses+=1
    for c in d["cases"]:
        assert c["id"].startswith(c["gate"]+"-")
        assert len(c["summary"])>=12
        assert evaluate(c)==c["expected"],(c["id"],evaluate(c),c["expected"])
        assert not c["expected"].startswith("AUTHOR_CERTIFIED")
    return {"status":"PARTIAL_G01_G05_ELIGIBILITY_AUDIT_PASSED","cases":11,"source_uses":uses,"proof":"OPEN","market":"NOT_RUN"}

if __name__=="__main__":
    print(json.dumps(audit(),ensure_ascii=False,sort_keys=True))
