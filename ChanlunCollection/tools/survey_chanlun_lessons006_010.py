#!/usr/bin/env python3
"""Read-only, version-pinned research survey: Chanlun volume 1 lessons 6..10.
Print structural evidence plus bounded source snippets, never full lesson text.
"""
import hashlib, json, re
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
v=index["volumes"][0]
p=ROOT/v["path"]
assert hashlib.sha256(p.read_bytes()).hexdigest()==v["sha256"],"Source version mismatch"
Q=re.compile(r"(?:互动问答|解盘及互动问答|网友.*[:：]|缠师[:：]|娇注[:：]|娇[:：])")
with fitz.open(p) as pdf:
    for n in range(6,11):
        start=v["lessons"][n-1]["start_pdf_page"]
        stop=v["lessons"][n]["start_pdf_page"]
        print("LESSON_START "+json.dumps({"lesson":n,"title":v["lessons"][n-1]["title"],"start":start,"end":stop-1,"sha":v["sha256"]},ensure_ascii=False),flush=True)
        for pn in range(start,stop):
            page=pdf[pn-1]
            s=page.get_text("text",sort=True).strip()
            imgs=page.get_images(full=True)
            lines=s.splitlines()
            markers=[{"line":i+1,"text":" ".join(x.split())[:110]} for i,x in enumerate(lines) if Q.search(x)]
            item={"lesson":n,"page":pn,"chars":len(s),"images":len(imgs),
                  "note_markers":markers[:12],
                  "images_geometry":[{"width":img[2],"height":img[3]} for img in imgs[:5]]}
            print("PAGE_AUDIT "+json.dumps(item,ensure_ascii=False),flush=True)
            if s and len(s)>85:
                # Research excerpts are intentionally bounded, not page-complete.
                excerpt=s[:min(1650,len(s)//2)]
                if pn==start:excerpt=s[:min(3000,len(s)-1)]
                print("BOUNDED_EXCERPT "+json.dumps({"lesson":n,"page":pn,"excerpt":excerpt},ensure_ascii=False),flush=True)
print("READONLY_SURVEY_COMPLETE lessons=5",flush=True)
