#!/usr/bin/env python3
"""Read original third-volume PDF with SHA lock, source strata and bounded visual thumbnails."""
import base64,hashlib,json,re
from pathlib import Path
import fitz
root=Path(__file__).resolve().parents[1]
idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
v=idx["volumes"][2]
path=root/v["path"]
assert hashlib.sha256(path.read_bytes()).hexdigest()==v["sha256"],"source changed"
divider=re.compile(r"^\*{6,}$|解盘及互动问答|互动问答[：:]|解盘及答疑|读者问答")
editor=re.compile(r"娇注|娇加注|编者注|思考贴|缠师[：:]")
terms=("印花税","530","5月30日","分笔","线段","中枢","级别","第一类","第二类","第三类","背驰","扩展","回抽","买点","卖点","当下","风险","图解","盘整")
image_targets={207,219,231,252,268}
with fitz.open(path) as pdf:
 for n in range(56,61):
  k=next(i for i,x in enumerate(v["lessons"]) if x["lesson"]==n)
  start=v["lessons"][k]["start_pdf_page"]
  end=v["lessons"][k+1]["start_pdf_page"]-1
  rec={"lesson":n,"volume":3,"title":v["lessons"][k]["title"],"original_pdf_path":v["path"],"sha256":v["sha256"],
       "start":start,"end":end,"original_date":None,"first_divider":None,"pages":[],"original_text_pages":[]}
  budget=0
  for p in range(start,end+1):
   page=pdf[p-1];raw=page.get_text("text",sort=True);lines=raw.splitlines()
   split=next(((j+1,line.strip()[:100]) for j,line in enumerate(lines) if divider.search(line.strip())),None)
   if split and rec["first_divider"] is None:rec["first_divider"]={"pdf_page":p,"line":split[0],"marker":split[1]}
   if p==start:
    m=re.search(r"(20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?)",raw)
    rec["original_date"]=m.group(1) if m else None
   imgs=page.get_image_info(xrefs=True)
   rec["pages"].append({"pdf_page":p,"native_chars":len(raw.strip()),"image_count":len(imgs),
                        "editor_cues":bool(editor.search(raw)),"divider":bool(split)})
   if rec["first_divider"] is None or p==rec["first_divider"]["pdf_page"]:
    authored=raw if not split else "\n".join(lines[:split[0]-1])
    present=[t for t in terms if t in authored]
    if present:rec["original_text_pages"].append({"pdf_page":p,"terms":present})
    if authored.strip() and budget<5600 and p<start+8:
     excerpt=" ".join(authored.split())[:min(1600,5700-budget)]
     print("AUTHOR_CUE "+json.dumps({"lesson":n,"pdf_page":p,"text":excerpt},ensure_ascii=False),flush=True)
     budget+=len(excerpt)
   if p in image_targets:
    pix=page.get_pixmap(matrix=fitz.Matrix(.78,.78),alpha=False,colorspace=fitz.csGRAY)
    from PIL import Image
    from io import BytesIO
    im=Image.frombytes("L",(pix.width,pix.height),pix.samples)
    im.thumbnail((720,900))
    buf=BytesIO();im.save(buf,format="JPEG",quality=43,optimize=True)
    print("FIGURE_JPEG "+json.dumps({"pdf_page":p,"lesson":n,"width":im.width,"height":im.height,"encoded":base64.b64encode(buf.getvalue()).decode()},ensure_ascii=False),flush=True)
  rec["page_count"]=len(rec["pages"]);rec["native_chars"]=sum(p["native_chars"] for p in rec["pages"])
  rec["image_pages"]=[p["pdf_page"] for p in rec["pages"] if p["image_count"]]
  rec["sparse_pages"]=[p["pdf_page"] for p in rec["pages"] if p["native_chars"]<100]
  print("LESSON_META "+json.dumps(rec,ensure_ascii=False),flush=True)
print("SOURCE_AUDIT_COMPLETED",flush=True)
