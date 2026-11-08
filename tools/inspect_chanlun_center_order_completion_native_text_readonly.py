#!/usr/bin/env python3
"""Read narrow, source-locked Chanlun pages 18/20: center relations and completion.

Discovery prints limited native prose cues and exact page text hashes. Default
mode requires reviewed hashes. No image pixel reading, OCR or market data.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "reports/source_inventory/chanlun_20261107_verified.json"
PINS = ROOT / "reports/source_inventory/chanlun_center_order_completion_native_text_sha256.json"
READER = "pymupdf_1.26.7_get_text_sort_true"
TARGETS = {
    234: ("中枢", "ZD", "ZG", "区间", "完成"),
    235: ("重叠", "高于", "低于", "趋势", "确认"),
    236: ("破坏", "第三", "离开", "中枢", "回抽"),
    245: ("GG", "DD", "ZG", "ZD", "延伸", "扩张"),
    246: ("GG", "DD", "ZG", "ZD", "区间", "延伸", "重叠"),
    247: ("ZG", "ZD", "GG", "DD", "回试", "破坏", "完成"),
}
MAX_HITS = 5
MAX_CHARS = 210


def sha_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def bounded_cues(raw, words):
    text = " ".join(raw.split())
    result, used = [], []
    for word in words:
        for match in re.finditer(re.escape(word), text, re.I):
            if any(abs(match.start() - k) < 90 for k in used):
                continue
            used.append(match.start())
            start = max(0, match.start() - 75)
            result.append({"token": word, "context": text[start:start + MAX_CHARS]})
            if len(result) >= MAX_HITS:
                return result
    return result


def run(discover=False):
    import pymupdf
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))["volumes"]
    src = next(v for v in inventory if v["path"].endswith("缠论_卷1.pdf"))
    pdfpath = ROOT / src["path"]
    if pdfpath.stat().st_size != src["bytes"] or sha_file(pdfpath) != src["sha256"]:
        raise ValueError("Original volume1 PDF digest or bytes mismatch")
    if discover:
        pins = None
    else:
        doc = json.loads(PINS.read_text(encoding="utf-8"))
        if doc["reader"] != READER or set(doc["page_native_text_sha256"]) != set(map(str, TARGETS)):
            raise ValueError("Invalid original page fingerprint lock")
        pins = doc["page_native_text_sha256"]
    out = []
    with pymupdf.open(pdfpath) as pdf:
        if pdf.page_count != src["page_count"]:
            raise ValueError("Original PDF page count changed")
        for page, terms in TARGETS.items():
            native = pdf[page - 1].get_text("text", sort=True)
            sha = hashlib.sha256(native.encode("utf-8")).hexdigest()
            if pins is not None and pins[str(page)] != sha:
                raise ValueError(f"Native original PDF text changed at physical page {page}")
            normalized = " ".join(native.split())
            row = {"volume": 1, "physical_pdf_page": page,
                   "source_sha256": src["sha256"], "native_text_sha256": sha,
                   "native_chars": len(native),
                   "editorial_markers": [t for t in ("娇注", "（娇：", "编者") if t in normalized],
                   "cues": bounded_cues(native, terms),
                   "image_read": False, "original_historical_publication_verified": False}
            print(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            out.append(row)
    print(json.dumps({"status": "DISCOVERY_UNPINNED" if discover else "PINNED_NATIVE_PROSE_PASS",
                      "pages": len(out), "pdf_images": 0, "market_data": 0}))
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--discover", action="store_true")
    run(parser.parse_args().discover)
