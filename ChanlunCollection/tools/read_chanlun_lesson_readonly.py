#!/usr/bin/env python3
"""Verify lesson-1 boundaries from indexed PDF; emit source-text only on --emit-text."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--lesson", type=int, default=1)
    ap.add_argument("--emit-text", action="store_true")
    args=ap.parse_args()
    index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    match=[]
    for v in index["volumes"]:
        for position,record in enumerate(v["lessons"]):
            if record["lesson"]==args.lesson:
                next_page=v["lessons"][position+1]["start_pdf_page"] if position+1<len(v["lessons"]) else v["pdf_page_count"]+1
                match.append((v,record,next_page))
    if len(match)!=1:
        raise RuntimeError(f"Ambiguous lesson id: {args.lesson}")
    v,l,end=match[0]
    pdf=ROOT/v["path"]
    if hashlib.sha256(pdf.read_bytes()).hexdigest()!=v["sha256"]:
        raise RuntimeError("Source PDF changed since indexed.")
    with fitz.open(pdf) as doc:
        if doc.page_count!=v["pdf_page_count"]:
            raise RuntimeError("Source page count changed.")
        if not 1<=l["start_pdf_page"]<end<=len(doc)+1:
            raise RuntimeError("Indexed lesson page span invalid.")
        print("LESSON_BOUNDARY "+json.dumps({"lesson":args.lesson,"title":l["title"],"source":v["path"],"sha256":v["sha256"],"start_pdf_page":l["start_pdf_page"],"end_pdf_page_inclusive":end-1,"page_count":end-l["start_pdf_page"]},ensure_ascii=False),flush=True)
        for page_no in range(l["start_pdf_page"],end):
            p=doc[page_no-1]
            text=p.get_text("text",sort=True)
            found_images=len(p.get_images(full=True))
            print("PAGE_META "+json.dumps({"pdf_page":page_no,"characters":len(text),"embedded_images":found_images},ensure_ascii=False),flush=True)
            if args.emit_text:
                print("PAGE_TEXT_BEGIN "+str(page_no),flush=True)
                print(text.replace("\x00",""),flush=True)
                print("PAGE_TEXT_END "+str(page_no),flush=True)
if __name__=="__main__":
    main()
