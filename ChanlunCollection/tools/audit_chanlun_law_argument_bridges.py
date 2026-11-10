#!/usr/bin/env python3
"""Conservative cross-card bridge and SOURCE provenance validator, text only."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGES = "catalog/chanlun_author_law_argument_bridges_v1.json"
CARDS = "catalog/chanlun_author_law_cards_v1.json"
ROLE = "AI_CROSS_LESSON_INTERPRETIVE_BRIDGE_NOT_AUTHOR_THEOREM"
VALIDATION = "EXISTING_SOURCE_CARD_CLAIM_AND_PAGE_ONLY"
ALLOWED = {
    "methodological_prerequisite", "definition_prerequisite",
    "structural_state_transition", "contextual_not_implication",
    "context_classification", "conditional_interpretation",
    "retest_branch", "multilevel_refinement", "asof_information_gate",
    "rule_version_gate", "decision_separation", "risk_execution_gate",
    "feedback_cycle"
}


def audit(root: Path, expected_count: int = 13) -> dict:
    b = json.loads((root / BRIDGES).read_text(encoding="utf-8"))
    c = json.loads((root / CARDS).read_text(encoding="utf-8"))
    assert b.get("schema_version") == 1 and b.get("book") == "chanlun"
    assert b.get("scope") == "text_only" and b.get("status") == "interpretive_bridges_not_verified_entailments"
    cards = {x["id"]: x for x in c["cards"]}
    edges = b["edges"]
    assert len(edges) == expected_count
    seen = set()
    anchor_count = 0
    for edge in edges:
        eid = edge["id"]
        assert eid not in seen and eid.startswith("CL-BRIDGE-"), eid
        seen.add(eid)
        assert set(edge) == {
            "id", "from", "to", "relation", "identity", "why", "how",
            "not_implied", "evidence", "validation"
        }, eid
        a, z = edge["from"], edge["to"]
        assert a in cards and z in cards and a != z, eid
        assert z in cards[a]["links_to"], (eid, "edge not in registered law card links")
        assert edge["identity"] == ROLE and edge["validation"] == VALIDATION, eid
        assert edge["relation"] in ALLOWED, eid
        for key in ("why", "how", "not_implied"):
            assert isinstance(edge[key], str) and len(edge[key].strip()) >= 12, (eid, key)
        assert isinstance(edge["evidence"], list) and edge["evidence"], eid
        assert len({(v["lesson"], v["claim_id"]) for v in edge["evidence"]}) == len(edge["evidence"]), eid
        permitted = {
            (v["lesson"], v["claim_id"]): v
            for card in (cards[a], cards[z]) for v in card["source_assertions"]
        }
        for v in edge["evidence"]:
            assert set(v) == {"claim_id", "lesson", "physical_pages"}, eid
            key = (v["lesson"], v["claim_id"])
            assert key in permitted, (eid, "unanchored SOURCE evidence", key)
            assert v["physical_pages"] == permitted[key]["physical_pages"], (eid, "page mismatch", key)
            source = root / f"knowledge/evidence/chanlun_lesson{v['lesson']:03d}.json"
            assert source.is_file(), (eid, "missing source", source)
            card = json.loads(source.read_text(encoding="utf-8"))
            matches = [claim for claim in card["claims"] if claim["id"] == v["claim_id"]]
            assert len(matches) == 1 and matches[0]["kind"] == "SOURCE", (eid, key)
            assert matches[0]["pdf_pages"] == v["physical_pages"], (eid, key)
            anchor_count += 1
    # Reachability is about navigable research organization, not a proof of entailment.
    reachable = {"CL-LAW-001"}
    while True:
        next_reach = reachable | {e["to"] for e in edges if e["from"] in reachable}
        if next_reach == reachable:
            break
        reachable = next_reach
    assert reachable == set(cards), ("incomplete research navigation", sorted(set(cards) - reachable))
    return {
        "status": "CHANLUN_ARGUMENT_BRIDGES_TEXT_SOURCE_AUDIT_PASSED",
        "bridges": len(edges), "evidence_occurrences": anchor_count,
        "reachable_cards": len(reachable), "market_backtest": "NOT_RUN",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=ROOT, type=Path)
    args = parser.parse_args()
    print("ARGUMENT_BRIDGE_AUDIT=" + json.dumps(audit(args.root), ensure_ascii=False, sort_keys=True))
