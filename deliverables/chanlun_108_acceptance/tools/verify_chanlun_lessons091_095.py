#!/usr/bin/env python3
"""Audit original Volume5 source, 91 physical pages, 35 typed claims, author/editor roles, graph and test boundaries."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KINDS={"SOURCE","EDITORIAL","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
LENSES=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
VISUAL=[65,94,125,144]
REQUIRED={(91,"EDITORIAL_NOTE"),(91,"SEPARATE_DATED_MARKET_POST"),(92,"EDITORIAL_NOTE"),(92,"SEPARATE_DATED_MARKET_POST"),(93,"EDITORIAL_EXPANSION"),(93,"EDITORIAL_SUMMARY"),(93,"STARRED_LATER_POST"),(94,"SEPARATE_DATED_MARKET_POST"),(95,"SEPARATE_DATED_MARKET_POST")}
def validate(index,source,claims,reports,synthesis,new,older,hashes):
    vol=index["volumes"][4]
    assert source["volume"]==5 and source["path"]==vol["path"] and source["sha256"]==vol["sha256"]==hashes[5]
    assert source["physical_pages"]==91 and len(source["lessons"])==len(claims)==len(reports)==5
    assert source["lessons"][0]["start"]==64 and source["lessons"][-1]["end"]==154
    assert [x["page_count"] for x in source["lessons"]]==[29,31,19,7,5]
    assert sum(x["page_count"] for x in source["lessons"])==91
    assert len(source["visual"]["rendered_pages"])==13
    assert source["visual"]["actually_visually_inspected_pages"]==VISUAL
    assert source["visual"]["precise_price_labels_verified"] is False
    assert REQUIRED.issubset({(x["lesson"],x["role"]) for x in source["provenance"]})
    ids=set()
    for n in range(91,96):
        r=source["lessons"][n-91];e=claims[n-91];md=reports[n-91]
        k=next(i for i,x in enumerate(vol["lessons"]) if x["lesson"]==n)
        pages=list(range(vol["lessons"][k]["start_pdf_page"],vol["lessons"][k+1]["start_pdf_page"]))
        assert r["lesson"]==e["lesson"]==n
        assert r["source_path"]==e["source"]["path"]==vol["path"]
        assert r["source_sha256"]==e["source"]["sha256"]==hashes[5]
        assert e["source"]["volume"]==5 and e["source"]["original_date"]==r["original_date"]
        assert [x["page"] for x in r["pages"]]==e["source"]["pdf_pages"]==pages
        assert e["source"]["first_starred_divider_candidate"]==(r["first_divider"]["page"] if r["first_divider"] else None)
        assert e["quality"]["physical_pages"]==r["page_count"]
        assert e["quality"]["native_chars"]==r["native_chars"]
        assert e["quality"]["image_pages"]==r["image_pages"]
        assert e["quality"]["rendered_pages"]==r["previews"]
        assert e["quality"]["visually_inspected_pages"]==[p for p in VISUAL if p in pages]
        assert e["quality"]["precise_chart_prices_verified"] is False and e["market_backtest"]=="not_run"
        assert all(h in md for h in LENSES) and hashes[5] in md and "未" in md
        assert len(e["claims"])==7
        for c in e["claims"]:
            assert c["id"] not in ids;ids.add(c["id"])
            assert c["kind"] in KINDS and c["volume"]==5
            assert c["pdf_pages"] and set(c["pdf_pages"]).issubset(pages)
            if c["kind"]=="HYPOTHESIS":assert c["test_status"]=="not_tested"
        if n==91:assert "四态" in md and "笔" in md
        if n==92:assert "Zn" in md and "第三类" in md
        if n==93:assert "(1,0)" in md and "策略" in md
        if n==94:assert "T+1" in md and "执行" in md
        if n==95:assert "成本" in md and "风险" in md
    assert len(ids)==35 and "91页" in synthesis and "Zn" in synthesis and "T+1" in synthesis
    assert all(f"lesson_{n:03d}.md" in synthesis for n in range(91,96))
    assert len(older)==6 and [len(x["nodes"]) for x in older]==[40,6,5,5,5,5]
    assert older[0]["source_pdf_sha256_by_volume"]=={str(k):hashes[k] for k in (1,2,3)}
    assert older[1]["source_pdf_sha256_by_volume"]=={"3":hashes[3],"4":hashes[4]}
    assert older[5]["source_pdf_sha256_by_volume"]=={"4":hashes[4],"5":hashes[5]}
    assert new["source_pdf_sha256_by_volume"]=={"5":hashes[5]}
    old_ids={z["id"] for g in older for z in g["nodes"]}
    new_ids={z["id"] for z in new["nodes"]}
    assert len(new_ids)==len(new["nodes"])==5 and not new_ids.intersection(old_ids)
    assert len(new["edges"])==12
    for node in new["nodes"]:
        assert node["source"]["volume"]==5
        assert node["source"]["pdf_pages"] and all(64<=p<=154 for p in node["source"]["pdf_pages"])
    for edge in new["edges"]:
        assert edge["from"] in new_ids and edge["to"] in (old_ids|new_ids) and edge["from"]!=edge["to"]
        assert edge["certainty"] in ("documented_conceptual_relation","ai_analysis")
    return {"lessons":5,"pages":91,"claims":35,"rendered":13,"inspected":4,"graph_nodes":5,"graph_edges":12}
def pdf_spotcheck(index,sha):
    import fitz
    p=ROOT/index["volumes"][4]["path"]
    assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
    probes={64:["缠中说禅笔定理"],65:["分型"],66:["矩阵"],
            93:["Zn","中轴"],94:["第三类买卖点"],
            124:["（1，0）"],125:["娇注"],
            143:["当机立断"],145:["T+1"],150:["市场"],151:["2008-01-23"]}
    with fitz.open(p) as pdf:
        for page,words in probes.items():
            raw=pdf[page-1].get_text("text",sort=True)
            for word in words:assert word in raw,(page,word)
    return len(probes)
def main():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    src=json.loads((ROOT/"catalog/chanlun_lessons091_095_source_layers.json").read_text(encoding="utf-8"))
    claims=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(91,96)]
    reports=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(91,96)]
    summary=(ROOT/"analyses/books/chanlun/volumes/LESSONS_091_095_SYNTHESIS.md").read_text(encoding="utf-8")
    new=json.loads((ROOT/"knowledge/claims/chanlun_lessons091_095_semantic_dependencies.json").read_text(encoding="utf-8"))
    older=[json.loads((ROOT/p).read_text(encoding="utf-8")) for p in (
        "knowledge/claims/chanlun_early_core_dependencies.json",
        "knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json",
        "knowledge/claims/chanlun_lessons071_075_semantic_dependencies.json",
        "knowledge/claims/chanlun_lessons076_080_semantic_dependencies.json",
        "knowledge/claims/chanlun_lessons081_085_semantic_dependencies.json",
        "knowledge/claims/chanlun_lessons086_090_crossvolume_dependencies.json")]
    sha={v["volume"]:hashlib.sha256((ROOT/v["path"]).read_bytes()).hexdigest() for v in idx["volumes"]}
    ans=validate(idx,src,claims,reports,summary,new,older,sha)
    ans["pdf_spots"]=pdf_spotcheck(idx,sha[5])
    print("PASS Chanlun 91–95 fifth-volume source, typed claims and graph "+json.dumps(ans))
if __name__=="__main__":main()
