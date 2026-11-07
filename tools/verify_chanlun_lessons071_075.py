#!/usr/bin/env python3
"""Check original PDF SHA, pages, actual-vs-rendered visual scope, 35 typed claims and new graph."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KINDS={"SOURCE","INTERPRETATION","INFERENCE","HYPOTHESIS","EDITORIAL","EVIDENCE"}
SEVEN=("第一重","第二重","第三重","第四重","第五重","第六重","第七重")
EXPECTED_VISUAL=[73,74,86,104,114,124]
def verify(index,src,evidence,reports,synthesis,new_graph,base_graph,old_ext,shas):
    vol=index["volumes"][3]
    assert src["volume"]==4 and src["original_pdf_path"]==vol["path"]
    assert src["sha256"]==vol["sha256"]==shas[4]
    assert src["total_pages"]==72 and len(src["lessons"])==len(evidence)==len(reports)==5
    assert sum(l["page_count"] for l in src["lessons"])==72
    assert src["visual"]["actually_visually_inspected_pages"]==EXPECTED_VISUAL
    assert src["visual"]["fine_price_labels_verified"] is False
    assert len(src["visual"]["rendered_pages"])==10
    assert set(EXPECTED_VISUAL).issubset(src["visual"]["rendered_pages"])
    flags={(f["lesson"],f["pdf_page"],f["kind"]) for f in src["provenance_flags"]}
    assert (72,85,"editorial_interruption") in flags
    assert (72,88,"distinct_dated_market_commentary") in flags
    assert (73,100,"separate_dated_market_commentary") in flags
    assert (74,113,"editorial_risk_classification_disagreement") in flags
    assert (75,123,"dated_followup") in flags
    all_ids=set()
    for n in range(71,76):
        x=src["lessons"][n-71];e=evidence[n-71];report=reports[n-71]
        ix=next(k for k,l in enumerate(vol["lessons"]) if l["lesson"]==n)
        pages=list(range(vol["lessons"][ix]["start_pdf_page"],vol["lessons"][ix+1]["start_pdf_page"]))
        assert x["lesson"]==e["lesson"]==n
        assert x["sha256"]==e["source"]["sha256"]==shas[4]
        assert x["pdf_path"]==e["source"]["path"]==vol["path"]
        assert x["original_date"]==e["source"]["original_date"]
        assert [p["pdf_page"] for p in x["pages"]]==e["source"]["pdf_pages"]==pages
        assert x["page_count"]==e["quality"]["physical_pages"]
        assert x["native_chars"]==e["quality"]["source_native_chars"]
        assert x["image_pages"]==e["quality"]["image_pages"]
        assert x["preview_pages"]==e["quality"]["rendered_preview_pages"]
        assert e["quality"]["actually_visually_inspected_pages"]==[p for p in EXPECTED_VISUAL if p in pages]
        assert e["quality"]["fine_price_labels_verified"] is False and e["empirical_status"]=="not_run"
        assert e["source"]["first_starred_appendix_candidate"]==(x["first_divider"]["pdf_page"] if x["first_divider"] else None)
        assert all(h in report for h in SEVEN)
        assert shas[4] in report and "未" in report and "图" in report
        assert len(e["claims"])==7
        for c in e["claims"]:
            assert c["id"] not in all_ids
            all_ids.add(c["id"])
            assert c["kind"] in KINDS and c["volume"]==4
            assert c["pdf_pages"] and set(c["pdf_pages"]).issubset(pages)
            if c["kind"]=="HYPOTHESIS":assert c.get("test_status")=="not_tested"
        if n==71:assert "同一" in report and "辅助" in report
        if n==72:assert "形态学" in report and "动力学" in report
        if n==73:assert "中枢上移" in report and "中枢震荡" in report
        if n==74:assert "系统性" in report and "娇注" in report
        if n==75:assert "梦话" in report and "未" in report
    assert len(all_ids)==35 and "72页" in synthesis and "特征序列" in synthesis and "政策" in synthesis
    assert all(f"lesson_{n:03d}.md" in synthesis for n in range(71,76))
    assert base_graph["source_pdf_sha256_by_volume"]=={str(i):shas[i] for i in (1,2,3)}
    assert len(base_graph["nodes"])==40 and len(old_ext["nodes"])==6
    assert old_ext["source_pdf_sha256_by_volume"]=={"3":shas[3],"4":shas[4]}
    assert new_graph["sources"]["volume4_sha256"]==shas[4]
    old_ids={z["id"] for z in base_graph["nodes"]}|{z["id"] for z in old_ext["nodes"]}
    new_ids={z["id"] for z in new_graph["nodes"]}
    assert len(new_ids)==len(new_graph["nodes"])==5 and not new_ids.intersection(old_ids)
    assert len(new_graph["edges"])>=9
    for node in new_graph["nodes"]:
        assert node["source"]["volume"]==4
        assert node["source"]["pdf_pages"] and all(71<=p<=142 for p in node["source"]["pdf_pages"])
    for e in new_graph["edges"]:
        assert e["from"] in new_ids and e["to"] in old_ids|new_ids and e["from"]!=e["to"]
        assert e["certainty"] in ("documented_conceptual_relation","ai_analysis")
    return {"lessons":5,"pages":72,"typed_claims":35,"rendered_pages":10,"visually_inspected":6,
            "extension_nodes":len(new_ids),"extension_edges":len(new_graph["edges"])}
def pdf_spot(index,sha):
    import fitz
    p=ROOT/index["volumes"][3]["path"]
    assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
    probes={71:["特征序列","包含"],72:["线段","缺口"],85:["娇注","形态学"],
            87:["特征序列"],98:["中枢上移","中枢震荡"],111:["政策性风险"],
            113:["娇注"],121:["梦话"]}
    with fitz.open(p) as pdf:
        for page,words in probes.items():
            raw=pdf[page-1].get_text("text",sort=True)
            for term in words:assert term in raw,(page,term)
    return len(probes)
def main():
    i=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    s=json.loads((ROOT/"catalog/chanlun_lessons071_075_source_layers.json").read_text(encoding="utf-8"))
    e=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(71,76)]
    r=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(71,76)]
    text=(ROOT/"analyses/books/chanlun/volumes/LESSONS_071_075_SYNTHESIS.md").read_text(encoding="utf-8")
    g=json.loads((ROOT/"knowledge/claims/chanlun_lessons071_075_semantic_dependencies.json").read_text(encoding="utf-8"))
    base=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    old=json.loads((ROOT/"knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json").read_text(encoding="utf-8"))
    shas={v["volume"]:hashlib.sha256((ROOT/v["path"]).read_bytes()).hexdigest() for v in i["volumes"][:4]}
    x=verify(i,s,e,r,text,g,base,old,shas)
    x["original_pdf_pages_spot_checked"]=pdf_spot(i,shas[4])
    print("PASS Chanlun 71–75 original PDF/source/version audits "+json.dumps(x))
if __name__=="__main__":main()
