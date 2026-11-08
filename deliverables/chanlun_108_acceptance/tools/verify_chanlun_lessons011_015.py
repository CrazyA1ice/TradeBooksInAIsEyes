#!/usr/bin/env python3
"""Verify source-grounded first-pass research for lessons 11–15."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
KINDS={"SOURCE","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
LAYERS=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")

def verify(index,source,claims,chapters,synthesis,sha):
    vol=index["volumes"][0]
    assert vol["sha256"]==sha==source["source_sha256"],"Source SHA mismatch"
    assert len(source["lessons"])==len(claims)==len(chapters)==5
    assert source["lessons"][0]["start"]==82
    assert source["lessons"][-1]["end"]==168
    assert sum(len(x["pages"]) for x in source["lessons"])==87
    all_claim_ids=set()
    for n in range(11,16):
        j=n-11
        cur,nxt=vol["lessons"][n-1],vol["lessons"][n]
        record,ev,md=source["lessons"][j],claims[j],chapters[j]
        p=list(range(cur["start_pdf_page"],nxt["start_pdf_page"]))
        assert record["lesson"]==ev["source"]["lesson_number"]==n
        assert ev["source"]["sha256"]==sha and ev["source"]["path"]==vol["path"]
        assert [x["page"] for x in record["pages"]]==p
        assert ev["source"]["pdf_pages"]==p
        assert record["start"]==p[0] and record["end"]==p[-1]
        assert ev["quality"]["native_text_chars"]==record["total_native_characters"]
        assert ev["quality"]["pages_with_images"]==record["image_pages"]
        assert ev["quality"]["low_native_text_pages"]==record["low_text_pages"]
        assert ev["source"]["appendix_divider_candidate_pdf_page"]==record["first_divider"]["pdf_page"]
        assert sha in md and "未" in md and len(md)>1700
        assert all(x in md for x in LAYERS)
        assert ev["empirical_status"]=="not_run"
        assert len(ev["claims"])>=5
        for c in ev["claims"]:
            assert c["kind"] in KINDS
            assert c["pdf_pages"] and set(c["pdf_pages"]).issubset(set(p))
            assert c["id"] not in all_claim_ids,"Claim id reused"
            all_claim_ids.add(c["id"])
            if c["kind"]=="HYPOTHESIS":assert c.get("test_status")=="not_tested"
        if n==14:
            assert "复权" in md and 121 in ev["source"]["pdf_pages"]
        if n==15:
            assert "后期" in md and "编者" in md and "相等" in md
    assert "最后一次缠绕" in synthesis and "后期" in synthesis and "三种走势" in synthesis
    for n in range(11,16):assert f"lesson_{n:03d}.md" in synthesis
    return {"lessons":5,"pages":87,"source_claims":len(all_claim_ids)}

def main():
    index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    source=json.loads((ROOT/"catalog/chanlun_lessons011_015_source_layers.json").read_text(encoding="utf-8"))
    claims=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(11,16)]
    chapters=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(11,16)]
    synthesis=(ROOT/"analyses/books/chanlun/volumes/LESSONS_011_015_SYNTHESIS.md").read_text(encoding="utf-8")
    sha=hashlib.sha256((ROOT/index["volumes"][0]["path"]).read_bytes()).hexdigest()
    print("PASS Chanlun 11–15 source and evidence checks "+json.dumps(verify(index,source,claims,chapters,synthesis,sha)))
if __name__=="__main__":main()
