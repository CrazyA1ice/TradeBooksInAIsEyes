#!/usr/bin/env python3
"""v4.91: stop editorial course placement from impersonating original comment host."""
import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog/chanlun_l70_comment_host_adjudication_v491.json"
SOURCES = {
    "lesson70": ("fangj/chan", "raw/sina_blog/chan_fenlei/jiaonichaogupiao/681.html", "d0b0891704a0b1c1c561ad87d5510dd73ed7f1ad"),
    "aug13": ("fangj/chan", "raw/sina_blog/chan_fenlei/shizhengjingji/584.html", "ac9e3b569cfdf5fc4a9ca49f21e51c9ebe84bfbd"),
    "aug16": ("fangj/chan", "raw/sina_blog/chan_fenlei/shizhengjingji/680.html", "06ffc2f7781e8e15725cf63621fbcb8dbdd48a81"),
    "editorial": ("GtXin/TDS", "references/chan_theory/070.md", "fc4e936b515de4c0e28bb5f7ba1182813fd29ff0"),
}
ORIGINAL = {
    "AUG13_215616": ("2007-08-13 21:56:16", "2007-08-13 21:40:22",
                       "深潜江湖", "41与1，本ID对二级市场兴趣已失",
                       "2007-08-13 21:26:14", "aug13"),
    "AUG16_155048": ("2007-08-16 15:50:48", "2007-08-16 15:45:17",
                       "新浪网友", "全球化，没有市场可与世隔绝",
                       "2007-08-16 15:41:56", "aug16"),
}
L70_PUBLISHED = "2007-08-15 22:41:35"


def require(ok, reason):
    if not ok:
        raise ValueError("L70_COMMENT_HOST_V491: " + reason)


def audit(catalog, root=ROOT):
    require(catalog.get("schema_version") == 1 and catalog.get("version") == "4.91.0"
            and catalog.get("id") == "CHANLUN-L70-MISATTRIBUTED-REPLY-HOST-PROVENANCE-V491",
            "version/catalog")
    lesson = catalog["lesson70"]
    require((lesson["id"], lesson["published_at"], lesson["article_title"]) ==
            ("L70", L70_PUBLISHED, "教你炒股票70：一个教科书式走势的示范分析"), "lesson parent")
    raw = lesson["archival_raw"]
    require((raw["repo"], raw["path"], raw["git_blob_sha"]) == SOURCES["lesson70"],
            "actual lesson70 snapshot")
    require(raw["article_datetime"] == "2007/8/15 22:41:35"
            and raw["exact_host_reply_div_count"] == 0, "lesson70 archive host count")
    comp = lesson["editor_compilation"]
    require((comp["repo"], comp["path"], comp["git_blob_sha"]) == SOURCES["editorial"],
            "editorial location")
    require(comp["source_role"] == "EDITION_WITH_TRANSPLANTED_CROSS_ARTICLE_AUTHOR_ATTRIBUTED_REPLIES",
            "misstated editorial role")
    ref = lesson["baseline"]
    require(ref["repo"] == "stockServ/chzhshch-108-plus"
            and ref["path"] == "108/0637-486e105c01000c86-070.md"
            and ref["git_blob_sha"] == "ffed7ff2175af35b55e9318ce2f428f8737fa305"
            and ref["uid_reply_count"] == 0
            and ref["reference"] == "catalog/chanlun_108_author_uid_reply_baseline_v490.json",
            "v4.90 lesson file")
    v490 = json.loads((root/ref["reference"]).read_text(encoding="utf-8"))
    matching = next(x for x in v490["records"] if x["lesson"] == 70)
    require(matching["author_uid_confirmed_count"] == 0 and matching["comments_total"] == 0
            and matching["blob_sha"] == ref["git_blob_sha"], "v4.90 prior source proof")
    replies = {x["id"]: x for x in catalog["actual_reply_hosts"]}
    require(set(replies) == set(ORIGINAL) and len(catalog["actual_reply_hosts"]) == 2,
            "two and only two registered misattributed receipts")
    for rid, (time, question_time, questioner, parent_title, parent_posted, snapshot_id) in ORIGINAL.items():
        x = replies[rid]
        require((x["author_at"], x["question_at"], x["questioner"], x["parent_article_title"],
                x["parent_published_at"]) == (time, question_time, questioner, parent_title, parent_posted),
                "original reply context " + rid)
        require((x["raw"]["repo"], x["raw"]["path"], x["raw"]["git_blob_sha"])
                == SOURCES[snapshot_id], "pinned original host " + rid)
        require(normalize_time(x["raw"]["host_reply_time"]) == time, "raw timestamp " + rid)
        require(x["appears_in_editorial_l70"] is True
                and x["may_belong_to_l70_original_comment_host"] is False,
                "editorial material promoted into original course comments " + rid)
        require(time != L70_PUBLISHED and parent_title != lesson["article_title"], "parent separation " + rid)
    require(replies["AUG13_215616"]["author_at"] < L70_PUBLISHED,
            "Aug13 reply cannot postdate target lesson")
    require(replies["AUG13_215616"]["why"] == "REPLY_PREDATES_L70_PUBLICATION_AND_HOST_ARTICLE_DIFFERS"
            and replies["AUG16_155048"]["why"] == "SEPARATE_AUG16_POST_REPLY_HAS_DISTINCT_PARENT",
            "evidence role changed")
    x = catalog["archive_counterexample"]
    require(set(x) == {"same_lesson_heading_does_not_imply_same_comment_host",
                       "same_author_label_does_not_imply_historical_original_identity",
                       "text_archived_under_course_does_not_mean_original_course_comments",
                       "canonical_source_keeps_no_UID_matching_l70_correct_for_that_source",
                       "do_not_merge_transplanted_replies_into_l70_same_host_count",
                       "transcript_crosspost_can_be_useful_commentary_when_labeled"}
            and all(v is True for v in x.values()), "host separation guard")
    y = catalog["false_claim_guards"]
    require(set(y) == {"original_2007_sina_comment_bytes_authenticated",
                       "gtXin_collection_proven_firsthand_or_independently_sourced",
                       "all_15_transcribed_author_blocks_proven_distinct_original_hosts",
                       "lesson70_original_total_reply_count_proven_zero",
                       "laohu_full_document_obtained", "laohu_compared_against_108_baseline",
                       "kaixiang_A087_identified_second_method", "market_real_data_backtest_run"}
            and all(v is False for v in y.values()), "false source/identity/coverage promotion")
    require(catalog["frontier"] == {"A087": "OPEN", "A016": "OPEN", "F01": "OPEN",
            "OB38": "OPEN", "OB99": "OPEN", "E1_E4": "NOT_RUN"}, "open gates")
    require(catalog["report"] == "other_views/chanlun/speaker-unknown-001/IDEA_L70_CROSS_ARTICLE_COMMENT_HOST_AUDIT_V491.md", "report path")
    body = (root/catalog["report"]).read_text(encoding="utf-8")
    require(all(x in body for x in ("2007-08-13 21:56:16","2007-08-16 15:50:48",
            "第70课", "实际宿主", "NOT_RUN", "A087")), "report proof")
    return {"status":"COMMENT_ORIGINAL_HOST_SEPARATED",
            "verified_cross_article_receipts": 2, "lesson70_archived_host_divs": 0,
            "actual_complete_historical_comment_count": "UNKNOWN",
            "A087":"OPEN"}


