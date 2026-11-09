#!/usr/bin/env python3
"""Source and claim provenance audit: lessons 31–35 and a provisional dependency graph."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
KINDS={"SOURCE","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
LAYERS=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
def audit(index,source,items,reports,overview,graph,hashes):
    vols={v["volume"]:v for v in index["volumes"]}
    assert hashes[1]==vols[1]["sha256"]
    assert hashes[2]==vols[2]["sha256"]==source["source_sha256"]
    assert source["source_path"]==vols[2]["path"]
    assert len(source["lessons"])==len(items)==len(reports)==5
    assert sum(x["page_count"] for x in source["lessons"])==113
    ids=set()
    for n in range(31,36):
        i=n-31
        src=source["lessons"][i];e=items[i];md=reports[i]
        vol=vols[2]
        k=next(j for j,x in enumerate(vol["lessons"]) if x["lesson"]==n)
        expected_pages=list(range(vol["lessons"][k]["start_pdf_page"],vol["lessons"][k+1]["start_pdf_page"]))
        assert src["lesson"]==e["source"]["lesson_number"]==n
        assert src["sha256"]==e["source"]["sha256"]==hashes[2]
        assert e["source"]["volume"]==2 and e["source"]["path"]==vol["path"]
        assert e["source"]["pdf_pages"]==expected_pages
        assert [p["pdf_page"] for p in src["pages"]]==expected_pages
        assert src["article_date"]==e["source"]["original_date"]
        assert src["first_appendix_divider"]["pdf_page"]==e["source"]["appendix_boundary_candidate"]
        assert sum(p["native_text_chars"] for p in src["pages"])==e["source_quality"]["native_chars"]
        assert [p["pdf_page"] for p in src["pages"] if p["image_count"]>0]==e["source_quality"]["image_pages"]
        assert e["empirical_status"]=="not_run"
        assert hashes[2] in md and all(layer in md for layer in LAYERS)
        assert len(md)>=1600 and "图像" in md and ("未" in md or "尚" in md)
        assert len(e["claims"])>=5
        for c in e["claims"]:
            assert c["kind"] in KINDS
            assert c["volume"]==2 and c["pdf_pages"]
            assert set(c["pdf_pages"]).issubset(set(expected_pages))
            assert c["id"] not in ids
            ids.add(c["id"])
            if c["kind"]=="HYPOTHESIS":assert c.get("test_status")=="not_tested"
        if n==31:assert "成本" in md and "市值" in md
        if n==32:assert "确认" in md and "当下" in md
        if n==33:assert "多义性" in md and "解析" in md
        if n==35:assert "结合律" in md and "递归" in md and "T+1" in md
    assert "113" in overview and "零成本" in overview and "结合律" in overview
    for n in range(31,36):assert f"lesson_{n:03d}.md" in overview
    # The dependency graph's chapter 17 node refers to volume 1; all others to volume 2.
    assert graph["source_pdf_sha256_by_volume"]=={"1":hashes[1],"2":hashes[2],"3":vols[3]["sha256"]}
    nodes={x["id"]:x for x in graph["nodes"]}
    assert len(nodes)==len(graph["nodes"]) and len(nodes)>=8
    for node in nodes.values():
        volno=node["source"]["volume"]
        assert volno in (1,2,3)
        assert node["source"]["pdf_pages"] and all(1<=p<=vols[volno]["pdf_page_count"] for p in node["source"]["pdf_pages"])
    for edge in graph["edges"]:
        assert edge["from"] in nodes and edge["to"] in nodes and edge["from"]!=edge["to"]
        assert edge["certainty"] in ("ai_analysis","documented_conceptual_relation")
    assert any(x["id"]=="L33-AMBIGUITY" for x in graph["nodes"])
    assert any(x["id"]=="L35-BASE" for x in graph["nodes"])
    return {"lessons":5,"pages":113,"claims":len(ids),"graph_nodes":len(nodes),"graph_edges":len(graph["edges"])}
def main():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    src=json.loads((ROOT/"catalog/chanlun_lessons031_035_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(31,36)]
    md=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(31,36)]
    overview=(ROOT/"analyses/books/chanlun/volumes/LESSONS_031_035_SYNTHESIS.md").read_text(encoding="utf-8")
    graph=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    hashes={v["volume"]:hashlib.sha256((ROOT/v["path"]).read_bytes()).hexdigest() for v in idx["volumes"][:2]}
    print("PASS lessons31–35 source evidence and dependency graph "+json.dumps(audit(idx,src,ev,md,overview,graph,hashes)))
if __name__=="__main__":main()
