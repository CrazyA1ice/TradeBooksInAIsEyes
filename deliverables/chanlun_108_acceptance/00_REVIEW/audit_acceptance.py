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

    hypotheses = []
    for a,b in ((1,16),(17,32),(33,48),(49,64),(65,80),(81,96),(97,108)):
        data = load("03_formal_cases/source_hypotheses_%03d_%03d.json" % (a,b))
        ok([v["lesson"] for v in data["entries"]] == list(range(a,b+1)),
           "Hypothesis inventory lesson range mismatch: %d–%d" % (a,b))
        hypotheses.extend(data["entries"])
    ok(len(hypotheses) == 108,"Must cover 108 evidence hypothesis inventories")
    expected_claims = {}
    for entry in hypotheses:
        n=entry["lesson"]
        path="knowledge/evidence/chanlun_lesson%03d.json" % n
        analysis="analyses/books/chanlun/chapters/lesson_%03d.md" % n
        ok(entry["source_path"] == path, "Bad source link: %s" % n)
        ok(entry["analysis_path"] == analysis, "Bad analysis link: %s" % n)
        ok((ROOT / analysis).is_file(), "Missing chapter analysis %s" % n)
        source=load(path)
        source_hyp={c["id"]:c for c in source["claims"]
                    if "hypothesis" in str(c.get("kind",c.get("type",""))).lower()}
        ok(len(source_hyp)==len(entry["explicit_hypotheses"]),
           "Claim count disagree with source evidence: %s" % n)
        for h in entry["explicit_hypotheses"]:
            cid=h["source_claim_id"]
            ok(cid in source_hyp, "Claim no longer in source: " + cid)
            if cid in source_hyp:
                c=source_hyp[cid]
                ok(h["statement"]==(c.get("summary") or c.get("statement") or c.get("claim")),
                   "Claim statement changed: " + cid)
                ok(h["pdf_pages"]==(c.get("pdf_pages") or c.get("pages") or []),
                   "Claim physical pages changed: " + cid)
            expected_claims[(n,cid)]=h
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
    summary={"status":"PASS" if not errors else "FAIL",
             "source_volume_pdfs_sha256_verified":len(index["volumes"]),
             "canonical_files_git_blob_sha1_verified":len(canonical),
             "duplicate_canonical_copies_in_acceptance":0,
             "canonical_bytes":manifest["canonical_bytes"],
             "lessons":len(lessons),"source_hypotheses":len(expected_claims),
             "prospective_cases":len(cs),"cross_lesson_examples":len(ex),
             "empirical_backtests_run":0,
             "complete_pen_parser_claimed":False,
             "visual_charts_all_confirmed":False,
             "errors":errors[:30]}
    return summary

if __name__=="__main__":
    report=verify()
    print(json.dumps(report,ensure_ascii=False,sort_keys=True))
    raise SystemExit(0 if report["status"]=="PASS" else 1)
