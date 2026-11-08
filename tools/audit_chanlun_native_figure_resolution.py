#!/usr/bin/env python3
"""Offline source-image-resolution gate for two Chanlun lesson58 charts.

Reads a manifest produced by render_chanlun_priority_original_pages.py.
No OCR, no interpolation, no history prices, no pixel endpoint claim.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

EXPECTED = {
    (3, 230): (601, 430),
    (3, 233): (1020, 621),
}
SOURCE_SHA256 = "fad3474e103353f6f67799aefec8c9fba28c9615c0c77a5c67fcbf2b6b4f8a7a"
SOURCE_PRICES = ("3994.57", "3994.21")
EXACT_PRICE_GAP_POINTS = 0.36


def audit(manifest: dict) -> dict:
    if manifest.get("target_set") != "lineage":
        raise ValueError("Require the second-pass lineage render")
    if manifest.get("fine_chart_prices_verified") is not False:
        raise ValueError("Must not claim exact chart prices are visually verified")
    if manifest.get("human_page_visual_verification_completed") is not False:
        raise ValueError("Rendering is not equivalent to complete visual verification")
    found = {}
    for item in manifest.get("pages", []):
        key = (item["volume"], item["pdf_physical_page"])
        if key not in EXPECTED:
            continue
        if item["source_sha256"] != SOURCE_SHA256:
            raise ValueError(f"Source fingerprint changed: {key}")
        images = item["embedded_images"]
        if len(images) != 1:
            raise ValueError(f"Expected exactly one embedded chart on {key}, got {len(images)}")
        width, height = images[0]["width"], images[0]["height"]
        if (width, height) != EXPECTED[key]:
            raise ValueError(f"Native image dimensions changed: {key} {(width, height)}")
        if item["visual_audit_status"] != "RENDERED_NOT_INDEPENDENTLY_VISUALLY_VERIFIED":
            raise ValueError("Render manifest silently upgraded its evidence status")
        found[key] = {"width": width, "height": height,
                      "native_xres": images[0].get("xres"),
                      "native_yres": images[0].get("yres"),
                      "source_pdf_page": key[1]}
    if set(found) != set(EXPECTED):
        raise ValueError("Missing one or both chart candidates")
    return {
        "status": "PASS_NATIVE_RASTER_PROVENANCE_ONLY",
        "original_pdf_volume_sha256": SOURCE_SHA256,
        "source_images": [
            {"pdf_volume": k[0], **v} for k, v in sorted(found.items())
        ],
        "price_strings_from_original_lesson59_text": list(SOURCE_PRICES),
        "difference_points": EXACT_PRICE_GAP_POINTS,
        "exact_price_pixel_endpoint_verified": False,
        "method_limitation": "DPI enlargements cannot restore details absent from embedded source raster",
        "do_not_infer": ["the two charts use the same numbering semantics",
                         "an exact price-to-pixel mapping", "a trading signal"],
        "market_backtests_run": 0
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    result = audit(json.loads(args.manifest.read_text(encoding="utf-8")))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
