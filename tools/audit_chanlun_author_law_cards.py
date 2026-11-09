#!/usr/bin/env python3
"""Conservative text-only provenance and graph audit for Chanlun law cards."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD_PATH = "catalog/chanlun_author_law_cards_v1.json"
EXPECTED_ROLE = "AI_SYNTHESIS_BASED_ON_EXISTING_SOURCE_CARDS"
REQUIRED = {"id", "title", "category", "source_role", "source_lessons", "source_cards", "thesis", "method", "limit", "links_to", "research_status"}


def audit(root: Path, *, expected_count: int | None = 12) -> dict:
    data = json.loads((root / CARD_PATH).read_text(encoding="utf-8"))
    assert data.get("schema_version") == 1 and data.get("book") == "chanlun"
    assert data.get("scope") == "text_only"
    cards = data["cards"]
    assert isinstance(cards, list) and cards
    if expected_count is not None:
        assert len(cards) == expected_count, "Unexpected card count"
    seen: set[str] = set()
    for card in cards:
        assert REQUIRED <= card.keys(), "Missing card fields"
        cid = card["id"]
        assert isinstance(cid, str) and cid.startswith("CL-LAW-") and cid not in seen
        seen.add(cid)
        assert card["source_role"] == EXPECTED_ROLE, cid
        assert card["research_status"] == "TEXTUAL_NOT_EMPIRICALLY_TESTED", cid
        for key in ("title", "thesis", "method", "limit"):
            assert isinstance(card[key], str) and card[key].strip(), (cid, key)
        lessons = card["source_lessons"]
        assert isinstance(lessons, list) and lessons and len(set(lessons)) == len(lessons)
        assert all(type(n) is int and 1 <= n <= 108 for n in lessons)
        expected = [f"knowledge/evidence/chanlun_lesson{n:03d}.json" for n in lessons]
        assert card["source_cards"] == expected, cid
        for p, lesson in zip(expected, lessons):
            f = root / p
            assert f.is_file(), f"{cid} missing source: {p}"
            source = json.loads(f.read_text(encoding="utf-8"))
            number = source.get("source", {}).get("lesson_number", source.get("lesson"))
            assert number == lesson, f"{cid} mismatched source lesson: {p}"
        assert isinstance(card["links_to"], list) and len(set(card["links_to"])) == len(card["links_to"])
        assert cid not in card["links_to"], cid
    edges = 0
    for card in cards:
        for link in card["links_to"]:
            assert link in seen, f"Broken law link {card['id']} -> {link}"
            edges += 1
    assert edges > 0
    return {"status": "TEXT_ONLY_LAW_CARD_GRAPH_AND_PROVENANCE_PASSED", "cards": len(cards), "links": edges, "scope": "text_only", "empirical": "NOT_RUN"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    print("LAW_CARD_AUDIT=" + json.dumps(audit(args.root), ensure_ascii=False, sort_keys=True))
