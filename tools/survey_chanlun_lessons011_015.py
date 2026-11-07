#!/usr/bin/env python3
"""Read-only SHA-locked lesson-11..15 source survey. Logs only bounded snippets."""
import hashlib,json,re
from pathlib import Path
import fitz
root=Path(__file__).resolve().parents[1]
idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
vol=idx["volumes"][0]; f=root/vol["path"]
assert hashlib.sha256(f.read_bytes()).hexdigest()==vol["sha256"]
div=re.compile(r"解盘及互动问答|互动问答：|缠师解盘及和网友|相关阅读[：:]")
note=re.compile(r"娇注|娇[：:]|编者注|网友|缠师[：:]")
with fitz.open(f) as doc:
    assert len(doc)==vol["pdf_page_count"]
    for n in range(11,16):
        s=vol["lessons"][n-1]["start_pdf_page"]
        end=vol["lessons"][n]["start_pdf_page"]
        previewchars=0
        summary={"lesson":n,"title":vol["lessons"][n-1]["title"],"start":s,"end":end-1,
                 "pdf_sha256":vol["sha256"],"pages":[],"first_divider":None,"source_date":None}
        print("LESSON_BEGIN "+json.dumps({k:summary[k] for k in ("lesson","title","start","end")},ensure_ascii=False),flush=True)
        for pn in range(s,end):
            page=doc[pn-1]; raw=page.get_text("text",sort=True)
            lines=raw.splitlines()
            imgs=page.get_image_info(xrefs=True)
            marked=[(" ".join(line.split())[:120],i) for i,line in enumerate(lines) if div.search(line)]
            if summary["first_divider"] is None and marked:summary["first_divider"]={"pdf_page":pn,"text":marked[0][0],"line":marked[0][1]+1}
            if summary["source_date"] is None and pn==s:
                dates=re.findall(r"20\d{2}[-/]\d\d[-/]\d\d\s+\d\d:\d\d(?::\d\d)?",raw)
                if dates:summary["source_date"]=dates[0]
            summary["pages"].append({"page":pn,"chars":len(raw.strip()),"images":len(imgs),
                "image_dimensions":[{"w":x["width"],"h":x["height"]} for x in imgs[:3]],
                "has_dialogue":bool(note.search(raw)),"has_divider":bool(marked)})
            # Three carefully bounded extracts from actual authored part, rather than 87 page texts.
            if summary["first_divider"] is None and previewchars<4500:
                content=" ".join(raw.split())
                if pn==s:fragment=content[:2500]
                else:fragment=content[90:1100] if len(content)>120 else ""
                if fragment:
                    print("SOURCE_EXCERPT "+json.dumps({"lesson":n,"page":pn,"text":fragment},ensure_ascii=False),flush=True)
                    previewchars+=len(fragment)
        p=summary["pages"]
        summary["total_native_characters"]=sum(x["chars"] for x in p)
        summary["image_pages"]=[x["page"] for x in p if x["images"]]
        summary["low_text_pages"]=[x["page"] for x in p if x["chars"]<100]
        print("LESSON_AUDIT "+json.dumps(summary,ensure_ascii=False),flush=True)
print("SOURCE_SURVEY_COMPLETE lessons=5",flush=True)
