#!/usr/bin/env python3
"""Validate four source-cued textual comparisons without claiming source-proof certainty."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = "catalog/chanlun_four_core_contrasts_v1.json"
EXPECTED = {"CL-CONTRAST-01", "CL-CONTRAST-02", "CL-CONTRAST-03", "CL-CONTRAST-04"}
FIELDS = {"id", "title", "question", "author_position", "early_later", "method", "counterexample", "non_implication", "source_claims", "editorial_caution", "status"}

def audit(root=ROOT):
    doc = json.loads((root / DATA).read_text(encoding="utf-8"))
    assert doc["scope"] == "EXISTING_TEXT_SOURCE_CARDS_ONLY"
    assert doc["research_role"] == "AI_CROSS_VERSION_COMPARISON_NOT_AUTHOR_PROOF"
    assert doc["market_data"] == doc["image_inspection"] == "NOT_RUN"
    groups = doc["groups"]
    assert len(groups) == 4 and {g["id"] for g in groups} == EXPECTED
    evidence = 0
    sources = {}
    for g in groups:
        assert set(g) == FIELDS, g.get("id")
        assert g["status"].startswith("TEXTUAL_CROSS_LESSON_INTERPRETATION")
        for field in ("title", "question", "author_position", "early_later", "method", "counterexample", "non_implication", "editorial_caution"):
            assert isinstance(g[field], str) and len(g[field].strip()) >= 20, (g["id"], field)
        assert isinstance(g["source_claims"], list) and len(g["source_claims"]) >= 5
        seen = set()
        for r in g["source_claims"]:
            assert set(r) == {"lesson", "id"}
            n, cid = r["lesson"], r["id"]
            assert type(n) is int and 1 <= n <= 108 and isinstance(cid, str)
            assert (n, cid) not in seen
            seen.add((n,cid))
            if n not in sources:
                path = root / f"knowledge/evidence/chanlun_lesson{n:03d}.json"
                sources[n] = json.loads(path.read_text(encoding="utf-8"))
            matches = [c for c in sources[n]["claims"] if c.get("id") == cid]
            assert len(matches) == 1 and matches[0].get("kind") == "SOURCE", (g["id"], cid)
            assert matches[0].get("pdf_pages"), (g["id"], cid)
            evidence += 1
    # An editorially described early definition change must not be called an authored
    # rule at the original date, even when an older source card says kind='SOURCE'.
    g2 = next(g for g in groups if g["id"] == "CL-CONTRAST-02")
    assert {"CL015-S-2", "CL027-S04"} <= {r["id"] for r in g2["source_claims"]}
    assert "编者" in g2["editorial_caution"]
    return {"status": "FOUR_CORE_CONTRAST_SOURCE_AUDIT_PASSED", "groups":4, "claim_uses": evidence, "source_lessons":len(sources), "empirical":"NOT_RUN"}

if __name__ == "__main__":
    print("CONTRAST_AUDIT="+json.dumps(audit(),ensure_ascii=False,sort_keys=True))
