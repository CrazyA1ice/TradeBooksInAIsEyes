#!/usr/bin/env python3
"""Audit author-source anchors and open construction proof gates; not a proof engine."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA="catalog/chanlun_recursive_construction_proof_chain_v1.json"
STEP_IDS={f"P{i:02d}" for i in range(1,10)}
GATE_IDS={f"G{i:02d}" for i in range(1,7)}
CUES="EXISTING_SOURCE_CARD_ONLY_NOT_FRESH_PDF_RECHECK"

def audit(root=ROOT):
    d=json.loads((root/DATA).read_text(encoding="utf-8"))
    assert d["schema_version"]==1 and d["book"]=="chanlun"
    assert d["scope"]=="EXISTING_TEXT_SOURCE_CARDS_ONLY"
    assert d["identity"]=="AI_RECONSTRUCTED_PROOF_CHAIN_NOT_AUTHOR_COMPLETE_PROOF"
    assert d["image_review"]==d["market_backtest"]=="NOT_RUN"
    steps=d["steps"];gates=d["gates"]
    assert len(steps)==9 and {s["id"] for s in steps}==STEP_IDS
    assert len(gates)==6 and {g["id"] for g in gates}==GATE_IDS
    usage=0
    for step in steps:
        assert set(step)=={"id","title","role","evidence","author_cue","proof_requirement","non_entailment","validation"}
        assert step["role"].startswith("AI_SYNTHESIS_OF_")
        assert step["validation"]==CUES
        assert isinstance(step["title"],str) and len(step["title"].strip())>=4,(step["id"],"title")
        for k in ("author_cue","proof_requirement","non_entailment"):
            assert isinstance(step[k],str) and len(step[k].strip())>=10,(step["id"],k)
        assert step["evidence"] and len({(a["lesson"],a["claim_id"]) for a in step["evidence"]})==len(step["evidence"])
        for a in step["evidence"]:
            assert set(a)=={"lesson","claim_id","physical_pages"}
            n=a["lesson"]
            assert type(n) is int and 1<=n<=108
            source=json.loads((root/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8"))
            matches=[x for x in source["claims"] if x.get("id")==a["claim_id"]]
            assert len(matches)==1 and matches[0].get("kind")=="SOURCE",(step["id"],a["claim_id"])
            assert matches[0]["pdf_pages"]==a["physical_pages"],(step["id"],a["claim_id"])
            usage+=1
    for gate in gates:
        assert set(gate)=={"id","from","to","relation","missing","frontier","status"}
        assert gate["from"] in STEP_IDS and gate["to"] in STEP_IDS and gate["from"]!=gate["to"]
        assert gate["status"]=="OPEN_NOT_DISPROVEN_AND_NOT_PROVEN"
        assert gate["frontier"] in {"F01","OB38","OB38_F01"}
        assert isinstance(gate["missing"],str) and len(gate["missing"])>=18
    assert {g["frontier"] for g in gates}>={"F01","OB38"}
    return {"status":"RECURSIVE_PROOF_CHAIN_TEXT_AUDIT_PASSED","steps":9,"gates":6,"source_uses":usage,"proof":"OPEN","market":"NOT_RUN"}

if __name__=="__main__":
    print("RECURSIVE_CHAIN_AUDIT="+json.dumps(audit(),sort_keys=True,ensure_ascii=False))
