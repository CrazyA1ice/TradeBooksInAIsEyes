#!/usr/bin/env python3
"""Read original PDF author-text cues, exact physical page bounds, images; lessons 41–45."""
import hashlib,json,re
from pathlib import Path
import fitz
root=Path(__file__).resolve().parents[1]
index=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
separators=re.compile(r"^\*{6,}$|解盘及互动问答|互动问答[：:]|解盘及答疑|读者问答|网友互动")
annot=re.compile(r"娇注|娇[：:]|编者注|网友|缠师[：:]")
topics=("背驰","盘整背驰","小级别","大级别","转折","持股","持币","节奏","风险","级别","中枢","第三类","走势","买卖点","操作","MACD","分解","一买","二买","卖点","仓位")
for volume in index["volumes"][1:3]:
 path=root/volume["path"]
 assert hashlib.sha256(path.read_bytes()).hexdigest()==volume["sha256"],"Original PDF SHA mismatch"
 with fitz.open(path) as pdf:
  assert len(pdf)==volume["pdf_page_count"]
  lessons=volume["lessons"]
  for i,c in enumerate(lessons):
   n=c["lesson"]
   if n<41 or n>45:continue
   start=c["start_pdf_page"]
   end=lessons[i+1]["start_pdf_page"]-1 if i+1<len(lessons) else len(pdf)
   rec={"lesson":n,"title":c["title"],"volume":volume["volume"],"pdf_path":volume["path"],
        "sha256":volume["sha256"],"start_page":start,"end_page":end,"original_date":None,
        "first_appendix":None,"pages":[],"topic_pages":[]}
   used=0
   for page_no in range(start,end+1):
    page=pdf[page_no-1];raw=page.get_text("text",sort=True);lines=raw.splitlines()
    mark=next(((j+1,line.strip()[:120]) for j,line in enumerate(lines) if separators.search(line.strip())),None)
    if mark and rec["first_appendix"] is None:rec["first_appendix"]={"pdf_page":page_no,"line":mark[0],"marker":mark[1]}
    if page_no==start:
     dt=re.search(r"(20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?)",raw)
     if dt:rec["original_date"]=dt.group(1)
    images=page.get_image_info(xrefs=True)
    rec["pages"].append({"pdf_page":page_no,"native_chars":len(raw.strip()),"images":len(images),
        "has_appendix_separator":bool(mark),"has_editor_or_reply_cue":bool(annot.search(raw))})
    if rec["first_appendix"] is None or rec["first_appendix"]["pdf_page"]==page_no:
     authored=raw if mark is None else "\n".join(lines[:mark[0]-1])
     tags=[x for x in topics if x in authored]
     if tags:rec["topic_pages"].append({"page":page_no,"terms":tags})
     if authored.strip() and used<9000 and page_no<start+13:
      excerpt=" ".join(authored.split())[:min(2400,9200-used)]
      print("AUTHOR_CUE "+json.dumps({"lesson":n,"volume":volume["volume"],"page":page_no,"text":excerpt},ensure_ascii=False),flush=True)
      used+=len(excerpt)
   rec["page_count"]=len(rec["pages"])
   rec["total_native_chars"]=sum(p["native_chars"] for p in rec["pages"])
   rec["image_pages"]=[p["pdf_page"] for p in rec["pages"] if p["images"]]
   rec["low_text_pages"]=[p["pdf_page"] for p in rec["pages"] if p["native_chars"]<100]
   print("SOURCE_RECORD "+json.dumps(rec,ensure_ascii=False),flush=True)
print("COMPLETE_ORIGINAL_SHA_LOCKED_TWO_VOLUMES_41_45",flush=True)
