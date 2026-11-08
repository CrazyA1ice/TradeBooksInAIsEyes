#!/usr/bin/env python3
"""Validate Chanlun 81–85 original PDF SHA, bounded page claims, 13 preview scope, version chronology and graph."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KINDS={"SOURCE","EDITORIAL","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
SEVEN=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
VISUAL=[234,237,246,257,269,277,290,294,303,314,327,340,344]
REQUIRED_FLAGS={(81,"AUTHOR_SOURCE_CORRECTION"),(81,"DIFFERENT_DATED_AUTHOR_RULE_REVISION"),(82,"LATER_EDITORIAL_NOTE"),(83,"DATE_PRECISION_LIMIT"),(84,"AUTHOR_TERMINOLOGY_REVISION"),(85,"UNVERIFIED_FIRST_PERSON_AND_LEGAL_CLAIM")}
def validate(index,source,claims,reports,summary,new,older,hashes):
    vol=index["volumes"][3]
    assert source["volume"]==4 and source["source_path"]==vol["path"]
    assert source["source_sha256"]==vol["sha256"]==hashes[4]
    assert source["total_pages"]==114 and len(source["lessons"])==len(claims)==len(reports)==5
    assert sum(x["page_count"] for x in source["lessons"])==114
    assert source["lessons"][0]["start"]==232 and source["lessons"][-1]["end"]==345
    assert source["visual"]["rendered_pages"]==source["visual"]["visually_inspected_pages"]==VISUAL
    assert source["visual"]["precise_chart_numbers_verified"] is False
    assert REQUIRED_FLAGS.issubset({(f["lesson"],f["role"]) for f in source["provenance_flags"]})
    ids=set()
    for n in range(81,86):
        r=source["lessons"][n-81];e=claims[n-81];md=reports[n-81]
        k=next(i for i,x in enumerate(vol["lessons"]) if x["lesson"]==n)
        pages=list(range(vol["lessons"][k]["start_pdf_page"],vol["lessons"][k+1]["start_pdf_page"]))
        expected_date=r["header_date"] or "仅日期2007-09-26，未提供时间"
        assert r["lesson"]==e["lesson"]==n and r["volume"]==e["source"]["volume"]==4
        assert r["source_path"]==e["source"]["path"]==vol["path"]
        assert r["source_sha256"]==e["source"]["sha256"]==hashes[4]
        assert [x["pdf_page"] for x in r["page_info"]]==e["source"]["pdf_pages"]==pages
        assert e["source"]["original_date"]==expected_date
        assert e["source"]["first_star_divider_candidate"]==(r["first_starred_divider"]["pdf_page"] if r["first_starred_divider"] else None)
        assert e["quality"]["page_count"]==r["page_count"] and e["quality"]["native_chars"]==r["total_native_chars"]
        assert e["quality"]["image_pages"]==r["image_pages"]
        assert e["quality"]["rendered_preview_pages"]==r["rendered_previews"]
        assert e["quality"]["visually_inspected_pages"]==[p for p in VISUAL if p in pages]
        assert e["quality"]["fine_price_annotations_verified"] is False and e["real_market_test"]=="not_run"
        assert all(h in md for h in SEVEN)
        assert hashes[4] in md and "未" in md and len(e["claims"])==7
        for claim in e["claims"]:
            assert claim["id"] not in ids
            ids.add(claim["id"])
            assert claim["kind"] in KINDS and claim["volume"]==4
            assert claim["pdf_pages"] and set(claim["pdf_pages"]).issubset(pages)
            if claim["kind"]=="HYPOTHESIS":assert claim.get("test_status")=="not_tested"
        if n==81:assert "修订" in md and "版本" in md and "2007-09-18" in md
        if n==82:assert "中继" in md and "笔" in md
        if n==83:assert "噪声" in md and "线段" in md
        if n==84:assert "自同构" in md and "f1" in md and "f2" in md
        if n==85:assert "法律" in md and "独立" in md
    assert len(ids)==35 and "114页" in summary and "新笔" in summary and "自同构" in summary
    assert all(f"lesson_{n:03d}.md" in summary for n in range(81,86))
    base,ext66,ext71,ext76=older
    assert base["source_pdf_sha256_by_volume"]=={str(k):hashes[k] for k in (1,2,3)}
    assert len(base["nodes"])==40 and len(ext66["nodes"])==6 and len(ext71["nodes"])==5 and len(ext76["nodes"])==5
    assert ext66["source_pdf_sha256_by_volume"]=={"3":hashes[3],"4":hashes[4]}
    assert ext71["sources"]["volume4_sha256"]==hashes[4]
    assert ext76["source_pdf_sha256_by_volume"]=={"4":hashes[4]}
    assert new["source_pdf_sha256_by_volume"]=={"4":hashes[4]}
    previous_ids={p["id"] for graph in older for p in graph["nodes"]}
    fresh_ids={node["id"] for node in new["nodes"]}
    assert len(fresh_ids)==len(new["nodes"])==5 and not fresh_ids.intersection(previous_ids)
    assert len(new["edges"])>=11
    for node in new["nodes"]:
        assert node["source"]["volume"]==4 and node["source"]["pdf_pages"]
        assert all(232<=p<=345 for p in node["source"]["pdf_pages"])
    for edge in new["edges"]:
        assert edge["from"] in fresh_ids and edge["to"] in fresh_ids|previous_ids and edge["from"]!=edge["to"]
        assert edge["certainty"] in ("documented_conceptual_relation","ai_analysis")
    return {"lessons":5,"pages":114,"claims":len(ids),"previews":len(VISUAL),"new_nodes":len(fresh_ids),"new_edges":len(new["edges"])}
def pdf_spotcheck(index,sha):
    import fitz
    path=ROOT/index["volumes"][3]["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
    probes={232:["更正"],234:["0.08"],236:["自相似性"],241:["分型","K 线"],
            266:["分型"],288:["线段","中枢"],299:["自同构性"],301:["f1","f2"],338:["证券法"]}
    with fitz.open(path) as pdf:
        for page,terms in probes.items():
            original=pdf[page-1].get_text("text",sort=True)
            for term in terms:assert term in original,(page,term)
    return len(probes)
def main():
    i=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    source=json.loads((ROOT/"catalog/chanlun_lessons081_085_source_layers.json").read_text(encoding="utf-8"))
    claims=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(81,86)]
    reports=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(81,86)]
    summary=(ROOT/"analyses/books/chanlun/volumes/LESSONS_081_085_SYNTHESIS.md").read_text(encoding="utf-8")
    new=json.loads((ROOT/"knowledge/claims/chanlun_lessons081_085_semantic_dependencies.json").read_text(encoding="utf-8"))
    others=[json.loads((ROOT/p).read_text(encoding="utf-8")) for p in (
       "knowledge/claims/chanlun_early_core_dependencies.json",
       "knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json",
       "knowledge/claims/chanlun_lessons071_075_semantic_dependencies.json",
       "knowledge/claims/chanlun_lessons076_080_semantic_dependencies.json")]
    hashes={v["volume"]:hashlib.sha256((ROOT/v["path"]).read_bytes()).hexdigest() for v in i["volumes"][:4]}
    x=validate(i,source,claims,reports,summary,new,others,hashes)
    x["original_pdf_spots"]=pdf_spotcheck(i,hashes[4])
    print("PASS Chanlun 81–85 source/versions/figures/claims/graph "+json.dumps(x))
if __name__=="__main__":main()
