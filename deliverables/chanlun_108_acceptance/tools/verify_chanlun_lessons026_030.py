#!/usr/bin/env python3
"""Audit lesson 26–30 analyses against immutable original PDF and source survey."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
KINDS={"SOURCE","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
LAYERS=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
def audit(index,inventory,evidence,reports,overview,digest):
    volume=index["volumes"][1]
    assert volume["path"]==inventory["original_path"]
    assert volume["sha256"]==inventory["source_sha256"]==digest
    assert len(inventory["lessons"])==len(evidence)==len(reports)==5
    assert sum(len(x["pages"]) for x in inventory["lessons"])==123
    seen=set()
    for n in range(26,31):
        k=n-26
        src=inventory["lessons"][k];e=evidence[k];md=reports[k]
        start=volume["lessons"][next(i for i,x in enumerate(volume["lessons"]) if x["lesson"]==n)]["start_pdf_page"]
        finish=volume["lessons"][next(i for i,x in enumerate(volume["lessons"]) if x["lesson"]==n+1)]["start_pdf_page"]
        pages=list(range(start,finish))
        assert src["lesson"]==e["source"]["lesson_number"]==n
        assert src["start"]==start and src["end"]==finish-1
        assert [x["pdf_page"] for x in src["pages"]]==pages
        assert e["source"]["pdf_pages"]==pages
        assert e["source"]["volume"]==2
        assert e["source"]["path"]==volume["path"]
        assert e["source"]["sha256"]==digest
        assert e["source"]["appendix_boundary_candidate"]==src["divider"]["page"]
        assert e["quality"]["native_text_chars"]==sum(x["native_text_chars"] for x in src["pages"])
        assert e["quality"]["image_pages"]==src["image_pages"]
        assert e["quality"]["low_text_pages"]==src["low_text_pages"]
        assert e["empirical_status"]=="not_run"
        assert digest in md and all(h in md for h in LAYERS) and "未" in md and "图像" in md
        assert len(e["claims"])>=6
        for cl in e["claims"]:
            assert cl["kind"] in KINDS
            assert cl["pdf_pages"] and set(cl["pdf_pages"]).issubset(pages)
            assert cl["volume"]==2 and cl["id"] not in seen
            seen.add(cl["id"])
            if cl["kind"]=="HYPOTHESIS":assert cl.get("test_status")=="not_tested"
        if n==26:assert "停止交易" in md and "期限" in md
        if n==27:assert "区间" in md and "在线" in md
        if n==28:assert "编者" in md and "基金" in md
        if n==29:assert "三种" in md and "完成" in md
        if n==30:assert "公理" in md and "前提" in md
    assert "123 页" in overview and "交易" in overview and "区间套" in overview
    assert all(f"lesson_{n:03d}.md" in overview for n in range(26,31))
    return {"lessons":5,"pages":123,"claims":len(seen),"volume":2}
def main():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    inv=json.loads((ROOT/"catalog/chanlun_lessons026_030_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(26,31)]
    reports=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(26,31)]
    overview=(ROOT/"analyses/books/chanlun/volumes/LESSONS_026_030_SYNTHESIS.md").read_text(encoding="utf-8")
    digest=hashlib.sha256((ROOT/idx["volumes"][1]["path"]).read_bytes()).hexdigest()
    print("PASS lesson 26–30 source and claims audit "+json.dumps(audit(idx,inv,ev,reports,overview,digest)))
if __name__=="__main__":main()
