#!/usr/bin/env python3
"""Ephemeral original-PDF source-page rendering for F01 figure interpretation.

Reads exact SHA-pinned volume-3/4 original PDF page numbers, emits bounded
JPEG thumbnails in temporary CI logs and page-image block geometry. Does not
write/alter PDFs, duplicate original images in git, OCR text, or access market.
Text extraction and page-image counts are NOT a semantic figure proof.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INVENTORY=ROOT/"reports/source_inventory/chanlun_20261107_verified.json"
TARGETS={3:[389,390,391,392],4:[73,74,75,174,175,176,177]}
MAX_PAGE_IMAGE_BYTES=110000
RENDER_SCALE=1.12
READING_KIND="EPHEMERAL_PDF_VISUAL_REFERENCES_NOT_AUTOMATIC_FIGURE_VALIDATION"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def original_pages(inventory):
    sources={int(Path(r["path"]).stem.split("卷")[-1]):r
             for r in inventory["volumes"]}
    assert set(TARGETS)<=set(sources)
    for vol,pages in TARGETS.items():
        source=sources[vol]
        assert max(pages)<=source["page_count"]
        assert min(pages)>=1
    return sources

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--emit-pages",action="store_true")
    args=ap.parse_args()
    import pymupdf as fitz
    sources=original_pages(json.loads(INVENTORY.read_text(encoding="utf-8")))
    count=0
    for vol,pages in TARGETS.items():
        source=sources[vol]
        p=ROOT/source["path"]
        assert p.exists() and sha(p)==source["sha256"],"Original PDF SHA mismatch"
        with fitz.open(p) as pdf:
            assert len(pdf)==source["page_count"],"PDF page count changed"
            for page_number in pages:
                page=pdf[page_number-1]
                imgs=page.get_images(full=True)
                placements=[]
                for row in imgs:
                    for box in page.get_image_rects(row[0]):
                        placements.append([round(v,1) for v in box])
                text=" ".join(page.get_text("text",sort=True).split())
                pix=page.get_pixmap(matrix=fitz.Matrix(RENDER_SCALE,RENDER_SCALE),
                                    colorspace=fitz.csRGB,alpha=False)
                jpg=pix.tobytes("jpeg",jpg_quality=55)
                assert len(jpg)<=MAX_PAGE_IMAGE_BYTES,("JPEG too large for bounded log",vol,page_number,len(jpg))
                digest=hashlib.sha256(jpg).hexdigest()
                meta={"volume":vol,"pdf_page":page_number,
                      "original_pdf_sha256":source["sha256"],
                      "original_pdf_num_pages":source["page_count"],
                      "render_jpeg_sha256":digest,"width_px":pix.width,
                      "height_px":pix.height,"image_objects":len(imgs),
                      "image_placements":placements[:12],
                      "native_text_chars":len(text),
                      "native_text_excerpt":text[:170],
                      "image_visual_semantics_checked":False,
                      "file_written_to_repo":False}
                print("FIGURE_PAGE_META="+json.dumps(meta,ensure_ascii=False,sort_keys=True),flush=True)
                if args.emit_pages:
                    payload=base64.b64encode(jpg).decode("ascii")
                    print(f"FIGURE_RENDER_JPEG_BASE64={vol}:{page_number}:{payload}",flush=True)
                count+=1
    print("FIGURE_SOURCE_AUDIT="+json.dumps(
        {"read_only":True,"pages":count,"images_semantically_proven":False,
         "kind":READING_KIND,"real_market":"NOT_RUN"},sort_keys=True),flush=True)

if __name__=="__main__":main()
