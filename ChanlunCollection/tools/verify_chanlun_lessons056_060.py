#!/usr/bin/env python3
"""Verify Chanlun lessons 56–60 provenance, 5 rendered page flags, typed claims, links and graph."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KINDS={"SOURCE","INTERPRETATION","INFERENCE","HYPOTHESIS","EDITORIAL","EVIDENCE"}
LENSES=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
def audit(idx,source,claims,reports,overview,graph,sha):
    v=idx["volumes"][2]
    assert source["volume"]==3 and source["source_path"]==v["path"]
    assert source["sha256"]==v["sha256"]==sha[3]
    assert source["total_pages"]==72
    assert len(source["lessons"])==len(claims)==len(reports)==5
    assert sum(s["page_count"] for s in source["lessons"])==72
    vis=source["visual_review"]
    assert vis["pdf_pages"]==[207,219,231,252,268]
    assert "low-resolution" in " ".join(vis["limitations"])
    allids=set()
    for n in range(56,61):
        r=source["lessons"][n-56];ev=claims[n-56];md=reports[n-56]
        pos=next(i for i,z in enumerate(v["lessons"]) if z["lesson"]==n)
        pages=list(range(v["lessons"][pos]["start_pdf_page"],v["lessons"][pos+1]["start_pdf_page"]))
        assert r["lesson"]==ev["lesson"]==n
        assert r["sha256"]==ev["source"]["sha256"]==sha[3]
        assert ev["source"]["volume"]==3 and ev["source"]["path"]==v["path"]
        assert r["original_date"]==ev["source"]["original_date"]
        assert [p["pdf_page"] for p in r["pages"]]==ev["source"]["pdf_pages"]==pages
        assert ev["source"]["appendix_divider_candidate"]==r["first_divider"]["pdf_page"]
        assert r["page_count"]==ev["quality"]["page_count"]
        assert r["native_chars"]==ev["quality"]["native_chars"]
        assert r["image_pages"]==ev["quality"]["image_pages"]
        assert ev["quality"]["thumbnail_pages_visual_reviewed"]==[p for p in vis["pdf_pages"] if p in pages]
        assert ev["quality"]["figure_prices_verified"] is False and ev["empirical_status"]=="not_run"
        assert all(x in md for x in LENSES) and sha[3] in md
        assert "未" in md and "图" in md
        assert len(ev["claims"])>=7
        for c in ev["claims"]:
            assert c["id"] not in allids
            allids.add(c["id"])
            assert c["kind"] in KINDS and c["volume"]==3
            assert c["pdf_pages"] and set(c["pdf_pages"]).issubset(pages)
            if c["kind"]=="HYPOTHESIS":assert c.get("test_status")=="not_tested"
        if n==56:assert "5·30" in md and "第一" in md
        if n==58:assert "PENDING" in md and "未来" in md
        if n==59:assert "3994.57" in md and "3994.21" in md and "舍入" in md
    assert "72页" in overview and "3994.57" in overview and "图像" in overview
    assert all(f"lesson_{n:03d}.md" in overview for n in range(56,61))
    assert graph["source_pdf_sha256_by_volume"]=={str(k):sha[k] for k in (1,2,3)}
    nodes={x["id"]:x for x in graph["nodes"]}
    assert len(nodes)==len(graph["nodes"]) and len(nodes)>=34
    for node_id in ("L56-GAP-ASOF","L57-SEGMENT-THRESHOLD","L58-PENDING-REVERSAL","L59-PRICE-QUANTIZATION","L60-SHOCK-SCALE"):
        assert node_id in nodes
    for node in nodes.values():
        vnumber=node["source"]["volume"]
        assert vnumber in (1,2,3) and node["source"]["pdf_pages"]
        assert all(1<=p<=idx["volumes"][vnumber-1]["pdf_page_count"] for p in node["source"]["pdf_pages"])
    for edge in graph["edges"]:
        assert edge["from"] in nodes and edge["to"] in nodes and edge["from"]!=edge["to"]
        assert edge["certainty"] in ("documented_conceptual_relation","ai_analysis")
    return {"lessons":5,"pages":72,"claims":len(allids),"visual_thumbnail_pages":len(vis["pdf_pages"]),"nodes":len(nodes),"edges":len(graph["edges"])}
def main():
    i=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    s=json.loads((ROOT/"catalog/chanlun_lessons056_060_source_layers.json").read_text(encoding="utf-8"))
    e=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(56,61)]
    r=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(56,61)]
    o=(ROOT/"analyses/books/chanlun/volumes/LESSONS_056_060_SYNTHESIS.md").read_text(encoding="utf-8")
    g=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    hashes={x["volume"]:hashlib.sha256((ROOT/x["path"]).read_bytes()).hexdigest() for x in i["volumes"][:3]}
    print("PASS source, figure and evidence audit 56–60 "+json.dumps(audit(i,s,e,r,o,g,hashes)))
if __name__=="__main__":main()
