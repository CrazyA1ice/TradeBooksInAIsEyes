#!/usr/bin/env python3
"""v4.92: census every author-attributed block in one editorial lesson70 source.

Evidence: pinned third-party Git blobs only. Raw-style HTML is *not*
authenticated 2007 Sina server data. No network or copyrighted-text copying.
"""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog/chanlun_l70_editorial_time_roles_v492.json"
EXPECTED_HOSTS = {
    "L70": ("fangj/chan", "raw/sina_blog/chan_fenlei/jiaonichaogupiao/681.html",
            "d0b0891704a0b1c1c561ad87d5510dd73ed7f1ad",
            "教你炒股票70：一个教科书式走势的示范分析", "2007-08-15 22:41:35", 0),
    "AUG13": ("fangj/chan", "raw/sina_blog/chan_fenlei/shizhengjingji/584.html",
             "ac9e3b569cfdf5fc4a9ca49f21e51c9ebe84bfbd",
             "41与1，本ID对二级市场兴趣已失", "2007-08-13 21:26:14", 6),
    "AUG16": ("fangj/chan", "raw/sina_blog/chan_fenlei/shizhengjingji/680.html",
             "06ffc2f7781e8e15725cf63621fbcb8dbdd48a81",
             "全球化，没有市场可与世隔绝", "2007-08-16 15:41:56", 20),
    "JUL31": ("fangj/chan", "raw/sina_blog/chan_fenlei/shizhengjingji/607.html",
             "f208869e8aab963d5ef900b6e351977d45e92d51",
             "完美的震荡制造完美的月线收盘", "2007-07-31 16:03:53", 19)
}
EDITORIAL = ("GtXin/TDS", "references/chan_theory/070.md",
             "fc4e936b515de4c0e28bb5f7ba1182813fd29ff0")
AUG16_EDITOR_TIMES = [
    "2007-08-16 15:50:48", "2007-08-16 15:51:35",
    "2007-08-16 16:04:18", "2007-08-16 16:08:05",
    "2007-08-16 16:16:47", "2007-08-16 16:25:02",
    "2007-08-16 16:29:29", "2007-08-16 16:34:13",
    "2007-08-16 16:35:57", "2007-08-16 16:41:04",
    "2007-08-16 16:44:08", "2007-08-16 16:46:08",
    "2007-08-16 16:54:24", "2007-08-16 16:59:27"
]
MISTAKEN_EDITORIAL_AT = "2007-07-31 16:10:56"
OLD_AUTHOR_AT = "2007-07-31 16:14:47"
AUG16_AUTHOR_ACTUAL_AT = "2007-08-16 15:58:06"
AUG13_AUTHOR_AT = "2007-08-13 21:56:16"
HISTORY_FALSE_FLAGS = {
    "laohu_source_document_obtained", "laohu_all_lessons_compared",
    "kaixiang_A087_actual_second_center_definition_identified",
    "independent_B3_new_center_axiom_proven", "market_E1_E4_experiments_run"
}
HISTORY_TRUE_FLAGS = {
    "archived_html_is_not_verified_original_2007_sina_server_bytes",
    "copies_are_not_proven_independent_collection_chain",
    "no_authored_full_2007_comment_corpus_proven",
    "no_automatic_authorship_authentication_from_display_name",
    "zero_l70_archive_host_blocks_not_proof_historical_zero",
    "editorial_order_not_original_post_order",
    "editor_july_time_not_actual_author_reply_time"
}


def require(condition, message):
    if not condition:
        raise ValueError("L70_TIME_ROLES_V492: " + message)


def normalize_time(time):
    value = time.strip().replace("/", "-")
    match = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2}) (\d{2}):(\d{2}):(\d{2})", value)
    require(match is not None, "malformed timestamp")
    y, m, d, hh, mm, ss = match.groups()
    return f"{int(y):04d}-{int(m):02d}-{int(d):02d} {hh}:{mm}:{ss}"


