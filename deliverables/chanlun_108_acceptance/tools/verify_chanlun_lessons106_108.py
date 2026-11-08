#!/usr/bin/env python3
"""Source-locked validation of the final 3/108 first-pass studies; no real market backtest."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
LENSES = tuple("第"+x+"重" for x in ("一","二","三","四","五","六","七"))
KINDS = {"SOURCE","EDITORIAL","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
RANGES = [(373,384),(385,394),(395,441)]
DATES = ("2008-07-10 12:12:22","2008-08-19 16:10:39","2008-08-29 09:15:01")
FLAGS = {(106,"AUTHOR_ORIGINAL"),(106,"DIFFERENT_DATED_POST"),(106,"EDITORIAL_GLOSS"),
         (107,"AUTHOR_ORIGINAL"),(107,"DIFFERENT_DATED_POST"),
         (108,"AUTHOR_ORIGINAL"),(108,"DIFFERENT_DATED_POST"),(108,"FIGURE_NOT_NUMERICALLY_VERIFIED")}
def validate(index, source, ev, chapters, synthesis, graph, prior_graphs, hashes):
    v = index["volumes"][4]
    assert source["original_volume"] == 5
    assert source["original_path"] == v["path"]
    assert source["original_sha256"] == v["sha256"] == hashes[5]
    assert source["total_physical_pages"] == 69
    assert len(source["lessons"]) == len(ev) == len(chapters) == 3
    assert len(source["visual"]["rendered_pages"]) == len(source["visual"]["actually_visually_reviewed_pages"]) == 0
    assert source["visual"]["fine_chart_price_labels_verified"] is False
    assert FLAGS.issubset({(x["lesson"], x["kind"]) for x in source["source_role_flags"]})
    ids = set()
    for i, n in enumerate(range(106,109)):
        row, evidence, text = source["lessons"][i], ev[i], chapters[i]
        start, end = RANGES[i]
        pages = list(range(start, end+1))
        assert row["lesson"] == evidence["lesson"] == n
        assert (row["start"], row["end"], row["page_count"]) == (start,end,len(pages))
        assert row["original_date"] == evidence["source"]["original_date"] == DATES[i]
        assert row["sha256"] == evidence["source"]["sha256"] == hashes[5]
        assert row["path"] == evidence["source"]["path"] == v["path"]
        assert [p["page"] for p in row["pages"]] == evidence["source"]["pdf_pages"] == pages
        assert row["title"] == next(l["title"] for l in v["lessons"] if l["lesson"] == n)
        assert start == next(l["start_pdf_page"] for l in v["lessons"] if l["lesson"] == n)
        assert evidence["quality"]["physical_pages"] == len(pages)
        assert evidence["quality"]["native_chars"] == row["native_chars"] == sum(p["chars"] for p in row["pages"])
        assert evidence["quality"]["image_pages"] == row["image_pages"]
        assert not evidence["quality"]["rendered_previews"] and not evidence["quality"]["actually_inspected_pages"]
        assert evidence["quality"]["fine_chart_numeric_verified"] is False
        assert evidence["real_market_backtest"] == "not_run"
        assert len(evidence["claims"]) == 7 and all(x in text for x in LENSES)
        assert hashes[5] in text and "未" in text
        for claim in evidence["claims"]:
            assert claim["id"] not in ids
            ids.add(claim["id"])
            assert claim["kind"] in KINDS and claim["volume"] == 5
            assert claim["pdf_pages"] and set(claim["pdf_pages"]).issubset(pages)
            if claim["kind"] == "HYPOTHESIS":
                assert claim["test_status"] == "not_tested"
    assert len(ids) == 21
    assert all(f"lesson_{n}.md" in synthesis for n in (106,107,108))
    assert "69物理页" in synthesis and "T+1" in synthesis
    assert len(graph["nodes"]) == 3 and len(graph["edges"]) == 7
    assert graph["source_pdf_sha256_by_volume"] == {"5":hashes[5]}
    old_ids = {n["id"] for g in prior_graphs for n in g["nodes"]}
    new_ids = {n["id"] for n in graph["nodes"]}
    assert len(new_ids) == 3 and not old_ids & new_ids
    for node in graph["nodes"]:
        assert node["source"]["volume"] == 5
        assert set(node["source"]["pdf_pages"]).issubset(set(range(373,442)))
    for edge in graph["edges"]:
        assert edge["from"] in new_ids
        assert edge["to"] in new_ids | old_ids
        assert edge["from"] != edge["to"]
        assert edge["certainty"] in ("ai_analysis","documented_conceptual_relation")
    return {"lessons":3,"physical_pages":69,"claims":len(ids),"visually_inspected":0,"nodes":3,"edges":7}
def original_pdf_spots(index, sha):
    import fitz
    p=ROOT/index["volumes"][4]["path"]
    assert hashlib.sha256(p.read_bytes()).hexdigest() == sha
    checks={373:("均线","轮动"),374:("板块","平均"),385:("反弹","30 分钟"),
            386:("第三类买点",),395:("何谓底部",),397:("2952",),399:("2008-08-29",)}
    with fitz.open(p) as pdf:
        assert len(pdf) == 441
        for page, tokens in checks.items():
            text=pdf[page-1].get_text("text",sort=True)
            assert all(tok in text for tok in tokens),(page,tokens)
    return len(checks)
def load():
    index=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text("utf-8"))
    src=json.loads((ROOT/"catalog/chanlun_lessons106_108_source_layers.json").read_text("utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n}.json").read_text("utf-8")) for n in range(106,109)]
    md=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n}.md").read_text("utf-8") for n in range(106,109)]
    syn=(ROOT/"analyses/books/chanlun/volumes/LESSONS_106_108_SYNTHESIS.md").read_text("utf-8")
    graph=json.loads((ROOT/"knowledge/claims/chanlun_lessons106_108_semantic_dependencies.json").read_text("utf-8"))
    prior=[json.loads((ROOT/p).read_text("utf-8")) for p in (
        "knowledge/claims/chanlun_lessons091_095_semantic_dependencies.json",
        "knowledge/claims/chanlun_lessons101_105_semantic_dependencies.json")]
    hashes={v["volume"]:v["sha256"] for v in index["volumes"]}
    return [index,src,ev,md,syn,graph,prior,hashes]
if __name__=="__main__":
    inputs=load()
    result=validate(*inputs)
    result["pdf_spots"]=original_pdf_spots(inputs[0],inputs[1]["original_sha256"])
    print("PASS Chanlun final lessons106-108 immutable source & typed evidence "+json.dumps(result))
