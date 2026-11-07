#!/usr/bin/env python3
"""Volume 2, lessons 31-35. Verified PDF SHA, per-page metadata, bounded original cues."""
import fitz,hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
v=idx["volumes"][1]
f=root/v["path"]
assert hashlib.sha256(f.read_bytes()).hexdigest()==v["sha256"]
divider=re.compile(r"^\*{6,}$|解盘及互动问答|互动问答[：:]|解盘及答疑|读者问答|网友互动")
editor=re.compile(r"娇注|娇[：:]|编者注|网友|缠师[：:]")
terms=["资金管理","级别","买卖点","中枢","走势","当下","多义性","结合律","结合性","分解","背驰","仓位","风险","模式","概率","操作","第三类买点"]
with fitz.open(f) as pdf:
 assert len(pdf)==v["pdf_page_count"]
 for n in range(31,36):
  i=next(j for j,x in enumerate(v["lessons"]) if x["lesson"]==n)
  s=v["lessons"][i]["start_pdf_page"];end=v["lessons"][i+1]["start_pdf_page"]
  rec={"lesson":n,"title":v["lessons"][i]["title"],"volume":2,"pdf_path":v["path"],"sha256":v["sha256"],
       "start_pdf_page":s,"end_pdf_page":end-1,"article_date":None,"first_appendix_divider":None,"pages":[],"original_topic_pages":[]}
  emitted=0
  for p in range(s,end):
   page=pdf[p-1];raw=page.get_text("text",sort=True);lines=raw.splitlines()
   d=next(((j+1,l.strip()[:110]) for j,l in enumerate(lines) if divider.search(l.strip())),None)
   if d and rec["first_appendix_divider"] is None:
    rec["first_appendix_divider"]={"pdf_page":p,"line":d[0],"text":d[1]}
   if p==s:
    dt=re.search(r"(20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?)",raw)
    if dt:rec["article_date"]=dt.group(1)
   imgs=page.get_image_info(xrefs=True)
   rec["pages"].append({"pdf_page":p,"native_text_chars":len(raw.strip()),"image_count":len(imgs),
      "has_editor_dialogue_cue":bool(editor.search(raw)),"has_appendix_divider":bool(d)})
   if rec["first_appendix_divider"] is None or rec["first_appendix_divider"]["pdf_page"]==p:
    article=raw if d is None else "\n".join(lines[:d[0]-1])
    matches=[term for term in terms if term in article]
    if matches:rec["original_topic_pages"].append({"pdf_page":p,"terms":matches})
    if article.strip() and emitted<8500 and p<s+13:
     preview=" ".join(article.split())[:min(1800,8750-emitted)]
     print("ORIGINAL_CUE "+json.dumps({"lesson":n,"page":p,"text":preview},ensure_ascii=False),flush=True)
     emitted+=len(preview)
  rec["page_count"]=len(rec["pages"])
  rec["text_chars"]=sum(x["native_text_chars"] for x in rec["pages"])
  rec["image_pages"]=[x["pdf_page"] for x in rec["pages"] if x["image_count"]>0]
  rec["low_native_text_pages"]=[x["pdf_page"] for x in rec["pages"] if x["native_text_chars"]<100]
  print("LESSON_AUDIT "+json.dumps(rec,ensure_ascii=False),flush=True)
print("SHA_LOCKED_SOURCE_SURVEY_31_35_OK",flush=True)
