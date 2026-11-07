#!/usr/bin/env python3
"""SHA-pinned read-only cross-volume survey of lessons 66-70; bounded excerpts and thumbnails."""
import base64,hashlib,json,re
from io import BytesIO
from pathlib import Path
import fitz
from PIL import Image
root=Path(__file__).resolve().parents[1]
idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
breaks=re.compile(r"^\*{6,}$|解盘及互动问答|互动问答[：:]|解盘及答疑|读者问答")
ed=re.compile(r"娇注|娇[：:]|编者注|新笔定义|附注|后来|特征序列")
terms=("主力","资金","食物链","线段","分型","特征序列","缺口","包含","走势","中枢","递归","背驰","预测","精确","月线","上海","买卖点","扩展","破坏","包含关系","段","高点","低点")
previews={3:{376,390,397,403},4:{5,11,29,34,55,60}}
for v in idx["volumes"][2:4]:
 path=root/v["path"]
 assert hashlib.sha256(path.read_bytes()).hexdigest()==v["sha256"],"source fingerprint mismatch"
 with fitz.open(path) as pdf:
  assert len(pdf)==v["pdf_page_count"]
  seq=v["lessons"]
  for n in range(66,71):
   positions=[k for k,x in enumerate(seq) if x["lesson"]==n]
   if not positions:continue
   k=positions[0];a=seq[k]["start_pdf_page"];b=seq[k+1]["start_pdf_page"]-1 if k+1<len(seq) else len(pdf)
   record={"lesson":n,"title":seq[k]["title"],"volume":v["volume"],"pdf_path":v["path"],"sha256":v["sha256"],
           "first_page":a,"last_page":b,"original_date":None,"first_divider":None,"pages":[],"author_terms":[]}
   budget=0
   for p in range(a,b+1):
    page=pdf[p-1];raw=page.get_text("text",sort=True);lines=raw.splitlines()
    marker=next(((i+1,l.strip()[:80]) for i,l in enumerate(lines) if breaks.search(l.strip())),None)
    if marker and record["first_divider"] is None:record["first_divider"]={"pdf_page":p,"line":marker[0],"label":marker[1]}
    if p==a:
     date=re.search(r"(20\d\d[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?)",raw)
     record["original_date"]=date.group(1) if date else None
    images=page.get_image_info(xrefs=True)
    record["pages"].append({"pdf_page":p,"native_chars":len(raw.strip()),"embedded_images":len(images),
                            "editorial_terms":bool(ed.search(raw)),"separator":bool(marker)})
    if record["first_divider"] is None or p==record["first_divider"]["pdf_page"]:
     author=raw if marker is None else "\n".join(lines[:marker[0]-1])
     words=[x for x in terms if x in author]
     if words:record["author_terms"].append({"pdf_page":p,"terms":words})
     if author.strip() and budget<8600 and p<a+14:
      cue=" ".join(author.split())[:min(1500,8800-budget)]
      budget+=len(cue)
      print("AUTHOR_CUE "+json.dumps({"lesson":n,"page":p,"text":cue},ensure_ascii=False),flush=True)
    if p in previews[v["volume"]]:
     pix=page.get_pixmap(matrix=fitz.Matrix(.66,.66),alpha=False,colorspace=fitz.csGRAY)
     im=Image.frombytes("L",(pix.width,pix.height),pix.samples);im.thumbnail((610,820))
     buf=BytesIO();im.save(buf,format="JPEG",quality=38,optimize=True)
     print("FIGURE_JPEG "+json.dumps({"lesson":n,"volume":v["volume"],"page":p,"width":im.width,
                                      "height":im.height,"encoded":base64.b64encode(buf.getvalue()).decode()},ensure_ascii=False),flush=True)
   record["page_count"]=len(record["pages"])
   record["image_pages"]=[x["pdf_page"] for x in record["pages"] if x["embedded_images"]]
   record["sparse_pages"]=[x["pdf_page"] for x in record["pages"] if x["native_chars"]<100]
   record["total_native_chars"]=sum(x["native_chars"] for x in record["pages"])
   print("LESSON_META "+json.dumps(record,ensure_ascii=False),flush=True)
print("SHA_VERIFIED_CROSS_VOLUME_66_70_COMPLETE",flush=True)
