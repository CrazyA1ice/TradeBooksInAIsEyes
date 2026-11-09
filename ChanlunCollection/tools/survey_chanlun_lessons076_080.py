#!/usr/bin/env python3
"""Read-only SHA-pinned PDF survey, bounded original excerpts and selected page previews."""
import hashlib,json,re,base64
from pathlib import Path
from io import BytesIO
import fitz
from PIL import Image
root=Path(__file__).resolve().parents[1]
idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
v=idx["volumes"][3];path=root/v["path"]
assert hashlib.sha256(path.read_bytes()).hexdigest()==v["sha256"]
star=re.compile(r"^\*{6,}$")
ed=re.compile(r"娇注|娇[:：]|编者|更正|修订|后期|勘误|注：")
date=re.compile(r"20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?")
topics=("特征序列","包含关系","线段","分型","笔","缺口","中枢","顶分型","底分型","第一种情况","第二种情况","划分","定义","走势类型","买卖点","背驰","市场","风险","反向","跳空","级别")
preview_candidates={76:[145,149],77:[160,165],78:[177,179],79:[189,194],80:[204,213,225]}
with fitz.open(path) as pdf:
 assert len(pdf)==v["pdf_page_count"]
 for n in range(76,81):
  pos=next(i for i,x in enumerate(v["lessons"]) if x["lesson"]==n)
  start=v["lessons"][pos]["start_pdf_page"];stop=v["lessons"][pos+1]["start_pdf_page"]
  x={"lesson":n,"title":v["lessons"][pos]["title"],"volume":4,"source_path":v["path"],"sha256":v["sha256"],
     "first_page":start,"last_page":stop-1,"header_date":None,"first_starred_divider":None,"pages":[],"key_terms":[],"dated_post_headers":[],"preview_pages":[]}
  budget=0
  for p in range(start,stop):
   page=pdf[p-1];text=page.get_text("text",sort=True);lines=text.splitlines()
   starred=next((k for k,l in enumerate(lines) if star.search(l.strip())),None)
   if starred is not None and x["first_starred_divider"] is None:
    x["first_starred_divider"]={"pdf_page":p,"line":starred+1}
   if p==start:
    z=date.search(text);x["header_date"]=z.group(0) if z else None
   d=date.findall(text)
   if d and p>start:x["dated_post_headers"].append({"page":p,"dates":d[:3]})
   images=page.get_image_info(xrefs=True)
   x["pages"].append({"pdf_page":p,"native_chars":len(text.strip()),"embedded_images":len(images),"has_editor_cue":bool(ed.search(text)),"has_star_divider":starred is not None})
   if x["first_starred_divider"] is None or p==x["first_starred_divider"]["pdf_page"]:
    author="\n".join(lines[:starred]) if starred is not None else text
    term=[z for z in topics if z in author]
    if term:x["key_terms"].append({"pdf_page":p,"terms":term})
    if budget<10500 and p<start+13 and len(author.strip())>55:
     excerpt=" ".join(author.split())[:min(1700,10800-budget)]
     print("AUTHOR_CUE "+json.dumps({"lesson":n,"page":p,"text":excerpt},ensure_ascii=False),flush=True)
     budget+=len(excerpt)
   if p in preview_candidates.get(n,[]):
    pix=page.get_pixmap(matrix=fitz.Matrix(.72,.72),alpha=False,colorspace=fitz.csGRAY)
    im=Image.frombytes("L",(pix.width,pix.height),pix.samples);im.thumbnail((650,880))
    buf=BytesIO();im.save(buf,format="JPEG",quality=40,optimize=True)
    print("FIGURE_JPEG "+json.dumps({"lesson":n,"pdf_page":p,"width":im.width,"height":im.height,"encoded":base64.b64encode(buf.getvalue()).decode()},ensure_ascii=False),flush=True)
    x["preview_pages"].append(p)
  x["page_count"]=len(x["pages"]);x["native_chars"]=sum(p["native_chars"] for p in x["pages"])
  x["image_pages"]=[p["pdf_page"] for p in x["pages"] if p["embedded_images"]]
  x["sparse_pages"]=[p["pdf_page"] for p in x["pages"] if p["native_chars"]<100]
  print("SOURCE_RECORD "+json.dumps(x,ensure_ascii=False),flush=True)
print("PDF_ORIGINAL_SHA_MATCHED_76_80",flush=True)
