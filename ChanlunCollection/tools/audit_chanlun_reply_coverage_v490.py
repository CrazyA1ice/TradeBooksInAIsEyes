#!/usr/bin/env python3
"""v4.90: bounded third-party 108-lesson UID reply inventory and edition intake.

All material is third-party, not historically authenticated Sina comments.
No external downloads, no redistribution of book text or private documents.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog/chanlun_108_author_uid_reply_baseline_v490.json"
UPSTREAM = "stockServ/chzhshch-108-plus"
COMMIT = "d2a87d5bd9c84baac2918edca668b9f82a20be52"
AUTHOR_UID = "1215172700"
AUTHOR = "缠中说禅"
UID_PATTERN = re.compile(r"UID:\[(\d+)\]\s*昵称：([^\r\n]+?)\s*日期：\(([^)]+)\)")
DATE_PATTERN = re.compile(r"(?<!\d)(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})")
REPLY_PATTERN = re.compile(r"^20\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
KEYWORDS = re.compile(r"第二种|两种方法|两种看法|两套定义")
PRIORITY_TIMES = {
    "FEB09_R29": "2007-02-09 16:20:18",
    "FEB12_R52": "2007-02-12 16:07:02",
    "MAR08_R55": "2007-03-08 16:38:56",
}


def demand(condition, reason):
    if not condition:
        raise ValueError("UID_REPLY_V490: " + reason)


def parse_uid_comments(text):
    """Only count explicitly author-UID+name matched source markers, never authenticate."""
    matches = list(UID_PATTERN.finditer(text))
    result = []
    for i, m in enumerate(matches):
        content = text[m.end():matches[i + 1].start() if i + 1 < len(matches) else len(text)]
        result.append({
            "uid": m.group(1),
            "name": m.group(2).strip(),
            "date": m.group(3),
            "keyword_mention_in_full_block": bool("中枢" in content and KEYWORDS.search(content)),
        })
    return result


def source_facts(data):
    comments = parse_uid_comments(data)
    author = [x for x in comments if x["uid"] == AUTHOR_UID and x["name"] == AUTHOR]
    return {
        "comments_total": len(comments),
        "author_uid_confirmed_count": len(author),
        "author_timestamps": [x["date"] for x in author],
        "unverified_uid0_name_count": sum(x["uid"] == "0" and AUTHOR in x["name"] for x in comments),
        "keyword_candidate_timestamps": [x["date"] for x in author if x["keyword_mention_in_full_block"]],
    }


def audit(catalog, root=ROOT):
    demand(catalog.get("schema_version") == 1 and catalog.get("version") == "4.90.0"
           and catalog.get("id") == "CHANLUN-108-THIRD_PARTY_AUTHOR_UID_REPLY_COVERAGE_BASELINE_V490",
           "catalog identity")
    src = catalog["source"]
    demand(src["repo"] == UPSTREAM and src["commit_sha"] == COMMIT and src["directory"] == "108", "upstream ref")
    demand(src["source_role"] == "THIRD_PARTY_TRANSCRIPT_NOT_ORIGINAL_SINA_SERVER_AUTHENTICATION", "source role")
    demand(src["source_registered_prior"] == "catalog/chanlun_two_methods_archives_laohu_v438.json", "prior source")
    old = json.loads((root/src["source_registered_prior"]).read_text(encoding="utf-8"))
    demand(old["third_party_crosscheck"]["repo"] == UPSTREAM and old["provenance"]["laohu_edition_file_bytes_obtained"] is False,
           "source prior-art registration")
    parser = catalog["parser"]
    demand(parser["exact_author_uid"] == AUTHOR_UID and parser["exact_author_name"] == AUTHOR
           and parser["missing_uid_does_not_prove_original_reply_absence"] is True
           and parser["keyword_hits_include_quoted_questions"] is True, "parser limitation")
    rows = catalog["records"]
    demand(len(rows) == 108, "exact 108 rows")
    for i, row in enumerate(rows, 1):
        path = row["path"]
        demand(row["lesson"] == i and path.startswith("108/") and path.endswith(f"-{i:03d}.md"), "lesson path/order")
        demand(re.fullmatch(r"[0-9a-f]{40}", row["blob_sha"]) is not None, "invalid Git blob")
        demand(isinstance(row["document_git_size"], int) and row["document_git_size"] > 100, "source size")
        times = row["author_timestamps"]
        demand(row["author_uid_confirmed_count"] == len(times)
               and row["comments_total"] >= len(times) >= 0
               and row["unverified_uid0_name_count"] >= 0, "source count consistency")
        demand(all(isinstance(t, str) and REPLY_PATTERN.fullmatch(t) for t in times)
               and len(times) == len(set(times)), "time format or duplicate")
        demand(set(row["keyword_candidate_timestamps"]).issubset(set(times)), "unattributed keyword")
    sm = catalog["summary"]
    expected = {
        "indexed_lesson_files": 108, "source_tree_md_items": 113, "excluded_supplemental_md_items": 5,
        "uid_format_comment_records": 2541, "matching_name_and_uid_records": 953,
        "lessons_with_matching_uid": 58, "lessons_with_any_uid_format_comments": 95,
        "lessons_without_matching_uid": 50, "lessons_61_108_without_matching_uid": 45,
        "keyword_candidates_records": 2,
    }
    demand(sm == expected, "frozen research statistics")
    demand(sum(x["comments_total"] for x in rows) == 2541
           and sum(x["author_uid_confirmed_count"] for x in rows) == 953
           and sum(bool(x["author_uid_confirmed_count"]) for x in rows) == 58
           and sum(bool(x["comments_total"]) for x in rows) == 95
           and sum(not x["author_uid_confirmed_count"] and x["lesson"] >= 61 for x in rows) == 45,
           "computed totals disagree")
    hits = [(x["lesson"], t) for x in rows for t in x["keyword_candidate_timestamps"]]
    demand(hits == [(54, "2007-05-24 15:58:51"), (54, "2007-05-24 16:04:41")], "keyword hits")
    demand(PRIORITY_TIMES["FEB09_R29"] in rows[28]["author_timestamps"], "Feb 9 receipt")
    expected_review = [
        (54, "2007-05-24 15:58:51", "QUESTION_QUOTES_SECOND_DECOMPOSITION_NOT_AUTHOR_SECOND_CENTER_AXIOM"),
        (54, "2007-05-24 16:04:41", "QUESTION_QUOTES_SECOND_DECOMPOSITION_NOT_AUTHOR_SECOND_CENTER_AXIOM"),
    ]
    demand([(x["lesson"], x["author_uid_comment_timestamp"], x["role"]) for x in catalog["keyword_review"]]
           == expected_review, "quoted question mistaken as author formula")
    flags = catalog["limits"]
    demand(set(flags) == {
        "not_verified_independent_2007_sina_comment_bytes",
        "not_complete_original_author_replies",
        "all_108_lessons_covered_does_not_imply_reply_coverage",
        "nickname_and_uid_may_be_copied",
        "missing_UID_or_author_matches_not_proof_no_comments",
        "keyword_hits_not_author_own_quotation",
        "laohu_file_bytes_obtained",
        "laohu_vs_baseline_compared",
        "kaixiang_A087_exact_reply_identified",
        "market_backtest_run"
    }, "limit set")
    demand(all(flags[k] is True for k in (
        "not_verified_independent_2007_sina_comment_bytes",
        "not_complete_original_author_replies",
        "all_108_lessons_covered_does_not_imply_reply_coverage",
        "nickname_and_uid_may_be_copied",
        "missing_UID_or_author_matches_not_proof_no_comments",
        "keyword_hits_not_author_own_quotation",
    )), "false completeness assurance")
    demand(all(flags[k] is False for k in (
        "laohu_file_bytes_obtained",
        "laohu_vs_baseline_compared",
        "kaixiang_A087_exact_reply_identified",
        "market_backtest_run"
    )), "false source or market promotion")
    demand(catalog["frontiers"] == {
        "A087": "OPEN", "A016": "OPEN", "F01": "OPEN",
        "OB38": "OPEN", "OB99": "OPEN", "E1_E4": "NOT_RUN"
    }, "research gates")
    demand(catalog["report"] == "other_views/chanlun/speaker-unknown-001/IDEA_108_AUTHOR_REPLY_COVERAGE_BASELINE_V490.md", "report")
    report = (root/catalog["report"]).read_text(encoding="utf-8")
    demand(all(q in report for q in ("2,541", "953", "58/108", "45/48", "A087", "NOT_RUN")),
           "research report missing qualification")
    return {"status": "ARCHIVED_UID_BASELINE_PASS", "lessons": len(rows),
            "visible_uid_comments": 2541, "matching_author_uid_comments": 953,
            "lessons_with_matching_author_uid": 58, "Laohu": "UNOBTAINED", "A087": "OPEN"}


def git_blob_sha(raw):
    prefix = b"blob " + str(len(raw)).encode("ascii") + b"\0"
    return hashlib.sha1(prefix + raw).hexdigest()


def reverify_source_dir(catalog, source_dir):
    """Optional *real* verification: require all upstream file bytes and exact blob SHAs."""
    outputs = []
    for entry in catalog["records"]:
        p = Path(source_dir)/entry["path"]
        demand(p.is_file(), "missing source snapshot " + entry["path"])
        raw = p.read_bytes()
        demand(git_blob_sha(raw) == entry["blob_sha"], "source content SHA mismatch " + entry["path"])
        parsed = source_facts(raw.decode("utf-8-sig"))
        demand(all(parsed[k] == entry[k] for k in parsed), "comment parsing mismatch " + entry["path"])
        outputs.append(entry["lesson"])
    return {"status": "EXACT_GIT_BLOBS_AND_UID_METADATA_VERIFIED",
            "verified_files": len(outputs),
            "third_party_authenticity": "NOT_CERTIFIED"}


def extract_edition_text(path):
    """Read a candidate local edition without uploading/redistributing its text."""
    p = Path(path)
    demand(p.is_file(), "edition path not a file")
    suffix = p.suffix.lower()
    if suffix in {".txt", ".md"}:
        return p.read_text(encoding="utf-8-sig")
    if suffix == ".docx":
        with zipfile.ZipFile(p) as archive:
            xml = archive.read("word/document.xml")
        root = ET.fromstring(xml)
        ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        lines = []
        for paragraph in root.iter(ns + "p"):
            lines.append("".join((node.text or "") for node in paragraph.iter(ns + "t")))
        return "\n".join(lines)
    if suffix == ".pdf":
        try:
            import fitz
        except ImportError as exc:
            raise ValueError("UID_REPLY_V490: PDF text extraction requires PyMuPDF; not installed") from exc
        with fitz.open(p) as pdf:
            return "\n".join(page.get_text("text") for page in pdf)
    raise ValueError("UID_REPLY_V490: edition file must be TXT, MD, DOCX or PDF")


def dated_strings(text):
    return {f"{int(m[1]):04d}-{int(m[2]):02d}-{int(m[3]):02d} {m[4]}:{m[5]}:{m[6]}"
            for m in DATE_PATTERN.finditer(text)}


def compare_edition_text(catalog, text):
    """Screening only. Date occurrences are NOT confirmed matching author replies."""
    baseline = {t for x in catalog["records"] for t in x["author_timestamps"]}
    markers = {x["date"] for x in parse_uid_comments(text)
               if x["uid"] == AUTHOR_UID and x["name"] == AUTHOR}
    all_dates = dated_strings(text)
    matched = baseline & markers
    loose = baseline & all_dates
    return {
        "status": "TEXT_SCREENING_ONLY_NOT_EDITORIAL_REPLY_VALIDATION"
                  if text.strip() else "NO_READABLE_TEXT_UNVERIFIABLE_OCR_OR_FORMAT",
        "edition_readable_characters": len(text),
        "baseline_archived_uid_count": len(baseline),
        "uid_and_name_timestamp_markers_shared": len(matched),
        "baseline_timestamps_appearing_anywhere_in_text": len(loose),
        "baseline_timestamps_not_observed_in_text_count": len(baseline - all_dates),
        "priority": {key: (
            "ARCHIVED_UID_AND_NAME_STRING_MATCH" if tm in markers else
            "TIMESTAMP_TEXT_ONLY_LOW_CONFIDENCE" if tm in all_dates else
            "NOT_OBSERVED_IN_EXTRACTED_TEXT_NOT_PROOF_OF_ABSENCE"
        ) for key, tm in PRIORITY_TIMES.items()},
        "provenance": "SINGLE_THIRD_PARTY_BASELINE_AND_UNVERIFIED_EDITION_TEXT",
        "claims_actual_edition_missing_replies": False,
        "claims_original_sina_historical_identity_authenticated": False,
        "claims_kaixiang_A087_identified": False,
    }


def main():
    p = argparse.ArgumentParser(description="108-lesson author-UID reply coverage (offline and fail-closed)")
    p.add_argument("--check", action="store_true")
    p.add_argument("--source-dir", type=Path, default=None)
    p.add_argument("--edition", type=Path, default=None)
    args = p.parse_args()
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    output = {"catalog": audit(catalog)}
    if args.source_dir is not None:
        output["source_reverified"] = reverify_source_dir(catalog, args.source_dir)
    if args.edition is not None:
        output["edition_screening"] = compare_edition_text(catalog, extract_edition_text(args.edition))
    print(json.dumps(output, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