def expected_records():
    rows = [{
        "record_id": "E00", "editorial_author_label_at": AUG13_AUTHOR_AT,
        "editorial_label_style": "INLINE_UNMARKED",
        "actual_author_reply_at": AUG13_AUTHOR_AT,
        "original_post_id": "AUG13",
        "match_status": "SAME_REPLY_TIME_OTHER_POST",
        "time_label_is_author_reply": True
    }]
    all_times = AUG16_EDITOR_TIMES[:2] + [MISTAKEN_EDITORIAL_AT] + AUG16_EDITOR_TIMES[2:]
    for i, time in enumerate(all_times, 1):
        mistaken = time == MISTAKEN_EDITORIAL_AT
        rows.append({
            "record_id": f"E{i:02d}", "editorial_author_label_at": time,
            "editorial_label_style": "BOLD_AUTHOR_LINE",
            "actual_author_reply_at": AUG16_AUTHOR_ACTUAL_AT if mistaken else time,
            "original_post_id": "AUG16",
            "match_status": ("NESTED_JUL31_QUESTION_TIME_MISTAKEN_FOR_AUG16_AUTHOR_TIME"
                             if mistaken else "SAME_REPLY_TIME_OTHER_POST"),
            "time_label_is_author_reply": not mistaken
        })
    return rows


def audit(catalog, root=ROOT):
    require(catalog.get("schema_version") == 1 and catalog.get("version") == "4.92.0"
            and catalog.get("id") == "CHANLUN-L70-ALL-EDITORIAL-AUTHOR-BLOCKS-REHOSTED-TIME-ROLES-V492",
            "identity/version")
    e = catalog["editorial_source"]
    require((e["repo"], e["path"], e["git_blob_sha"]) == EDITORIAL, "editorial blob")
    require((e["author_attributed_block_total"], e["inline_unmarked_block_count"],
            e["bold_author_header_block_count"]) == (16, 1, 15),
            "editorial counts")
    hosts = catalog["original_post_archives"]
    require(set(hosts) == set(EXPECTED_HOSTS), "all four origin posts required")
    for post, expected in EXPECTED_HOSTS.items():
        a = hosts[post]
        require(tuple(a[k] for k in (
            "repo", "path", "git_blob_sha", "article_title",
            "article_published_at", "archived_author_host_block_count"
        )) == expected, "host source identity " + post)
    require(catalog["author_attributed_entries"] == expected_records(),
            "each one of 16 editorial labels and parent reply times must match")
    receipts = catalog["tallies"]
    demand = {
        "editorial_author_attributed_entries": 16,
        "explicitly_labelled_entries": 15,
        "inline_unmarked_entries": 1,
        "exact_editorial_author_time_matches_different_post": 15,
        "mislabeled_question_time_entries": 1,
        "mapped_actual_author_replies_from_aug13": 1,
        "mapped_actual_author_replies_from_aug16": 15,
        "archived_aug16_total_host_replies": 20,
        "archived_aug13_total_host_replies": 6,
        "archived_jul31_total_host_replies": 19,
        "archived_lesson70_host_replies": 0,
        "source_post_count": 4,
    }
    require(receipts == demand, "tallies inflated, deduplicated or mismatched")
    q = catalog["historical_question_time_disambiguation"]
    require(q == {
        "editorial_record_id": "E03",
        "incorrectly_displayed_under_author": MISTAKEN_EDITORIAL_AT,
        "time_role_of_that_string": "JUL31_QUESTION_TIME_COPIED_INTO_AUG16_COMMENTER_QUOTE",
        "historical_original_post": "JUL31",
        "historical_questioner": "新浪网友",
        "historical_question_at": MISTAKEN_EDITORIAL_AT,
        "historical_original_author_reply_at": OLD_AUTHOR_AT,
        "august_quote_questioner": "蓝羽",
        "august_question_at": "2007-08-16 15:48:44",
        "august_actual_author_reply_at": AUG16_AUTHOR_ACTUAL_AT,
        "august_original_post": "AUG16",
        "display_record_time_is_original_author_reply_time": False,
        "text_copy_does_not_certify_sina_2007_bytes": True,
    }, "July question vs original answer vs August answer role confusion")
    prior = catalog["prior_art"]
    require(prior["v491"] == "catalog/chanlun_l70_comment_host_adjudication_v491.json"
            and prior["v490"] == "catalog/chanlun_108_author_uid_reply_baseline_v490.json"
            and prior["v491_first_two_cross_host_examples_are_not_new_discoveries"] is True
            and prior["new_contribution"] ==
            "FULL_16_EDITORIAL_BLOCK_ORIGINAL_POST_RECONCILIATION_AND_QUESTION_VS_AUTHOR_TIME_CORRECTION",
            "prior-art attribution")
    v491 = json.loads((root/prior["v491"]).read_text(encoding="utf-8"))
    require(v491["version"] == "4.91.0"
            and v491["lesson70"]["archival_raw"]["git_blob_sha"] == hosts["L70"]["git_blob_sha"]
            and v491["lesson70"]["editor_compilation"]["git_blob_sha"] == e["git_blob_sha"]
            and len(v491["actual_reply_hosts"]) == 2, "v4.91 archive baseline")
    v490 = json.loads((root/prior["v490"]).read_text(encoding="utf-8"))
    lesson70 = next(x for x in v490["records"] if x["lesson"] == 70)
    require(v490["version"] == "4.90.0" and lesson70["author_uid_confirmed_count"] == 0,
            "v4.90 source coverage guard")
    flags = catalog["source_limits"]
    require(set(flags) == HISTORY_FALSE_FLAGS | HISTORY_TRUE_FLAGS
            and all(flags[k] is False for k in HISTORY_FALSE_FLAGS)
            and all(flags[k] is True for k in HISTORY_TRUE_FLAGS), "unproven claims promoted")
    require(catalog["research_gates"] == {
        "A087": "OPEN", "A016": "OPEN", "F01": "OPEN",
        "OB38": "OPEN", "OB99": "OPEN", "E1_E4": "NOT_RUN"
    }, "research state promoted")
    require(catalog["report"] ==
            "other_views/chanlun/speaker-unknown-001/IDEA_L70_COMPLETE_EDITORIAL_REPLY_TIME_ROLES_V492.md",
            "report location")
    report = (root/catalog["report"]).read_text(encoding="utf-8")
    require(all(q in report for q in (
        "2007-07-31 16:10:56", "2007-07-31 16:14:47",
        "2007-08-16 15:58:06", "16处", "A087", "NOT_RUN"
    )), "missing case explanation in report")
    return {"status": "ALL_16_AUTHOR_BLOCKS_MAPPED_WITH_ONE_TIME_ROLE_CORRECTION",
            "editorial_blocks": 16, "direct_other_host_time_matches": 15,
            "editorial_question_timestamp_in_author_heading": 1,
            "candidate_l70_original_comment_replies": 0,
            "exact_historical_sina_comment_authentication": False,
            "A087": "OPEN"}


