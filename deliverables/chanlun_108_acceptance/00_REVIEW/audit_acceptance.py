#!/usr/bin/env python3
"""Offline acceptance audit of the de-duplicated Chanlun 108-lesson review index.

This script verifies files, provenance links and prospective case inventories.
It deliberately DOES NOT run the old market/pen/strategy experimental tools,
test trading hypotheses, or declare that illustrations or claims are proven.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

BUNDLE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]   # canonical repo root
READ = BUNDLE / "00_REVIEW"
CASES = BUNDLE / "03_formal_cases"
VOLUMES = ROOT / "ChineseBooks" / "缠论"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def load(relative_path):
    home = BUNDLE if relative_path.startswith(("00_REVIEW/", "03_formal_cases/")) else ROOT
    return json.loads((home / relative_path).read_text(encoding="utf-8"))


def git_blob_hash(path):
    size = path.stat().st_size
    hasher = hashlib.sha1()
    hasher.update(("blob " + str(size) + "\0").encode())
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def sha256_file(path):
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify():
    errors = []
    def ok(cond, message):
        if not cond:
            errors.append(message)

    manifest = load("00_REVIEW/FILE_MANIFEST.json")
    canonical = manifest["canonical_files"]
    ok(len(canonical) == manifest["canonical_file_count"] == 625,
       "Expected 625 canonical referenced source files")
    ok(len(set(row["path"] for row in canonical)) == len(canonical),
       "Duplicate canonical manifest paths")
    ok(sum(row["bytes"] for row in canonical) == manifest["canonical_bytes"],
       "Canonical source byte total mismatch")
    ok(manifest["file_index_kind"]=="canonical_reference_not_duplicate_file",
       "Manifest must describe references, not second copies")
    for entry in canonical:
        relative = Path(entry["path"])
        ok(not relative.is_absolute() and ".." not in relative.parts,
           "Invalid path in file manifest: " + entry["path"])
        path = ROOT / relative
        ok(not (BUNDLE / relative).exists(), "Duplicated source file found in acceptance: " + entry["path"])
        if not path.is_file():
            errors.append("File missing: " + entry["path"])
            continue
        ok(path.stat().st_size == entry["bytes"], "Wrong size: " + entry["path"])
        ok(SHA_RE.fullmatch(entry["git_blob_sha1"]) is not None,
           "Malformed blob identity: " + entry["path"])
        ok(git_blob_hash(path) == entry["git_blob_sha1"],
           "Git blob content mismatch: " + entry["path"])

    for entry in manifest["case_files"]:
        path = BUNDLE / entry["path"]
        if not path.is_file():
            errors.append("Formal-case file missing: " + entry["path"])
            continue
        ok(path.stat().st_size == entry["bytes"], "Formal-case size changed: " + entry["path"])
        ok(git_blob_hash(path) == entry["git_blob_sha1"],
           "Formal-case source SHA changed: " + entry["path"])

    index = load("catalog/chanlun_lesson_index.json")
    lessons = {}
    for vol in index["volumes"]:
        path = ROOT / vol["path"]
        ok(path.is_file(), "Source PDF absent: " + vol["path"])
        if path.is_file():
            ok(sha256_file(path) == vol["sha256"], "Original PDF SHA256 changed: " + vol["path"])
        for lesson in vol["lessons"]:
            number = lesson["lesson"]
            ok(number not in lessons, "Duplicate source lesson number: " + str(number))
            lessons[number] = (vol, lesson)
    ok(set(lessons) == set(range(1,109)), "Expected exactly continuous lessons 1–108")

    # Extract directly from canonical evidence. Intermediate hypothesis batches
    # were intentionally deleted: they duplicate these authoritative records.
    expected_claims = {}
    for n in range(1,109):
        evidence="knowledge/evidence/chanlun_lesson%03d.json" % n
        analysis="analyses/books/chanlun/chapters/lesson_%03d.md" % n
        ok((ROOT / analysis).is_file(), "Missing canonical chapter analysis %s" % n)
        source=load(evidence)
        tagged=[c for c in source["claims"]
                if "hypothesis" in str(c.get("kind",c.get("type",""))).lower()]
        for h in tagged:
            key=(n,h["id"])
            ok(key not in expected_claims,"Duplicate source claim: "+h["id"])
            expected_claims[key]={
                "statement":h.get("summary") or h.get("statement") or h.get("claim"),
                "pdf_pages":h.get("pdf_pages") or h.get("pages") or []}
    cases=load("03_formal_cases/ALL_110_PROSPECTIVE_FORMAL_CASES.json")
    cs=cases["cases"]
    ok(len(cs)==cases["source_hypothesis_count"]==110,"110 claim cases required")
    ok(len(set(v["case_id"] for v in cs))==110,"Repeated formal-case identifiers")
    ok(len(expected_claims)==110,"Expected 110 unique source claims")
    ok({(v["lesson"],v["claim_id"]) for v in cs}==set(expected_claims),
       "One-to-one mapping from formal cases to source hypotheses broken")
    for c in cs:
        key=(c["lesson"],c["claim_id"])
        if key not in expected_claims:
            continue
        ok(c["original_hypothesis"]==expected_claims[key]["statement"],
           "Formal-case statement does not match evidence " + c["case_id"])
        ok(c["claim_pages"]==expected_claims[key]["pdf_pages"],
           "Formal-case page mismatch " + c["case_id"])
        ok(c["volume_source_sha256"]==lessons[c["lesson"]][0]["sha256"],
           "Volume SHA link mismatched for " + c["case_id"])
        ok(c["experiment_status"]=="NOT_RUN" and c["result"] is None,
           "Must not claim performed empirical result: " + c["case_id"])
        ok(c["pre_registration_status"]=="NOT_FROZEN_NEEDS_OPERATIONAL_DEFINITION",
           "Missing study-registration boundary: "+c["case_id"])
    curated=load("03_formal_cases/36_CROSS_LESSON_FORMAL_EXAMPLES.json")
    ex=curated["examples"]
    ok(len(ex)==curated["example_count"]==36,"36 independently described cross-lesson examples required")
    ok(len({x["example_id"] for x in ex})==36,"Repeated curated case id")
    for x in ex:
        ok(bool(x["lessons"]) and all(n in lessons for n in x["lessons"]),
           "Curated case has lesson reference outside 1–108")
        ok(x["result_status"]=="NOT_RUN" and x["empirical_result"] is None,
           "Curated case illegally claims empirical outcome: "+x["example_id"])
        ok(all(x.get(k) for k in ("formal_example","required_inputs",
                                 "observables_or_metrics","negative_control_and_bias_guard")),
           "Curated case missing a prospective validation protocol: "+x["example_id"])
    ok((BUNDLE/"00_REVIEW/LESSON_ACCEPTANCE_MATRIX.md").is_file(),
       "Missing 108-lesson acceptance checklist")
    ok((BUNDLE/"00_REVIEW/FINAL_BOOK_SYNTHESIS.md").is_file(),
       "Missing whole-book synthesis")
    ok((BUNDLE/"03_formal_cases/README.md").is_file(),
       "Missing formal cases reading guide")
    ok((ROOT/"docs/BOOK_RESEARCH_WORKFLOW.md").is_file(), "Missing next-book reusable workflow")
    ok((BUNDLE/"03_formal_cases/110_CASES_REVIEW_TABLE.md").is_file(), "Missing human-readable 110 cases index")
    ok(not list((BUNDLE/"03_formal_cases").glob("source_hypotheses_*.json")),
       "Redundant intermediate hypothesis extracts must not be retained")
    ok(not (BUNDLE/"ChineseBooks").exists() and not (BUNDLE/"analyses").exists(),
       "Duplicated book content folders must not be present")

    # Reader-first entry points must exist and allow navigation to canonical
    # evidence. Long-tail details are selected, not falsely claimed exhaustive.
    guides=(BUNDLE/"01_FAST_READ.md", BUNDLE/"02_SPARK_INDEX.md",
            READ/"DETAIL_COVERAGE_GAPS.md")
    local_links_checked=0
    for doc in guides:
        ok(doc.is_file(), "Missing reader-first guide: "+str(doc))
        if not doc.is_file():
            continue
        content=doc.read_text(encoding="utf-8")
        for m in re.finditer(r"\]\(([^)\n]+)\)",content):
            link=m.group(1).split("#",1)[0]
            if not link or link.startswith(("https://","http://","mailto:","#")):
                continue
            from urllib.parse import unquote
            target=(doc.parent/unquote(link)).resolve()
            ok(target.is_relative_to(ROOT.resolve()),"Reader link escapes repo "+link)
            ok(target.exists(),"Broken reader-guide link "+str(doc)+" -> "+link)
            local_links_checked+=1
    overview=(guides[0].read_text(encoding="utf-8") if guides[0].is_file() else "")
    spark_text=(guides[1].read_text(encoding="utf-8") if guides[1].is_file() else "")
    spark_ids=re.findall(r"\*\*(SPARK-\d{3})",spark_text)
    ok("一句话" in overview and "思想地图" in overview and "首轮" in overview,
       "Five-minute overview must disclose summary, map and coverage limits")
    ok(len(spark_ids)>=20 and len(set(spark_ids))==len(spark_ids),
       "At least 20 distinct source-linked detail inspiration entries required")
    ok("未" in spark_text and "AI联想" in spark_text,
       "Spark catalog must distinguish AI invention and unverified details")
    gap_ledger=(guides[2].read_text(encoding="utf-8") if guides[2].is_file() else "")
    gap_evidence_lessons=set(re.findall(r"knowledge/evidence/chanlun_lesson(\\d{3})\\.json", gap_ledger))
    ok("REGION_AUDIT_NOT_DOCUMENTED" in gap_ledger and
       "VISUAL_LIMITED" in gap_ledger and "PROVENANCE_LIMITED" in gap_ledger,
       "Detail gap ledger must distinguish first-pass from region and visual verification")
    ok(len(gap_evidence_lessons)>=11 and {"009","053","059","100","108"}.issubset(gap_evidence_lessons),
       "Reader gap ledger must identify source-linked high-priority evidence")
    ok("未做" in gap_ledger and "NOT_RUN" in gap_ledger,
       "Detail gap ledger must disclose unperformed visual review and empirical tests")
    summary={"status":"PASS" if not errors else "FAIL",
             "source_volume_pdfs_sha256_verified":len(index["volumes"]),
             "canonical_files_git_blob_sha1_verified":len(canonical),
             "duplicate_canonical_copies_in_acceptance":0,
             "canonical_bytes":manifest["canonical_bytes"],
             "lessons":len(lessons),"source_hypotheses":len(expected_claims),
             "prospective_cases":len(cs),"cross_lesson_examples":len(ex),
             "reader_first_overview_present":guides[0].is_file(),
             "inspiration_cards":len(spark_ids),
             "detail_gap_ledger_present":guides[2].is_file(),
             "prioritized_gap_evidence_lessons":len(gap_evidence_lessons),
             "reader_guide_local_links_checked":local_links_checked,
             "empirical_backtests_run":0,
             "complete_pen_parser_claimed":False,
             "visual_charts_all_confirmed":False,
             "errors":errors[:30]}
    return summary

if __name__=="__main__":
    report=verify()
    print(json.dumps(report,ensure_ascii=False,sort_keys=True))
    raise SystemExit(0 if report["status"]=="PASS" else 1)
