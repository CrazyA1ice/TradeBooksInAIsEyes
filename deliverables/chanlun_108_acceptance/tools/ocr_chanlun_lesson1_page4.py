#!/usr/bin/env python3
"""OCR one source PDF page for research review; no source file modifications."""
import hashlib
import json
import subprocess
from pathlib import Path
import fitz
ROOT = Path(__file__).resolve().parents[1]
index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
volume=index["volumes"][0]
pdf=ROOT/volume["path"]
if hashlib.sha256(pdf.read_bytes()).hexdigest()!=volume["sha256"]:
    raise RuntimeError("PDF SHA does not match indexed original")
with fitz.open(pdf) as doc:
    page=doc[3]  # PDF page 4, 1-based
    sources=page.get_image_info(xrefs=True)
    print("PAGE4_IMAGE_GEOMETRY "+json.dumps({"pdf_page":4,"page_rect":list(page.rect),"images":[{"bbox":list(x["bbox"]),"width":x["width"],"height":x["height"]} for x in sources]},ensure_ascii=False),flush=True)
    raster=page.get_pixmap(matrix=fitz.Matrix(2.5,2.5),alpha=False).tobytes("png")
proc=subprocess.run(["tesseract","stdin","stdout","-l","chi_sim+eng","--psm","3"],input=raster,capture_output=True)
print("OCR_RETURN_CODE",proc.returncode,flush=True)
if proc.returncode:
    raise RuntimeError(proc.stderr.decode("utf-8","replace")[:1000])
out=proc.stdout.decode("utf-8","replace")
print("OCR_TEXT_BEGIN page=4",flush=True)
print(out,flush=True)
print("OCR_TEXT_END page=4",flush=True)
print("OCR_STATS "+json.dumps({"pdf_page":4,"ocr_chars":len(out),"method":"tesseract chi_sim+eng psm3 2.5x rendered page","status":"unverified_ocr_requires_crosschecking"},ensure_ascii=False),flush=True)