def actual_host_blocks(raw):
    """Read only *elements* with true host class, never CSS/JS/header references."""
    blocks = re.findall(r'<div\s+class=["\']divReplyIsHostTrue["\'][^>]*>(.*?)</fieldset>',
                        raw, re.S | re.I)
    out = []
    for block in blocks:
        name = re.search(r'<span\s+class=["\']author["\']\s*>(.*?)</span>', block, re.S | re.I)
        when = re.search(r'<span\s+class=["\']pubtime["\']\s*>(.*?)</span>', block, re.S | re.I)
        require(name is not None and when is not None, "unparseable marked author block")
        text = html.unescape(re.sub(r"<[^>]+>", " ", block)).replace("\xa0", " ")
        out.append({"author": html.unescape(name.group(1)).strip(),
                    "author_at": normalize_time(when.group(1)),
                    "text": re.sub(r"\s+", "", text)})
    return out


def actual_host_article(raw):
    title = re.search(r"<title>(.*?)</title>", raw, re.S | re.I)
    pub = re.search(r'<span\s+class=["\']pubtime["\']\s*>(.*?)</span>', raw, re.S | re.I)
    require(title is not None and pub is not None, "missing article title or published clock")
    return html.unescape(title.group(1)).strip(), normalize_time(pub.group(1))


