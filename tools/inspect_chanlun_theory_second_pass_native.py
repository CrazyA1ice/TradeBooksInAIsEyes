#!/usr/bin/env python3
"""Bounded original-PDF native-text check for cross-lesson theory second pass.

Only extracts short source-context windows to CI logs, retaining PDF SHA,
page SHA, and editor-marker warnings. No PDF images/OCR/market-data access.
This never confers independent authorship or confirms literal truth of
the claims; it is a reader-side original compilation text preflight.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INV=ROOT/"reports/source_inventory/chanlun_20261107_verified.json"
PINS=ROOT/"reports/source_inventory/chanlun_theory_second_pass_native_text_sha256.json"
TARGETS={
  1:{247:("第三类买点","回试","中枢"),253:("三类买卖点","完备","安全"),254:("第三类","第二类","中枢")},
  2:{3:("MACD","背驰","中枢"),4:("面积","MACD","背驰"),91:("区间套","背驰","级别"),93:("区间套","走势","背驰")},
  3:{17:("必要条件","第三类卖点","背驰"),18:("充分条件","大转折","娇"),161:("买卖点","次级别","中枢"),162:("2009","第三类","娇")},
  4:{299:("自同构","结构","分形"),300:("自同构","级别","逻辑"),301:("f1","f2","初始化")},
  5:{64:("第一重表里","四种","笔"),65:("（1，1）","状态","延伸"),93:("Zn","中枢","中轴"),94:("Zn","第三类","A、B")}
}
EDITOR_CUES=("娇注","（娇：","(娇：","编者","后附","注：")
MAX_EXCERPTS=2
MAX_CHARS=190

def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def main():
    import pymupdf
    manifest=json.loads(INV.read_text(encoding="utf-8"))["volumes"]
    pins=json.loads(PINS.read_text(encoding="utf-8"))
    if pins["method"]!="pymupdf_1.26.7_get_text_sort_true" or pins["original_pages_count"]!=18 or pins["original_pdf_images_inspected"] is not False or pins["real_market_data_read"] is not False:
        raise ValueError("Original native text method/scope changed")
    declared={f"{vol}:{page}" for vol,ps in TARGETS.items() for page in ps}
    if set(pins["original_pages_native_text_sha256"])!=declared:
        raise ValueError("Original text page pin membership changed")
    volumes={int(Path(v["path"]).stem.split("卷")[-1]):v for v in manifest}
    n=0
    for vol,page_terms in TARGETS.items():
        v=volumes[vol]
        path=ROOT/v["path"]
        if pins["original_pdf_sha256"][str(vol)]!=v["sha256"]:
            raise ValueError("Source-pinned volume PDF SHA drift")
        if digest(path)!=v["sha256"] or path.stat().st_size!=v["bytes"]:
            raise ValueError("Original canonical PDF binary SHA drift")
        with pymupdf.open(path) as pdf:
            if pdf.page_count!=v["page_count"]: raise ValueError("Original PDF page count drift")
            for page,needles in page_terms.items():
                raw=pdf.load_page(page-1).get_text("text",sort=True)
                native_sha=hashlib.sha256(raw.encode("utf-8")).hexdigest()
                if pins["original_pages_native_text_sha256"][f"{vol}:{page}"]!=native_sha:
                    raise ValueError(f"Pinned original native text changed v{vol} p{page}")
                simplified=" ".join(raw.split())
                excerpts=[]
                for term in needles:
                    match=re.search(re.escape(term),simplified,re.I)
                    if not match:continue
                    left=max(0,match.start()-70)
                    excerpt=simplified[left:left+MAX_CHARS]
                    if any(excerpt in old["context"] for old in excerpts): continue
                    excerpts.append({"keyword":term,"context":excerpt})
                    if len(excerpts)>=MAX_EXCERPTS:break
                if not excerpts:raise ValueError(f"Critical original source text not found at v{vol} p{page}")
                print("SECOND_PASS_PDF_SOURCE="+json.dumps({
                  "volume":vol,"physical_pdf_page":page,
                  "native_text_sha256":hashlib.sha256(raw.encode("utf-8")).hexdigest(),
                  "char_count":len(raw),"original_pdf_sha256":v["sha256"],
                  "excerpts":excerpts,
                  "editor_cues":{k:simplified.count(k) for k in EDITOR_CUES if k in simplified},
                  "source_role":"COMPILATION_MIXED_PROVENANCE_NOT_FIRST_PUBLICATION_PROVEN",
                  "image_reviewed":False,
                },ensure_ascii=False))
                n+=1
    if n!=18:raise ValueError("Expected 18 specific original chapter pages")
    print("SECOND_PASS_PDF_SUMMARY="+json.dumps({"pages":n,"volumes":5,
          "source_pdf_shas_checked":True,"image_pages_ocr_read":False,
          "market_data_read":False},ensure_ascii=False))

if __name__=="__main__":
    main()
