#!/usr/bin/env python3
"""Read-only Zhihu answer export reconciliation, without a 100-answer cap.

Protect stable prior A001+ citations. No network, scraping, author verification,
comment invention, full-text copying, or automatic overwrites. Output is only
an append/review proposal; importing approved source text is a separate act.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

MAX_BYTES = 40 * 1024 * 1024
MAX_ANSWERS = 50000
HEADING = re.compile(r"^##[ \t]+(.+?)\s*$")
COUNT = re.compile(r"^-[ \t]*回答总数:[ \t]*(\d+)\s*$")
PROFILE = re.compile(r"^-[ \t]*用户主页:[ \t]*(https://www\.zhihu\.com/people/[A-Za-z0-9_-]+)/?\s*$")
LINK = re.compile(r"^-[ \t]*原文链接:[ \t]*(https://(?:www\.)?zhihu\.com/question/\d+/answer/\d+)/?\s*$")
DATE = re.compile(r"^-[ \t]*发布时间:[ \t]*(\d{4}-\d{2}-\d{2}(?:[ \t]+\d{2}:\d{2})?)\s*$")
ASSIGNED = re.compile(r"A(\d{3,8})\Z")
SCHEMA = "tradebooks-zhihu-answers-reconcile-v1"


class CoverageError(ValueError):
    pass


def ensure(ok, message):
    if not ok:
        raise CoverageError(message)


def _read_bytes(path):
    path = Path(path)
    ensure(path.is_file() and not path.is_symlink(), "source_must_be_regular_file")
    ensure(0 < path.stat().st_size <= MAX_BYTES, "source_size_out_of_bounds")
    return path.read_bytes()


def _parse_profile(text, speaker):
    lines = text.splitlines()
    values = [m.group(1) for line in lines[:15] if (m := PROFILE.fullmatch(line))]
    ensure(len(values) == 1, "one_export_profile_required")
    actual = urlparse(values[0]).path.rsplit("/", 1)[-1]
    ensure(actual == speaker, "zhihu_speaker_mismatch")
    counts = [int(m.group(1)) for line in lines[:15] if (m := COUNT.fullmatch(line))]
    ensure(len(counts) == 1, "one_declared_answer_count_required")
    ensure(0 <= counts[0] <= MAX_ANSWERS, "declared_count_out_of_bounds")
    return counts[0], lines


def parse_export(path, speaker):
    ensure(type(speaker) is str and
           re.fullmatch(r"[A-Za-z0-9_-]{1,80}", speaker) is not None,
           "speaker_token_required")
    blob = _read_bytes(path)
    try:
        text = blob.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CoverageError("export_must_be_utf8") from exc
    declared, lines = _parse_profile(text, speaker)
    # Only headings with actual answer metadata count as answer boundaries;
    # an embedded Markdown ## subtitle without metadata is still body text.
    starts = []
    for i, line in enumerate(lines):
        title = HEADING.fullmatch(line)
        if title is None:
            continue
        # A real answer's *immediate* first nonblank line must be a
        # recognizable export metadata field. Otherwise a ## subheading in
        # the body followed by the *next* answer is not another answer.
        following = lines[i + 1:i + 9]
        first = next((x for x in following if x.strip()), "")
        if not (first.startswith("- 原文链接:")
                or first.startswith("- 发布时间:")):
            continue
        metadata = []
        for x in following:
            if x.startswith("## ") or x.strip() == "---":
                break
            metadata.append(x)
        has_link = any(LINK.fullmatch(x) for x in metadata)
        has_date = any(DATE.fullmatch(x) for x in metadata)
        # Malformed answers fail instead of disappearing from the count.
        ensure(has_link, "invalid_answer_url_or_metadata")
        ensure(has_date, "answer_date_metadata_missing")
        starts.append((i, title.group(1)))
    ensure(bool(starts), "no_structured_answers_found")
    ensure(len(starts) <= MAX_ANSWERS, "parsed_count_out_of_bounds")
    ensure(declared == len(starts), "declared_and_parsed_counts_differ")
    rows = []
    ids = {}
    for pos, (start, title) in enumerate(starts):
        stop = starts[pos + 1][0] if pos + 1 < len(starts) else len(lines)
        section = lines[start + 1:stop]
        # Metadata is expected at the beginning, as in the supplied export.
        link_at = [(k, LINK.fullmatch(x)) for k, x in enumerate(section[:8])]
        urls = [(k, m.group(1).rstrip("/")) for k, m in link_at if m]
        ensure(len(urls) == 1, "ambiguous_answer_url")
        k, url = urls[0]
        aid = url.rsplit("/", 1)[-1]
        ensure(aid not in ids, "duplicate_answer_id_in_export")
        ids[aid] = True
        date = next((m.group(1) for x in section[:8]
                     if (m := DATE.fullmatch(x))), None)
        ensure(date is not None, "answer_date_metadata_missing")
        # Exclude metadata/header and the separator from the normalized body.
        body_start = max(k + 1, next((
            n + 1 for n, x in enumerate(section[:8])
            if x.lstrip().startswith("- 赞同数:")), k + 1))
        body_lines = list(section[body_start:])
        while body_lines and not body_lines[-1].strip():
            body_lines.pop()
        if body_lines and body_lines[-1].strip() == "---":
            body_lines.pop()
        body = "\n".join(body_lines).strip()
        ensure(bool(body), "empty_answer_body")
        rows.append({
            "answer_id": aid, "url": url, "title": title,
            "published": date,
            "normalized_body_sha256": hashlib.sha256(
                body.encode("utf-8")).hexdigest(),
        })
    return {
        "source_sha256": hashlib.sha256(blob).hexdigest(),
        "source_bytes": len(blob),
        "declared_count": declared,
        "parsed_count": len(rows),
        "speaker_token": speaker,
        "rows": rows,
    }


def reconcile(base_md, base_index_json, candidate_md, speaker, *, min_candidate=1):
    ensure(type(min_candidate) is int and 1 <= min_candidate <= MAX_ANSWERS,
           "invalid_minimum_candidate")
    base = parse_export(base_md, speaker)
    candidate = parse_export(candidate_md, speaker)
    ensure(candidate["parsed_count"] >= min_candidate,
           "candidate_below_explicit_minimum")
    raw = _read_bytes(base_index_json)
    try:
        idx = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CoverageError("invalid_existing_index") from exc
    ensure(type(idx) is dict and idx.get("schema_version") == 1 and
           type(idx.get("answers")) is list,
           "unsupported_existing_answer_index")
    ensure(idx.get("source_sha256") == base["source_sha256"],
           "base_export_sha_not_indexed")
    ensure(idx.get("answer_count") == base["parsed_count"] ==
           len(idx["answers"]), "base_index_count_drift")
    baseline = {r["answer_id"]: r for r in base["rows"]}
    assigned = {}
    numbers = set()
    for entry in idx["answers"]:
        ensure(type(entry) is dict and type(entry.get("id")) is str and
               ASSIGNED.fullmatch(entry["id"]) is not None,
               "invalid_stable_answer_reference")
        aid = str(entry.get("answer_id", ""))
        ensure(aid in baseline and entry.get("url", "").rstrip("/") ==
               baseline[aid]["url"], "base_index_source_mismatch")
        ensure(aid not in assigned, "duplicate_existing_answer_reference")
        number = int(ASSIGNED.fullmatch(entry["id"]).group(1))
        ensure(number not in numbers, "duplicate_stable_answer_number")
        numbers.add(number)
        assigned[aid] = entry["id"]
    ensure(len(assigned) == len(baseline), "base_export_not_fully_indexed")
    candidate_by_id = {r["answer_id"]: r for r in candidate["rows"]}
    newly_seen = [r for r in candidate["rows"] if r["answer_id"] not in assigned]
    changed = []
    unchanged_count = 0
    for aid, old in baseline.items():
        curr = candidate_by_id.get(aid)
        if curr is None:
            continue
        ensure(curr["url"] == old["url"], "same_answer_id_different_question")
        if (curr["normalized_body_sha256"] != old["normalized_body_sha256"]
                or curr["title"] != old["title"]
                or curr["published"] != old["published"]):
            changed.append({"stable_id": assigned[aid], "answer_id": aid,
                            "url": curr["url"],
                            "review_reason": "content_or_metadata_changed"})
        else:
            unchanged_count += 1
    missing = [{"stable_id": assigned[aid], "answer_id": aid}
               for aid in baseline if aid not in candidate_by_id]
    next_number = max(numbers, default=0) + 1
    additions = []
    for row in newly_seen:
        additions.append({
            "proposed_id": "A" + str(next_number).zfill(3),
            "answer_id": row["answer_id"],
            "url": row["url"],
            "published": row["published"],
            "source_status": "USER_EXPORT_NOT_PLATFORM_AUTHENTICATED",
        })
        next_number += 1
    return {
        "schema": SCHEMA, "speaker_token": speaker,
        "base": {"sha256": base["source_sha256"],
                 "declared_answers": base["declared_count"],
                 "parsed_answers": base["parsed_count"]},
        "incoming": {"sha256": candidate["source_sha256"],
                     "declared_answers": candidate["declared_count"],
                     "parsed_answers": candidate["parsed_count"]},
        "kept_stable_answer_references": len(assigned),
        "unchanged_overlaps": unchanged_count,
        "new_proposed": len(additions),
        "changed_prior_answers_needing_review": len(changed),
        "prior_answers_not_in_this_export": len(missing),
        "proposed_total_after_append": len(assigned) + len(additions),
        "new_answer_refs": additions,
        "changed_prior_refs": changed,
        "absent_prior_refs": missing,
        "status": ("REVIEW_CHANGES_OR_PARTIAL_EXPORT"
                   if changed or missing else
                   "APPEND_PROPOSAL_NOT_IMPORTED" if additions else
                   "SAME_COVERAGE_NO_NEW_ANSWERS"),
        "baseline_not_overwritten": True,
        "opinions_not_interpreted": True,
        "speaker_identity_independently_verified": False,
        "comments_fetched": False,
        "full_zhihu_account_coverage_verified": False,
        "no_source_body_in_report": True,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Offline Zhihu answer coverage + stable-ID append plan")
    ap.add_argument("--base-md", required=True, type=Path)
    ap.add_argument("--base-index", required=True, type=Path)
    ap.add_argument("--incoming-md", required=True, type=Path)
    ap.add_argument("--speaker-token", required=True)
    ap.add_argument("--min-incoming-answers", type=int, default=1)
    ap.add_argument("--output", type=Path,
                    help="Optional NEW .private.json file outside source tree")
    args = ap.parse_args(argv)
    try:
        result = reconcile(args.base_md, args.base_index, args.incoming_md,
                           args.speaker_token,
                           min_candidate=args.min_incoming_answers)
        payload = json.dumps(result, ensure_ascii=False, indent=2,
                             sort_keys=True) + "\n"
        if args.output is not None:
            p = args.output
            ensure(p.name.endswith(".private.json"), "output_must_be_private_json")
            ensure(p.parent.is_dir() and not p.parent.is_symlink(),
                   "output_parent_must_exist")
            ensure(p.resolve() not in {args.base_md.resolve(),
                                     args.base_index.resolve(),
                                     args.incoming_md.resolve()},
                   "output_cannot_replace_inputs")
            # Prevent overwriting a prior review or accidentally editing canonical
            # research material; only explicit new receipt files are allowed.
            with p.open("x", encoding="utf-8") as out:
                out.write(payload)
        else:
            print(payload, end="")
        return 0
    except (CoverageError, OSError) as exc:
        print("REFUSED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
