#!/usr/bin/env python3
"""Verify 61–65 source dates, images, typed evidence and graph; includes original PDF spot checks."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KINDS={"SOURCE","INTERPRETATION","INFERENCE","HYPOTHESIS","EDITORIAL","EVIDENCE"}
SEVEN=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
def validate(idx,source,evidence,reports,overview,graph,hashes):
    volume=idx["volumes"][2]
    assert source["source_path"]==volume["path"] and source["source_sha256"]==volume["sha256"]==hashes[3]
    assert source["volume"]==3 and source["total_physical_pdf_pages"]==96
    assert len(source["lessons"])==len(evidence)==len(reports)==5
    assert sum(x["page_count"] for x in source["lessons"])==96
    assert source["visual_preview"]["pages"]==[280,292,294,304,310,349,352,355]
    assert source["visual_preview"]["fine_price_annotations_verified"] is False
    flags={(x["lesson"],x["kind"]) for x in source["provenance_flags"]}
    assert (61,"mixed_chronology") in flags and (62,"version_note") in flags
    assert (64,"later_or_other_posts") in flags and (65,"after_asterisk") in flags
    seen=set()
    for n in range(61,66):
        s=source["lessons"][n-61];e=evidence[n-61];md=reports[n-61]
        k=next(j for j,x in enumerate(volume["lessons"]) if x["lesson"]==n)
        pages=list(range(volume["lessons"][k]["start_pdf_page"],volume["lessons"][k+1]["start_pdf_page"]))
        assert s["lesson"]==e["lesson"]==n and s["volume"]==e["source"]["volume"]==3
        assert e["source"]["path"]==volume["path"] and e["source"]["sha256"]==hashes[3]
        assert e["source"]["pdf_pages"]==[p["pdf_page"] for p in s["pages"]]==pages
        assert e["source"]["visible_first_date"]==s["original_date"]
        assert e["source"]["first_appendix_separator"]==(s["first_divider"]["pdf_page"] if s["first_divider"] else None)
        assert e["quality"]["page_count"]==s["page_count"]
        assert e["quality"]["native_chars"]==s["total_native_chars"]
        assert e["quality"]["image_pages"]==s["image_pages"]
        assert e["quality"]["visually_previewed_pages"]==[p for p in source["visual_preview"]["pages"] if p in pages]
        assert e["quality"]["numeric_figures_verified"] is False and e["empirical_status"]=="not_run"
        assert all(h in md for h in SEVEN) and hashes[3] in md
        assert "图" in md and "未" in md and len(e["claims"])>=6
        for claim in e["claims"]:
            assert claim["id"] not in seen
            seen.add(claim["id"])
            assert claim["kind"] in KINDS and claim["volume"]==3 and claim["pdf_pages"]
            assert set(claim["pdf_pages"]).issubset(pages)
            if claim["kind"]=="HYPOTHESIS":assert claim.get("test_status")=="not_tested"
        if n==61:assert "2010" in md and "2007" in md
        if n==62:assert "新笔定义" in md and "版本" in md
        if n==64:assert "0.5" in md and "传递" in md
        if n==65:assert "不" in md and "传递" in md and "顺序" in md
    assert "96页" in overview and "2010" in overview and "非传递" in overview
    assert all(f"lesson_{n:03d}.md" in overview for n in range(61,66))
    assert graph["source_pdf_sha256_by_volume"]=={str(k):hashes[k] for k in (1,2,3)}
    nodes={x["id"]:x for x in graph["nodes"]}
    assert len(nodes)==len(graph["nodes"]) and len(nodes)>=40
    for k in ("L61-DATE-STRATA","L62-FRACTAL-PEN","L62-REVISED-PEN","L63-OBSERVATION-SCALE","L64-TOLERANCE","L65-ORDERED-CONTAINMENT"):assert k in nodes
    for node in nodes.values():
        v=node["source"]["volume"]
        assert v in (1,2,3) and node["source"]["pdf_pages"]
        assert all(1<=p<=idx["volumes"][v-1]["pdf_page_count"] for p in node["source"]["pdf_pages"])
    for edge in graph["edges"]:
        assert edge["from"] in nodes and edge["to"] in nodes and edge["from"]!=edge["to"]
        assert edge["certainty"] in ("documented_conceptual_relation","ai_analysis")
    return {"lessons":5,"pages":96,"claims":len(seen),"visually_previewed":len(source["visual_preview"]["pages"]),"graph_nodes":len(nodes),"graph_edges":len(graph["edges"])}
def pdf_spot_check(path,sha):
    import fitz
    assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
    with fitz.open(path) as pdf:
        probes={
          278:("2010-08-13",),
          279:("2007-06-22",),
          292:("顶分型","底分型"),
          295:("新笔定义",),
          311:("0.5","取整"),
          347:("不符合传递律","包含关系")
        }
        for page,words in probes.items():
            raw=pdf[page-1].get_text("text",sort=True)
            for word in words:assert word in raw,(page,word)
    return len(probes)
def main():
    i=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    s=json.loads((ROOT/"catalog/chanlun_lessons061_065_source_layers.json").read_text(encoding="utf-8"))
    e=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(61,66)]
    r=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(61,66)]
    o=(ROOT/"analyses/books/chanlun/volumes/LESSONS_061_065_SYNTHESIS.md").read_text(encoding="utf-8")
    g=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    hashes={v["volume"]:hashlib.sha256((ROOT/v["path"]).read_bytes()).hexdigest() for v in i["volumes"][:3]}
    summary=validate(i,s,e,r,o,g,hashes)
    summary["pdf_original_pages_spotchecked"]=pdf_spot_check(ROOT/i["volumes"][2]["path"],hashes[3])
    print("PASS source, citations and chronology of Chanlun 61–65 "+json.dumps(summary))
if __name__=="__main__":main()
