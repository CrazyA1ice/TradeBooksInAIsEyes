#!/usr/bin/env python3
"""Read-only SHA-pinned volume 3 survey lessons 46-50, limited native text cues; do not edit PDF."""
import fitz,hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
index=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
v=index["volumes"][2]
f=root/v["path"]
assert hashlib.sha256(f.read_bytes()).hexdigest()==v["sha256"]
seps=re.compile(r"^\*{6,}$|解盘及互动问答|互动问答[：:]|解盘及答疑|读者问答|网友互动")
notes=re.compile(r"娇注|娇[：:]|编者注|网友|缠师[：:]")
terms=("每日","走势","分类","一夜情","暴跌","利润率","操作模式","细节","背驰","盘整背驰","开盘","收盘","中枢","级别","买卖点","T+1","风险","资金","仓位","高点","低点","30分钟","5分钟")
with fitz.open(f) as pdf:
 assert len(pdf)==v["pdf_page_count"]
 for n in range(46,51):
  k=next(i for i,z in enumerate(v["lessons"]) if z["lesson"]==n)
  a=v["lessons"][k]["start_pdf_page"];b=v["lessons"][k+1]["start_pdf_page"]
  rec={"lesson":n,"title":v["lessons"][k]["title"],"volume":v["volume"],"path":v["path"],"sha256":v["sha256"],"start":a,"end":b-1,
       "date":None,"first_appendix":None,"pages":[],"topics":[]}
  budget=0
  for page_no in range(a,b):
   page=pdf[page_no-1];raw=page.get_text("text",sort=True);lines=raw.splitlines()
   div=next(((j+1,line.strip()[:100]) for j,line in enumerate(lines) if seps.search(line.strip())),None)
   if div and rec["first_appendix"] is None:rec["first_appendix"]={"page":page_no,"line":div[0],"marker":div[1]}
   if page_no==a:
    dt=re.search(r"(20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?)",raw)
    if dt:rec["date"]=dt.group(1)
   im=page.get_image_info(xrefs=True)
   rec["pages"].append({"pdf_page":page_no,"native_chars":len(raw.strip()),"image_count":len(im),
                       "has_editor_cue":bool(notes.search(raw)),"has_appendix_separator":bool(div)})
   if rec["first_appendix"] is None or page_no==rec["first_appendix"]["page"]:
    author=raw if div is None else "\n".join(lines[:div[0]-1])
    ts=[w for w in terms if w in author]
    if ts:rec["topics"].append({"page":page_no,"terms":ts})
    if author.strip() and budget<11000 and page_no<a+13:
     excerpt=" ".join(author.split())[:min(2300,11200-budget)]
     print("AUTHOR_CUE "+json.dumps({"lesson":n,"page":page_no,"text":excerpt},ensure_ascii=False),flush=True)
     budget+=len(excerpt)
  rec["page_count"]=len(rec["pages"]);rec["native_chars"]=sum(p["native_chars"] for p in rec["pages"])
  rec["image_pages"]=[p["pdf_page"] for p in rec["pages"] if p["image_count"]]
  rec["sparse_pages"]=[p["pdf_page"] for p in rec["pages"] if p["native_chars"]<100]
  print("LESSON_META "+json.dumps(rec,ensure_ascii=False),flush=True)
print("LESSONS46_50_VERIFIED_ORIGINAL_PDF_READONLY",flush=True)
