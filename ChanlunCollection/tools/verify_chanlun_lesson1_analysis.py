#!/usr/bin/env python3
"""Audit published lesson-1 review against version-locked source lesson index."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"knowledge/evidence/chanlun_lesson001.json"
INDEX=ROOT/"catalog/chanlun_lesson_index.json"
REPORT=ROOT/"analyses/books/chanlun/chapters/lesson_001.md"
KINDS={"SOURCE","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}

def verify(index: dict, data: dict, report: str):
    book=index["volumes"][0]
    first,second=book["lessons"][:2]
    src=data["source"]
    assert first["lesson"]==src["lesson_number"]==1
    assert second["lesson"]==2
    assert src["sha256"]==book["sha256"],"Source fingerprint mismatch"
    assert src["path"]==book["path"],"Source file mismatch"
    assert src["pdf_pages"]==list(range(first["start_pdf_page"],second["start_pdf_page"]))
    assert src["next_lesson_pdf_start"]==second["start_pdf_page"]
    assert [x["pdf_page"] for x in data["page_audit"]]==src["pdf_pages"]
    image_pages=[x for x in data["page_audit"] if x["embedded_images"]]
    assert image_pages and any("unverified" in x["status"] for x in image_pages),"Must disclose unverified image"
    claims=data["claims"]
    assert len(claims)>=8
    assert len({x["id"] for x in claims})==len(claims),"Duplicate claim id"
    for claim in claims:
        assert claim["kind"] in KINDS
        assert set(claim["pages"]).issubset(set(src["pdf_pages"])),"Invalid cited page"
        if claim["kind"]=="HYPOTHESIS":
            assert claim.get("test_status")=="not_tested","Unverified hypothesis must be marked"
    for marker in ("第一重","第二重","第三重","第四重","第五重","第六重","第七重",
                   "未检验","原著","图像","暂不"):
        assert marker in report, f"Missing review marker {marker}"
    assert "PDF p.3–5" in report or "PDF 页 **3–5**" in report
    return len(claims)

def main():
    idx=json.loads(INDEX.read_text(encoding="utf-8"))
    evidence=json.loads(EVIDENCE.read_text(encoding="utf-8"))
    report=REPORT.read_text(encoding="utf-8")
    n=verify(idx,evidence,report)
    print(f"PASS lesson1 source evidence audit: {n} distinct claims, seven layers, source SHA and page span verified")
if __name__=="__main__":
    main()
