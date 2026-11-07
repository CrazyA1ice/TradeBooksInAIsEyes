#!/usr/bin/env python3
"""SHA-locked dual-volume source survey: lessons 21–25, bounded authored excerpts only."""
from pathlib import Path
import hashlib,json,re
import fitz
root=Path(__file__).resolve().parents[1]
idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
vols=idx["volumes"]
divider=re.compile(r"解盘及互动问答[：:]|解盘及互动问答|互动问答[：:]|^\*{6,}|解盘及答疑")
notes=re.compile(r"娇注|娇[：:]|编者注|(?:网友|缠师).{0,10}[：:]")
terms=["买卖点","完备性","走势中枢","第三类买点","第三类卖点","背驰","背弛","MACD","黄白线","红柱","绿柱","DIF","DEA","盘整","趋势","级别","严格","中枢震荡"]
for v in vols[:2]:
    f=root/v["path"]
    assert hashlib.sha256(f.read_bytes()).hexdigest()==v["sha256"],"SHA mismatch"
    with fitz.open(f) as pdf:
        assert len(pdf)==v["pdf_page_count"]
        for i,chapter in enumerate(v["lessons"]):
            n=chapter["lesson"]
            if not 21<=n<=25:continue
            start=chapter["start_pdf_page"]
            end=v["lessons"][i+1]["start_pdf_page"] if i+1<len(v["lessons"]) else v["pdf_page_count"]+1
            data={"lesson":n,"volume":v["volume"],"source":v["path"],"sha256":v["sha256"],"title":chapter["title"],
                  "start":start,"end":end-1,"first_dialogue":None,"editor_note_pages":[],
                  "pages":[],"initial_article_date":None,"topic_pages":[]}
            quote_budget=0
            for pno in range(start,end):
                page=pdf[pno-1];raw=page.get_text("text",sort=True);lines=raw.splitlines()
                d=next(((j+1,l.strip()[:110]) for j,l in enumerate(lines) if divider.search(l)),None)
                if data["first_dialogue"] is None and d:
                    data["first_dialogue"]={"pdf_page":pno,"line":d[0],"marker":d[1]}
                if notes.search(raw):data["editor_note_pages"].append(pno)
                if pno==start:
                    dt=re.search(r"(20\d\d[-年/\s]+(?:\d\d)[-/月\s]+(?:\d\d).{0,4}\d\d[:：]\d\d(?::\d\d)?)",raw)
                    if dt:data["initial_article_date"]=dt.group(1)
                pic=page.get_image_info(xrefs=True)
                data["pages"].append({"pdf_page":pno,"native_chars":len(raw.strip()),"images":len(pic),
                                     "has_dialogue_divider":bool(d),"has_editor_or_dialogue_markers":bool(notes.search(raw))})
                if data["first_dialogue"] is None or data["first_dialogue"]["pdf_page"]==pno:
                    orig=raw if d is None else "\n".join(lines[:d[0]-1])
                    if orig.strip():
                        found=[t for t in terms if t in orig]
                        if found:data["topic_pages"].append({"page":pno,"terms":found})
                        if quote_budget<4500 and pno<start+9:
                            bounded=" ".join(orig.split())[:min(1800,5000-quote_budget)]
                            print("ORIGINAL_CUE "+json.dumps({"lesson":n,"volume":v["volume"],"page":pno,"text":bounded},ensure_ascii=False),flush=True)
                            quote_budget+=len(bounded)
            data["total_native_chars"]=sum(p["native_chars"] for p in data["pages"])
            data["image_pages"]=[p["pdf_page"] for p in data["pages"] if p["images"]]
            data["low_text_pages"]=[p["pdf_page"] for p in data["pages"] if p["native_chars"]<100]
            print("LESSON_AUDIT "+json.dumps(data,ensure_ascii=False),flush=True)
print("SURVEY_COMPLETE_DUAL_VOLUME_21_25",flush=True)
