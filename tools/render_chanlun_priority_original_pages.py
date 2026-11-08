#!/usr/bin/env python3
"""Render *original* PDF page/figure evidence into a temporary CI artifact.

Does not OCR, invent missing labels, write to the repository, claim subjective
visual verification, perform any backtest, or modify canonical evidence.
Requires PyMuPDF; safeguards source hashes and page counts before rendering.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFIED = ROOT / "reports/source_inventory/chanlun_20261107_verified.json"

# Physical PDF page numbers, 1-based. Only selected high-value gaps, not an
# assertion that other pages in these lessons have been independently inspected.
TARGETS = {
    1: [30],                        # L009 image/formula page
    3: [162, 254, 255, 256, 257, 292, 293, 294, 295, 296, 297, 300, 301],  # L053/L059/L062
    5: [225, 395, 396, 397, 398, 400],                   # L100/L108
}
MAX_PAGES = 20


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def printable_blocks(page) -> list[dict]:
    result = []
    for block in page.get_text("blocks"):
        x0, y0, x1, y1, text, *_ = block
        txt = re.sub(r"\s+", " ", text).strip()
        if txt:
            result.append({
                "box": [round(float(v), 1) for v in (x0, y0, x1, y1)],
                "text": txt[:260],
            })
    return result


def native_check(page, reference: dict) -> dict:
    text = page.get_text("text")
    return {
        "native_text_characters": len(text),
        "native_matches": {
            term: (term in text) for term in reference.get("needles", [])
        },
        "visible_text_blocks": printable_blocks(page)[:80],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--full-dpi", type=int, default=185)
    parser.add_argument("--crop-dpi", type=int, default=300)
    args = parser.parse_args()
    if not 90 <= args.full_dpi <= 280 or not 130 <= args.crop_dpi <= 400:
        raise ValueError("Out-of-range render resolution")
    out = args.out.resolve()
    if out == ROOT or ROOT in out.parents:
        raise ValueError("Never write PDF renders into source repository")
    if out.exists() and any(out.iterdir()):
        raise ValueError("Output folder must be empty")
    out.mkdir(parents=True, exist_ok=True)

    import pymupdf as fitz

    inventory = json.loads(VERIFIED.read_text(encoding="utf-8"))
    volumes = {int(Path(x["path"]).stem.split("卷")[-1]): x for x in inventory["volumes"]}
    metadata = {
        "schema_version": 1,
        "review_type": "original_pdf_priority_page_render_automated_geometry_only",
        "source_inventory": VERIFIED.relative_to(ROOT).as_posix(),
        "rendered_page_count": 0,
        "human_page_visual_verification_completed": False,
        "fine_chart_prices_verified": False,
        "claims_from_text_need_separate_source_role_review": True,
        "human_visual_audit_replaced": False,
        "market_backtests_run": 0,
        "volumes": [],
        "pages": [],
    }
    needle_map = {
        (1, 30): ["30%", "40%", "3.6%"],
        (3, 162): ["2009", "第三类"],
        (3, 257): ["3994.57", "3994.21"],
        (3, 292): ["分型", "顶"],
        (3, 293): ["笔", "包含"],
        (5, 225): ["娇", "卖点"],
        (5, 395): ["底部", "三买", "三卖"],
    }
    if sum(map(len, TARGETS.values())) > MAX_PAGES:
        raise ValueError("Too many pages requested")
    for vol, pages in TARGETS.items():
        item = volumes[vol]
        orig = ROOT / item["path"]
        digest = file_sha256(orig)
        if digest != item["sha256"] or orig.stat().st_size != item["bytes"]:
            raise ValueError(f"Canonical source hash/size mismatch for volume {vol}")
        doc = fitz.open(orig)
        if doc.page_count != item["page_count"]:
            raise ValueError(f"Canonical page-count mismatch for volume {vol}")
        metadata["volumes"].append({
            "volume": vol, "canonical_source": item["path"], "sha256": digest,
            "page_count": doc.page_count, "original_bytes": item["bytes"]
        })
        for number in pages:
            if not 1 <= number <= doc.page_count:
                raise ValueError(f"Illegal page number {vol}:{number}")
            page = doc.load_page(number - 1)
            stem = f"volume{vol}_physical_page{number:04}"
            rect = page.rect
            pix = page.get_pixmap(matrix=fitz.Matrix(args.full_dpi / 72, args.full_dpi / 72), alpha=False)
            name = stem + "_full.jpg"
            (out / name).write_bytes(pix.tobytes("jpeg", jpg_quality=86))
            images = []
            for im in page.get_image_info(xrefs=True):
                bbox = fitz.Rect(im["bbox"]) & rect
                if bbox.is_empty or bbox.is_infinite:
                    continue
                frac = round(bbox.get_area() / rect.get_area(), 5)
                images.append({
                    "bbox_pdf_points": [round(float(v), 2) for v in bbox],
                    "area_fraction_of_page": frac,
                    "xres": im.get("xres"), "yres": im.get("yres"),
                    "width": im.get("width"), "height": im.get("height"),
                    "xref": im.get("xref"),
                })
            # Figure crops in artifact only; do not call these "verified".
            eligible = sorted((im for im in images if im["area_fraction_of_page"] >= 0.045),
                              key=lambda x: x["area_fraction_of_page"], reverse=True)
            crops = []
            for idx, im in enumerate(eligible[:2], 1):
                box = fitz.Rect(im["bbox_pdf_points"])
                px = page.get_pixmap(matrix=fitz.Matrix(args.crop_dpi / 72, args.crop_dpi / 72),
                                     clip=box, alpha=False)
                crop_name = f"{stem}_embedded_image_region{idx:02}.jpg"
                (out / crop_name).write_bytes(px.tobytes("jpeg", jpg_quality=89))
                crops.append({"path": crop_name, "image_bbox_pdf_points": im["bbox_pdf_points"]})
            textcheck = native_check(page, {"needles": needle_map.get((vol, number), [])})
            metadata["pages"].append({
                "volume": vol, "pdf_physical_page": number,
                "source_sha256": digest, "page_size_pdf_points": [rect.width, rect.height],
                "render_full_file": name, "full_render_dpi": args.full_dpi,
                "embedded_images": images, "embedded_image_count": len(images),
                "large_image_crops": crops, "crop_dpi": args.crop_dpi,
                "native_text": textcheck,
                "visual_audit_status": "RENDERED_NOT_INDEPENDENTLY_VISUALLY_VERIFIED",
            })
            metadata["rendered_page_count"] += 1
            print(json.dumps({
                "page": f"{vol}:{number}", "render": name,
                "embedded_image_count": len(images), "crop_count": len(crops),
                "native_matches": textcheck["native_matches"],
                "status": "RENDERED_NOT_INDEPENDENTLY_VISUALLY_VERIFIED",
            }, ensure_ascii=False))
        doc.close()
    (out / "page_evidence_manifest.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if metadata["rendered_page_count"] != sum(map(len, TARGETS.values())):
        raise AssertionError("Incomplete page render")
    print(json.dumps({
        "status": "PASS_PRIORITY_PDF_PAGE_RENDERED",
        "physical_pdf_pages": metadata["rendered_page_count"],
        "source_volumes_sha256_verified": len(metadata["volumes"]),
        "render_artifact_folder": str(out),
        "visual_content_verified_by_human": False,
        "backtests_run": 0,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
