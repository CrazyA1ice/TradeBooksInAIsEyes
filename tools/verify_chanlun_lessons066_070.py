#!/usr/bin/env python3
"""Cross-volume Chanlun 66–70 source pages, split graph, hypotheses and six literal probes."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KINDS={"SOURCE","EDITORIAL","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
SEVEN=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
EXPECTED_PREVIEWS=[(3,376),(3,390),(3,397),(3,403),(4,5),(4,11),(4,29),(4,34),(4,55),(4,60)]
def validate(idx,src,evidence,reports,overview,extension,base_graph,hashes):
    assert len(src["lessons"])==len(evidence)==len(reports)==5
    assert src["total_pages"]==100 and sum(x["page_count"] for x in src["lessons"])==100
    assert src["pdf_sha256_by_volume"]=={"3":hashes[3],"4":hashes[4]}
    assert [(p["volume"],p["pdf_page"]) for p in src["visually_inspected_page_refs"]]==EXPECTED_PREVIEWS
    assert "numeric" not in src.get("image_verified_fields",[])
    flags={(f["lesson"],f["volume"],f["pdf_page"]) for f in src["editorial_flags"]}
    assert {(67,3,388),(67,3,389),(67,3,390),(68,4,5),(69,4,28),(70,4,53)}.issubset(flags)
    seen=set()
    for n in range(66,71):
        r=src["lessons"][n-66];e=evidence[n-66];md=reports[n-66]
        volume=3 if n<=67 else 4
        v=idx["volumes"][volume-1];k=next(i for i,x in enumerate(v["lessons"]) if x["lesson"]==n)
        pages=list(range(v["lessons"][k]["start_pdf_page"],v["lessons"][k+1]["start_pdf_page"]))
        assert r["lesson"]==e["lesson"]==n and r["volume"]==e["source"]["volume"]==volume
        assert r["pdf_path"]==e["source"]["path"]==v["path"]
        assert r["sha256"]==e["source"]["sha256"]==hashes[volume]
        assert r["original_date"]==e["source"]["original_date"]
        assert [p["pdf_page"] for p in r["pages"]]==e["source"]["pdf_pages"]==pages
        assert r["page_count"]==e["quality"]["page_count"] and r["total_native_chars"]==e["quality"]["native_chars"]
        assert r["image_pages"]==e["quality"]["image_pages"]
        assert e["source"]["first_appendix_separator"]==r["first_divider"]["pdf_page"]
        preview=[p for v,p in EXPECTED_PREVIEWS if v==volume and p in pages]
        assert preview==e["quality"]["visual_preview_pages"]
        assert e["quality"]["numeric_chart_values_verified"] is False
        assert e["real_market_tests"]=="not_run"
        assert all(s in md for s in SEVEN) and hashes[volume] in md
        assert "未" in md and "图" in md
        assert len(e["claims"])>=6
        for c in e["claims"]:
            assert c["id"] not in seen
            seen.add(c["id"])
            assert c["kind"] in KINDS and c["volume"]==volume
            assert c["pdf_pages"] and set(c["pdf_pages"]).issubset(pages)
            if c["kind"]=="HYPOTHESIS":assert c.get("test_status")=="not_tested"
        if n==67:assert "缺口" in md and "反向" in md and "编辑" in md
        if n==68:assert "边界" in md and "分段" in md
        if n==69:assert "候选" in md and "修改" in md
    assert "100页" in overview and "特征序列" in overview and "状态" in overview
    assert all(f"lesson_{n:03d}.md" in overview for n in range(66,71))
    assert base_graph["source_pdf_sha256_by_volume"]=={str(n):hashes[n] for n in (1,2,3)}
    assert extension["source_pdf_sha256_by_volume"]=={"3":hashes[3],"4":hashes[4]}
    old_ids={n["id"] for n in base_graph["nodes"]}
    new_ids={n["id"] for n in extension["nodes"]}
    assert len(new_ids)==len(extension["nodes"])==6 and not (old_ids&new_ids)
    assert len(extension["edges"])>=8
    for node in extension["nodes"]:
        vol=node["source"]["volume"]
        assert vol in (3,4) and node["source"]["pdf_pages"]
        assert all(1<=p<=idx["volumes"][vol-1]["pdf_page_count"] for p in node["source"]["pdf_pages"])
    for ed in extension["edges"]:
        assert ed["from"] in new_ids and ed["to"] in old_ids|new_ids and ed["from"]!=ed["to"]
        assert ed["certainty"] in ("documented_conceptual_relation","ai_analysis")
    return {"lessons":5,"pages":100,"claims":len(seen),"volumes":[3,4],
            "previews":len(EXPECTED_PREVIEWS),"new_graph_nodes":len(new_ids),"new_graph_edges":len(extension["edges"])}
def spot_check(idx,hashes):
    import fitz
    probes={3:{374:["主力资金的食物链"],388:["特征序列","缺口"],389:["第二种情况"]},
            4:{3:["走势预测的精确意义"],28:["分型","修改"],52:["三种走势"]}}
    for vol,pages in probes.items():
        path=ROOT/idx["volumes"][vol-1]["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest()==hashes[vol]
        with fitz.open(path) as doc:
            for page,terms in pages.items():
                txt=doc[page-1].get_text("text",sort=True)
                for term in terms:assert term in txt,(vol,page,term)
    return 6
def main():
    i=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    s=json.loads((ROOT/"catalog/chanlun_lessons066_070_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(66,71)]
    r=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(66,71)]
    o=(ROOT/"analyses/books/chanlun/volumes/LESSONS_066_070_SYNTHESIS.md").read_text(encoding="utf-8")
    ext=json.loads((ROOT/"knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json").read_text(encoding="utf-8"))
    graph=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    sha={v["volume"]:hashlib.sha256((ROOT/v["path"]).read_bytes()).hexdigest() for v in i["volumes"][:4]}
    x=validate(i,s,ev,r,o,ext,graph,sha)
    x["original_pdf_probes"]=spot_check(i,sha)
    print("PASS Chanlun lessons 66–70 crossvolume provenance and evidence "+json.dumps(x))
if __name__=="__main__":main()
