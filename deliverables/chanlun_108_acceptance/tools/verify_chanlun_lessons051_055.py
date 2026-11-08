#!/usr/bin/env python3
"""Lessons 51–55 source, 2009 insert, 35 typed claims and concept graph audit."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TYPES={"SOURCE","EDITORIAL","INTERPRETATION","INFERENCE","HYPOTHESIS","EVIDENCE"}
SEVEN=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
def audit(index,source,evidence,reports,summary,graph,sha):
    v=index["volumes"][2]
    assert source["source_path"]==v["path"]
    assert source["sha256"]==v["sha256"]==sha[3]
    assert len(source["lessons"])==len(evidence)==len(reports)==5
    assert sum(row["page_count"] for row in source["lessons"])==89
    overrides={o["lesson"]:o for o in source["editorial_boundary_overrides"]}
    assert set(overrides)=={53,54}
    assert overrides[53]["pdf_page"]==162 and overrides[53]["date"]=="2009-01-05 12:00:58"
    assert overrides[54]["pdf_page"]==170
    seen=set()
    for n in range(51,56):
        z=source["lessons"][n-51];e=evidence[n-51];doc=reports[n-51]
        k=next(i for i,x in enumerate(v["lessons"]) if x["lesson"]==n)
        pages=list(range(v["lessons"][k]["start_pdf_page"],v["lessons"][k+1]["start_pdf_page"]))
        assert z["lesson"]==e["lesson"]==n and z["volume"]==e["source"]["volume"]==3
        assert z["path"]==e["source"]["path"]==v["path"]
        assert z["sha256"]==e["source"]["sha256"]==sha[3]
        assert z["original_date"]==e["source"]["original_date"]
        assert [p["pdf_page"] for p in z["pages"]]==e["source"]["pdf_pages"]==pages
        assert z["image_pages"]==e["quality"]["image_pages"]
        assert z["native_chars"]==e["quality"]["characters"]
        assert z["page_count"]==e["quality"]["page_count"]
        assert e["source"]["asterisk_appendix_candidate"]==z["first_appendix"]["page"]
        assert e["source"]["provenance_override"]==overrides.get(n)
        assert e["empirical_status"]=="not_run"
        assert all(title in doc for title in SEVEN)
        assert sha[3] in doc and "未" in doc and "图" in doc
        for claim in e["claims"]:
            assert claim["id"] not in seen
            seen.add(claim["id"])
            assert claim["kind"] in TYPES and claim["volume"]==3 and claim["pdf_pages"]
            assert set(claim["pdf_pages"]).issubset(pages)
            if claim["kind"]=="HYPOTHESIS":assert claim.get("test_status")=="not_tested"
            if n==53 and claim["kind"]=="SOURCE":assert set(claim["pdf_pages"]).issubset({161,162})
            if n==53 and claim["kind"]=="EDITORIAL":assert 163 in claim["pdf_pages"] or 164 in claim["pdf_pages"]
        assert len(e["claims"])>=6
        if n==53:assert "2009" in doc and "2007" in doc and "编" in doc
        if n==54:assert "连接" in doc and "结合律" in doc
        if n==55:assert "现金" in doc and "股份" in doc
    assert "89" in summary and "2009" in summary and "第54课" in summary
    assert all(f"lesson_{n:03d}.md" in summary for n in range(51,56))
    assert graph["source_pdf_sha256_by_volume"]=={str(n):sha[n] for n in (1,2,3)}
    nodes={node["id"]:node for node in graph["nodes"]}
    assert len(nodes)==len(graph["nodes"]) and len(nodes)>=29
    for key in ("L51-REFLEXIVITY","L52-OBSERVER-MARKET","L53-THREE-POINT-TYPES","L53-LATER-2009-INSERT","L54-LEGAL-GROUPING","L55-BUY-SELL-ASYMMETRY"):
        assert key in nodes
    for x in nodes.values():
        vol=x["source"]["volume"]
        assert vol in (1,2,3) and x["source"]["pdf_pages"]
        assert all(1<=p<=index["volumes"][vol-1]["pdf_page_count"] for p in x["source"]["pdf_pages"])
    for edge in graph["edges"]:
        assert edge["from"] in nodes and edge["to"] in nodes and edge["from"]!=edge["to"]
        assert edge["certainty"] in ("documented_conceptual_relation","ai_analysis")
    assert any(e["from"]=="L53-LATER-2009-INSERT" and e["to"]=="L53-THREE-POINT-TYPES" for e in graph["edges"])
    return {"lessons":5,"pages":89,"claims":len(seen),"graph_nodes":len(nodes),"graph_edges":len(graph["edges"]),"editorial_overrides":len(overrides)}
def main():
    i=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    s=json.loads((ROOT/"catalog/chanlun_lessons051_055_source_layers.json").read_text(encoding="utf-8"))
    e=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(51,56)]
    r=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(51,56)]
    summary=(ROOT/"analyses/books/chanlun/volumes/LESSONS_051_055_SYNTHESIS.md").read_text(encoding="utf-8")
    g=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    sha={v["volume"]:hashlib.sha256((ROOT/v["path"]).read_bytes()).hexdigest() for v in i["volumes"][:3]}
    print("PASS lessons 51–55 original provenance/claims audit "+json.dumps(audit(i,s,e,r,summary,g,sha)))
if __name__=="__main__":main()
