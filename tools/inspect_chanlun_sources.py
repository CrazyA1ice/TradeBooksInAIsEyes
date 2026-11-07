#!/usr/bin/env python3
"""Read-only inventory of the five existing Chanlun PDFs. No OCR or source writes."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / "ChineseBooks" / "缠论" / f"缠论_卷{i}.pdf" for i in range(1, 6)]
HEADING = re.compile(r"^\s*(?:第[一二三四五六七八九十百千〇零两0-9]+[编篇章节课讲回]|[0-9]{1,3}[、.．]\s*[^0-9])")

LESSON_HEADER = re.compile(r"^教你炒股票\s*([0-9]{1,3})\s*[：:]\s*(.{2,100})$")

def normalize(text: str) -> str:
    return " ".join(text.split())

def inspect_one(path: Path, limit: int = 35) -> dict:
    data = path.read_bytes()
    info = {"path": path.relative_to(ROOT).as_posix(),
            "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "status": "read_only_inspected"}
    with fitz.open(path) as doc:
        info["page_count"] = len(doc)
        info["pdf_metadata_title"] = doc.metadata.get("title") or None
        toc = doc.get_toc(simple=True)
        info["embedded_toc_count"] = len(toc)
        info["embedded_toc_preview"] = [
            {"level": level, "title": normalize(title)[:110], "pdf_page": page}
            for level, title, page in toc[:80]]
        nonempty = native = image_pages = total_chars = 0
        empty_pages, sparse_pages, headings, previews, page_errors = [], [], [], [], []
        lessons = {}
        for idx in range(len(doc)):
            pn = idx + 1
            try:
                page = doc.load_page(idx)
                txt = page.get_text("text", sort=True)
                for raw in txt.splitlines()[:12]:
                    match = LESSON_HEADER.match(normalize(raw))
                    if match:
                        number = int(match.group(1))
                        if 1 <= number <= 200 and number not in lessons:
                            lessons[number] = {"lesson": number, "title": match.group(2).strip(), "start_pdf_page": pn}
                chars = len(txt.strip())
                total_chars += chars
                image_pages += int(bool(page.get_images(full=True)))
                native += int(chars >= 100)
                nonempty += int(chars > 0)
                if not chars:
                    empty_pages.append(pn)
                elif chars < 100:
                    sparse_pages.append(pn)
                if idx < limit:
                    for raw in txt.splitlines():
                        line = normalize(raw)
                        if 5 <= len(line) <= 105 and HEADING.match(line):
                            headings.append({"pdf_page": pn, "text": line[:105]})
                    if len(previews) < 8 and chars > 150:
                        previews.append({"pdf_page": pn, "text_preview": normalize(txt)[:250]})
            except Exception as exc:
                page_errors.append({"pdf_page": pn, "error": type(exc).__name__})
        info.update({
            "native_text_pages_100plus_chars": native,
            "nonempty_text_pages": nonempty,
            "empty_text_pages": len(empty_pages),
            "empty_text_page_numbers_preview": empty_pages[:60],
            "sparse_text_pages_1_to_99_chars": len(sparse_pages),
            "sparse_page_numbers_preview": sparse_pages[:60],
            "pages_with_embedded_images": image_pages,
            "text_character_count": total_chars,
            "page_errors": page_errors[:60],
            "heading_candidates_first_pages": headings[:60],
            "first_text_previews": previews,
            "lesson_starts": [lessons[k] for k in sorted(lessons)]})
    return info

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--heading-pages", type=int, default=35)
    args = ap.parse_args()
    report = {
        "schema_version": 1,
        "method": "pymupdf_readonly_native_text_survey_no_ocr",
        "interpretation": ">=100 text chars is only a candidate, not proof of correct text. Embedded images need not be charts.",
        "volumes": []}
    for path in FILES:
        if not path.is_file():
            raise FileNotFoundError(f"Expected source file missing: {path}")
        item = inspect_one(path, args.heading_pages)
        report["volumes"].append(item)
        keys = ["path", "bytes", "sha256", "page_count", "embedded_toc_count",
                "native_text_pages_100plus_chars", "empty_text_pages",
                "pages_with_embedded_images", "text_character_count", "page_errors"]
        print("INVENTORY " + json.dumps({k: item[k] for k in keys}, ensure_ascii=False), flush=True)
        print("OUTLINE " + json.dumps({
            "path": item["path"], "embedded": item["embedded_toc_preview"][:30],
            "candidates": item["heading_candidates_first_pages"][:30],
            "sample": item["first_text_previews"][:3]}, ensure_ascii=False), flush=True)
        print("LESSONS " + json.dumps({"path": item["path"], "lessons": item["lesson_starts"]}, ensure_ascii=False), flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f'INVENTORY_DONE volumes={len(report["volumes"])} path={args.out}', flush=True)

if __name__ == "__main__":
    main()
