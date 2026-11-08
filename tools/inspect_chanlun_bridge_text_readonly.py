#!/usr/bin/env python3
"""SHA-check original Chanlun PDFs; inspect *bounded native text only* on bridge pages.

Discovery mode prints page text fingerprints, not a claim of full source
verification. Normal mode requires an exact page-SHA lockfile and fails
closed on differences. Neither mode renders PDF images, uses OCR, runs
market data, or changes evidence records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "reports/source_inventory/chanlun_20261107_verified.json"
PINS = ROOT / "reports/source_inventory/chanlun_bridge_native_text_sha256.json"

# Physical PDF pages (1-based); no complete source claim outside these pages.
TARGETS = {
    2: {
        353: ("Ai", "盘整背驰", "买卖", "背驰", "创新高"),
        354: ("娇注", "娇", "创新高", "新低", "Ai+3", "Ai+2"),
    },
    5: {
        192: ("回拉", "背驰", "线段", "破坏"),
        193: ("回拉", "背驰", "线段", "破坏"),
        194: ("回拉", "线段", "T+1", "延伸"),
        224: ("娇注", "第三类卖点", "中枢", "5分钟", "30分钟"),
        225: ("娇注", "娇", "卖点", "后面", "走势"),
    },
}
MAX_EXCERPTS_PER_PAGE = 3
MAX_CONTEXT_CHARS = 150
ROLE_CUES = ("娇注", "娇按", "（娇：", "(娇：", "编者", "后记", "后附")
REQUIRED_NATIVE_ANCHORS = {
    "2:353": ("盘整背驰", "30 分钟中枢"),
    "2:354": ("娇注", "Ai+3"),
    "5:192": ("回拉", "完全的分类"),
    "5:193": ("线段",),
    "5:194": ("线段", "中枢"),
    "5:224": ("第三类卖点", "（娇："),
    "5:225": ("娇注", "第三类卖点"),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bounded_excerpts(text: str, tokens: tuple[str, ...]) -> list[dict]:
    """Each excerpt is bounded, overlaps are suppressed, and absence is visible."""
    flattened = " ".join(text.split())
    selected = []
    used = []
    for term in tokens:
        for match in re.finditer(re.escape(term), flattened, re.I):
            if any(abs(match.start() - pos) < 75 for pos in used):
                continue
            used.append(match.start())
            start = max(0, match.start() - 60)
            selected.append({
                "needle": term,
                "context": flattened[start:start + MAX_CONTEXT_CHARS],
            })
            if len(selected) >= MAX_EXCERPTS_PER_PAGE:
                return selected
    return selected


def load_pins() -> dict[str, str]:
    data = json.loads(PINS.read_text(encoding="utf-8"))
    assert data["method"] == "pymupdf_1.26.7_get_text_sort_true", "Different extraction method"
    return data["page_text_sha256"]


def inspect(discovery_only: bool = False) -> list[dict]:
    import pymupdf

    catalog = json.loads(INVENTORY.read_text(encoding="utf-8"))["volumes"]
    volumes = {int(Path(v["path"]).stem.split("卷")[-1]): v for v in catalog}
    pinned = None if discovery_only else load_pins()
    keys = {f"{volume}:{page}" for volume, pages in TARGETS.items() for page in pages}
    if pinned is not None and set(pinned) != keys:
        raise ValueError("Pinned native-text page key set differs from target set")
    result = []
    for volume, pages in TARGETS.items():
        item = volumes[volume]
        pdf = ROOT / item["path"]
        if pdf.stat().st_size != item["bytes"] or sha256_file(pdf) != item["sha256"]:
            raise ValueError(f"Canonical PDF content identity changed: volume {volume}")
        with pymupdf.open(pdf) as document:
            if document.page_count != item["page_count"]:
                raise ValueError(f"Canonical PDF page count changed: volume {volume}")
            for page_number, needles in pages.items():
                if not 1 <= page_number <= document.page_count:
                    raise ValueError(f"Invalid original physical page {volume}:{page_number}")
                raw = document.load_page(page_number - 1).get_text("text", sort=True)
                page_sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
                key = f"{volume}:{page_number}"
                if pinned is not None and pinned[key] != page_sha:
                    raise ValueError(f"Original native page text differs at {key}")
                simplified = " ".join(raw.split())
                for required in REQUIRED_NATIVE_ANCHORS[key]:
                    if required not in simplified:
                        raise ValueError(f"Original source anchor missing at {key}: {required!r}")
                row = {
                    "key": key,
                    "original_volume_pdf_sha256": item["sha256"],
                    "original_pdf_physical_page": page_number,
                    "native_text_sha256": page_sha,
                    "native_text_chars": len(raw),
                    "editorial_cue_hits": {x: simplified.count(x) for x in ROLE_CUES if x in simplified},
                    "bounded_cues": bounded_excerpts(raw, needles),
                    "original_author_attribution_verified": False,
                    "source_role_still_requires_contextual_review": True,
                    "images_or_ocr_inspected": False,
                }
                result.append(row)
                print(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
    assert len(result) == len(keys) == 7
    print(json.dumps({
        "status": "DISCOVERY_UNPINNED" if discovery_only else "PASS_SHA_PINNED_NATIVE_TEXT_EXTRACTION",
        "page_count": len(result),
        "original_pdf_sha256_verified": len(TARGETS),
        "text_full_transcripts_saved": 0,
        "images_rendered": 0,
        "market_backtests": 0,
    }, ensure_ascii=False))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--discovery-only", action="store_true",
                        help="Print page hashes; DO NOT treat this as locked text review")
    args = parser.parse_args()
    inspect(args.discovery_only)


if __name__ == "__main__":
    main()
