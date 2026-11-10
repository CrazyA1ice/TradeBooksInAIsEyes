#!/usr/bin/env python3
"""Text-only, fail-closed classification audit for author-claim logical modality."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = "catalog/chanlun_claim_modality_v1.json"
CARDS = "catalog/chanlun_author_law_cards_v1.json"
VALID = {
    "DEFINITION", "NECESSARY_ONLY", "CONDITIONAL_CLASSIFICATION",
    "CONDITIONAL_BRANCH", "HEURISTIC", "OPERATING_GUIDANCE",
    "AUTHOR_STRONG_CLAIM_UNPROVEN",
}
REQUIRED = {
    "id", "title", "modality", "interpretation_role", "claim",
    "preconditions", "not_sufficient", "source_claims", "law_card", "empirical_status",
}
ROLE = "AI_CLASSIFICATION_OF_EXISTING_SOURCE_CLAIMS_NOT_AUTHOR_FORMAL_PROOF"
EDITOR = ("27", "CL027-S04")

def audit(root: Path = ROOT) -> dict:
    doc = json.loads((root / DATA).read_text(encoding="utf-8"))
    assert doc["schema_version"] == 1 and doc["book"] == "chanlun"
    assert doc["source_scope"] == "EXISTING_TEXT_EVIDENCE_CARDS_ONLY"
    assert "NECESSARY_ONLY_IS_NOT_SUFFICIENT" in doc["classification_rule"]
    cards = doc["classes"]
    assert len(cards) == 16, "Unexpected classification count"
    lawids = {x["id"] for x in json.loads((root / CARDS).read_text(encoding="utf-8"))["cards"]}
    assert len({x["id"] for x in cards}) == len(cards)
    seen = set()
    claims = 0
    for c in cards:
        assert set(c) == REQUIRED, c.get("id")
        assert c["id"].startswith("CL-MODAL-")
        assert c["modality"] in VALID
        assert c["interpretation_role"] == ROLE
        assert c["law_card"] in lawids
        assert c["empirical_status"] == "NOT_RUN"
        for field in ("title", "claim", "preconditions", "not_sufficient"):
            minimum = 4 if field == "title" else 8
            assert isinstance(c[field], str) and len(c[field].strip()) >= minimum, (c["id"], field)
        assert c["source_claims"]
        local_seen = set()
        for r in c["source_claims"]:
            assert set(r) == {"lesson", "id"}
            n, cid = r["lesson"], r["id"]
            assert type(n) is int and 1 <= n <= 108
            assert isinstance(cid, str) and cid
            assert (n, cid) not in local_seen
            local_seen.add((n,cid))
            path = root / f"knowledge/evidence/chanlun_lesson{n:03d}.json"
            obj = json.loads(path.read_text(encoding="utf-8"))
            matches = [x for x in obj["claims"] if x.get("id") == cid]
            assert len(matches) == 1 and matches[0].get("kind") == "SOURCE", (c["id"], n, cid)
            assert matches[0].get("pdf_pages"), (c["id"], cid)
            seen.add((n,cid))
            claims += 1
    warnings = doc["editorial_exceptions"]
    assert isinstance(warnings, list) and warnings
    assert any(x.get("lesson") == 27 and x.get("claim_id") == "CL027-S04"
        and x.get("role") == "EDITORIAL_NOTICE_IN_SOURCE_SUMMARY"
        and len(x.get("warning","")) >= 20 for x in warnings)
    assert (27, "CL027-S04") in seen
    assert {x["modality"] for x in cards} == VALID
    assert all(c["modality"] == "AUTHOR_STRONG_CLAIM_UNPROVEN"
        for c in cards if c["id"] in ("CL-MODAL-12","CL-MODAL-13"))
    return {"status":"CLAIM_MODALITY_TEXT_ONLY_SOURCE_AUDIT_PASSED",
            "classifications":len(cards),"evidence_uses":claims,
            "distinct_source_claims":len(seen),"modalities":len(VALID),
            "market_tests":"NOT_RUN"}

if __name__ == "__main__":
    print("MODALITY_AUDIT="+json.dumps(audit(),ensure_ascii=False,sort_keys=True))
