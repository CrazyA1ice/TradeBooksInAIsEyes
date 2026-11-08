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
# Exact native-text extraction SHA-256 at PyMuPDF==1.26.7, sorted text,
# verified in GitHub Actions run 42480286214. These are TEXT hashes, not
# image recognition, and must be reviewed before any intentional changes.
EXPECTED_TEXT_SHA256 = {
    (1, 196): "30986ca4815b717d49b2bb7921b1979895fdc966bc958f28e75e26a7bfccc55d",
    (1, 197): "6aaecd9ad072715180c28c4bac0cdc2e5135604d17e26cabae449c8e47ec2936",
    (2, 291): "1a2c291cff189ea4de5bef2ecf152e9888773d1194b0ed4e7218f4cd0f3b846b",
    (2, 292): "f253ed2039c756133443ac2b43a846ef8ba06de3bcfe34e75f78a1ed635d9f37",
    (2, 293): "f4af9069932c5ec876b459743303b222eb8ffe90189dc5c737c581c32e1b21da7",
    (2, 338): "369d79117897f949976704c21e81818f9e75899b0e925f637c581c32e1b21da7",
    (2, 339): "1f48433d41259c6f82e4f5233dccd3728c823e9ab3723fe3ac77a06697689ce8",
    (5, 202): "1ff79bb24d18734344e4c9035065a0b3fc37e59c1a40c01264ab01dc49feb0d1",
    (5, 203): "0b7f597241ac2e13d11ca1e6bacae06af66a393349fabe93e3dbc98d16171de6",
    (5, 241): "c7e46bd14e757ec48b9e8ca51fce682fe405bd382beed5de6a63f0a012a75f96",
    (5, 242): "75bfe849f767127f77520079c6bbc40c84d3359527006b71d190910f1630ba19",
}
REQUIRED_TEXT_ANCHORS = {
    (1, 196): ["走势终完美", "走势类型终要完成"],
    (1, 197): ["三个连续次级别走势类型", "单位K"],
    (2, 291): ["连续三笔相同价位", "最低级别"],
    (2, 292): ["走势分解定理一", "走势分解定理二", "结合律"],
    (2, 338): ["同级别分解", "唯一性"],
    (2, 339): ["中枢延伸", "盘整+盘整", "唯一"],
    (5, 202): ["中阴", "同级别的划分"],
    (5, 203): ["30 分钟", "中枢震荡"],
    (5, 241): ["自然数", "唯一分解"],
    (5, 242): ["a1A1+a5A5+a30A30", "娇注"],
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
                page_hash = hashlib.sha256(txt.encode("utf-8")).hexdigest()
                if page_hash != EXPECTED_TEXT_SHA256[(vol, number)]:
                    raise ValueError(f"Native original text changed at volume {vol} p.{number}")
                normalized = re.sub(r"\\s+", " ", txt)
                for needle in REQUIRED_TEXT_ANCHORS.get((vol, number), []):
                    if needle not in normalized:
                        raise ValueError(f"Missing source wording {needle!r} at volume {vol} p.{number}")
                row = {
                    "volume": vol,
                    "physical_pdf_page": number,
                    "canonical_pdf_sha256": sha,
                    "native_text_chars": len(txt),
                    "native_page_text_sha256": page_hash,
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
