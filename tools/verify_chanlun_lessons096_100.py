#!/usr/bin/env python3
"""Check fifth volume original PDF, 78 pages, typed claims, visual scope and author/editor dispute."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KINDS={"SOURCE","EDITORIAL","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
LENSES=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
VIEWED=[156,193,203,225]
FLAGS={(96,"DIFFERENT_DATED_POST"),(97,"DIFFERENT_DATED_POST"),(98,"DIFFERENT_DATED_POST"),(99,"EDITORIAL_INTRUSION"),(100,"EDITORIAL_COUNTEREXAMPLE"),(100,"DIFFERENT_DATED_POST")}
def validate(index,source,claims,reports,synthesis,graph,older,hashes):
    v=index["volumes"][4]
    assert source["volume"]==5 and source["original_pdf"]==v["path"] and source["original_sha256"]==v["sha256"]==hashes[5]
    assert source["source_pages_total"]==78 and len(source["lessons"])==len(claims)==len(reports)==5
    assert [r["page_count"] for r in source["lessons"]]==[17,20,10,22,9]
    assert source["lessons"][0]["start"]==155 and source["lessons"][-1]["end"]==232
    assert len(source["visual"]["rendered"])==13 and source["visual"]["actually_inspected"]==VIEWED
    assert source["visual"]["all_fine_numeric_labels_verified"] is False
    assert FLAGS.issubset({(x["lesson"],x["kind"]) for x in source["role_flags"]})
    ids=set()
    for n in range(96,101):
        r=source["lessons"][n-96];e=claims[n-96];md=reports[n-96]
        k=next(i for i,x in enumerate(v["lessons"]) if x["lesson"]==n)
        pages=list(range(v["lessons"][k]["start_pdf_page"],v["lessons"][k+1]["start_pdf_page"]))
        assert r["lesson"]==e["lesson"]==n
        assert r["source_path"]==e["source"]["path"]==v["path"]
        assert r["source_sha256"]==e["source"]["sha256"]==hashes[5] and e["source"]["volume"]==5
        assert r["original_date"]==e["source"]["original_date"]
        assert [x["page"] for x in r["page_info"]]==e["source"]["pdf_pages"]==pages
        assert e["quality"]["physical_pages"]==r["page_count"] and e["quality"]["native_chars"]==r["native_chars"]
        assert e["quality"]["image_pages"]==r["image_pages"] and e["quality"]["rendered_previews"]==r["rendered"]
        assert e["quality"]["actually_inspected_pages"]==[p for p in VIEWED if p in pages]
        assert e["quality"]["precise_chart_numbers_verified"] is False
        assert e["real_market_backtest"]=="not_run"
        assert len(e["claims"])==7 and all(x in md for x in LENSES)
        assert hashes[5] in md and "未" in md
        for claim in e["claims"]:
            assert claim["id"] not in ids;ids.add(claim["id"])
            assert claim["volume"]==5 and claim["kind"] in KINDS
            assert claim["pdf_pages"] and set(claim["pdf_pages"]).issubset(pages)
            if claim["kind"]=="HYPOTHESIS":assert claim["test_status"]=="not_tested"
        if n==96:assert "赌徒" in md and "资金" in md
        if n==97:assert "理论" in md and "执行" in md
        if n==98:assert "T+1" in md and "分支" in md
        if n==99:assert "中阴" in md and "结合律" in md
        if n==100:assert "娇注" in md and "分支" in md
    assert len(ids)==35 and "78页" in synthesis and "娇注" in synthesis and "中阴" in synthesis
    assert all(f"lesson_{n:03d}.md" in synthesis for n in range(96,101))
    assert len(older)==7 and [len(g["nodes"]) for g in older]==[40,6,5,5,5,5,5]
    assert older[0]["source_pdf_sha256_by_volume"]=={str(i):hashes[i] for i in (1,2,3)}
    assert older[6]["source_pdf_sha256_by_volume"]=={"5":hashes[5]}
    assert graph["source_pdf_sha256_by_volume"]=={"5":hashes[5]}
    older_ids={x["id"] for g in older for x in g["nodes"]}
    new_ids={x["id"] for x in graph["nodes"]}
    assert len(new_ids)==len(graph["nodes"])==5 and not new_ids&older_ids and len(graph["edges"])==12
    for node in graph["nodes"]:
        assert node["source"]["volume"]==5 and node["source"]["pdf_pages"]
        assert all(155<=p<=232 for p in node["source"]["pdf_pages"])
    for edge in graph["edges"]:
        assert edge["from"] in new_ids and edge["to"] in (new_ids|older_ids) and edge["from"]!=edge["to"]
        assert edge["certainty"] in ("documented_conceptual_relation","ai_analysis")
    return {"lessons":5,"physical_pages":78,"typed_claims":35,"source_previews":13,"actually_inspected":4,"graph_nodes":5,"graph_edges":12}
def pdf_spotcheck(index,sha):
    import fitz
    p=ROOT/index["volumes"][4]["path"]
    assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
    probes={155:["赌徒心理"],156:["2008-01-24"],172:["中医","操作"],173:["望闻问切"],
            192:["背驰"],194:["T+1"],202:["中阴","结合律"],203:["中枢"],224:["级别"],225:["娇注"]}
    with fitz.open(p) as pdf:
        for page,words in probes.items():
            data=pdf[page-1].get_text("text",sort=True)
            for word in words:assert word in data,(page,word)
    return len(probes)
def main():
    index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf8"))
    src=json.loads((ROOT/"catalog/chanlun_lessons096_100_source_layers.json").read_text(encoding="utf8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf8")) for n in range(96,101)]
    md=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf8") for n in range(96,101)]
    syn=(ROOT/"analyses/books/chanlun/volumes/LESSONS_096_100_SYNTHESIS.md").read_text(encoding="utf8")
    graph=json.loads((ROOT/"knowledge/claims/chanlun_lessons096_100_semantic_dependencies.json").read_text(encoding="utf8"))
    old=[json.loads((ROOT/p).read_text(encoding="utf8")) for p in (
      "knowledge/claims/chanlun_early_core_dependencies.json",
      "knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json",
      "knowledge/claims/chanlun_lessons071_075_semantic_dependencies.json",
      "knowledge/claims/chanlun_lessons076_080_semantic_dependencies.json",
      "knowledge/claims/chanlun_lessons081_085_semantic_dependencies.json",
      "knowledge/claims/chanlun_lessons086_090_crossvolume_dependencies.json",
      "knowledge/claims/chanlun_lessons091_095_semantic_dependencies.json")]
    hashes={v["volume"]:hashlib.sha256((ROOT/v["path"]).read_bytes()).hexdigest() for v in index["volumes"]}
    answer=validate(index,src,ev,md,syn,graph,old,hashes)
    answer["pdf_text_spots"]=pdf_spotcheck(index,hashes[5])
    print("PASS Chanlun 96–100 original PDF, editorial dispute and typed source "+json.dumps(answer))
if __name__=="__main__":main()
