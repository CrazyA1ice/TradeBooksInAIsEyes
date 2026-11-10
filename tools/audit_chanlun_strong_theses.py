#!/usr/bin/env python3
"""Fail-closed textual provenance and quantifier audit; this is NOT a proof engine."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA="catalog/chanlun_strong_theses_proof_map_v1.json"
THESIS_IDS={"CL-THESIS-17","CL-THESIS-21","CL-THESIS-38","CL-THESIS-99"}
ROLE="AI_PROOF_OBLIGATION_MAP_NOT_FORMAL_THEOREM"
VALID={"AUTHOR_STRONG_CLAIM_WITH_OPEN_FORMAL_PROOF",
       "AUTHOR_STRONG_CLAIM_WITH_OPEN_FORMAL_AND_EMPIRICAL_PROOF"}
FIELDS={"id","name","source","domain","quantifier","candidate_formula",
        "required_inputs","author_reasoning","open_obligations","cannot_derive","status"}
REL_FIELDS={"id","from","to","relation","reason","missing"}

def audit(root=ROOT):
    doc=json.loads((root/DATA).read_text(encoding="utf-8"))
    assert doc["schema_version"]==1 and doc["book"]=="chanlun"
    assert doc["scope"]=="EXISTING_TEXT_SOURCE_CARDS_NOT_FRESH_PDF_RECHECK"
    assert doc["research_role"]==ROLE
    assert doc["market_backtest"]==doc["image_review"]=="NOT_RUN"
    ts=doc["theses"]
    assert len(ts)==4 and {t["id"] for t in ts}==THESIS_IDS
    total=0
    evidence_seen={}
    for t in ts:
        assert set(t)==FIELDS
        assert t["status"] in VALID
        for key in ("name","domain","quantifier","candidate_formula","author_reasoning","cannot_derive"):
            assert isinstance(t[key],str) and len(t[key].strip())>=15,(t["id"],key)
        assert len(t["required_inputs"])>=3 and len(t["open_obligations"])>=3
        assert all(isinstance(x,str) and len(x)>=15 for x in t["open_obligations"])
        assert t["source"] and len({(s["lesson"],s["claim_id"]) for s in t["source"]})==len(t["source"])
        for s in t["source"]:
            assert set(s)=={"lesson","claim_id","pages"}
            n=s["lesson"]
            assert type(n) is int and 1<=n<=108
            if n not in evidence_seen:
                path=root/f"knowledge/evidence/chanlun_lesson{n:03d}.json"
                evidence_seen[n]=json.loads(path.read_text(encoding="utf-8"))
            hits=[c for c in evidence_seen[n]["claims"] if c.get("id")==s["claim_id"]]
            assert len(hits)==1 and hits[0]["kind"]=="SOURCE",(t["id"],s["claim_id"])
            assert hits[0].get("pdf_pages")==s["pages"],(t["id"],s["claim_id"],"wrong physical pages")
            total+=1
    assert len(doc["relations"])==6
    assert len({r["id"] for r in doc["relations"]})==6
    for r in doc["relations"]:
        assert set(r)==REL_FIELDS
        assert r["from"] in THESIS_IDS and r["to"] in THESIS_IDS and r["from"]!=r["to"]
        assert r["relation"] in {"DOES_NOT_ENTAIL","NO_AUTHORED_PROOF_BRIDGE"}
        assert all(isinstance(r[k],str) and len(r[k])>=20 for k in ("reason","missing"))
    assert next(t for t in ts if t["id"]=="CL-THESIS-21")["status"]=="AUTHOR_STRONG_CLAIM_WITH_OPEN_FORMAL_AND_EMPIRICAL_PROOF"
    return {"status":"STRONG_THESES_TEXT_SOURCE_AND_PROOF_BOUNDARY_PASSED",
            "theses":4,"non_entailment_relations":6,"claim_uses":total,
            "proof":"OPEN","market":"NOT_RUN"}

if __name__=="__main__":
    print("STRONG_THESES_AUDIT="+json.dumps(audit(),ensure_ascii=False,sort_keys=True))
