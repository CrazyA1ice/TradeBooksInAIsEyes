#!/usr/bin/env python3
"""Check deep 108-lesson second-pass argument provenance and proof boundaries.

Designed for SOURCE-card fidelity, not to prove original authorship or financial
claims. The deep analysis is interpretive; this only checks that every cited
claim is a real existing original-source-card entry, with consistent PDF origin,
and no machine claim of complete formal proof or empirical validation.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"catalog/chanlun_theory_argument_links_v1.json"
ESSAY=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_DEEP_THEORY_SECOND_PASS.md"
SYNTHESIS=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_INTEGRATED_STUDY.md"
ATLAS=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_108_SOURCE_ATLAS.md"
INDEX=ROOT/"catalog/chanlun_lesson_index.json"
PERMITTED={"NON_IMPLICATION","CONDITIONAL_DEDUCTION","UNRESOLVED"}
OPEN_LIMITS=("real_market_accessed","original_figures_all_reviewed",
             "original_authorship_all_verified","rule_versions_frozen")

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def require(ok, message):
    if not ok:
        raise ValueError(message)

def verify_document():
    essay=ESSAY.read_text(encoding="utf-8")
    require(len(essay)>=14000,"Deep theory second-pass report is too thin")
    for phrase in ("三类买卖点","背驰","自同构","中枢延伸","线段",
                   "OB38-UNIQUE","OB99-EXIST","NOT_RUN","作者","AI研究"):
        require(phrase in essay,"Missing theory research boundary: "+phrase)
    for p in ("中枢","背驰","分解唯一性","自同构","第108课"):
        require(p in essay,"Missing one of the core 108-lesson theory axes")
    require(SYNTHESIS.is_file() and ATLAS.is_file(),
            "Deep research no longer grounded in continuous 108-lesson baseline")
    require("108课" in SYNTHESIS.read_text(encoding="utf-8"),
            "Previous unified study altered")
    require("SOURCE" in ATLAS.read_text(encoding="utf-8"),
            "Whole-book original-source atlas missing")
    require("已证明缠论普遍盈利" not in essay and
            "数学上全部严格证明" not in essay,
            "Unsupported full-market/full-theorem assertion")
    return essay

def verify():
    index=load(INDEX)
    by_lesson={}
    for vol in index["volumes"]:
        for item in vol["lessons"]:
            by_lesson[item["lesson"]]=vol
    require(set(by_lesson)==set(range(1,109)),
            "Complete five-volume 108-source index is unavailable")
    essay=verify_document()
    doc=load(LEDGER)
    require(doc["schema_version"]==1 and
            doc["applies_to"]==ESSAY.name and
            doc["source_status"]==
            "SOURCE_CARD_ANCHORS_WITH_PARTIAL_ORIGINAL_PDF_NATIVE_VERIFICATION_NOT_FULL_AUTHOR_PROOF",
            "Source-role or second-pass target altered")
    require(doc["completion_state"]==
            "DEEP_THEORY_SECOND_PASS_PARTIAL_NOT_THEOREM_OR_FULL_FIGURE_CERTIFICATION",
            "Second pass falsely upgraded to complete author/theorem proof")
    require(all(doc.get(k) is False for k in OPEN_LIMITS),
            "Unsupported proof/market/source provenance promoted")
    rows=doc["arguments"]
    require(isinstance(rows,list) and len(rows)==16 and
            [x["id"] for x in rows]==[f"D{i:02d}" for i in range(1,17)],
            "Exactly 16 fixed cross-lesson research arguments required")
    refs=set()
    volumes=set()
    counts={}
    for item in rows:
        require(item["reasoning_role"] in PERMITTED and
                item["formal_proof_completed"] is False and
                item["market_empirical_test"]=="NOT_RUN" and
                isinstance(item["open_premises"],list) and
                len(item["open_premises"])>=2 and
                isinstance(item["research_conclusion"],str) and
                len(item["research_conclusion"])>=20,
                "Cross-lesson reasoning was falsely upgraded or made vacuous")
        claims=item.get("source_claims")
        require(isinstance(claims,list) and len(claims)>=2,
                "Each theory argument needs at least two original SOURCE references")
        require(len({(c["lesson"],c["claim_id"]) for c in claims})==len(claims),
                "Duplicate author card in a single theory proposition")
        for row in claims:
            n=row["lesson"]
            require(type(n) is int and n in by_lesson,
                    "Theory claim referenced nonexistent original lesson")
            cards=load(ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json")
            vol=by_lesson[n]
            require(cards["source"]["path"]==vol["path"] and
                    cards["source"]["sha256"]==vol["sha256"],
                    "Source-card original PDF SHA does not match original volume index")
            matched=[x for x in cards["claims"] if x["id"]==row["claim_id"]]
            require(len(matched)==1 and matched[0]["kind"]=="SOURCE",
                    "Theory claim must refer to an existing SOURCE-card claim, not AI inference")
            pages=matched[0]["pdf_pages"]
            require(isinstance(pages,list) and len(pages)>0 and
                    all(isinstance(k,int) and 1<=k<=vol["pdf_page_count"] for k in pages),
                    "Theory SOURCE has invalid original physical PDF page anchor")
            refs.add((n,row["claim_id"]))
            volumes.add(vol["volume"])
            require(f"chanlun_lesson{n:03d}.json" in essay,
                    f"Essay missing a direct evidence link to lesson {n}")
        counts[item["reasoning_role"]]=counts.get(item["reasoning_role"],0)+1
    require(len(refs)>=45 and len(volumes)==5,
            "Cross-lesson source coverage too narrow")
    require(all(counts.get(s,0)>0 for s in PERMITTED),
            "Must retain conditional, non-implication and open-proof reasoning")
    return {"status":"DEEP_THEORY_SOURCE_LINKS_PASS_NOT_COMPLETE_FORMAL_PROOF",
            "arguments":len(rows),"distinct_source_claims":len(refs),
            "original_volumes":len(volumes),"conclusions_by_type":counts,
            "deep_manuscript_characters":len(essay),
            "original_pdf_image_reviewed":False,
            "all_original_author_roles_proven":False,
            "real_market_experiment":"NOT_RUN"}

if __name__=="__main__":
    print(json.dumps(verify(),ensure_ascii=False,sort_keys=True))
