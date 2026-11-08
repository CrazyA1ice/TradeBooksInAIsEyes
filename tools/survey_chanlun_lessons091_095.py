#!/usr/bin/env python3
"""Immutable original PDF source scan, bounded excerpts and selected low-res previews, 91–95."""
import hashlib,json,re,base64
from pathlib import Path
from io import BytesIO
import fitz
from PIL import Image
root=Path(__file__).resolve().parents[1]
idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
v=idx["volumes"][4];p=root/v["path"]
assert hashlib.sha256(p.read_bytes()).hexdigest()==v["sha256"]
date=re.compile(r"20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?")
star=re.compile(r"^\*{6,}$")
editor=re.compile(r"娇注|娇加|娇[:：]|编者|更正|勘误|修订|补充说明")
terms=("表里","中枢","同级别","不同级别","线段","笔","震荡","监视器","区间套","力度","背驰","MACD","交易","确认","当下","分型","构造","结构","转折","操作","心理","走势","自动","策略")
previews={91:[65,72,84],92:[94,103,114],93:[125,131,139],94:[144,148],95:[151,154]}
with fitz.open(p) as pdf:
 assert len(pdf)==v["pdf_page_count"]
 for n in range(91,96):
  k=next(i for i,x in enumerate(v["lessons"]) if x["lesson"]==n)
  start=v["lessons"][k]["start_pdf_page"];end=v["lessons"][k+1]["start_pdf_page"]-1
  row={"lesson":n,"title":v["lessons"][k]["title"],"volume":5,
       "source_path":v["path"],"source_sha256":v["sha256"],"start":start,"end":end,
       "original_date":None,"first_divider":None,"pages":[],"topic_pages":[],"dated_material":[],"previews":[]}
  budget=0
  for page in range(start,end+1):
   x=pdf[page-1];raw=x.get_text("text",sort=True);lines=raw.splitlines()
   div=next((i+1 for i,l in enumerate(lines) if star.match(l.strip())),None)
   if div and row["first_divider"] is None:row["first_divider"]={"page":page,"line":div}
   if page==start:
    d=date.search(raw);row["original_date"]=d.group(0) if d else None
   dates=date.findall(raw)
   if dates and page>start:row["dated_material"].append({"page":page,"dates":dates[:3]})
   imagecount=len(x.get_image_info(xrefs=True))
   row["pages"].append({"page":page,"text_chars":len(raw.strip()),"image_count":imagecount,
                        "editor_cue":bool(editor.search(raw)),"starred":bool(div)})
   if row["first_divider"] is None or row["first_divider"]["page"]==page:
    author=raw if div is None else "\n".join(lines[:div-1])
    found=[s for s in terms if s in author]
    if found:row["topic_pages"].append({"page":page,"terms":found})
    if page<start+15 and budget<11500 and len(author.strip())>90:
     excerpt=" ".join(author.split())[:min(1550,11700-budget)];budget+=len(excerpt)
     print("AUTHOR_CUE "+json.dumps({"n":n,"p":page,"text":excerpt},ensure_ascii=False),flush=True)
   if page in previews[n]:
    pix=x.get_pixmap(matrix=fitz.Matrix(.70,.70),alpha=False,colorspace=fitz.csGRAY)
    img=Image.frombytes("L",(pix.width,pix.height),pix.samples);img.thumbnail((640,850))
    buf=BytesIO();img.save(buf,format="JPEG",quality=42,optimize=True)
    print("PDF_PREVIEW "+json.dumps({"n":n,"p":page,"image":base64.b64encode(buf.getvalue()).decode()},ensure_ascii=False),flush=True)
    row["previews"].append(page)
  row["page_count"]=end-start+1
  row["native_chars"]=sum(x["text_chars"] for x in row["pages"])
  row["image_pages"]=[x["page"] for x in row["pages"] if x["image_count"]]
  row["sparse_pages"]=[x["page"] for x in row["pages"] if x["text_chars"]<100]
  print("SOURCE_RECORD "+json.dumps(row,ensure_ascii=False),flush=True)
print("PASS_PINNED_PDF_91_95",flush=True)
