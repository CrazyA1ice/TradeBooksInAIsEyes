#!/usr/bin/env python3
"""Source-cued *conditional* G01/G05 rule contract: NOT a complete Chanlun parser."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA="catalog/chanlun_g01_g05_typed_rule_contract_v1.json"
G01_VERSION="TEXTUAL_67_71_78"
POLICIES={"UNSPECIFIED","LEXICOGRAPHIC_AI_ONLY"}

def evaluate(case: dict) -> tuple[str, list[int] | None]:
    a=case["input"]
    if case["gate"]=="G01":
        assert a["rule_version"]==G01_VERSION
        assert type(a["as_of"]) is int and a["as_of"]>=0
        for field in ("strict_feature_membership","local_l67_pattern","gap_branch"):
            assert type(a[field]) is bool
        for field in ("opposite_fractal_confirmed_at","opposite_segment_legality_assumed_at"):
            assert a[field] is None or (type(a[field]) is int and a[field]>=0)
        if not a["strict_feature_membership"]:
            return "INVALID_FEATURE_SCOPE",None
        if not a["local_l67_pattern"]:
            return "PENDING_LOCAL_PATTERN",None
        if a["gap_branch"] and (a["opposite_fractal_confirmed_at"] is None or a["opposite_fractal_confirmed_at"]>a["as_of"]):
            return "PENDING_GAP_OPPOSITE_FRACTAL",None
        if a["opposite_segment_legality_assumed_at"] is None or a["opposite_segment_legality_assumed_at"]>a["as_of"]:
            return ("PENDING_LEGAL_REVERSE_SEGMENT" if a["gap_branch"] else "LOCAL_PATTERN_ONLY"),None
        return "EXTERNAL_REVERSE_SEGMENT_ASSUMED_NOT_FINISHED_LOWER_TYPE",None
    assert case["gate"]=="G05"
    assert isinstance(a["rule_version"],str) and a["rule_version"].startswith("R_STUDY_")
    assert type(a["input_complete"]) is bool
    assert a["tie_policy"] in POLICIES
    assert isinstance(a["candidate_cutpoints"],list)
    for cuts in a["candidate_cutpoints"]:
        assert isinstance(cuts,list) and all(type(i) is int and i>0 for i in cuts)
        assert cuts==sorted(set(cuts))
    if not a["input_complete"]:
        return "WAIT_COMPLETE_INPUT",None
    distinct=sorted({tuple(cuts) for cuts in a["candidate_cutpoints"]})
    if not distinct:
        return "NO_CANDIDATE_EXISTENCE_OPEN",None
    if len(distinct)==1:
        return "ONE_ASSUMED_PARSE_NO_UNIVERSAL_PROOF",None
    if a["tie_policy"]=="UNSPECIFIED":
        return "MULTIPLE_ASSUMED_PARSES_UNRESOLVED",None
    return "AI_ONLY_DETERMINISTIC_SELECTION_NOT_AUTHOR_UNIQUENESS",list(distinct[0])

def audit(root: Path=ROOT) -> dict:
    d=json.loads((root/DATA).read_text(encoding="utf-8"))
    assert d["schema_version"]==1 and d["book"]=="chanlun"
    assert d["scope"]=="FINITE_ASSUMPTION_TYPED_TRANSITION_AND_NORMALIZATION_PRECONDITIONS_NOT_FULL_CHANLUN"
    assert d["role"]=="AI_RESEARCH_CONTRACT_NOT_AUTHOR_CERTIFICATION"
    assert d["proof_status"]=="OPEN" and d["market_backtest"]==d["image_review"]=="NOT_RUN"
    for contract, prohibited in ((d["g01_contract"],"AUTHOR_AUTHENTICATED_FINISHED_CHILD"),(d["g05_contract"],"OB38_PROVEN")):
        assert prohibited in contract["prohibited_outputs"]
        assert "not" in contract["identity_note"].lower() or "不能" in contract["identity_note"]
    assert set(d["prior_contracts"]) >= {
        "catalog/chanlun_f01_typed_completion_obligations_v1.json",
        "catalog/chanlun_f01_segment_termination_reconciliation_v1.json",
        "catalog/chanlun_rule_history_v1.json"
    }
    for p in d["prior_contracts"]:
        assert (root/p).is_file(),p
    assert len(d["cases"])==12 and len({x["id"] for x in d["cases"]})==12
    assert {x["id"] for x in d["cases"]}=={
        *(f"G01-T{i:02d}" for i in range(1,7)),
        *(f"G05-T{i:02d}" for i in range(1,7))
    }
    uses=0
    for gate,cues in d["evidence"].items():
        assert gate in ("G01","G05") and len(cues)>=5
        for cue in cues:
            assert set(cue)=={"lesson","claim_id","pages"}
            n=cue["lesson"]
            assert type(n) is int and 1<=n<=108
            src=json.loads((root/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8"))
            matching=[x for x in src["claims"] if x.get("id")==cue["claim_id"]]
            assert len(matching)==1 and matching[0].get("kind")=="SOURCE"
            assert matching[0]["pdf_pages"]==cue["pages"]
            uses+=1
    for case in d["cases"]:
        assert set(case) in ({"id","gate","scenario","input","expected"},{"id","gate","scenario","input","expected","ai_selected"})
        assert case["id"].startswith(case["gate"]+"-")
        assert isinstance(case["scenario"],str) and len(case["scenario"])>=14
        status,selected=evaluate(case)
        assert status==case["expected"],(case["id"],status,case["expected"])
        assert selected==case.get("ai_selected"),case["id"]
        if case["gate"]=="G01":
            assert status in d["g01_contract"]["states"]
        else:
            assert status in d["g05_contract"]["states"]
    return {"status":"TYPED_G01_G05_RULE_CONTRACT_AUDIT_PASSED","cases":12,"source_uses":uses,"proof":"OPEN","market":"NOT_RUN"}

if __name__=="__main__":
    print("RULE_CONTRACT_AUDIT="+json.dumps(audit(),ensure_ascii=False,sort_keys=True))
