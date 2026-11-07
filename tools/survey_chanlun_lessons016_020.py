#!/usr/bin/env python3
"""SHA-locked read-only PDF survey, authored layers and bounded source cues."""
import hashlib,json,re
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
v=idx["volumes"][0]; pdf=ROOT/v["path"]
assert hashlib.sha256(pdf.read_bytes()).hexdigest()==v["sha256"]
div=re.compile(r"(?:解盘及互动问答|互动问答[：:]|网友与缠师|网友互动|解盘及回复)")
note=re.compile(r"(?:娇注|娇[：:]|编者注|缠师[：:]|网友.{0,14}[：:])")
tokens=["走势中枢","中枢","第三类买点","第三类卖点","第一类买点","第二类买点","走势终完美","级别","背驰","递归","当下","分解"]
with fitz.open(pdf) as doc:
    assert len(doc)==v["pdf_page_count"]
    for lesson in range(16,21):
        begin=v["lessons"][lesson-1]["start_pdf_page"]
        after=v["lessons"][lesson]["start_pdf_page"]
        info={"lesson":lesson,"title":v["lessons"][lesson-1]["title"],"start":begin,"end":after-1,"pages":[],
              "author_date":None,"first_dialogue":None,"sha256":v["sha256"],"source_cues":[]}
        for pno in range(begin,after):
            page=doc[pno-1]
            raw=page.get_text("text",sort=True)
            lines=raw.splitlines()
            mark=next(((k+1,line.strip()[:95]) for k,line in enumerate(lines) if div.search(line)),None)
            if mark and info["first_dialogue"] is None:info["first_dialogue"]={"page":pno,"line":mark[0],"marker":mark[1]}
            if pno==begin:
                match=re.search(r"\(?(20\d\d-\d\d-\d\d\s+\d\d:\d\d(?::\d\d)?)\)?",raw)
                if match:info["author_date"]=match.group(1)
            imgs=page.get_image_info(xrefs=True)
            row={"pdf_page":pno,"native_text_chars":len(raw.strip()),"image_count":len(imgs),
                 "has_dialogue_marker":bool(mark),"has_editor_or_dialogue_cues":bool(note.search(raw))}
            info["pages"].append(row)
            # Only original first-page and short snippets of original continuation:
            if info["first_dialogue"] is None or (info["first_dialogue"]["page"]==pno and mark):
                original=raw if not mark else "\n".join(lines[:mark[0]-1])
                stripped=" ".join(original.split())
                if stripped:
                    head=2400 if pno==begin else 1200
                    if pno<=begin+5:
                        print("SOURCE_CUE "+json.dumps({"lesson":lesson,"pdf_page":pno,
                            "excerpt":stripped[:head]},ensure_ascii=False),flush=True)
                    cues=[t for t in tokens if t in original]
                    if cues:info["source_cues"].append({"page":pno,"terms":cues})
        info["total_native_text_chars"]=sum(x["native_text_chars"] for x in info["pages"])
        info["image_pages"]=[x["pdf_page"] for x in info["pages"] if x["image_count"]]
        info["low_text_pages"]=[x["pdf_page"] for x in info["pages"] if x["native_text_chars"]<100]
        print("SOURCE_AUDIT "+json.dumps(info,ensure_ascii=False),flush=True)
print("SOURCE_SURVEY_DONE_16_20",flush=True)
