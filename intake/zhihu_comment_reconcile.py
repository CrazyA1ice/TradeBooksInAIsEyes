#!/usr/bin/env python3
"""Offline, fail-closed Zhihu comment export review; never writes research sources.

The supplied export is not a platform-verified transcript. Proposed C IDs are
review candidates only; authorship, timestamps, completeness and quoted words
are not certified by this program. No network access or content reproduction.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys

from zhihu_answer_reconcile import CoverageError, ensure, parse_export, _read_bytes

SCHEMA = "tradebooks-zhihu-comments-export-v1"
LEDGER_SCHEMA = "tradebooks-zhihu-comment-ledger-v1"
REPORT_SCHEMA = "tradebooks-zhihu-comments-review-v1"
MAX_BYTES = 40 * 1024 * 1024
MAX_COMMENTS = 50000
COMMENT_ID = re.compile(r"[0-9]{1,30}\Z")
REFERENCE = re.compile(r"C([0-9]{3,8})\Z")
URL = re.compile(r"https://(?:www\.)?zhihu\.com/question/([0-9]+)/answer/([0-9]+)/?\Z")
TARGETS = ("A094", "A058", "A084")
ROLES = {"ANSWER_AUTHOR", "OTHER", "UNKNOWN"}


def json_file(path):
    raw = _read_bytes(path)
    ensure(len(raw) <= MAX_BYTES, "json_size_out_of_bounds")
    try:
        doc = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeError, ValueError) as exc:
        raise CoverageError("invalid_utf8_json") from exc
    ensure(type(doc) is dict, "json_root_must_be_object")
    return doc, hashlib.sha256(raw).hexdigest()


def stamped(value, field, *, optional=False):
    if value is None and optional:
        return None
    ensure(type(value) is str, field + "_must_be_timezone_aware")
    try:
        dt = datetime.fromisoformat(value)
    except ValueError as exc:
        raise CoverageError(field + "_invalid_iso_datetime") from exc
    ensure(dt.tzinfo is not None and dt.utcoffset() is not None,
           field + "_must_be_timezone_aware")
    return dt


def answer_map(md, index_json, token):
    parsed = parse_export(md, token)
    idx, _ = json_file(index_json)
    ensure(idx.get("schema_version") == 1 and type(idx.get("answers")) is list,
           "unsupported_answer_index")
    ensure(idx.get("source_sha256") == parsed["source_sha256"],
           "answer_index_source_sha_mismatch")
    ensure(type(idx.get("answer_count")) is int and
           idx["answer_count"] == parsed["parsed_count"] == len(idx["answers"]),
           "answer_index_count_mismatch")
    by_id = {x["answer_id"]: x for x in parsed["rows"]}
    answer_urls, seen_refs = {}, set()
    for row in idx["answers"]:
        ensure(type(row) is dict and type(row.get("id")) is str and
               re.fullmatch(r"A[0-9]{3,8}", row["id"]) is not None,
               "invalid_answer_reference")
        ident = row.get("answer_id")
        ensure(type(ident) is str and ident in by_id and
               row.get("url") == by_id[ident]["url"],
               "answer_index_url_or_identity_drift")
        ensure(ident not in answer_urls and row["id"] not in seen_refs,
               "duplicate_answer_index_identity")
        answer_urls[ident] = (row["id"], row["url"])
        seen_refs.add(row["id"])
    ensure(len(answer_urls) == len(by_id), "answer_index_not_complete")
    return answer_urls, parsed["source_sha256"]


def normalize_id(value, *, optional=False):
    if value is None and optional:
        return None
    ensure(type(value) is str and COMMENT_ID.fullmatch(value) is not None,
           "invalid_comment_id")
    return value


def incoming_comments(path, speaker):
    doc, sha = json_file(path)
    ensure(doc.get("schema") == SCHEMA and type(doc.get("comments")) is list,
           "unsupported_comment_export_schema")
    ensure(doc.get("profile_url") ==
           "https://www.zhihu.com/people/" + speaker,
           "comment_export_profile_mismatch")
    capture = stamped(doc.get("captured_at"), "captured_at")
    items = doc["comments"]
    ensure(len(items) <= MAX_COMMENTS, "too_many_comments")
    seen, rows = set(), []
    for item in items:
        ensure(type(item) is dict, "comment_must_be_object")
        cid = normalize_id(item.get("comment_id"))
        ensure(cid not in seen, "duplicate_comment_id_in_export")
        seen.add(cid)
        url = item.get("answer_url")
        ensure(type(url) is str and URL.fullmatch(url) is not None,
               "invalid_comment_answer_url")
        url = url.rstrip("/")
        role = item.get("reported_author_role")
        ensure(type(role) is str and role in ROLES,
               "invalid_reported_author_role")
        label = item.get("author_label")
        ensure(type(label) is str and bool(label.strip()) and len(label) <= 200,
               "author_label_required")
        body = item.get("content")
        ensure(type(body) is str and 0 < len(body.strip()) <= 100000,
               "comment_content_required")
        parent = normalize_id(item.get("parent_comment_id"), optional=True)
        ensure(parent != cid, "self_parent_comment")
        when = stamped(item.get("published_at"), "published_at", optional=True)
        ensure(when is None or when <= capture, "comment_after_export_capture")
        rows.append({
            "comment_id": cid, "answer_id": URL.fullmatch(url).group(2),
            "answer_url": url, "parent_comment_id": parent,
            "published_at": item.get("published_at"),
            "reported_author_role": role,
            "content_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "author_label_sha256": hashlib.sha256(label.encode("utf-8")).hexdigest(),
        })
    return rows, sha, doc["captured_at"]


def existing_ledger(path, speaker, answer_urls):
    if path is None:
        return {}, set()
    doc, _ = json_file(path)
    ensure(doc.get("schema") == LEDGER_SCHEMA and
           doc.get("speaker_token") == speaker and
           type(doc.get("comments")) is list,
           "unsupported_existing_comment_ledger")
    by_id, used = {}, set()
    existing_answer_refs = {ref for ref, _ in answer_urls.values()}
    for item in doc["comments"]:
        ensure(type(item) is dict and type(item.get("stable_id")) is str and
               REFERENCE.fullmatch(item["stable_id"]) is not None,
               "bad_existing_stable_comment_reference")
        cid = normalize_id(item.get("comment_id"))
        ensure(cid not in by_id and item["stable_id"] not in used,
               "duplicate_existing_comment_identity")
        ensure(item.get("answer_ref") in existing_answer_refs,
               "existing_comment_answer_not_indexed")
        for field in ("content_sha256", "author_label_sha256"):
            ensure(type(item.get(field)) is str and
                   re.fullmatch(r"[0-9a-f]{64}", item[field]) is not None,
                   "existing_comment_hash_required")
        ensure(item.get("reported_author_role") in ROLES,
               "invalid_existing_author_role")
        stamped(item.get("published_at"), "existing_published_at")
        normalize_id(item.get("parent_comment_id"), optional=True)
        by_id[cid] = item
        used.add(item["stable_id"])
    return by_id, used


def review(answers_md, answers_index, incoming_json, speaker, *, ledger_json=None):
    ensure(type(speaker) is str and
           re.fullmatch(r"[A-Za-z0-9_-]{1,80}", speaker) is not None,
           "speaker_token_required")
    answers, answer_sha = answer_map(answers_md, answers_index, speaker)
    incoming, src_sha, capture = incoming_comments(incoming_json, speaker)
    old, used = existing_ledger(ledger_json, speaker, answers)
    by_id = {r["comment_id"]: r for r in incoming}
    expected_by_id = {k: v["answer_ref"] for k, v in old.items()}
    proposed = {}
    for r in incoming:
        linked = answers.get(r["answer_id"])
        existing = old.get(r["comment_id"])
        if existing:
            ensure(linked is not None and
                   existing["answer_ref"] == linked[0],
                   "comment_id_reassigned_to_other_answer")
        if linked is not None:
            ensure(r["answer_url"] == linked[1],
                   "indexed_answer_url_mismatch")
            expected_by_id[r["comment_id"]] = linked[0]
            proposed[r["comment_id"]] = linked[0]
    # Absence of a parent is a review blocker, never evidence of no reply.
    missing_parent = set()
    for r in incoming:
        parent = r["parent_comment_id"]
        if parent is None:
            continue
        if parent not in expected_by_id:
            missing_parent.add(r["comment_id"])
        elif r["comment_id"] in expected_by_id:
            ensure(expected_by_id[parent] == expected_by_id[r["comment_id"]],
                   "cross_answer_parent_relation")
    graph = {k: v.get("parent_comment_id") for k, v in old.items()}
    graph.update({x["comment_id"]: x["parent_comment_id"] for x in incoming})
    for key in graph:
        current, visited = key, set()
        while current in graph and graph[current] is not None:
            ensure(current not in visited, "comment_reply_cycle")
            visited.add(current)
            current = graph[current]
    new, changed, overlap, blocked = [], [], 0, []
    for r in sorted(incoming, key=lambda x: (x["published_at"] or "", x["comment_id"])):
        cid = r["comment_id"]
        prior = old.get(cid)
        if prior is not None:
            if any(prior.get(k) != r.get(k) for k in
                   ("content_sha256", "author_label_sha256", "published_at",
                    "parent_comment_id", "reported_author_role")):
                changed.append({"stable_id": prior["stable_id"],
                                "comment_id": cid,
                                "review_reason": "metadata_or_content_changed"})
            else:
                overlap += 1
            continue
        reasons = []
        if cid not in proposed:
            reasons.append("ANSWER_NOT_IN_BASE_INDEX")
        if r["published_at"] is None:
            reasons.append("COMMENT_TIMESTAMP_MISSING")
        if cid in missing_parent:
            reasons.append("PARENT_CONTEXT_NOT_IN_EXPORT_OR_LEDGER")
        if reasons:
            blocked.append({"comment_id": cid,
                            "answer_ref": proposed.get(cid),
                            "review_reasons": reasons})
        else:
            new.append(r)
    next_num = max((int(REFERENCE.fullmatch(s).group(1)) for s in used), default=0) + 1
    additions = []
    for r in new:
        additions.append({
            "proposed_id": "C" + str(next_num).zfill(3),
            "comment_id": r["comment_id"],
            "answer_ref": proposed[r["comment_id"]],
            "parent_comment_id": r["parent_comment_id"],
            "published_at": r["published_at"],
            "reported_author_role": r["reported_author_role"],
            "content_sha256": r["content_sha256"],
            "author_label_sha256": r["author_label_sha256"],
            "provenance_status": "USER_EXPORT_NOT_PLATFORM_AUTHENTICATED",
        })
        next_num += 1
    priority = []
    for ref in TARGETS:
        seen_count = sum(1 for cid, aid in proposed.items() if aid == ref)
        priority.append({"answer_ref": ref,
                         "records_in_this_export": seen_count,
                         "status": ("EXPORTED_UNVERIFIED_NOT_RESEARCH_APPROVED"
                                    if seen_count else "NOT_OBSERVED_IN_THIS_EXPORT")})
    return {
        "schema": REPORT_SCHEMA,
        "speaker_token": speaker,
        "source_sha256": src_sha,
        "base_answer_sha256": answer_sha,
        "captured_at_claimed_by_export": capture,
        "comments_in_export": len(incoming),
        "existing_approved_refs_provided": len(old),
        "unchanged_existing_overlaps": overlap,
        "changed_existing_needing_review": changed,
        "existing_not_in_this_export": [
            {"stable_id": v["stable_id"], "comment_id": k}
            for k, v in sorted(old.items()) if k not in by_id],
        "new_proposed": len(additions),
        "new_comment_refs": additions,
        "blocked_for_context_review": blocked,
        "priority_answer_coverage": priority,
        "status": "REVIEW_ONLY_NO_IMPORT",
        "authorship_independently_verified": False,
        "platform_comment_history_complete": False,
        "comment_content_reproduced": False,
        "research_sources_modified": False,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Offline Zhihu comment source, parent and stable-reference review")
    ap.add_argument("--answers-md", type=Path, required=True)
    ap.add_argument("--answers-index", type=Path, required=True)
    ap.add_argument("--incoming-json", type=Path, required=True)
    ap.add_argument("--speaker-token", required=True)
    ap.add_argument("--existing-ledger", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args(argv)
    try:
        result = review(args.answers_md, args.answers_index, args.incoming_json,
                        args.speaker_token, ledger_json=args.existing_ledger)
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.output is None:
            print(payload, end="")
        else:
            path = args.output
            ensure(path.name.endswith(".private.json"), "output_must_be_private_json")
            ensure(path.parent.is_dir() and not path.parent.is_symlink(),
                   "output_parent_must_exist")
            sources = [args.answers_md, args.answers_index, args.incoming_json]
            if args.existing_ledger is not None:
                sources.append(args.existing_ledger)
            ensure(path.resolve() not in {p.resolve() for p in sources},
                   "output_cannot_replace_input")
            with path.open("x", encoding="utf-8") as fh:
                fh.write(payload)
        return 0
    except (CoverageError, OSError) as exc:
        print("REFUSED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
