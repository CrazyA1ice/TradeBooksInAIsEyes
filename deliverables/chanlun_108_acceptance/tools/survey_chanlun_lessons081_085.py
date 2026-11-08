#!/usr/bin/env python3
"""SHA-pinned original PDF source audit for lessons 81–85: page metadata, bounded cues, selected page previews."""
import hashlib, json, re, base64
from pathlib import Path
from io import BytesIO
import fitz
from PIL import Image
root=Path(__file__).resolve().parents[1]
idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
v=idx["volumes"][3];path=root/v["path"]
assert hashlib.sha256(path.read_bytes()).hexdigest()==v["sha256"],"original source fingerprint changed"
date=re.compile(r"20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?")
star=re.compile(r"^\*{6,}$")
editor=re.compile(r"娇注|娇加注|娇[:：]|编者|更正|勘误|补充说明|原图错误|修订|修正")
terms=("图例","更正","分型","走势类型","线段","笔","缺口","中枢","底分型","顶分型","包含","第一种情况","第二种情况","心理","资金","交易","背驰","当下","确认","预测","规则","哲学","未完成","K线")
previews={81:[234,237,246,257],82:[269,277],83:[290,294],84:[303,314,327],85:[340,344]}
with fitz.open(path) as pdf:
 assert len(pdf)==v["pdf_page_count"]
 for n in range(81,86):
  k=next(i for i,x in enumerate(v["lessons"]) if x["lesson"]==n)
  begin=v["lessons"][k]["start_pdf_page"]
  stop=v["lessons"][k+1]["start_pdf_page"]
  rec={"lesson":n,"title":v["lessons"][k]["title"],"volume":4,"source_path":v["path"],
       "source_sha256":v["sha256"],"start":begin,"end":stop-1,"header_date":None,
       "first_starred_divider":None,"page_info":[],"page_terms":[],"extra_dated_material":[],"rendered_previews":[]}
  budget=0
  for p in range(begin,stop):
   page=pdf[p-1];raw=page.get_text("text",sort=True);lines=raw.splitlines()
   mark=next((j+1 for j,l in enumerate(lines) if star.match(l.strip())),None)
   if mark is not None and rec["first_starred_divider"] is None:
    rec["first_starred_divider"]={"pdf_page":p,"line":mark}
   if p==begin:
    dates=date.search(raw);rec["header_date"]=dates.group(0) if dates else None
   d=date.findall(raw)
   if d and p>begin:rec["extra_dated_material"].append({"pdf_page":p,"date_candidates":d[:4]})
   images=page.get_image_info(xrefs=True)
   rec["page_info"].append({"pdf_page":p,"native_chars":len(raw.strip()),"embedded_image_count":len(images),
                             "has_editorial_cue":bool(editor.search(raw)),"star_divider":mark is not None})
   if rec["first_starred_divider"] is None or p==rec["first_starred_divider"]["pdf_page"]:
    body=raw if mark is None else "\n".join(lines[:mark-1])
    tt=[t for t in terms if t in body]
    if tt:rec["page_terms"].append({"pdf_page":p,"terms":tt})
    if body.strip() and budget<12500 and p<begin+15:
     short=" ".join(body.split())[:min(1600,12700-budget)];budget+=len(short)
     print("AUTHOR_CUE "+json.dumps({"lesson":n,"page":p,"text":short},ensure_ascii=False),flush=True)
   if p in previews[n]:
    pix=page.get_pixmap(matrix=fitz.Matrix(.76,.76),alpha=False,colorspace=fitz.csGRAY)
    im=Image.frombytes("L",(pix.width,pix.height),pix.samples);im.thumbnail((710,950))
    bf=BytesIO();im.save(bf,format="JPEG",quality=42,optimize=True)
    print("PDF_PREVIEW "+json.dumps({"lesson":n,"page":p,"w":im.width,"h":im.height,"image_base64":base64.b64encode(bf.getvalue()).decode()},ensure_ascii=False),flush=True)
    rec["rendered_previews"].append(p)
  rec["page_count"]=stop-begin
  rec["total_native_chars"]=sum(x["native_chars"] for x in rec["page_info"])
  rec["image_pages"]=[x["pdf_page"] for x in rec["page_info"] if x["embedded_image_count"]]
  rec["sparse_pages"]=[x["pdf_page"] for x in rec["page_info"] if x["native_chars"]<100]
  print("LESSON_META "+json.dumps(rec,ensure_ascii=False),flush=True)
print("ORIGINAL_SHA_PDF_SURVEY_081_085_PASS",flush=True)
