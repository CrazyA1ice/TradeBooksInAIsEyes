#!/usr/bin/env python3
"""Inspect narrow original-PDF native prose around Chanlun 35/38/99 proof claims.

Discovery prints bounded source cues + page SHA256. The default mode requires
locked exact page SHA256 values from a separate reviewed JSON file. Neither
mode claims to prove the book's theorems or verifies chart pixels.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "reports/source_inventory/chanlun_20261107_verified.json"
PINS = ROOT / "reports/source_inventory/chanlun_35_38_99_native_text_sha256.json"
METHOD = "pymupdf_1.26.7_get_text_sort_true"
TARGETS = {
    2: {
        294: ("分解", "定理", "级别", "中枢", "唯一"),
        295: ("分解", "级别", "最低", "三段", "中枢"),
        340: ("同级别", "唯一", "盘整", "完成", "分解"),
        341: ("同级别", "盘整", "分解", "中枢", "娇"),
    },
    5: {
        204: ("中枢", "震荡", "必然", "级别", "走势"),
        205: ("中枢", "级别", "必然", "落在", "走势"),
        206: ("中枢", "级别", "必然", "位置", "走势"),
        207: ("中枢", "级别", "完成", "位置", "走势"),
    },
}
ROLE_MARKERS = ("娇注", "（娇：", "(娇：", "编者", "回复", "留言")
MAX_EXCERPTS_PER_PAGE = 3
MAX_EXCERPT_CHARS = 160
# These are document-source boundaries, not assertions of author identity.
PAGE_SCOPES = {
    "2:294": "LOW_NATIVE_TEXT_IMAGE_UNREVIEWED",
    "2:295": "LOW_NATIVE_TEXT_IMAGE_UNREVIEWED",
    "2:340": "LOW_NATIVE_TEXT_IMAGE_UNREVIEWED",
    "2:341": "APPENDED_INTERACTIVE_QA_NOT_MAIN_PROOF",
    "5:204": "CONTINUED_MARKET_EXAMPLE_NOT_THEOREM_PROOF",
    "5:205": "CONTINUED_MARKET_EXAMPLE_NOT_THEOREM_PROOF",
    "5:206": "SEPARATELY_DATED_2008_02_20_ARTICLE",
    "5:207": "FOLLOWING_SEPARATELY_DATED_ARTICLE",
}
REQUIRED_BOUNDARY_TEXT = {
    "2:340": ("同级别",),
    "2:341": ("解盘及互动问答",),
    "5:204": ("4672",),
    "5:205": ("4672",),
    "5:206": ("2008-02-20", "大规模增发猛于虎"),
    "5:207": ("多头",),
}



def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def cues(text: str, terms: tuple[str, ...]) -> list[dict]:
    normalized = " ".join(text.split())
    hits, selected = [], []
    for needle in terms:
        for match in re.finditer(re.escape(needle), normalized, re.I):
            if any(abs(match.start() - v) < 80 for v in selected):
                continue
            selected.append(match.start())
            left = max(0, match.start() - 65)
            hits.append({"needle": needle, "context": normalized[left:left + MAX_EXCERPT_CHARS]})
            if len(hits) >= MAX_EXCERPTS_PER_PAGE:
                return hits
    return hits


def pin_map() -> dict[str, str]:
    data = json.loads(PINS.read_text(encoding="utf-8"))
    if data["method"] != METHOD:
        raise ValueError("Incorrect native PDF reader version")
    hashes = data["page_text_sha256"]
    expected = {f"{v}:{p}" for v, pages in TARGETS.items() for p in pages}
    if set(hashes) != expected or any(not re.fullmatch("[0-9a-f]{64}", h) for h in hashes.values()):
        raise ValueError("Page SHA256 lock is incomplete or invalid")
    return hashes


def scan(discovery: bool = False) -> list[dict]:
    import pymupdf
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))["volumes"]
    volumes = {int(Path(item["path"]).stem.split("卷")[-1]): item for item in inventory}
    pins = None if discovery else pin_map()
    result = []
    for volume, targets in TARGETS.items():
        item = volumes[volume]
        path = ROOT / item["path"]
        if path.stat().st_size != item["bytes"] or digest_file(path) != item["sha256"]:
            raise ValueError(f"Source PDF changed: volume {volume}")
        with pymupdf.open(path) as pdf:
            if pdf.page_count != item["page_count"]:
                raise ValueError(f"Source PDF pages changed: volume {volume}")
            for physical_page, terms in targets.items():
                if not 1 <= physical_page <= pdf.page_count:
                    raise ValueError("Original physical PDF page out of bounds")
                raw = pdf.load_page(physical_page - 1).get_text("text", sort=True)
                sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
                key = f"{volume}:{physical_page}"
                if pins is not None and pins[key] != sha:
                    raise ValueError(f"Original native text changed: {key}")
                normalized = " ".join(raw.split())
                for anchor in REQUIRED_BOUNDARY_TEXT.get(key, ()):
                    if anchor not in normalized:
                        raise ValueError(f"Document scope separator or source cue missing: {key} {anchor!r}")
                if PAGE_SCOPES[key] == "LOW_NATIVE_TEXT_IMAGE_UNREVIEWED" and len(raw) >= 100:
                    raise ValueError(f"Low-text page evidence status must be reviewed: {key}")
                row = {
                    "key": key,
                    "source_pdf_sha256": item["sha256"],
                    "native_text_sha256": sha,
                    "native_text_chars": len(raw),
                    "source_scope": PAGE_SCOPES[key],
                    "native_text_coverage": "LOW_IMAGE_NOT_REVIEWED" if len(raw) < 100 else "BOUNDED_TEXT_ONLY",
                    "role_markers": {m: normalized.count(m) for m in ROLE_MARKERS if m in normalized},
                    "bounded_cues": cues(raw, terms),
                    "author_or_editor_historical_identity_verified": False,
                    "complete_page_prose_copied": False,
                    "image_inspection": False,
                }
                result.append(row)
                print(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
    if len(result) != sum(len(p) for p in TARGETS.values()):
        raise ValueError("Incomplete scan")
    print(json.dumps({"status": "DISCOVERY_UNPINNED" if discovery else "PASS_PINNED_NATIVE_TEXT",
        "pages_scanned": len(result), "original_pdfs_hash_checked": len(TARGETS),
        "images_inspected": 0, "market_data_read": 0, "market_backtests_run": 0}))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--discover", action="store_true",
                        help="Get unreviewed text hashes; not a final accepted verification")
    args = parser.parse_args()
    scan(discovery=args.discover)


if __name__ == "__main__":
    main()
