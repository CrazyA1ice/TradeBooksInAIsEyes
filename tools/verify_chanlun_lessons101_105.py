#!/usr/bin/env python3
"""Verify Chanlun 101-105 original source inventory, source roles, 35 claims, visual scope and prior graph compatibility."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LENSES=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
KINDS={"SOURCE","EDITORIAL","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
INSPECTED=[234,242,270,291,326]
REQUIRED={(101,"AUTHOR_ORIGINAL"),(101,"DIFFERENT_DATED_POST"),(102,"EDITORIAL_GLOSS"),(103,"STARRED_DIVIDER"),(104,"LATER_DATED_EDIT"),(104,"DIFFERENT_DATED_POST"),(105,"EDITORIAL_GLOSS")}
def validate(index,src,evid,chapters,synthesis,graph,old,hashes):
    v=index["volumes"][4]
    assert src["original_volume"]==5 and src["original_path"]==v["path"] and src["original_sha256"]==v["sha256"]==hashes[5]
    assert len(src["lessons"])==len(evid)==len(chapters)==5 and src["total_physical_pages"]==140
    assert [r["page_count"] for r in src["lessons"]]==[8,28,21,35,48]
    assert src["lessons"][0]["start"]==233 and src["lessons"][-1]["end"]==372
    assert len(src["visual"]["rendered_pages"])==15 and src["visual"]["actually_visually_reviewed_pages"]==INSPECTED
    assert set(INSPECTED).issubset(src["visual"]["rendered_pages"])
    assert src["visual"]["fine_chart_price_labels_verified"] is False
    assert REQUIRED.issubset({(x["lesson"],x["kind"]) for x in src["source_role_flags"]})
    ids=set()
    for n in range(101,106):
        r=src["lessons"][n-101];e=evid[n-101];md=chapters[n-101]
        k=next(j for j,ls in enumerate(v["lessons"]) if ls["lesson"]==n)
        pages=list(range(v["lessons"][k]["start_pdf_page"],v["lessons"][k+1]["start_pdf_page"]))
        assert r["lesson"]==e["lesson"]==n and r["path"]==e["source"]["path"]==v["path"]
        assert r["sha256"]==e["source"]["sha256"]==hashes[5] and e["source"]["volume"]==5
        assert r["original_date"]==e["source"]["original_date"]
        assert e["source"]["pdf_pages"]==[x["page"] for x in r["pages"]]==pages
        assert e["quality"]["physical_pages"]==r["page_count"] and e["quality"]["native_chars"]==r["native_chars"]
        assert e["quality"]["image_pages"]==r["image_pages"] and e["quality"]["rendered_previews"]==r["rendered_previews"]
        assert e["quality"]["actually_inspected_pages"]==[p for p in INSPECTED if p in pages]
        assert e["quality"]["fine_chart_numeric_verified"] is False and e["real_market_backtest"]=="not_run"
        assert len(e["claims"])==7 and all(x in md for x in LENSES) and hashes[5] in md and "未" in md
        for cl in e["claims"]:
            assert cl["id"] not in ids;ids.add(cl["id"])
            assert cl["kind"] in KINDS and cl["volume"]==5
            assert cl["pdf_pages"] and set(cl["pdf_pages"]).issubset(pages)
            if cl["kind"]=="HYPOTHESIS":assert cl["test_status"]=="not_tested"
        if n==101:assert "第二" in md and "低于" in md
        if n==102:assert "唯一" in md and "证明" in md
        if n==103:assert "MACD" in md and "零轴" in md
        if n==104:assert "2010" in md and "几何" in md
        if n==105:assert "机械" in md and "成交" in md
    assert len(ids)==35 and "140物理页" in synthesis and "MACD" in synthesis and "2010" in synthesis
    assert all(f"lesson_{n:03d}.md" in synthesis for n in range(101,106))
    assert len(old)==8 and [len(g["nodes"]) for g in old]==[40,6,5,5,5,5,5,5]
    assert old[0]["source_pdf_sha256_by_volume"]=={str(i):hashes[i] for i in (1,2,3)}
    assert old[7]["source_pdf_sha256_by_volume"]=={"5":hashes[5]}
    assert graph["source_pdf_sha256_by_volume"]=={"5":hashes[5]}
    existing={n["id"] for g in old for n in g["nodes"]}
    fresh={n["id"] for n in graph["nodes"]}
    assert len(fresh)==len(graph["nodes"])==5 and not fresh&existing
    assert len(graph["edges"])==13
    for n in graph["nodes"]:
        assert n["source"]["volume"]==5 and n["source"]["pdf_pages"]
        assert all(233<=p<=372 for p in n["source"]["pdf_pages"])
    for edge in graph["edges"]:
        assert edge["from"] in fresh and edge["to"] in fresh|existing and edge["from"]!=edge["to"]
        assert edge["certainty"] in ("documented_conceptual_relation","ai_analysis")
    return {"lessons":5,"physical_pages":140,"claims":35,"rendered":15,"actually_inspected":5,"new_nodes":5,"new_edges":13}
def pdf_spots(index,sha):
    import fitz
    p=ROOT/index["volumes"][4]["path"]
    assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
    probes={233:["第二类买点"],234:["走势必完美"],235:["2008-03-05"],
            241:["自然数","唯一分解"],242:["区间套"],
            269:["MACD"],271:["0 轴"],
            290:["广义相对论"],291:["2010-07-02"],
            325:["机械化操作"],326:["2008-04-14"]}
    with fitz.open(p) as pdf:
        for page,terms in probes.items():
            text=pdf[page-1].get_text("text",sort=True)
            for term in terms:assert term in text,(page,term)
    return len(probes)
def main():
    index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text("utf8"))
    src=json.loads((ROOT/"catalog/chanlun_lessons101_105_source_layers.json").read_text("utf8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text("utf8")) for n in range(101,106)]
    md=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text("utf8") for n in range(101,106)]
    syn=(ROOT/"analyses/books/chanlun/volumes/LESSONS_101_105_SYNTHESIS.md").read_text("utf8")
    graph=json.loads((ROOT/"knowledge/claims/chanlun_lessons101_105_semantic_dependencies.json").read_text("utf8"))
    old=[json.loads((ROOT/p).read_text("utf8")) for p in (
        "knowledge/claims/chanlun_early_core_dependencies.json",
        "knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json",
        "knowledge/claims/chanlun_lessons071_075_semantic_dependencies.json",
        "knowledge/claims/chanlun_lessons076_080_semantic_dependencies.json",
        "knowledge/claims/chanlun_lessons081_085_semantic_dependencies.json",
        "knowledge/claims/chanlun_lessons086_090_crossvolume_dependencies.json",
        "knowledge/claims/chanlun_lessons091_095_semantic_dependencies.json",
        "knowledge/claims/chanlun_lessons096_100_semantic_dependencies.json")]
    hashes={v["volume"]:hashlib.sha256((ROOT/v["path"]).read_bytes()).hexdigest() for v in index["volumes"]}
    result=validate(index,src,ev,md,syn,graph,old,hashes)
    result["pdf_source_spots"]=pdf_spots(index,hashes[5])
    print("PASS Chanlun lessons101-105 original SHA, original/editor roles and typed claim checks "+json.dumps(result))
if __name__=="__main__":main()
