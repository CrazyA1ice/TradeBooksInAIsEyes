#!/usr/bin/env python3
"""Read-only volume-2 PDF survey, lessons 26–30; bounded excerpts, SHA verified."""
from pathlib import Path
import hashlib,json,re
import fitz
root=Path(__file__).resolve().parents[1]
idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
v=idx["volumes"][1]
f=root/v["path"]
assert hashlib.sha256(f.read_bytes()).hexdigest()==v["sha256"]
separator=re.compile(r"^\*{6,}$|解盘及互动问答|互动问答[：:]|解盘及答疑|读者问答")
annotations=re.compile(r"娇注|娇[：:]|编者注|网友|缠师[：:]")
terms=["第一类买点","第二类买点","第三类买点","背驰","背弛","盘整背驰","风险","级别","中枢","走势必完美","资金管理","MACD","转折","绝对性","止损","历史性底部"]
with fitz.open(f) as pdf:
 assert len(pdf)==v["pdf_page_count"]
 for n in range(26,31):
  k=next(i for i,x in enumerate(v["lessons"]) if x["lesson"]==n)
  start=v["lessons"][k]["start_pdf_page"];end=v["lessons"][k+1]["start_pdf_page"]
  meta={"lesson":n,"title":v["lessons"][k]["title"],"volume":v["volume"],"source_path":v["path"],
        "sha256":v["sha256"],"start":start,"end":end-1,"original_date":None,"divider":None,
        "pages":[],"original_topic_pages":[]}
  emitted=0
  for no in range(start,end):
   page=pdf[no-1];s=page.get_text("text",sort=True);ls=s.splitlines()
   match=next(((i+1,line.strip()[:90]) for i,line in enumerate(ls) if separator.search(line.strip())),None)
   if match and meta["divider"] is None:
    meta["divider"]={"page":no,"line":match[0],"marker":match[1]}
   if no==start:
    dt=re.search(r"(20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?)",s)
    if dt:meta["original_date"]=dt.group(1)
   images=page.get_image_info(xrefs=True)
   meta["pages"].append({"pdf_page":no,"native_text_chars":len(s.strip()),"image_count":len(images),
       "has_divider":bool(match),"has_dialogue_or_editor_cues":bool(annotations.search(s))})
   if meta["divider"] is None or meta["divider"]["page"]==no:
    orig=s if match is None else "\n".join(ls[:match[0]-1])
    found=[term for term in terms if term in orig]
    if found:meta["original_topic_pages"].append({"pdf_page":no,"terms":found})
    if orig.strip() and emitted<6200 and no<start+11:
     words=" ".join(orig.split())
     excerpt=words[:min(1850,6500-emitted)]
     print("SOURCE_EXCERPT "+json.dumps({"lesson":n,"page":no,"text":excerpt},ensure_ascii=False),flush=True)
     emitted+=len(excerpt)
  meta["total_native_text_chars"]=sum(x["native_text_chars"] for x in meta["pages"])
  meta["image_pages"]=[x["pdf_page"] for x in meta["pages"] if x["image_count"]]
  meta["low_text_pages"]=[x["pdf_page"] for x in meta["pages"] if x["native_text_chars"]<100]
  print("SOURCE_RECORD "+json.dumps(meta,ensure_ascii=False),flush=True)
print("SURVEY_COMPLETE_26_30",flush=True)
