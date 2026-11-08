#!/usr/bin/env python3
"""Read-only SHA-pinned original volumes 4/5 lessons 86–90; bounded source cues and selected 0.7x previews."""
import hashlib,json,re,base64
from pathlib import Path
from io import BytesIO
import fitz
from PIL import Image
root=Path(__file__).resolve().parents[1]
idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
date=re.compile(r"20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?")
star=re.compile(r"^\*{6,}$")
editor=re.compile(r"娇注|娇加注|娇[:：]|编者|更正|勘误|补充说明|原图错误|修订|修正")
terms=("图例","更正","分型","走势类型","线段","笔","缺口","中枢","底分型","顶分型","包含","买卖点","第一种情况","第二种情况","心理","资金","交易","背驰","当下","确认","预测","级别","震荡","中阴","生长","风险","变化","力度")
previews={86:[347,352,361],87:[370,376],88:[386,392,403],89:[5,14,25],90:[31,44,57]}
records=[]
for v in idx["volumes"][3:5]:
 path=root/v["path"]
 assert hashlib.sha256(path.read_bytes()).hexdigest()==v["sha256"],"pdf original SHA changed"
 with fitz.open(path) as pdf:
  assert len(pdf)==v["pdf_page_count"]
  for n in range(86,91):
   found=[i for i,x in enumerate(v["lessons"]) if x["lesson"]==n]
   if not found:continue
   k=found[0];start=v["lessons"][k]["start_pdf_page"]
   end=(v["lessons"][k+1]["start_pdf_page"]-1 if k+1<len(v["lessons"]) else v["pdf_page_count"])
   row={"lesson":n,"title":v["lessons"][k]["title"],"volume":v["volume"],
        "source_path":v["path"],"source_sha256":v["sha256"],"start_page":start,"last_page":end,
        "header_date":None,"first_starred_divider":None,"pages":[],"topical_pages":[],"extra_dates":[],"preview_pages":[]}
   budget=0
   for p in range(start,end+1):
    page=pdf[p-1];raw=page.get_text("text",sort=True);lines=raw.splitlines()
    mark=next((i+1 for i,l in enumerate(lines) if star.match(l.strip())),None)
    if mark and row["first_starred_divider"] is None:row["first_starred_divider"]={"pdf_page":p,"line":mark}
    if p==start:
     d=date.search(raw);row["header_date"]=d.group(0) if d else None
    dates=date.findall(raw)
    if dates and p>start:row["extra_dates"].append({"page":p,"date_candidates":dates[:3]})
    images=page.get_image_info(xrefs=True)
    row["pages"].append({"pdf_page":p,"chars":len(raw.strip()),"image_count":len(images),
        "editor_cue":bool(editor.search(raw)),"star_divider":mark is not None})
    if row["first_starred_divider"] is None or p==row["first_starred_divider"]["pdf_page"]:
     author=raw if not mark else "\n".join(lines[:mark-1])
     terms_found=[term for term in terms if term in author]
     if terms_found:row["topical_pages"].append({"page":p,"terms":terms_found})
     if budget<13000 and p<start+12 and len(author.strip())>50:
      short=" ".join(author.split())[:min(2000,13200-budget)];budget+=len(short)
      print("AUTHOR_CUE "+json.dumps({"lesson":n,"volume":v["volume"],"page":p,"text":short},ensure_ascii=False),flush=True)
    if p in previews[n]:
     pix=page.get_pixmap(matrix=fitz.Matrix(.72,.72),alpha=False,colorspace=fitz.csGRAY)
     im=Image.frombytes("L",(pix.width,pix.height),pix.samples);im.thumbnail((670,900))
     bf=BytesIO();im.save(bf,format="JPEG",quality=42,optimize=True)
     print("PDF_PREVIEW "+json.dumps({"lesson":n,"volume":v["volume"],"page":p,"image_base64":base64.b64encode(bf.getvalue()).decode()},ensure_ascii=False),flush=True)
     row["preview_pages"].append(p)
   row["page_count"]=end-start+1
   row["native_chars"]=sum(x["chars"] for x in row["pages"])
   row["image_pages"]=[x["pdf_page"] for x in row["pages"] if x["image_count"]]
   row["sparse_pages"]=[x["pdf_page"] for x in row["pages"] if x["chars"]<100]
   print("SOURCE_RECORD "+json.dumps(row,ensure_ascii=False),flush=True)
   records.append(row)
assert len(records)==5 and [x["lesson"] for x in records]==[86,87,88,89,90]
print("ORIGINAL_PDFS_86_90_SHA_VERIFIED",flush=True)
