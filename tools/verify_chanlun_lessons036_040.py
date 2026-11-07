#!/usr/bin/env python3
"""Audit lesson 36–40 PDF provenance, claim statuses, source correction notes and dependency graph."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TYPES={"SOURCE","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
LENSES=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
def audit(index,inventory,claims,reports,overview,graph,sha_by_volume):
    v=index["volumes"][1]
    assert inventory["original_pdf_sha256"]==v["sha256"]==sha_by_volume[2]
    assert inventory["original_pdf_path"]==v["path"]
    assert len(inventory["lessons"])==len(claims)==len(reports)==5
    assert sum(len(x["pages"]) for x in inventory["lessons"])==73
    ids=set()
    for n in range(36,41):
        k=n-36;src=inventory["lessons"][k];ev=claims[k];md=reports[k]
        i=next(j for j,x in enumerate(v["lessons"]) if x["lesson"]==n)
        pages=list(range(v["lessons"][i]["start_pdf_page"],v["lessons"][i+1]["start_pdf_page"]))
        assert src["lesson"]==ev["lesson"]==n
        assert src["sha256"]==ev["source"]["sha256"]==sha_by_volume[2]
        assert ev["source"]["path"]==v["path"] and ev["source"]["volume"]==2
        assert ev["source"]["pdf_pages"]==pages
        assert [x["pdf_page"] for x in src["pages"]]==pages
        assert ev["source"]["original_date"]==src["date"]
        assert ev["source"]["appendix_divider"]==(src["first_appendix"]["page"] if src["first_appendix"] else None)
        assert ev["quality"]["page_count"]==len(pages)
        assert ev["quality"]["native_text_chars"]==sum(x["native_chars"] for x in src["pages"])
        assert ev["quality"]["image_pages"]==src["image_pages"]
        assert ev["empirical_status"]=="not_run"
        assert sha_by_volume[2] in md and all(x in md for x in LENSES)
        assert "图" in md and ("未" in md or "尚" in md)
        assert len(ev["claims"])>=6
        for c in ev["claims"]:
            assert c["id"] not in ids
            ids.add(c["id"])
            assert c["kind"] in TYPES and c["volume"]==2
            assert c["pdf_pages"] and set(c["pdf_pages"]).issubset(pages)
            if c["kind"]=="HYPOTHESIS":assert c.get("test_status")=="not_tested"
        if n==36:assert "编者" in md and "重组" in md
        if n==37:assert "同级别" in md and "创新" in md
        if n==38:assert "唯一" in md and "盘整" in md
        if n==39:assert "编者" in md and "遗漏" in md
        if n==40:assert "现金" in md and "库存" in md
    assert "73" in overview and "唯一性" in overview and "编者" in overview
    for n in range(36,41):assert f"lesson_{n}.md" in overview
    assert graph["source_pdf_sha256_by_volume"]=={str(k):v for k,v in sha_by_volume.items()}
    nodes={node["id"]:node for node in graph["nodes"]}
    assert len(nodes)==len(graph["nodes"]) and len(nodes)>=13
    for id in ("L36-MULTIPARSE","L37-TREND-TYPECHECK","L38-FIXED-LEVEL","L39-MISSING-BRANCH","L40-SHARED-INVENTORY"):
        assert id in nodes
    for node in nodes.values():
        vol=node["source"]["volume"]
        assert vol in (1,2) and node["source"]["pdf_pages"]
        assert all(1<=p<=index["volumes"][vol-1]["pdf_page_count"] for p in node["source"]["pdf_pages"])
    for edge in graph["edges"]:
        assert edge["from"] in nodes and edge["to"] in nodes and edge["from"]!=edge["to"]
        assert edge["certainty"] in ("documented_conceptual_relation","ai_analysis")
    assert any(e["to"]=="L39-MISSING-BRANCH" for e in graph["edges"])
    return {"lessons":5,"pages":73,"claims":len(ids),"graph_nodes":len(nodes),"graph_edges":len(graph["edges"])}
def main():
    index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    inv=json.loads((ROOT/"catalog/chanlun_lessons036_040_source_layers.json").read_text(encoding="utf-8"))
    claims=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n}.json").read_text(encoding="utf-8")) for n in range(36,41)]
    reports=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n}.md").read_text(encoding="utf-8") for n in range(36,41)]
    overview=(ROOT/"analyses/books/chanlun/volumes/LESSONS_036_040_SYNTHESIS.md").read_text(encoding="utf-8")
    graph=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    hashes={v["volume"]:hashlib.sha256((ROOT/v["path"]).read_bytes()).hexdigest() for v in index["volumes"][:2]}
    print("PASS lessons36-40 source and concept revision audit "+json.dumps(audit(index,inv,claims,reports,overview,graph,hashes)))
if __name__=="__main__":main()
