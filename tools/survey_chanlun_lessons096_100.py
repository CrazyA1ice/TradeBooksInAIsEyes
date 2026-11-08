#!/usr/bin/env python3
"""Immutable SHA-pinned fifth-volume source audit, 96–100: metadata, bounded excerpts, preview subset."""
from pathlib import Path
from io import BytesIO
import hashlib,json,re,base64
import fitz
from PIL import Image
root=Path(__file__).resolve().parents[1]
idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf8"))
v=idx["volumes"][4];path=root/v["path"]
assert hashlib.sha256(path.read_bytes()).hexdigest()==v["sha256"]
dates=re.compile(r"20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?")
divider=re.compile(r"^\*{6,}$")
edit=re.compile(r"娇注|娇加|娇[:：]|编者|更正|勘误|修订|补充说明|读后感")
terms=("赌徒","心理","概率","风险","买卖点","资金","中医","兵法","诗歌","操作","走势","表里","笔","分型","线段","力度","结构","级别","当下","生克","中枢","背驰","动力","二重","重叠","决定","可能","必然","利润")
previews={96:[156,162,169],97:[173,180,190],98:[193,199],99:[203,210,222],100:[225,230]}
with fitz.open(path) as pdf:
 assert len(pdf)==v["pdf_page_count"]
 for n in range(96,101):
  k=next(i for i,x in enumerate(v["lessons"]) if x["lesson"]==n)
  start=v["lessons"][k]["start_pdf_page"];end=v["lessons"][k+1]["start_pdf_page"]-1
  row={"lesson":n,"title":v["lessons"][k]["title"],"source_path":v["path"],"source_sha256":v["sha256"],"volume":5,
       "start":start,"end":end,"original_date":None,"first_star_divider":None,"page_info":[],"topics":[],"dated_followups":[],"rendered":[]}
  budget=0
  for p in range(start,end+1):
   page=pdf[p-1];raw=page.get_text("text",sort=True);lines=raw.splitlines()
   div=next((i+1 for i,s in enumerate(lines) if divider.match(s.strip())),None)
   if div and row["first_star_divider"] is None:row["first_star_divider"]={"page":p,"line":div}
   if p==start:
    q=dates.search(raw);row["original_date"]=q.group(0) if q else None
   dt=dates.findall(raw)
   if dt and p>start:row["dated_followups"].append({"page":p,"dates":dt[:3]})
   row["page_info"].append({"page":p,"chars":len(raw.strip()),"image_count":len(page.get_image_info(xrefs=True)), "editor_cue":bool(edit.search(raw)),"divider":bool(div)})
   if row["first_star_divider"] is None or p==row["first_star_divider"]["page"]:
    author=raw if not div else "\n".join(lines[:div-1])
    found=[s for s in terms if s in author]
    if found:row["topics"].append({"page":p,"terms":found})
    if p<start+12 and budget<14000 and len(author.strip())>100:
     excerpt=" ".join(author.split())[:min(1700,14500-budget)];budget+=len(excerpt)
     print("AUTHOR_CUE "+json.dumps({"n":n,"page":p,"text":excerpt},ensure_ascii=False),flush=True)
   if p in previews[n]:
    pix=page.get_pixmap(matrix=fitz.Matrix(.70,.70),colorspace=fitz.csGRAY,alpha=False)
    img=Image.frombytes("L",(pix.width,pix.height),pix.samples);img.thumbnail((650,850))
    buf=BytesIO();img.save(buf,format="JPEG",quality=40,optimize=True)
    print("PDF_PREVIEW "+json.dumps({"n":n,"page":p,"base64":base64.b64encode(buf.getvalue()).decode()},ensure_ascii=False),flush=True)
    row["rendered"].append(p)
  row["page_count"]=end-start+1
  row["native_chars"]=sum(x["chars"] for x in row["page_info"])
  row["image_pages"]=[x["page"] for x in row["page_info"] if x["image_count"]>0]
  row["sparse_pages"]=[x["page"] for x in row["page_info"] if x["chars"]<100]
  print("SOURCE_RECORD "+json.dumps(row,ensure_ascii=False),flush=True)
print("PASS_SOURCE96_100_ORIGINAL_PDF_SHA",flush=True)
