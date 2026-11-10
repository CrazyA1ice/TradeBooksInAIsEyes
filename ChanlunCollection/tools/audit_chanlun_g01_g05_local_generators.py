#!/usr/bin/env python3
"""Composed local lesson 67/71 gates + exhaustive *assumption-scoped* cut enumeration.

The supplied G05 admissible-span table is NOT generated from the author's full
same-level grammar. This is not F01 certification, OB38 proof, or market research.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_chanlun_lesson067_feature_gap as lesson67
import audit_chanlun_lesson071_typed_membership as lesson71

DATA = "catalog/chanlun_g01_g05_local_generators_v1.json"
ALLOWED_G01 = {
    "FEATURE_NOT_YET_ASOF", "INVALID_STRICT_MEMBER", "PENDING_THREE_FEATURES",
    "NOT_EXPECTED_FRACTAL", "PENDING_OPPOSITE",
    "LOCAL_NO_GAP_NOT_SEGMENT_CERTIFIED", "LOCAL_GAP_NOT_SEGMENT_CERTIFIED"
}
ALLOWED_G05 = {
    "WAIT_COMPLETE_INPUT", "NO_PARSE_UNDER_EXTERNAL_SPANS",
    "ONE_PARSE_UNDER_EXTERNAL_SPANS", "MULTIPLE_PARSES_UNDER_EXTERNAL_SPANS"
}

def local_feature_candidate(x):
    """Generate a local candidate by composing existing 67 and 71 primitives."""
    assert set(x) == {"as_of", "expected", "sequence_id", "features", "opposite_index"}
    assert type(x["as_of"]) is int and x["as_of"] >= 0
    assert x["expected"] in ("TOP", "BOTTOM")
    assert type(x["sequence_id"]) is str and x["sequence_id"]
    features = x["features"]
    assert isinstance(features, list) and len(features) <= 3
    assert x["opposite_index"] is None or (type(x["opposite_index"]) is int and x["opposite_index"] >= 0)
    built = []
    previous_index = -1
    for item in features:
        assert set(item) == {"index", "low", "high", "sequence_id", "role", "confirmed_at"}
        idx, confirmed = item["index"], item["confirmed_at"]
        assert type(idx) is int and idx > previous_index and type(confirmed) is int and confirmed >= idx
        previous_index = idx
        assert type(item["low"]) in (int, float) and type(item["high"]) in (int, float)
        assert item["low"] <= item["high"]
        el = lesson71.Element(item["sequence_id"], item["role"], item["low"], item["high"], confirmed)
        if el.role != "STRICT" or el.sequence_id != x["sequence_id"]:
            return {"status": "INVALID_STRICT_MEMBER", "candidate_at": None}
        built.append(lesson67.Feature(item["low"], item["high"], idx))
    if len(built) < 3:
        return {"status": "PENDING_THREE_FEATURES", "candidate_at": None}
    if any(item["confirmed_at"] > x["as_of"] for item in features):
        return {"status": "FEATURE_NOT_YET_ASOF", "candidate_at": None}
    opposite = x["opposite_index"]
    observed = opposite is not None and opposite <= x["as_of"]
    result = lesson67.classify(built, x["expected"], observed, opposite if observed else None)
    status = result["status"]
    if status == "NOT_EXPECTED_FRACTAL":
        return {"status": status, "candidate_at": None}
    if status == "PENDING_OPPOSITE":
        return {"status": status, "candidate_at": None}
    assert status in ("LOCAL_END_CONDITION_WITH_GAP", "LOCAL_END_CONDITION_NO_GAP")
    return {
        "status": "LOCAL_GAP_NOT_SEGMENT_CERTIFIED" if result["gap_first_second"] else "LOCAL_NO_GAP_NOT_SEGMENT_CERTIFIED",
        "candidate_at": max(result["confirmed_at"], max(z["confirmed_at"] for z in features)),
    }

def enumerate_conditional_parses(x):
    """Exhaustively enumerate cutpoints under *declared* allowed spans only."""
    assert set(x) == {"n", "input_complete", "allowed_spans"}
    n = x["n"]
    assert type(n) is int and 1 <= n <= 7
    assert type(x["input_complete"]) is bool
    spans = x["allowed_spans"]
    assert isinstance(spans, list) and len(spans) <= 28
    allowed = set()
    for pair in spans:
        assert isinstance(pair, list) and len(pair) == 2
        a, b = pair
        assert type(a) is int and type(b) is int and 0 <= a < b <= n
        allowed.add((a, b))
    if not x["input_complete"]:
        return {"status": "WAIT_COMPLETE_INPUT", "cutpoints": []}
    paths = []
    def visit(position, cuts):
        if position == n:
            paths.append(cuts)
            return
        for a, b in sorted(allowed):
            if a == position:
                visit(b, cuts + ([b] if b < n else []))
    visit(0, [])
    assert len(paths) <= 128, "Input exceeds bounded research enumeration"
    assert len(paths) == len({tuple(p) for p in paths})
    if not paths:
        status = "NO_PARSE_UNDER_EXTERNAL_SPANS"
    elif len(paths) == 1:
        status = "ONE_PARSE_UNDER_EXTERNAL_SPANS"
    else:
        status = "MULTIPLE_PARSES_UNDER_EXTERNAL_SPANS"
    return {"status": status, "cutpoints": sorted(paths)}

def audit(root=ROOT):
    doc = json.loads((root / DATA).read_text(encoding="utf-8"))
    assert doc["schema_version"] == 1 and doc["book"] == "chanlun"
    assert doc["role"] == "AI_COMPOSITION_AND_DECLARED_SPAN_ENUMERATOR_NOT_AUTHOR_PARSER"
    assert doc["proof_status"] == "OPEN"
    assert doc["image_review"] == doc["market_backtest"] == "NOT_RUN"
    assert doc["source_scope"] == "EXISTING_SOURCE_CARDS_ONLY"
    assert (root / doc["prior_contract"]).is_file()
    for name in ("tools/audit_chanlun_lesson067_feature_gap.py", "tools/audit_chanlun_lesson071_typed_membership.py"):
        assert (root / name).is_file()
    source_count = 0
    for entry in doc["source_evidence"]:
        assert set(entry) == {"lesson", "claim_id", "pages"}
        lesson = entry["lesson"]
        card = json.loads((root / f"knowledge/evidence/chanlun_lesson{lesson:03d}.json").read_text(encoding="utf-8"))
        matches = [claim for claim in card["claims"] if claim["id"] == entry["claim_id"]]
        assert len(matches) == 1 and matches[0]["kind"] == "SOURCE"
        assert matches[0]["pdf_pages"] == entry["pages"]
        source_count += 1
    assert len(doc["cases"]) == 11 and len({c["id"] for c in doc["cases"]}) == 11
    assert sum(c["gate"] == "G01" for c in doc["cases"]) == 6
    assert sum(c["gate"] == "G05" for c in doc["cases"]) == 5
    for case in doc["cases"]:
        assert set(case) == {"id", "gate", "input", "expected", "research_note"}
        assert len(case["research_note"]) >= 12
        assert case["id"].startswith(case["gate"] + "-")
        result = local_feature_candidate(case["input"]) if case["gate"] == "G01" else enumerate_conditional_parses(case["input"])
        assert result == case["expected"], (case["id"], result, case["expected"])
        assert result["status"] in (ALLOWED_G01 if case["gate"] == "G01" else ALLOWED_G05)
    return {"status": "LOCAL_GENERATORS_SOURCE_AND_REGRESSION_PASS",
            "cases": len(doc["cases"]), "source_uses": source_count,
            "author_parser": "NOT_IMPLEMENTED", "proof": "OPEN"}

if __name__ == "__main__":
    print("LOCAL_GENERATORS=" + json.dumps(audit(), ensure_ascii=False, sort_keys=True))
