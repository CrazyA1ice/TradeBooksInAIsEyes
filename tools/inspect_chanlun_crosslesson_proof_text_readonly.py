#!/usr/bin/env python3
"""Inspect 5 bounded, previously unpinned original PDF native-text pages.

Two modes: --discover reports unpinned page hashes for review; default requires
the exact checked-in hashes and fails closed on file/page/anchor changes.
No OCR, image access, full-page transcription, market data or author attribution
inferred merely from an editor-assembled book.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "reports/source_inventory/chanlun_20261107_verified.json"
PINS = ROOT / "reports/source_inventory/chanlun_crosslesson_proof_native_text_sha256.json"
TARGETS = {
    256: ("多义性", "中枢", "级别"),
    257: ("多义性", "分解", "中枢"),
    305: ("结合律", "分解", "级别"),
    310: ("娇", "中枢", "线段"),
    320: ("背驰", "级别", "中枢"),
}
VOLUME = 2
MAX_EXCERPTS_PER_PAGE = 3
MAX_CONTEXT_CHARS = 145
SOURCE_ROLE_CUES = ("娇注", "（娇：", "(娇：", "编者", "后记", "后附")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bounded_cues(raw: str, terms: tuple[str, ...]) -> list[dict]:
    flattened = " ".join(raw.split())
    selected, positions = [], []
    for word in terms:
        for match in re.finditer(re.escape(word), flattened, re.I):
            if any(abs(match.start() - p) < 65 for p in positions):
                continue
            positions.append(match.start())
            start = max(0, match.start() - 60)
            selected.append({"needle": word, "context": flattened[start:start + MAX_CONTEXT_CHARS]})
            if len(selected) == MAX_EXCERPTS_PER_PAGE:
                return selected
    return selected


def locked_hashes() -> dict:
    j = json.loads(PINS.read_text(encoding="utf-8"))
    if j["method"] != "pymupdf_1.26.7_get_text_sort_true":
        raise ValueError("Unrecognized text extraction method")
    hashes = j["page_text_sha256"]
    if set(hashes) != set(map(str, TARGETS)):
        raise ValueError("Pinned page set changed")
    if not all(re.fullmatch("[0-9a-f]{64}", value) for value in hashes.values()):
        raise ValueError("Invalid SHA-256 value")
    return hashes


def inspect(discover: bool) -> list[dict]:
    import pymupdf
    volumes = json.loads(INVENTORY.read_text(encoding="utf-8"))["volumes"]
    book = next(x for x in volumes if x["path"].endswith("缠论_卷2.pdf"))
    pdf = ROOT / book["path"]
    if pdf.stat().st_size != book["bytes"] or digest(pdf) != book["sha256"]:
        raise ValueError("Canonical volume 2 content changed")
    pins = None if discover else locked_hashes()
    rows = []
    with pymupdf.open(pdf) as doc:
        if doc.page_count != book["page_count"]:
            raise ValueError("Canonical volume 2 page count changed")
        for page, terms in TARGETS.items():
            raw = doc.load_page(page - 1).get_text("text", sort=True)
            sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            if pins is not None and pins[str(page)] != sha:
                raise ValueError(f"Native text changed: volume 2 page {page}")
            text = " ".join(raw.split())
            entry = {
                "volume": VOLUME,
                "physical_page": page,
                "native_text_sha256": sha,
                "native_chars": len(raw),
                "bounded_cues": bounded_cues(raw, terms),
                "editorial_markers": {s: text.count(s) for s in SOURCE_ROLE_CUES if s in text},
                "original_author_attribution_verified": False,
                "full_page_transcript_committed": False,
                "pdf_images_read": False,
                "market_research_run": False,
            }
            rows.append(entry)
            print(json.dumps(entry, ensure_ascii=False, separators=(",", ":")))
    if len(rows) != len(TARGETS):
        raise ValueError("Missing original physical page")
    print(json.dumps({"status": "DISCOVERY_UNPINNED" if discover else "PASS_SHA_PINNED_NATIVE_TEXT",
                      "canonical_pdf_sha256": book["sha256"], "pages": len(rows),
                      "images_read": 0, "market_backtests": 0}))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--discover", action="store_true", help="Unpinned exploratory report; not final verification")
    args = parser.parse_args()
    inspect(args.discover)


if __name__ == "__main__":
    main()
