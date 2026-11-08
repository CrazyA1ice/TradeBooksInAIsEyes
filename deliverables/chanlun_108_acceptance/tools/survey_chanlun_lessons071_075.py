#!/usr/bin/env python3
"""Read-only SHA-pinned survey of original PDF lessons 71–75; bounded excerpts, page metadata and compact previews."""
import hashlib,json,re,base64
from pathlib import Path
from io import BytesIO
import fitz
from PIL import Image
root=Path(__file__).resolve().parents[1]
idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
v=idx["volumes"][3];pdfpath=root/v["path"]
assert hashlib.sha256(pdfpath.read_bytes()).hexdigest()==v["sha256"],"source SHA mismatch"
divider=re.compile(r"^\*{6,}$|解盘及互动问答|互动问答[：:]|解盘及答疑|读者问答")
editor=re.compile(r"娇[：:]|娇注|娇加注|编者|勘误|后期|修正|质疑")
topics=("特征序列","线段","缺口","分型","买卖点","第三类","第一类","第二类","预测","政策","背驰","趋势","获利","机会","风险","获利模式","级别","中枢","区间","分解","包含关系","递归","无穷","确认","炒股","庄家","资金")
with fitz.open(pdfpath) as pdf:
 assert len(pdf)==v["pdf_page_count"]
 for n in range(71,76):
  k=next(i for i,x in enumerate(v["lessons"]) if x["lesson"]==n)
  a=v["lessons"][k]["start_pdf_page"];b=v["lessons"][k+1]["start_pdf_page"]-1
  out={"lesson":n,"title":v["lessons"][k]["title"],"volume":v["volume"],"pdf_path":v["path"],"sha256":v["sha256"],"start":a,"end":b,
       "original_date":None,"first_divider":None,"pages":[],"author_topics":[],"native_chars":0,"preview_pages":[]}
  budget=0;preview_count=0
  for p in range(a,b+1):
   page=pdf[p-1];raw=page.get_text("text",sort=True);lines=raw.splitlines()
   mark=next(((i+1,line.strip()[:90]) for i,line in enumerate(lines) if divider.search(line.strip())),None)
   if mark and out["first_divider"] is None:out["first_divider"]={"pdf_page":p,"line":mark[0],"marker":mark[1]}
   if p==a:
    dt=re.search(r"(20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?)",raw)
    out["original_date"]=dt.group(1) if dt else None
   img_count=len(page.get_image_info(xrefs=True))
   out["pages"].append({"pdf_page":p,"native_chars":len(raw.strip()),"images":img_count,"editorial_cue":bool(editor.search(raw)),"starred_divider":bool(mark)})
   out["native_chars"]+=len(raw.strip())
   if out["first_divider"] is None or p==out["first_divider"]["pdf_page"]:
    author=raw if mark is None else "\n".join(lines[:mark[0]-1])
    found=[s for s in topics if s in author]
    if found:out["author_topics"].append({"pdf_page":p,"terms":found})
    if author.strip() and budget<8200 and p<a+12:
     excerpt=" ".join(author.split())[:min(1450,8300-budget)]
     budget+=len(excerpt)
     print("AUTHOR_CUE "+json.dumps({"lesson":n,"page":p,"text":excerpt},ensure_ascii=False),flush=True)
   if img_count and preview_count<2 and p<a+14:
    pix=page.get_pixmap(matrix=fitz.Matrix(.70,.70),alpha=False,colorspace=fitz.csGRAY)
    im=Image.frombytes("L",(pix.width,pix.height),pix.samples);im.thumbnail((650,880))
    buf=BytesIO();im.save(buf,format="JPEG",quality=43,optimize=True)
    print("FIGURE_JPEG "+json.dumps({"lesson":n,"page":p,"width":im.width,"height":im.height,"encoded":base64.b64encode(buf.getvalue()).decode()},ensure_ascii=False),flush=True)
    preview_count+=1;out["preview_pages"].append(p)
  out["page_count"]=len(out["pages"])
  out["image_pages"]=[z["pdf_page"] for z in out["pages"] if z["images"]]
  out["sparse_pages"]=[z["pdf_page"] for z in out["pages"] if z["native_chars"]<100]
  print("SOURCE_RECORD "+json.dumps(out,ensure_ascii=False),flush=True)
print("ORIGINAL_PDF_LESSONS_071_075_SHA_VERIFIED",flush=True)
