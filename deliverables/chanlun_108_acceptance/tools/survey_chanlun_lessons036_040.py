#!/usr/bin/env python3
"""Read-only, SHA-locked survey of second-volume lessons 36–40; limited excerpts for reasoning."""
from pathlib import Path
import fitz,hashlib,json,re
root=Path(__file__).resolve().parents[1]
index=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
v=index["volumes"][1]
assert v["volume"]==2 and hashlib.sha256((root/v["path"]).read_bytes()).hexdigest()==v["sha256"]
separators=re.compile(r"^\*{6,}$|解盘及互动问答|互动问答[：:]|解盘及答疑|网友互动|读者问答")
notes=re.compile(r"娇注|娇[：:]|编者注|网友|缠师[：:]")
topics=("连接","结合律","交换律","分解","同级别","多义性","背驰","盘整背驰","中枢","级别","第三类买卖点","第三类买点","风险","递归","a+A+b+B+c","结束","区间套")
with fitz.open(root/v["path"]) as pdf:
 assert len(pdf)==v["pdf_page_count"]
 for n in range(36,41):
  k=next(i for i,lesson in enumerate(v["lessons"]) if lesson["lesson"]==n)
  a=v["lessons"][k]["start_pdf_page"];b=v["lessons"][k+1]["start_pdf_page"]
  meta={"lesson":n,"volume":2,"title":v["lessons"][k]["title"],"source":v["path"],"sha256":v["sha256"],
        "start":a,"end":b-1,"date":None,"first_appendix":None,"pages":[],"topic_pages":[]}
  budget=0
  for p in range(a,b):
   page=pdf[p-1];raw=page.get_text("text",sort=True);ls=raw.splitlines()
   mark=next(((i+1,l.strip()[:110]) for i,l in enumerate(ls) if separators.search(l.strip())),None)
   if mark and meta["first_appendix"] is None:meta["first_appendix"]={"page":p,"line":mark[0],"marker":mark[1]}
   if p==a:
    dt=re.search(r"(20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?)",raw)
    if dt:meta["date"]=dt.group(1)
   images=page.get_image_info(xrefs=True)
   meta["pages"].append({"pdf_page":p,"native_chars":len(raw.strip()),"images":len(images),
                         "has_editor_cues":bool(notes.search(raw)),"has_appendix_divider":bool(mark)})
   if meta["first_appendix"] is None or p==meta["first_appendix"]["page"]:
    authored=raw if mark is None else "\n".join(ls[:mark[0]-1])
    topic=[t for t in topics if t in authored]
    if topic:meta["topic_pages"].append({"page":p,"terms":topic})
    if authored.strip() and budget<7400 and p<a+10:
     excerpt=" ".join(authored.split())[:min(2200,7550-budget)]
     print("SOURCE_CUE "+json.dumps({"lesson":n,"page":p,"excerpt":excerpt},ensure_ascii=False),flush=True)
     budget+=len(excerpt)
  meta["total_pages"]=len(meta["pages"])
  meta["native_chars"]=sum(q["native_chars"] for q in meta["pages"])
  meta["image_pages"]=[q["pdf_page"] for q in meta["pages"] if q["images"]]
  meta["sparse_pages"]=[q["pdf_page"] for q in meta["pages"] if q["native_chars"]<100]
  print("SOURCE_AUDIT "+json.dumps(meta,ensure_ascii=False),flush=True)
print("END_READONLY_36_40",flush=True)
