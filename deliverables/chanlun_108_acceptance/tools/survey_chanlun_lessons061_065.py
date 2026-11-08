#!/usr/bin/env python3
"""Read-only SHA-pinned original PDF text/figure scan; bounded excerpts, no source mutation."""
import base64,hashlib,json,re
from io import BytesIO
from pathlib import Path
import fitz
from PIL import Image
root=Path(__file__).resolve().parents[1]
idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
v=idx["volumes"][2];pdfpath=root/v["path"]
assert hashlib.sha256(pdfpath.read_bytes()).hexdigest()==v["sha256"]
sep=re.compile(r"^\*{6,}$|解盘及互动问答|互动问答[：:]|解盘及答疑|读者问答")
editor=re.compile(r"娇注|娇[：:]|编者注|思考贴|后期|分段后|缠师[：:]")
topics=("区间套","分型","笔","线段","中枢","走势类型","次级别","背驰","包含关系","顶分型","底分型","特征序列","破坏","精确定位","缺口","最低级别","第三类","买卖点","级别","显微镜","多义性","成交","确认")
# Small, visible, full-page raster previews. A page's image presence is not its semantic interpretation.
preview_pages={280,292,294,304,310,349,352,355}
with fitz.open(pdfpath) as pdf:
 assert len(pdf)==v["pdf_page_count"]
 for n in range(61,66):
  k=next(i for i,c in enumerate(v["lessons"]) if c["lesson"]==n)
  a=v["lessons"][k]["start_pdf_page"];b=v["lessons"][k+1]["start_pdf_page"]-1
  info={"lesson":n,"title":v["lessons"][k]["title"],"volume":3,"path":v["path"],"sha256":v["sha256"],
        "start":a,"end":b,"original_date":None,"first_divider":None,"pages":[],"author_terms":[]}
  budget=0
  for p in range(a,b+1):
   page=pdf[p-1];raw=page.get_text("text",sort=True);lines=raw.splitlines()
   mark=next(((j+1,l.strip()[:90]) for j,l in enumerate(lines) if sep.search(l.strip())),None)
   if mark and not info["first_divider"]:info["first_divider"]={"pdf_page":p,"line":mark[0],"label":mark[1]}
   if p==a:
    match=re.search(r"(20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?)",raw)
    info["original_date"]=match.group(1) if match else None
   imgs=page.get_image_info(xrefs=True)
   info["pages"].append({"pdf_page":p,"native_chars":len(raw.strip()),"images":len(imgs),"editorial_cue":bool(editor.search(raw)),"divider":bool(mark)})
   if not info["first_divider"] or p==info["first_divider"]["pdf_page"]:
    author=raw if not mark else "\n".join(lines[:mark[0]-1])
    words=[x for x in topics if x in author]
    if words:info["author_terms"].append({"pdf_page":p,"terms":words})
    if author.strip() and budget<10800 and p<a+13:
     excerpt=" ".join(author.split())[:min(2200,10900-budget)]
     print("AUTHOR_CUE "+json.dumps({"lesson":n,"pdf_page":p,"text":excerpt},ensure_ascii=False),flush=True)
     budget+=len(excerpt)
   if p in preview_pages:
    pix=page.get_pixmap(matrix=fitz.Matrix(.7,.7),alpha=False,colorspace=fitz.csGRAY)
    im=Image.frombytes("L",(pix.width,pix.height),pix.samples);im.thumbnail((640,820))
    buf=BytesIO();im.save(buf,format="JPEG",quality=40,optimize=True)
    print("FIGURE_JPEG "+json.dumps({"lesson":n,"page":p,"width":im.width,"height":im.height,"encoded":base64.b64encode(buf.getvalue()).decode()},ensure_ascii=False),flush=True)
  info["page_count"]=len(info["pages"]);info["total_native_chars"]=sum(z["native_chars"] for z in info["pages"])
  info["image_pages"]=[z["pdf_page"] for z in info["pages"] if z["images"]]
  info["sparse_pages"]=[z["pdf_page"] for z in info["pages"] if z["native_chars"]<100]
  print("SOURCE_RECORD "+json.dumps(info,ensure_ascii=False),flush=True)
print("ORIGINAL_PDF_61_65_SHA_VERIFIED",flush=True)
