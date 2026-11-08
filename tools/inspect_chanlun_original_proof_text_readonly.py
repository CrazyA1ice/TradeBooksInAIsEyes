#!/usr/bin/env python3
"""Read original PDF native *text only* for narrowly scoped argument checking.

Verifies authoritative PDF SHA/page-count, extracts bounded in-context text
excerpts from specific physical pages in ephemeral CI logs, does not OCR or
read images, and never checks the material into source control.
Excerpts are for manual argument verification, not a proof or full transcript.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INV = ROOT / "reports/source_inventory/chanlun_20261107_verified.json"
# Anchors are drawn from existing source cards; no assumption that every
# variant appears on each page. Physical PDF pages are 1-based.
TARGETS = {
    1: {
        196: ["走势终完美", "走势必完美", "走势类型"],
        197: ["走势终完美", "中枢", "级别"],
    },
    2: {
        291: ["走势分解定理", "最低级别", "三笔", "中枢"],
        292: ["走势分解定理", "结合律", "次级别", "交易"],
        293: ["结合律", "级别", "定理", "手续费"],
        338: ["唯一", "同级别", "延伸", "盘整"],
        339: ["同级别", "买卖", "盘整", "上涨"],
    },
    5: {
        202: ["中阴", "结合律", "中枢", "走势类型"],
        203: ["中枢", "必然", "娇", "走势"],
        241: ["唯一", "自然数", "走势", "分解"],
        242: ["分解", "级别", "娇", "唯一"],
    },
}
MAX_HITS_PER_PAGE = 5
MAX_EXCERPT_CHARS = 240


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for buf in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(buf)
    return h.hexdigest()


def excerpts(text: str, tokens: list[str]) -> list[dict]:
    compressed = re.sub(r"\s+", " ", text).strip()
    result = []
    occupied = []
    for token in tokens:
        for match in re.finditer(re.escape(token), compressed, flags=re.I):
            start = max(0, match.start() - 105)
            end = min(len(compressed), match.end() + 125)
            if any(abs(match.start() - x) < 80 for x in occupied):
                continue
            occupied.append(match.start())
            result.append({
                "needle": token,
                "start_in_normalized_page_text": match.start(),
                "context": compressed[start:end][:MAX_EXCERPT_CHARS],
            })
            if len(result) >= MAX_HITS_PER_PAGE:
                return result
    return result


def main() -> int:
    import pymupdf as fitz

    sources = json.loads(INV.read_text(encoding="utf-8"))["volumes"]
    volumes = {int(Path(item["path"]).stem.split("卷")[-1]): item
               for item in sources}
    overall = []
    for vol, targets in TARGETS.items():
        manifest = volumes[vol]
        pdf = ROOT / manifest["path"]
        sha = sha256_file(pdf)
        if sha != manifest["sha256"] or pdf.stat().st_size != manifest["bytes"]:
            raise ValueError(f"Canonical source fingerprint differs for volume {vol}")
        with fitz.open(pdf) as document:
            if document.page_count != manifest["page_count"]:
                raise ValueError(f"PDF page count differs for volume {vol}")
            for number, needles in targets.items():
                page = document.load_page(number - 1)
                txt = page.get_text("text", sort=True)
                row = {
                    "volume": vol,
                    "physical_pdf_page": number,
                    "canonical_pdf_sha256": sha,
                    "native_text_chars": len(txt),
                    "native_page_text_sha256": hashlib.sha256(txt.encode("utf-8")).hexdigest(),
                    "anchor_excerpts": excerpts(txt, needles),
                    "no_visual_figure_inspection": True,
                    "proof_status": "TEXT_EXCERPT_REQUIRES_CONTEXTUAL_REVIEW",
                }
                overall.append(row)
                print(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
    if len(overall) != sum(len(x) for x in TARGETS.values()):
        raise ValueError("Incomplete targeted original text extraction")
    print(json.dumps({
        "status": "PASS_SHA_PINNED_PDF_TEXT_EXCERPT_EXTRACTION_ONLY",
        "total_original_pdf_physical_pages": len(overall),
        "original_pdfs_sha_verified": len(TARGETS),
        "images_inspected": 0,
        "text_full_original_transcript_committed": False,
        "market_backtests_run": 0,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
