#!/usr/bin/env python3
"""Audited limited PDF-figure visual review, source roles and truth boundaries.

Metadata from actual SHA-pinned PDF renders. A JPEG thumbnail review does NOT
certify fine-grained graph labels, the origin date of embedded screenshot, or
a complete historical pen/segment parser. Optional --pdf-check verifies PDF
image objects, placements and render SHA with pinned PyMuPDF 1.26.7 in CI.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"catalog/chanlun_f01_source_figure_review_v1.json"
INV=ROOT/"reports/source_inventory/chanlun_20261107_verified.json"
UPSTREAM=ROOT/"catalog/chanlun_f01_segment_termination_reconciliation_v1.json"
ARTICLE=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_F01_FIGURE_EVIDENCE_67_71_78.md"
EXPECTED={3:[388,389,390,391,392],
          4:[71,72,73,74,75,174,175,176,177,232,233,234,241]}
KEYS={"F01-VIS-01","F01-VIS-02","F01-VIS-03","F01-VIS-04","F01-VIS-05"}
PAGE_TAGS={
(3,388):"AUTHOR_AND_LATER_EDITORIAL_ON_SAME_PAGE",
(3,389):"AUTHOR_TWO_BRANCH_DIAGRAM",
(3,390):"EDITORIAL_OBJECTION_AND_LATER_EXAMPLE",
(4,73):"CORRECTED_LAST_DIAGRAM_WARNING",
(4,175):"AUTHOR_ONE_PEN_VS_SEGMENT_DESTRUCTION_AND_EDITOR_COMMENT",
(4,177):"AUTHOR_EXPLICIT_B_BREAK_PREREQUISITE",
(4,232):"AUTHOR_L81_RETROSPECTIVE_CORRECTION",
(4,241):"SEPARATE_LATER_DATED_PEN_REVISION",
}
GAPS={
"LOCAL_L67_NO_GAP_END_VS_L78_BREAK",
"FIRST_REVERSE_PEN_ROLE_L71",
"L67_GAP_CONFIRMATION_VS_L78_REVERSE_SEGMENT",
"SEGMENT_BREAK_TO_FINISHED_LOWER_TYPE"
}
FALSE_KEYS=("original_charts_fine_coordinates_verified",
"original_figure_every_embedded_annotation_resolved",
"source_author_first_publication_authenticated",
"completed_lower_trend_author_certified",
"OB38_or_99_proven","real_market_data_accessed")
RENDER_SCALE=1.12

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def need(x,msg):
    if not x: raise ValueError(msg)

def sha_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda:f.read(1024*1024),b""):
            h.update(part)
    return h.hexdigest()

def verify_header(data):
    need(data.get("schema_version")==1 and
         data.get("id")=="CHANLUN-F01-FIGURE-SHA-PINNED-VISUAL-REVIEW-V1" and
         data.get("scope")=="VISUALLY_REVIEWED_BOUND_SOURCE_PAGES_WITH_LIMITED_THUMBNAIL_LEGIBILITY_NOT_AUTHOR_THEOREM_CERTIFICATION" and
         data.get("source_github_run")==42617362956 and
         data.get("pdf_renderer")=="PyMuPDF 1.26.7" and
         data.get("page_readback_script")=="tools/inspect_chanlun_f01_original_figures_readonly.py",
         "Unapproved source-figure attribution or renderer drift")
    need(all(data.get(x) is False for x in FALSE_KEYS) and
         data.get("backtesting")=="NOT_RUN",
         "Figure contact sheet falsely promoted to author theorem / market")
    need(len(data.get("pages",[]))==18 and
         len(data.get("source_discoveries",[]))==5 and
         {x["id"] for x in data["source_discoveries"]}==KEYS and
         set(data["semantic_bridges_remaining_open"])==GAPS,
         "Original visual review coverage or unresolved four gates erased")
    sources={int(Path(x["path"]).stem.split("卷")[-1]):x for x in load(INV)["volumes"]}
    actual={}
    for p in data["pages"]:
        v,n=p["volume"],p["physical_pdf_page"]
        need(v in EXPECTED and n in EXPECTED[v] and (v,n) not in actual and
             p["original_pdf_sha256"]==sources[v]["sha256"] and
             p["thumbnail_visually_reviewed"] is True and
             p["fine_grained_price_and_member_labels_independently_verified"] is False and
             len(p["render_jpeg_sha256"])==64 and
             type(p["pdf_native_image_objects"]) is int and
             type(p["figure_placements"]) is list and
             len(p["visible_finding"])>80,
             "Original PDF visual page role, hash or coverage mismatch")
        actual[(v,n)]=p
    need(set(actual)=={(v,p) for v,ps in EXPECTED.items() for p in ps},
         "Not every original source figure page inspected")
    need(sum(x["pdf_native_image_objects"]>0 for x in actual.values())==10,
         "Source PDF image object layout changed")
    for key,tag in PAGE_TAGS.items():
        need(actual[key]["source_tag"]==tag,
             "Historical source figure correction/prerequisite lost")
    upstream=load(UPSTREAM)
    need({x["key"] for x in upstream["unresolved_text_scope"]}==GAPS and
         upstream["complete_Rg_frozen"] is False and
         upstream["real_market_backtests"]=="NOT_RUN",
         "Earlier F01 open source/segment obligations suppressed")
    chapter={n:load(ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json") for n in (67,71,78,81)}
    for n,page in ((67,389),(71,73),(78,176),(81,232)):
        v=3 if n==67 else 4
        need(chapter[n]["source"]["sha256"]==sources[v]["sha256"] and
            (v,page) in actual,
            "Figure belongs to an invalid source-card original volume")
    return sources,actual

def verify_pdf(sources,actual):
    import pymupdf as fitz
    import importlib.util
    from pathlib import Path
    script=ROOT/"tools/inspect_chanlun_f01_original_figures_readonly.py"
    spec=importlib.util.spec_from_file_location("figure_render_source",script)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    need(mod.TARGETS==EXPECTED,"Rendered target page set no longer matches verified visual study")
    for v in sorted(EXPECTED):
        path=ROOT/sources[v]["path"]
        need(sha_file(path)==sources[v]["sha256"],"Original PDF changed")
        with fitz.open(path) as pdf:
            need(len(pdf)==sources[v]["page_count"],"Original PDF page count changed")
            for n in EXPECTED[v]:
                page=pdf[n-1];target=actual[(v,n)]
                imgs=page.get_images(full=True)
                coords=[]
                for row in imgs:
                    for b in page.get_image_rects(row[0]):
                        coords.append([round(x,1) for x in b])
                need(len(imgs)==target["pdf_native_image_objects"] and
                     coords[:12]==target["figure_placements"],
                     "Figure image block changed: vol/page "+str((v,n)))
                pix=page.get_pixmap(matrix=fitz.Matrix(RENDER_SCALE,RENDER_SCALE),
                    colorspace=fitz.csRGB,alpha=False)
                digest=hashlib.sha256(pix.tobytes("jpeg",jpg_quality=55)).hexdigest()
                need(digest==target["render_jpeg_sha256"] and
                     [pix.width,pix.height]==target["render_size"],
                     "Rendered figure pixel identity changed: vol/page "+str((v,n)))
    return True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pdf-check",action="store_true")
    args=ap.parse_args()
    data=load(REG);sources,actual=verify_header(data)
    s=ARTICLE.read_text(encoding="utf-8")
    need(len(s)>6200 and all(x in s for x in (
      "第67课","第71课","第78课","第81课","2007年9月19日",
      "第73页","第232页","第177页","线段B",
      "SOURCE","EDITORIAL","视觉","未决","NOT_RUN","四项")),
      "Source figure interpretation document not complete")
    if args.pdf_check:verify_pdf(sources,actual)
    print("F01_FIGURE_SOURCE_VERIFIED="+json.dumps({
      "status":"ACTUALLY_RENDERED_VISUAL_PAGES_REVIEWED_WITH_SOURCE_ROLE_BOUNDARIES",
      "original_pdf_pages":len(actual),
      "original_embedded_figure_pages":sum(x["pdf_native_image_objects"]>0 for x in actual.values()),
      "original_pdf_shas":len({x["original_pdf_sha256"] for x in actual.values()}),
      "lesson71_error_crosschecked_with_lesson81":True,
      "lesson67_later_screenshot_provenance_flagged":True,
      "lesson78_prior_confirmed_B_break_required":True,
      "f01_semantic_bridges_remaining_open":len(GAPS),
      "pixel_and_fine_price_labels_independently_accepted":False,
      "actual_legal_author_segment_parser_proven":False,
      "PDF_figure_identity_check_run":args.pdf_check,
      "real_market":"NOT_RUN"
    },ensure_ascii=False,sort_keys=True))

if __name__=="__main__":main()
