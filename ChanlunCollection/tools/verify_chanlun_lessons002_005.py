#!/usr/bin/env python3
"""Deterministic source-index and evidence audit for Chanlun lessons 2–5."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LAYERS=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
KINDS={"SOURCE","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
def verify(index, evidences, reports, graph, synthesis, digest):
    volume=index["volumes"][0]
    assert volume["sha256"]==digest,"Source PDF was changed"
    assert len(evidences)==len(reports)==4
    ids=set()
    for n,(ev,text) in enumerate(zip(evidences,reports),2):
        lesson,nxt=volume["lessons"][n-1:n+1]
        src=ev["source"]
        assert lesson["lesson"]==src["lesson_number"]==n
        assert src["sha256"]==digest and src["path"]==volume["path"]
        pages=list(range(lesson["start_pdf_page"],nxt["start_pdf_page"]))
        assert src["pdf_pages"]==pages and src["next_lesson_pdf_start"]==nxt["start_pdf_page"]
        assert [x["pdf_page"] for x in ev["page_audit"]]==pages
        assert digest in text and src["title"] in text
        assert all(h in text for h in LAYERS)
        assert len(text)>1200
        for x in ev["page_audit"]:
            assert x["extracted_characters"]>=0
            if x["embedded_images"]:assert x["image_semantics_verified"] is False
        for cl in ev["claims"]:
            assert cl["kind"] in KINDS
            assert cl["id"] not in ids,"Duplicate claim identifier"
            assert cl["pages"] and set(cl["pages"]).issubset(set(pages))
            if cl["kind"]=="HYPOTHESIS":assert cl.get("test_status")=="not_tested"
            ids.add(cl["id"])
        assert ev["hypothesis"]["status"]=="not_tested"
        if n==4:
            assert {x["pdf_page"] for x in ev["page_audit"] if x["embedded_images"]}=={9,10}
            assert "2006-11-22" in text and "事后" in text and "图像" in text
        if n==5:assert "编者" in text
    nodes={x["id"] for x in graph["nodes"]}
    assert nodes=={f"L{i:03d}" for i in range(1,6)}
    for e in graph["edges"]:
        assert e["from"] in nodes and e["to"] in nodes and e["from"]!=e["to"]
        assert all(3<=p<=12 for p in e["pages"])
    assert "2006-11-22" in synthesis
    assert all(f"lesson_{n:03d}.md" in synthesis for n in range(1,6))
    return {"lessons":4,"claims":len(ids),"cross_links":len(graph["edges"])}
def main():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    evidences=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(2,6)]
    reports=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(2,6)]
    graph=json.loads((ROOT/"knowledge/relations/chanlun_lessons001_005.json").read_text(encoding="utf-8"))
    synth=(ROOT/"analyses/books/chanlun/volumes/LESSONS_001_005_SYNTHESIS.md").read_text(encoding="utf-8")
    digest=hashlib.sha256((ROOT/"ChineseBooks/缠论/缠论_卷1.pdf").read_bytes()).hexdigest()
    print("PASS source-grounded lesson 2–5 audit "+json.dumps(verify(idx,evidences,reports,graph,synth,digest)))
if __name__=="__main__":main()
