#!/usr/bin/env python3
"""Read original immutable Volume5 PDF, lessons 101-105, source-bounded clues & previews."""
import base64,hashlib,json,re
from io import BytesIO
from pathlib import Path
import fitz
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text("utf-8"))
vol=index["volumes"][4]
p=ROOT/vol["path"]
assert hashlib.sha256(p.read_bytes()).hexdigest()==vol["sha256"]
date=re.compile(r"20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?")
sep=re.compile(r"^\*{5,}$")
editor=re.compile(r"娇注|娇加|娇[:：]|编者|勘误|后记|读后感|更正|修订")
terms=("疑问","答疑","中枢","线段","笔","分型","背驰","必完美","几何","能量","动力","面积","机械","走势","扩展","盘整","趋势","操作","分类","确认","当下","时间","确定","买卖点","级别","包含","均线","MACD","风险","力量")
preview={101:[234,238],102:[242,248,259,266],103:[270,280,288],104:[291,305,319],105:[326,344,368]}
with fitz.open(p) as pdf:
 assert len(pdf)==vol["pdf_page_count"]
 records=[]
 for lesson in range(101,106):
  k=next(i for i,l in enumerate(vol["lessons"]) if l["lesson"]==lesson)
  start=vol["lessons"][k]["start_pdf_page"];end=vol["lessons"][k+1]["start_pdf_page"]-1
  row={"lesson":lesson,"title":vol["lessons"][k]["title"],"volume":5,"start":start,"end":end,
       "path":vol["path"],"sha256":vol["sha256"],"original_date":None,"first_starred_divider":None,
       "pages":[],"later_dates":[],"rendered_previews":[],"early_topic_pages":[]}
  budget=0
  for page in range(start,end+1):
   obj=pdf[page-1];raw=obj.get_text("text",sort=True);lines=raw.splitlines()
   hit=next((i+1 for i,line in enumerate(lines) if sep.match(line.strip())),None)
   if hit and row["first_starred_divider"] is None:row["first_starred_divider"]={"page":page,"line":hit}
   if page==start:
    match=date.search(raw);row["original_date"]=match.group(0) if match else None
   dates=date.findall(raw)
   if dates and page>start:row["later_dates"].append({"page":page,"candidate_dates":dates[:4]})
   image_count=len(obj.get_image_info(xrefs=True))
   row["pages"].append({"page":page,"text_chars":len(raw.strip()),"image_count":image_count,
                        "editor_cue":bool(editor.search(raw)),"star_separator":bool(hit)})
   if page<start+12:
    early=raw if not hit else "\n".join(lines[:hit-1])
    matches=[t for t in terms if t in early]
    if matches:row["early_topic_pages"].append({"page":page,"terms":matches})
    if budget<13500 and len(early.strip())>90:
     excerpt=" ".join(early.split())[:min(1600,14000-budget)]
     budget+=len(excerpt)
     print("AUTHOR_CUE "+json.dumps({"lesson":lesson,"page":page,"text":excerpt},ensure_ascii=False),flush=True)
   if page in preview[lesson]:
    pix=obj.get_pixmap(matrix=fitz.Matrix(.70,.70),colorspace=fitz.csGRAY,alpha=False)
    img=Image.frombytes("L",(pix.width,pix.height),pix.samples)
    img.thumbnail((650,900))
    data=BytesIO();img.save(data,format="JPEG",quality=43,optimize=True)
    print("PDF_PREVIEW "+json.dumps({"lesson":lesson,"page":page,"base64":base64.b64encode(data.getvalue()).decode()},ensure_ascii=False),flush=True)
    row["rendered_previews"].append(page)
  row["page_count"]=end-start+1
  row["native_chars"]=sum(x["text_chars"] for x in row["pages"])
  row["image_pages"]=[x["page"] for x in row["pages"] if x["image_count"]]
  row["sparse_pages"]=[x["page"] for x in row["pages"] if x["text_chars"]<100]
  print("SOURCE_RECORD "+json.dumps(row,ensure_ascii=False),flush=True)
  records.append(row)
 assert [r["lesson"] for r in records]==[101,102,103,104,105]
 print("PASS_SOURCE101_105_ORIGINAL_PDF_SHA",flush=True)
