#!/usr/bin/env python3
"""Page-level OCR assessment, not validated reconstruction of figures."""
import hashlib
import json
import subprocess
from pathlib import Path
import fitz
root=Path(__file__).resolve().parents[1]
idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
v=idx["volumes"][0]
path=root/v["path"]
assert hashlib.sha256(path.read_bytes()).hexdigest()==v["sha256"]
with fitz.open(path) as doc:
    for pno in [9,10]:
        page=doc[pno-1]
        imgs=page.get_image_info(xrefs=True)
        raster=page.get_pixmap(matrix=fitz.Matrix(2.4,2.4),alpha=False).tobytes("png")
        r=subprocess.run(["tesseract","stdin","stdout","-l","chi_sim+eng","--psm","3"],input=raster,capture_output=True)
        if r.returncode: raise RuntimeError(r.stderr.decode("utf-8","replace"))
        content=" ".join(r.stdout.decode("utf-8","replace").split())
        print("FIGURE_QA "+json.dumps({"pdf_page":pno,"image_count":len(imgs),
             "image_boxes":[{"bbox":list(x["bbox"]),"width":x["width"],"height":x["height"]} for x in imgs],
             "ocr_chars":len(content),"ocr_uncertain_excerpt":content[:480],
             "status":"not_visually_validated_no_quantitative_claims"},ensure_ascii=False),flush=True)
