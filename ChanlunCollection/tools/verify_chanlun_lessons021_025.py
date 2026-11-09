#!/usr/bin/env python3
"""Pin two real PDF SHA fingerprints and audit lesson 21–25 source evidence."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KINDS={"SOURCE","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
LAYERS=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
def audit(index,scan,evidences,reports,synthesis,actual_hashes):
    volumes={v["volume"]:v for v in index["volumes"]}
    assert set(actual_hashes)>={1,2}
    for n in (1,2): assert volumes[n]["sha256"]==actual_hashes[n]
    assert len(scan["lessons"])==len(evidences)==len(reports)==5
    assert sum(len(r["pages"]) for r in scan["lessons"])==151
    IDs=set()
    for lesson,(src,ev,md) in enumerate(zip(scan["lessons"],evidences,reports),21):
        vol=1 if lesson<=23 else 2
        v=volumes[vol]
        ix=next(i for i,x in enumerate(v["lessons"]) if x["lesson"]==lesson)
        expected_start=v["lessons"][ix]["start_pdf_page"]
        end=v["lessons"][ix+1]["start_pdf_page"]-1 if ix+1<len(v["lessons"]) else v["pdf_page_count"]
        pages=list(range(expected_start,end+1))
        assert src["lesson"]==ev["source"]["lesson_number"]==lesson
        assert src["volume"]==ev["source"]["volume"]==vol
        assert src["source"]==ev["source"]["path"]==v["path"]
        assert src["sha256"]==ev["source"]["sha256"]==actual_hashes[vol]
        assert src["start"]==expected_start and src["end"]==end
        assert [x["pdf_page"] for x in src["pages"]]==pages
        assert ev["source"]["pdf_pages"]==pages
        assert ev["source"]["first_dialogue_candidate"]==src["first_dialogue"]["pdf_page"]
        assert ev["page_audit"]["native_characters"]==sum(x["native_chars"] for x in src["pages"])
        assert ev["page_audit"]["image_pages"]==src["image_pages"]
        assert ev["empirical_status"]=="not_run"
        assert all(a in md for a in LAYERS)
        assert src["sha256"] in md and ("尚" in md or "未" in md) and "图像" in md
        assert len(ev["claims"])>=5
        for c in ev["claims"]:
            assert c["kind"] in KINDS and c["volume"]==vol
            assert c["pdf_pages"] and set(c["pdf_pages"]).issubset(pages)
            assert c["id"] not in IDs
            IDs.add(c["id"])
            if c["kind"]=="HYPOTHESIS":assert c.get("test_status")=="not_tested"
        if lesson==21:assert "100%" in md and "完备" in md
        if lesson==24:assert "乘二" in md and "面积" in md
        if lesson==25:assert "辅助" in md and "中枢" in md
    assert "第一卷" in synthesis and "第二卷" in synthesis
    assert "151" in synthesis and "MACD" in synthesis
    for n in range(21,26):assert f"lesson_{n:03d}.md" in synthesis
    return {"lessons":5,"pages":151,"claim_ids":len(IDs),"source_volumes":2}
def main():
    index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    scan=json.loads((ROOT/"catalog/chanlun_lessons021_025_source_layers.json").read_text(encoding="utf-8"))
    evidences=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(21,26)]
    reports=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(21,26)]
    synthesis=(ROOT/"analyses/books/chanlun/volumes/LESSONS_021_025_SYNTHESIS.md").read_text(encoding="utf-8")
    hashes={v["volume"]:hashlib.sha256((ROOT/v["path"]).read_bytes()).hexdigest() for v in index["volumes"][:2]}
    print("PASS dual-volume source and evidence audit "+json.dumps(audit(index,scan,evidences,reports,synthesis,hashes)))
if __name__=="__main__":main()
