#!/usr/bin/env python3
"""Validate lessons 41–45 dual-volume provenance, typed claims and extended concept graph."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KINDS={"SOURCE","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
SEVEN=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
def audit(index,scan,evidence,reports,summary,graph,hashes):
    vols={v["volume"]:v for v in index["volumes"]}
    assert scan["original_source_sha_by_volume"]=={str(n):hashes[n] for n in (2,3)}
    assert len(scan["lessons"])==len(evidence)==len(reports)==5
    assert sum(s["page_count"] for s in scan["lessons"])==75
    ids=set()
    for n in range(41,46):
        j=n-41;s=scan["lessons"][j];ev=evidence[j];md=reports[j]
        v=vols[s["volume"]];k=next(i for i,r in enumerate(v["lessons"]) if r["lesson"]==n)
        end=v["lessons"][k+1]["start_pdf_page"] if k+1<len(v["lessons"]) else v["pdf_page_count"]+1
        pages=list(range(v["lessons"][k]["start_pdf_page"],end))
        assert s["lesson"]==ev["source"]["lesson_number"]==n
        assert s["volume"]==ev["source"]["volume"]==(2 if n<43 else 3)
        assert s["pdf_path"]==ev["source"]["path"]==v["path"]
        assert s["sha256"]==ev["source"]["sha256"]==hashes[s["volume"]]
        assert [p["pdf_page"] for p in s["pages"]]==ev["source"]["pdf_pages"]==pages
        assert s["page_count"]==ev["quality"]["page_count"]
        assert s["total_native_chars"]==ev["quality"]["native_text_chars"]
        assert s["image_pages"]==ev["quality"]["image_pages"]
        assert ev["source"]["appendix_boundary_candidate"]==(s["first_appendix"]["pdf_page"] if s["first_appendix"] else None)
        assert s["original_date"]==ev["source"]["original_date"]
        assert ev["empirical_status"]=="not_run"
        assert all(h in md for h in SEVEN)
        assert hashes[s["volume"]] in md and "未" in md and "图" in md
        assert len(ev["claims"])>=6
        for c in ev["claims"]:
            assert c["kind"] in KINDS and c["volume"]==s["volume"]
            assert c["pdf_pages"] and set(c["pdf_pages"]).issubset(set(pages))
            assert c["id"] not in ids
            ids.add(c["id"])
            if c["kind"]=="HYPOTHESIS":assert c.get("test_status")=="not_tested"
        if n==43:assert "级别" in md and "盘整" in md
        if n==44:assert "必要条件" in md and "充分条件" in md
        if n==45:assert "持股" in md and "持币" in md and "等待" in md
    assert "75" in summary and "必要条件" in summary and "等待" in summary
    assert all(f"lesson_{n:03d}.md" in summary for n in range(41,46))
    assert graph["source_pdf_sha256_by_volume"]=={str(n):hashes[n] for n in (1,2,3)}
    nodes={x["id"]:x for x in graph["nodes"]}
    assert len(nodes)==len(graph["nodes"]) and len(nodes)>=18
    for key in ("L41-LEVEL-DISCIPLINE","L42-DECISION-REVIEW","L43-MULTISCALE-REVERSAL","L44-NECESSARY-NOT-SUFFICIENT","L45-HOLD-WAIT"):
        assert key in nodes
    for x in nodes.values():
        v=x["source"]["volume"]
        assert v in (1,2,3) and all(1<=p<=vols[v]["pdf_page_count"] for p in x["source"]["pdf_pages"])
    for edge in graph["edges"]:
        assert edge["from"] in nodes and edge["to"] in nodes and edge["from"]!=edge["to"]
        assert edge["certainty"] in ("documented_conceptual_relation","ai_analysis")
    assert any(e["to"]=="L44-NECESSARY-NOT-SUFFICIENT" for e in graph["edges"])
    return {"lessons":5,"pages":75,"claims":len(ids),"volumes":[2,3],"graph_nodes":len(nodes),"graph_edges":len(graph["edges"])}
def main():
    i=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    s=json.loads((ROOT/"catalog/chanlun_lessons041_045_source_layers.json").read_text(encoding="utf-8"))
    e=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(41,46)]
    m=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(41,46)]
    o=(ROOT/"analyses/books/chanlun/volumes/LESSONS_041_045_SYNTHESIS.md").read_text(encoding="utf-8")
    g=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    hashes={v["volume"]:hashlib.sha256((ROOT/v["path"]).read_bytes()).hexdigest() for v in i["volumes"][:3]}
    print("PASS lessons41–45 dual-volume source and evidence audit "+json.dumps(audit(i,s,e,m,o,g,hashes)))
if __name__=="__main__":main()
