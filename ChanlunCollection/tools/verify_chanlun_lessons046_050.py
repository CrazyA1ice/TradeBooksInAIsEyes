#!/usr/bin/env python3
"""Audit lessons 46–50 original volume-3 PDF, typed claims and versioned concept map."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TYPES={"SOURCE","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
LENSES=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
def audit(index,inventory,claims,reports,summary,graph,sha_by_volume):
    v=index["volumes"][2]
    assert inventory["source_path"]==v["path"]
    assert inventory["source_sha256"]==sha_by_volume[3]==v["sha256"]
    assert len(inventory["lessons"])==len(claims)==len(reports)==5
    assert sum(x["page_count"] for x in inventory["lessons"])==68
    seen=set()
    for n in range(46,51):
        i=n-46;src=inventory["lessons"][i];ev=claims[i];doc=reports[i]
        k=next(k for k,x in enumerate(v["lessons"]) if x["lesson"]==n)
        pages=list(range(v["lessons"][k]["start_pdf_page"],v["lessons"][k+1]["start_pdf_page"]))
        assert src["lesson"]==ev["source"]["lesson_number"]==n
        assert src["volume"]==ev["source"]["volume"]==3
        assert src["path"]==ev["source"]["path"]==v["path"]
        assert src["sha256"]==ev["source"]["sha256"]==sha_by_volume[3]
        assert src["date"]==ev["source"]["original_date"]
        assert [p["pdf_page"] for p in src["pages"]]==ev["source"]["pdf_pages"]==pages
        assert ev["source"]["first_appendix_candidate"]==src["first_appendix"]["page"]
        assert src["native_chars"]==ev["quality"]["native_chars"]==sum(p["native_chars"] for p in src["pages"])
        assert ev["quality"]["page_count"]==len(pages)
        assert ev["quality"]["image_pages"]==[p["pdf_page"] for p in src["pages"] if p["image_count"]]
        assert ev["empirical_status"]=="not_run"
        assert all(h in doc for h in LENSES)
        assert sha_by_volume[3] in doc and "图" in doc and ("未" in doc or "尚" in doc)
        assert len(ev["claims"])>=7
        for claim in ev["claims"]:
            assert claim["kind"] in TYPES and claim["volume"]==3
            assert claim["pdf_pages"] and set(claim["pdf_pages"]).issubset(set(pages))
            assert claim["id"] not in seen
            seen.add(claim["id"])
            if claim["kind"]=="HYPOTHESIS":assert claim.get("test_status")=="not_tested"
        if n==46: assert "30分钟" in doc and "全天" in doc
        if n==48: assert "零成本" in doc and "风险" in doc
        if n==49: assert "最大" in doc and "目标" in doc
        if n==50: assert "MACD" in doc and "模拟" in doc
    assert "68页" in summary and "最大" in summary and "MACD" in summary
    assert all(f"lesson_{n:03d}.md" in summary for n in range(46,51))
    expected={str(n):sha_by_volume[n] for n in (1,2,3)}
    assert graph["source_pdf_sha256_by_volume"]==expected
    nodes={x["id"]:x for x in graph["nodes"]}
    assert len(nodes)==len(graph["nodes"]) and len(nodes)>=23
    new={"L46-DAY-ASOF","L47-CASE-EXECUTION","L48-COST-RISK","L49-PROFIT-OPTIMUM","L50-MACD-PROXY"}
    assert new.issubset(nodes)
    for x in nodes.values():
        volume=x["source"]["volume"]
        assert volume in (1,2,3) and x["source"]["pdf_pages"]
        assert all(1<=p<=index["volumes"][volume-1]["pdf_page_count"] for p in x["source"]["pdf_pages"])
    for edge in graph["edges"]:
        assert edge["from"] in nodes and edge["to"] in nodes and edge["from"]!=edge["to"]
        assert edge["certainty"] in ("documented_conceptual_relation","ai_analysis")
    return {"lessons":5,"pages":68,"claims":len(seen),"volume":3,"graph_nodes":len(nodes),"graph_edges":len(graph["edges"])}
def main():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    inv=json.loads((ROOT/"catalog/chanlun_lessons046_050_source_layers.json").read_text(encoding="utf-8"))
    ev=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(46,51)]
    r=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(46,51)]
    s=(ROOT/"analyses/books/chanlun/volumes/LESSONS_046_050_SYNTHESIS.md").read_text(encoding="utf-8")
    graph=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    hashes={v["volume"]:hashlib.sha256((ROOT/v["path"]).read_bytes()).hexdigest() for v in idx["volumes"][:3]}
    print("PASS source and concept audit lessons46-50 "+json.dumps(audit(idx,inv,ev,r,s,graph,hashes)))
if __name__=="__main__":main()
