#!/usr/bin/env python3
"""Read-only, SHA-locked survey of the three remaining indexed lessons."""
import hashlib
import json
import re
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]
index = json.loads((ROOT / "catalog/chanlun_lesson_index.json").read_text("utf-8"))
volume = index["volumes"][4]
path = ROOT / volume["path"]
sha = hashlib.sha256(path.read_bytes()).hexdigest()
assert sha == volume["sha256"], "Immutable source SHA differs from index"
date_pattern = re.compile(r"20\\d\\d[-/]\\d\\d[-/]\\d\\d\\s+\\d\\d:\\d\\d(?::\\d\\d)?")
editor_pattern = re.compile(r"娇注|娇加|娇[:：]|编者|勘误|后记|更正|修订")
separators = re.compile(r"^\\*{5,}$")
with fitz.open(path) as pdf:
    assert len(pdf) == 441
    for lesson in (106, 107, 108):
        k = next(i for i, row in enumerate(volume["lessons"]) if row["lesson"] == lesson)
        start = volume["lessons"][k]["start_pdf_page"]
        end = volume["lessons"][k + 1]["start_pdf_page"] - 1 if k + 1 < len(volume["lessons"]) else len(pdf)
        image_pages = []
        sparse_pages = []
        pages = []
        late_dates = []
        excerpt_budget = 6100
        for page_number in range(start, end + 1):
            p = pdf[page_number - 1]
            raw = p.get_text("text", sort=True)
            dates = date_pattern.findall(raw)
            is_editorial = bool(editor_pattern.search(raw))
            has_divider = any(separators.match(t.strip()) for t in raw.splitlines())
            if page_number > start and dates:
                late_dates.append({"page": page_number, "dates": dates[:5]})
            images = len(p.get_image_info(xrefs=True))
            if images:
                image_pages.append(page_number)
            if len(raw.strip()) < 100:
                sparse_pages.append(page_number)
            pages.append({"page": page_number, "chars": len(raw.strip()), "images": images, "editor_cue": is_editorial, "divider": has_divider})
            if page_number < start + 5 and excerpt_budget > 0:
                preview = " ".join(raw.split())[:min(excerpt_budget, 1600)]
                excerpt_budget -= len(preview)
                print("SOURCE_CUE " + json.dumps({"lesson": lesson, "page": page_number, "text": preview}, ensure_ascii=False), flush=True)
        print("LESSON_SURVEY " + json.dumps({
            "lesson": lesson, "title": volume["lessons"][k]["title"],
            "volume": 5, "path": volume["path"], "sha256": sha,
            "start": start, "end": end, "physical_pages": end - start + 1,
            "original_date_candidates": date_pattern.findall(pdf[start-1].get_text("text", sort=True))[:3],
            "native_chars": sum(x["chars"] for x in pages),
            "image_pages": image_pages, "sparse_pages": sparse_pages,
            "pages": pages, "later_dates": late_dates
        }, ensure_ascii=False), flush=True)
print("PASS_SOURCE106_108_IMMUTABLE_PDF", flush=True)
