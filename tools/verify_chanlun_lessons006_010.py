#!/usr/bin/env python3
"""Traceability audit of lessons 6..10 source screening and first-pass analyses.
It tests citations and explicit limitations; it does NOT validate unreviewed images.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VALID={"SOURCE","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
LAYERS=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
def audit(index,layer,items,reports,overview,source_digest):
    v=index["volumes"][0]
    assert v["sha256"]==source_digest,"PDF version mismatch"
    assert len(layer["lessons"])==len(items)==len(reports)==5
    claims=set()
    for lesson in range(6,11):
        k=lesson-6
        l=layer["lessons"][k]
        e=items[k]
        text=reports[k]
        begin=index["volumes"][0]["lessons"][lesson-1]
        after=index["volumes"][0]["lessons"][lesson]
        expected_pages=list(range(begin["start_pdf_page"],after["start_pdf_page"]))
        assert l["lesson"]==e["source"]["lesson_number"]==lesson
        assert l["start_pdf_page"]==expected_pages[0]
        assert l["end_pdf_page_inclusive"]==expected_pages[-1]
        assert len(l["pages"])==len(expected_pages)
        assert [x["pdf_page"] for x in l["pages"]]==expected_pages
        assert sum(x["native_text_characters"] for x in l["pages"])==l["total_native_extracted_characters"]
        assert e["source"]["sha256"]==source_digest
        assert e["source"]["pdf_pages"]==expected_pages
        assert e["source"]["appendix_boundary_candidate_page"]==l["author_to_appendix_boundary_candidate_pdf_page"]
        assert e["source_quality"]["image_pages"]==l["image_pages"]
        assert e["source_quality"]["low_text_pages"]==l["low_text_pages"]
        assert all(tag in text for tag in LAYERS)
        assert source_digest in text
        assert "第一轮" in text and "未" in text
        assert len(text)>=1500
        assert len(e["claims"])>=6
        assert e["empirical_status"]=="not_run"
        for cl in e["claims"]:
            assert cl["kind"] in VALID
            assert cl["pdf_pages"] and set(cl["pdf_pages"]).issubset(expected_pages)
            assert cl["id"] not in claims,"Repeated claim identifier"
            claims.add(cl["id"])
            if cl["kind"]=="HYPOTHESIS": assert cl.get("test_status")=="not_tested"
    assert any(30 in l["image_pages"] for l in layer["lessons"] if l["lesson"]==9)
    assert all(x in overview for x in ["第 9","3.6%","前十课"])
    assert "没有执行真实市场回测" in reports[3] or "没有执行真实市场实验" in reports[3]
    return {"lessons":5,"pages":sum(l["page_count"] for l in layer["lessons"]),"claims":len(claims)}
def main():
    index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    layer=json.loads((ROOT/"catalog/chanlun_lessons006_010_layers.json").read_text(encoding="utf-8"))
    items=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{i:03d}.json").read_text(encoding="utf-8")) for i in range(6,11)]
    reports=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{i:03d}.md").read_text(encoding="utf-8") for i in range(6,11)]
    overview=(ROOT/"analyses/books/chanlun/volumes/LESSONS_001_010_SYNTHESIS.md").read_text(encoding="utf-8")
    digest=hashlib.sha256((ROOT/index["volumes"][0]["path"]).read_bytes()).hexdigest()
    print("PASS audited source lessons 6-10: "+json.dumps(audit(index,layer,items,reports,overview,digest)))
if __name__=="__main__":main()
