#!/usr/bin/env python3
"""Source-locked volumes4/5 lessons86–90 with 123 pages, typed claims, visual scope and graph continuity."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KINDS={"SOURCE","EDITORIAL","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
LENSES=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
VIEWED=[(4,352),(4,386),(5,5),(5,31),(5,44)]
REQ={(86,"EDITORIAL_COMPLETION"),(87,"UNVERIFIED_ANECDOTE"),(88,"DATED_FOLLOWUP"),(89,"EDITORIAL_SIDE_NOTE"),(90,"AUTHOR_AUXILIARY_NOT_ABSOLUTE")}
def validate(index,source,evidence,reports,synthesis,graph,old,hashes):
    assert source["all_original_physical_pages"]==123
    assert source["volume_shas"]=={"4":hashes[4],"5":hashes[5]}
    assert len(source["lessons"])==len(evidence)==len(reports)==5
    assert sum(x["page_count"] for x in source["lessons"])==123
    assert [(x["volume"],x["start_page"],x["last_page"]) for x in source["lessons"]]==[(4,346,368),(4,369,383),(4,384,407),(5,3,29),(5,30,63)]
    rendered=[(p["volume"],p["pdf_page"]) for p in source["figure_review"]["rendered"]]
    viewed=[(p["volume"],p["pdf_page"]) for p in source["figure_review"]["visually_inspected"]]
    assert len(rendered)==14 and viewed==VIEWED and set(viewed).issubset(rendered)
    assert source["figure_review"]["fine_chart_prices_verified"] is False
    assert REQ.issubset({(x["lesson"],x["role"]) for x in source["provenance"]})
    ids=set()
    for n in range(86,91):
        r=source["lessons"][n-86];e=evidence[n-86];md=reports[n-86]
        vol=index["volumes"][r["volume"]-1]
        k=next(i for i,l in enumerate(vol["lessons"]) if l["lesson"]==n)
        end=(vol["lessons"][k+1]["start_pdf_page"] if k+1<len(vol["lessons"]) else vol["pdf_page_count"]+1)
        pages=list(range(vol["lessons"][k]["start_pdf_page"],end))
        assert r["lesson"]==e["lesson"]==n
        assert r["volume"]==e["source"]["volume"]
        assert r["source_path"]==e["source"]["path"]==vol["path"]
        assert r["source_sha256"]==e["source"]["sha256"]==vol["sha256"]==hashes[r["volume"]]
        assert r["header_date"]==e["source"]["first_post_date"]
        assert [p["pdf_page"] for p in r["pages"]]==e["source"]["pdf_pages"]==pages
        assert r["page_count"]==e["quality"]["physical_pages"]
        assert e["quality"]["image_pages"]==r["image_pages"]
        assert e["quality"]["rendered_previews"]==r["preview_pages"]
        assert e["quality"]["actually_visually_reviewed"]==[p for v,p in VIEWED if v==r["volume"] and p in pages]
        assert e["quality"]["fine_numeric_chart_verified"] is False and e["real_market_backtest"]=="not_run"
        assert all(x in md for x in LENSES) and hashes[r["volume"]] in md
        assert "未" in md and len(e["claims"])==7
        for cl in e["claims"]:
            assert cl["id"] not in ids;ids.add(cl["id"])
            assert cl["kind"] in KINDS and cl["volume"]==r["volume"]
            assert cl["pdf_pages"] and set(cl["pdf_pages"]).issubset(pages)
            if cl["kind"]=="HYPOTHESIS":assert cl["test_status"]=="not_tested"
        if n==86:assert "娇" in md and "级别" in md
        if n==87:assert "梦话" in md and "证据" in md
        if n==88:assert "中阴" in md and "确认" in md
        if n==89:assert "中枢" in md and "盘整" in md
        if n==90:assert "BOLL" in md and "辅助" in md
    assert len(ids)==35 and "123页" in synthesis and "BOLL" in synthesis and "中阴" in synthesis
    assert all(f"lesson_{n:03d}.md" in synthesis for n in range(86,91))
    base,g66,g71,g76,g81=old
    assert len(base["nodes"])==40 and len(g66["nodes"])==6 and len(g71["nodes"])==len(g76["nodes"])==len(g81["nodes"])==5
    assert base["source_pdf_sha256_by_volume"]=={str(n):hashes[n] for n in (1,2,3)}
    assert g66["source_pdf_sha256_by_volume"]=={"3":hashes[3],"4":hashes[4]}
    assert g81["source_pdf_sha256_by_volume"]=={"4":hashes[4]}
    assert graph["source_pdf_sha256_by_volume"]=={"4":hashes[4],"5":hashes[5]}
    old_ids={n["id"] for g in old for n in g["nodes"]}
    new_ids={n["id"] for n in graph["nodes"]}
    assert len(new_ids)==len(graph["nodes"])==5 and not new_ids&old_ids and len(graph["edges"])==11
    for node in graph["nodes"]:
        v=node["source"]["volume"]
        assert v in (4,5) and node["source"]["pdf_pages"]
        assert all(1<=p<=index["volumes"][v-1]["pdf_page_count"] for p in node["source"]["pdf_pages"])
    for edge in graph["edges"]:
        assert edge["from"] in new_ids and edge["to"] in (new_ids|old_ids) and edge["from"]!=edge["to"]
        assert edge["certainty"] in ("documented_conceptual_relation","ai_analysis")
    return {"lessons":5,"physical_pages":123,"typed_claims":35,"previewed_pages":14,"inspected_pages":5,"graph_nodes":5,"graph_edges":11}
def pdf_spots(index,hashes):
    import fitz
    refs={4:{346:["第三类卖点"],350:["娇加"],369:["梦话"],384:["中阴"],386:["191"]},
          5:{3:["中阴"],4:["5 分钟中枢"],6:["盘整"],30:["布林通道"],35:["布林通道"]}}
    for v,pages in refs.items():
        path=ROOT/index["volumes"][v-1]["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest()==hashes[v]
        with fitz.open(path) as pdf:
            for p,words in pages.items():
                raw=pdf[p-1].get_text("text",sort=True)
                for word in words:assert word in raw,(v,p,word)
    return 10
def main():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    src=json.loads((ROOT/"catalog/chanlun_lessons086_090_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(86,91)]
    reports=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(86,91)]
    syn=(ROOT/"analyses/books/chanlun/volumes/LESSONS_086_090_SYNTHESIS.md").read_text(encoding="utf-8")
    graph=json.loads((ROOT/"knowledge/claims/chanlun_lessons086_090_crossvolume_dependencies.json").read_text(encoding="utf-8"))
    older=[json.loads((ROOT/p).read_text(encoding="utf-8")) for p in (
      "knowledge/claims/chanlun_early_core_dependencies.json",
      "knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json",
      "knowledge/claims/chanlun_lessons071_075_semantic_dependencies.json",
      "knowledge/claims/chanlun_lessons076_080_semantic_dependencies.json",
      "knowledge/claims/chanlun_lessons081_085_semantic_dependencies.json")]
    shas={v["volume"]:hashlib.sha256((ROOT/v["path"]).read_bytes()).hexdigest() for v in idx["volumes"]}
    ans=validate(idx,src,ev,reports,syn,graph,older,shas)
    ans["pdf_spots"]=pdf_spots(idx,shas)
    print("PASS Chanlun 86–90 original PDFs and contextual/auxiliary source audits "+json.dumps(ans))
if __name__=="__main__":main()