def normalize_time(s):
    parts = s.strip().replace("/", "-").split(" ", 1)
    require(len(parts) == 2, "invalid time")
    ymd = parts[0].split("-")
    require(len(ymd) == 3, "invalid date")
    return f"{int(ymd[0]):04d}-{int(ymd[1]):02d}-{int(ymd[2]):02d} {parts[1]}"


def archived_host_entries(source):
    """HostReply true needs a class attribute and an author span, not CSS or JS text."""
    blocks = re.findall(r'<div\b[^>]*\bclass=["\']divReplyIsHostTrue["\'][^>]*>(.*?)</fieldset>',
                        source, flags=re.S | re.I)
    found = []
    for block in blocks:
        m = re.search(r'<span\s+class=["\']author["\']\s*>(.*?)</span>', block, re.S | re.I)
        date = re.search(r'<span\s+class=["\']pubtime["\']\s*>(.*?)</span>', block, re.S | re.I)
        if m and date:
            found.append({"author": html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip(),
                          "when": normalize_time(html.unescape(date.group(1))),
                          "body": re.sub(r"\s+", "", html.unescape(re.sub(r"<[^>]+>", "", block)))})
    return found


def check_snapshot_dir(catalog, folder):
    folder = Path(folder)
    lesson_raw = (folder/"lesson70.html").read_text(encoding="utf-8")
    lesson_title = html.unescape(re.search(r"<title>(.*?)</title>", lesson_raw, re.S).group(1)).strip()
    require(lesson_title == catalog["lesson70"]["article_title"], "wrong lesson70 document")
    date = re.search(r'<span\s+class="pubtime"\s*>(.*?)</span>',lesson_raw,re.S)
    require(date is not None and normalize_time(date.group(1)) == L70_PUBLISHED, "lesson70 publication")
    require(archived_host_entries(lesson_raw) == [], "false original lesson70 host replies")
    text = (folder/"editorial70.md").read_text(encoding="utf-8")
    require("教你炒股票70" in text, "wrong editorial text")
    results={}
    for rid, (tm,qtime,questioner,parent_title,parent_pub,local) in ORIGINAL.items():
        source = (folder/(local+".html")).read_text(encoding="utf-8")
        title = html.unescape(re.search(r"<title>(.*?)</title>",source,re.S).group(1)).strip()
        published = re.search(r'<span\s+class="pubtime"\s*>(.*?)</span>',source,re.S)
        require(title == parent_title and published is not None
                and normalize_time(published.group(1)) == parent_pub, "wrong original host "+rid)
        valid = [x for x in archived_host_entries(source)
                 if x["author"]=="缠中说禅" and x["when"]==tm
                 and questioner in x["body"] and qtime in x["body"]]
        require(len(valid)==1, "attributed reply absent or ambiguous under original host "+rid)
        require(tm in text, "editorial source does not contain migrated date "+rid)
        results[rid]={"original_parent_title":parent_title,"author_reply_time":tm,
                      "editorial_time_present":True,"not_original_l70_comment":True}
    return {"status":"FOUR_LOCAL_FILES_HOST_DISTINCTION_PASSED",
            "checked_cases":results,
            "historical_server_authentication":False}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--snapshot-dir",type=Path)
    a=p.parse_args()
    c=json.loads(CATALOG.read_text(encoding="utf-8"))
    output={"catalog":audit(c)}
    if a.snapshot_dir:
        output["offline_snapshots"]=check_snapshot_dir(c,a.snapshot_dir)
    print(json.dumps(output,sort_keys=True,ensure_ascii=False))
