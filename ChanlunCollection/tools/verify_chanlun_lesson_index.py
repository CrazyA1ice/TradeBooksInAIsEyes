#!/usr/bin/env python3
"""Compare a read-only source survey with the committed 108-lesson map."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

def verify(index: dict, observation: dict) -> None:
    expected = index.get("volumes", [])
    actual = observation.get("volumes", [])
    if len(expected) != 5 or len(actual) != 5:
        raise ValueError("Expected precisely five volume entries")
    lesson_ids = []
    for ref, obs in zip(expected, actual):
        if ref["path"] != obs["path"]:
            raise ValueError("Source path mismatch")
        if ref["pdf_page_count"] != obs["page_count"] or ref["sha256"] != obs["sha256"]:
            raise ValueError(f"Source PDF version mismatch: {ref['path']}")
        if ref["lessons"] != obs["lesson_starts"]:
            raise ValueError(f"Lesson start map mismatch: {ref['path']}")
        lesson_ids += [v["lesson"] for v in ref["lessons"]]
    if lesson_ids != list(range(1, 109)):
        raise ValueError("Lesson IDs are not the complete unique sequence 1..108")
    if index.get("lesson_count") != 108 or index.get("volume_count") != 5:
        raise ValueError("Index summary counts incorrect")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observed", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    args = parser.parse_args()
    observed = json.loads(args.observed.read_text(encoding="utf-8"))
    index = json.loads(args.index.read_text(encoding="utf-8"))
    verify(index, observed)
    print("PASS: 108 unique lesson headers, page starts, source SHAs and five volumes match")

if __name__ == "__main__":
    main()