def parse_editorial_labels(text):
    labelled = re.findall(
        r"\*\*缠中说禅\*\*：\s*(2007-\d{2}-\d{2} \d{2}:\d{2}:\d{2})",
        text)
    inline = re.findall(r"(?<!\*)缠中说禅\s+(2007-08-13 21:56:16)", text)
    require(len(inline) == 1, "missing or duplicated original Aug13 inline label")
    return [inline[0]] + labelled


def git_blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def verify_snapshot_dir(catalog, folder, verify_blobs=False):
    filenames = {
        "L70": "lesson070.html", "AUG13": "aug13.html",
        "AUG16": "aug16.html", "JUL31": "jul31.html",
    }
    src = Path(folder)
    posts = {}
    for post, filename in filenames.items():
        raw = (src / filename).read_bytes()
        if verify_blobs:
            require(git_blob_sha(raw) == catalog["original_post_archives"][post]["git_blob_sha"],
                    "actual Git blob bytes disagree " + post)
        decoded = raw.decode("utf-8-sig")
        meta = catalog["original_post_archives"][post]
        require(actual_host_article(decoded) ==
                (meta["article_title"], meta["article_published_at"]),
                "wrong original host document " + post)
        authors = actual_host_blocks(decoded)
        require(len(authors) == meta["archived_author_host_block_count"],
                "raw host reply block count mismatch " + post)
        require(all(x["author"] == "缠中说禅" for x in authors),
                "an unrelated author inserted under host marker " + post)
        posts[post] = authors
    editor_raw = (src/"editorial070.md").read_bytes()
    if verify_blobs:
        require(git_blob_sha(editor_raw) == catalog["editorial_source"]["git_blob_sha"],
                "editorial Git blob differs")
    editor = editor_raw.decode("utf-8-sig")
    require("教你炒股票70" in editor, "wrong editorial document")
    labels = parse_editorial_labels(editor)
    require(labels == [x["editorial_author_label_at"]
                       for x in catalog["author_attributed_entries"]],
            "16 editorial labels/order/time mismatch")
    actual_by_post = {p: [x["author_at"] for x in arr] for p, arr in posts.items()}
    for row in catalog["author_attributed_entries"]:
        require(actual_by_post[row["original_post_id"]].count(row["actual_author_reply_at"]) == 1,
                "missing/duplicated original author time " + row["record_id"])
        require(row["actual_author_reply_at"] not in actual_by_post["L70"],
                "original L70 wrongly contains rehosted reply " + row["record_id"])
    require(MISTAKEN_EDITORIAL_AT not in actual_by_post["JUL31"],
            "July31 question time must not be misread as author's own time")
    july = next(x for x in posts["JUL31"] if x["author_at"] == OLD_AUTHOR_AT)
    aug = next(x for x in posts["AUG16"] if x["author_at"] == AUG16_AUTHOR_ACTUAL_AT)
    require(re.sub(r"\s+", "", MISTAKEN_EDITORIAL_AT) in july["text"]
            and "新浪网友" in july["text"], "old question time/identity missing from July response")
    require(re.sub(r"\s+", "", MISTAKEN_EDITORIAL_AT) in aug["text"]
            and "蓝羽" in aug["text"]
            and "2007-08-1615:48:44" in aug["text"],
            "August answer must contain user's nested July quote and August question time")
    require("2007-08-16 15:58:06" not in labels,
            "editorial already contains correct August timestamp - case changed")
    return {"status":"FIVE_LOCAL_ARCHIVES_CROSSCHECKED",
            "blocks":len(labels),"timestamp_role_corrected":1,
            "actual_author_host_distribution":{"AUG13":1,"AUG16":15,"L70":0},
            "verify_exact_git_bytes":bool(verify_blobs),
            "historical_2007_sina_identity_certified":False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    p.add_argument("--snapshot-dir", type=Path, default=None)
    p.add_argument("--verify-git-blobs", action="store_true")
    args = p.parse_args()
    require(not args.verify_git_blobs or args.snapshot_dir is not None,
            "--verify-git-blobs requires --snapshot-dir")
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    out = {"catalog": audit(data)}
    if args.snapshot_dir is not None:
        out["snapshots"] = verify_snapshot_dir(data, args.snapshot_dir,
                                                verify_blobs=args.verify_git_blobs)
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
