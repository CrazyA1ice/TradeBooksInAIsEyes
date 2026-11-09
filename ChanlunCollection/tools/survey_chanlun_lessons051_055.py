#!/usr/bin/env python3
"""SHA-pinned, read-only original PDF lesson survey; author text capped in CI logs."""
import hashlib,json,re
from pathlib import Path
import fitz
root=Path(__file__).resolve().parents[1]
idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
v=idx["volumes"][2]
pdfpath=root/v["path"]
assert hashlib.sha256(pdfpath.read_bytes()).hexdigest()==v["sha256"]
divider=re.compile(r"^\*{6,}$|解盘及互动问答|互动问答[：:]|解盘及答疑|读者问答|网友互动")
editor=re.compile(r"娇注|娇[：:]|编者注|网友|缠师[：:]")
terms=("荐股","股评","传销","学佛","三类买卖点","第一类买点","第二类买点","第三类买点","中枢","走势","级别","背驰","盘整背驰","日内","交易","530","分笔","线段","买入","卖出","确认","风险","股票","资金")
with fitz.open(pdfpath) as pdf:
 assert len(pdf)==v["pdf_page_count"]
 for n in range(51,56):
  j=next(i for i,x in enumerate(v["lessons"]) if x["lesson"]==n)
  start=v["lessons"][j]["start_pdf_page"];end=v["lessons"][j+1]["start_pdf_page"]-1
  record={"lesson":n,"title":v["lessons"][j]["title"],"volume":3,"path":v["path"],"sha256":v["sha256"],
          "start":start,"end":end,"original_date":None,"first_appendix":None,"pages":[],"author_topics":[]}
  budget=0
  for p in range(start,end+1):
   page=pdf[p-1];raw=page.get_text("text",sort=True);lines=raw.splitlines()
   split=next(((k+1,line.strip()[:100]) for k,line in enumerate(lines) if divider.search(line.strip())),None)
   if split and record["first_appendix"] is None:record["first_appendix"]={"page":p,"line":split[0],"marker":split[1]}
   if p==start:
    dt=re.search(r"(20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?)",raw)
    if dt:record["original_date"]=dt.group(1)
   im=page.get_image_info(xrefs=True)
   record["pages"].append({"pdf_page":p,"native_chars":len(raw.strip()),"embedded_images":len(im),
                           "has_editor_cues":bool(editor.search(raw)),"has_appendix_marker":bool(split)})
   if record["first_appendix"] is None or p==record["first_appendix"]["page"]:
    author=raw if not split else "\n".join(lines[:split[0]-1])
    tags=[t for t in terms if t in author]
    if tags:record["author_topics"].append({"page":p,"terms":tags})
    if author.strip() and budget<12500 and p<start+15:
     cue=" ".join(author.split())[:min(2600,12600-budget)]
     print("AUTHOR_CUE "+json.dumps({"lesson":n,"pdf_page":p,"text":cue},ensure_ascii=False),flush=True)
     budget+=len(cue)
  record["page_count"]=len(record["pages"])
  record["native_chars"]=sum(x["native_chars"] for x in record["pages"])
  record["image_pages"]=[x["pdf_page"] for x in record["pages"] if x["embedded_images"]>0]
  record["sparse_pages"]=[x["pdf_page"] for x in record["pages"] if x["native_chars"]<100]
  print("SOURCE_RECORD "+json.dumps(record,ensure_ascii=False),flush=True)
print("SHA_PINNED_51_55_SOURCE_READ_COMPLETE",flush=True)
