#!/usr/bin/env python3
"""Ensure first-pass readings of lessons 16-20 track source content and status."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TYPES={"SOURCE","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
SEVEN=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
def audit(index,source,claims,reports,synthesis,digest):
    v=index["volumes"][0]
    assert digest==v["sha256"]==source["sha256"]
    assert source["source"]==v["path"]
    assert len(source["lessons"])==len(claims)==len(reports)==5
    assert sum(len(x["pages"]) for x in source["lessons"])==84
    identifiers=set()
    for lesson in range(16,21):
        i=lesson-16; info=source["lessons"][i];ev=claims[i];md=reports[i]
        start=v["lessons"][lesson-1]["start_pdf_page"]
        end=v["lessons"][lesson]["start_pdf_page"]
        pages=list(range(start,end))
        assert info["lesson"]==ev["source"]["lesson_number"]==lesson
        assert info["start"]==start and info["end"]==end-1
        assert [p["pdf_page"] for p in info["pages"]]==pages
        assert sum(p["native_text_chars"] for p in info["pages"])==info["total_native_text_chars"]
        assert [p["pdf_page"] for p in info["pages"] if p["image_count"]>0]==info["image_pages"]
        assert ev["source"]["path"]==source["source"]
        assert ev["source"]["sha256"]==digest
        assert ev["source"]["pdf_pages"]==pages
        assert ev["source"]["first_dialogue_boundary_candidate"]==info["first_dialogue"]["page"]
        assert ev["audit"]["image_pages"]==info["image_pages"]
        assert ev["audit"]["native_text_characters"]==info["total_native_text_chars"]
        assert digest in md and all(x in md for x in SEVEN) and "图像" in md
        assert ev["empirical_status"]=="not_run"
        assert len(ev["claims"])>=5
        for cl in ev["claims"]:
            assert cl["kind"] in TYPES
            assert cl["pdf_pages"] and set(cl["pdf_pages"]).issubset(set(pages))
            assert cl["id"] not in identifiers
            identifiers.add(cl["id"])
            if cl["kind"]=="HYPOTHESIS":assert cl.get("status")=="not_tested"
        if lesson==17:
            assert "三个" in md and "完成" in md and "中枢" in md
        if lesson==20:
            assert "必然" in md and "成本" in md and "第三类" in md
    assert "第三类买点" in synthesis
    for i in range(16,21):assert f"lesson_{i:03d}.md" in synthesis
    assert "不是" in synthesis and "确认" in synthesis
    return {"lessons":5,"pages":84,"claims":len(identifiers)}
def main():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    source=json.loads((ROOT/"catalog/chanlun_lessons016_020_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{i:03d}.json").read_text(encoding="utf-8")) for i in range(16,21)]
    md=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{i:03d}.md").read_text(encoding="utf-8") for i in range(16,21)]
    overview=(ROOT/"analyses/books/chanlun/volumes/LESSONS_016_020_SYNTHESIS.md").read_text(encoding="utf-8")
    digest=hashlib.sha256((ROOT/idx["volumes"][0]["path"]).read_bytes()).hexdigest()
    print("PASS lessons 16–20 source-grounding "+json.dumps(audit(idx,source,ev,md,overview,digest)))
if __name__=="__main__":main()
