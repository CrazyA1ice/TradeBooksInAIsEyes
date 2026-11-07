#!/usr/bin/env python3
"""Original PDF & 76–80 typed evidence audit; protects old source/CI contracts."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KINDS={"SOURCE","EDITORIAL","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
LENSES=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
EXPECTED_VIEWED=[160,165,177,189,194,204,213]
def validate(index,inv,claims,reports,synthesis,new,graphs,shas):
    v=index["volumes"][3]
    assert inv["source_path"]==v["path"] and inv["source_sha256"]==v["sha256"]==shas[4]
    assert inv["volume"]==4 and inv["total_pdf_pages"]==89
    assert len(inv["lessons"])==len(claims)==len(reports)==5
    assert sum(x["page_count"] for x in inv["lessons"])==89
    assert inv["lessons"][0]["first_page"]==143 and inv["lessons"][-1]["last_page"]==231
    assert len(inv["visual"]["rendered_pages"])==11
    assert inv["visual"]["actually_inspected_pages"]==EXPECTED_VIEWED
    assert inv["visual"]["fine_chart_values_verified"] is False
    prov={(x["lesson"],x["kind"]) for x in inv["provenance"]}
    for tup in [(76,"different_date"),(77,"figure_dominant"),(78,"author_vs_editor_dispute"),(79,"author_vs_editor_side_note"),(80,"retrospective_correction_note")]:
        assert tup in prov
    seen=set()
    for n in range(76,81):
        x=inv["lessons"][n-76];e=claims[n-76];md=reports[n-76]
        k=next(j for j,z in enumerate(v["lessons"]) if z["lesson"]==n)
        pages=list(range(v["lessons"][k]["start_pdf_page"],v["lessons"][k+1]["start_pdf_page"]))
        assert x["lesson"]==e["lesson"]==n and x["volume"]==e["source"]["volume"]==4
        assert x["source_path"]==e["source"]["path"]==v["path"]
        assert x["sha256"]==e["source"]["sha256"]==shas[4]
        assert [z["pdf_page"] for z in x["pages"]]==e["source"]["pdf_pages"]==pages
        assert x["header_date"]==e["source"]["original_post_date"]
        assert x["page_count"]==e["quality"]["page_count"] and x["native_chars"]==e["quality"]["native_chars"]
        assert x["image_pages"]==e["quality"]["image_pages"]
        assert e["source"]["starred_divider_candidate"]==(x["first_starred_divider"]["pdf_page"] if x["first_starred_divider"] else None)
        assert e["quality"]["preview_pages"]==x["preview_pages"]
        assert e["quality"]["visually_inspected_pages"]==[p for p in EXPECTED_VIEWED if p in pages]
        assert e["quality"]["fine_chart_values_verified"] is False and e["real_market_backtest"]=="not_run"
        assert all(s in md for s in LENSES) and shas[4] in md and "未" in md
        assert len(e["claims"])==7
        for c in e["claims"]:
            assert c["id"] not in seen
            seen.add(c["id"])
            assert c["volume"]==4 and c["kind"] in KINDS and c["pdf_pages"] and set(c["pdf_pages"]).issubset(pages)
            if c["kind"]=="HYPOTHESIS":assert c["test_status"]=="not_tested"
        if n==76:assert "梦话" in md
        if n==77:assert "唯一" in md and "等" in md
        if n==78:assert "标准化" in md and "原始" in md
        if n==79:assert "盘中" in md and "未" in md
        if n==80:assert "机会成本" in md
    assert len(seen)==35 and "89页" in synthesis and "唯一" in synthesis and "盘中" in synthesis
    assert all(f"lesson_{n:03d}.md" in synthesis for n in range(76,81))
    base,ext66,ext71=graphs
    assert base["source_pdf_sha256_by_volume"]=={str(k):shas[k] for k in (1,2,3)}
    assert len(base["nodes"])==40 and len(ext66["nodes"])==6 and len(ext71["nodes"])==5
    assert ext66["source_pdf_sha256_by_volume"]=={"3":shas[3],"4":shas[4]}
    assert ext71["sources"]["volume4_sha256"]==shas[4]
    assert new["source_pdf_sha256_by_volume"]=={"4":shas[4]}
    old_ids={a["id"] for g in graphs for a in g["nodes"]}
    ids={z["id"] for z in new["nodes"]}
    assert len(ids)==len(new["nodes"])==5 and not ids&old_ids and len(new["edges"])>=9
    for node in new["nodes"]:
        assert node["source"]["volume"]==4
        assert node["source"]["pdf_pages"] and all(143<=p<=231 for p in node["source"]["pdf_pages"])
    for edge in new["edges"]:
        assert edge["from"] in ids and edge["to"] in (ids|old_ids) and edge["from"]!=edge["to"]
        assert edge["certainty"] in ("documented_conceptual_relation","ai_analysis")
    return {"lessons":5,"pages":89,"claims":len(seen),"figures_rendered":11,"actually_inspected":len(EXPECTED_VIEWED),"new_nodes":len(ids),"new_edges":len(new["edges"])}
def spotcheck(index,sha):
    import fitz
    path=ROOT/index["volumes"][3]["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
    examples={143:["梦话"],157:["缺口"],158:["分型"],159:["线段"],174:["线段"],177:["标准化"],187:["分型"],201:["顶分型"]}
    with fitz.open(path) as pdf:
        for page,words in examples.items():
            doc=pdf[page-1].get_text("text",sort=True)
            for word in words:assert word in doc,(page,word)
    return len(examples)
def main():
    index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    inv=json.loads((ROOT/"catalog/chanlun_lessons076_080_source_layers.json").read_text(encoding="utf-8"))
    claims=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(76,81)]
    reports=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(76,81)]
    synthesis=(ROOT/"analyses/books/chanlun/volumes/LESSONS_076_080_SYNTHESIS.md").read_text(encoding="utf-8")
    new=json.loads((ROOT/"knowledge/claims/chanlun_lessons076_080_semantic_dependencies.json").read_text(encoding="utf-8"))
    gs=[json.loads((ROOT/p).read_text(encoding="utf-8")) for p in (
         "knowledge/claims/chanlun_early_core_dependencies.json",
         "knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json",
         "knowledge/claims/chanlun_lessons071_075_semantic_dependencies.json")]
    shas={v["volume"]:hashlib.sha256((ROOT/v["path"]).read_bytes()).hexdigest() for v in index["volumes"][:4]}
    x=validate(index,inv,claims,reports,synthesis,new,gs,shas)
    x["original_pdf_spotcheck"]=spotcheck(index,shas[4])
    print("PASS Chanlun 76–80 original PDF, claims, visuals and graphs "+json.dumps(x))
if __name__=="__main__":main()
