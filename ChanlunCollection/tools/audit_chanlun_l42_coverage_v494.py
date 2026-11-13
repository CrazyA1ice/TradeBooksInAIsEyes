#!/usr/bin/env python3
"""v4.94: distinguish archived author marker counts from readable reply evidence.

A 2022 HTTrack copy of a third-party website is not original 2007 Sina bytes.
The public 963 figure is site-reported, NOT a byte-audited local corpus.
"""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog/chanlun_l42_reply_coverage_quality_v494.json"
RAW_BLOB = "6f313ad616836c43b9d55b74be6a54b480d127ac"
RAW_PATH = "raw/sina_blog/chan_fenlei/jiaonichaogupiao/519.html"
MD_PATH = "108/0497-486e105c010009l8-042.md"
MD_BLOB = "6e28604d9e1dc1b5e0a7105b1a2260bad060ba72"
EXTRA = "2007-04-07 14:52:10"
H02 = "2007-04-04 16:31:43"
EXPECTED_SITE_LESSONS = [(10,41),(28,40),(9,38),(31,35),(16,34),(23,32),(42,30),(11,29)]


def require(condition, reason):
    if not condition:
        raise ValueError("L42_REPLY_COVERAGE_V494: " + reason)


def git_blob_sha(content):
    return hashlib.sha1(b"blob "+str(len(content)).encode("ascii")+b"\0"+content).hexdigest()


def normalize_time(text):
    m = re.fullmatch(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2}) (\d{2}):(\d{2}):(\d{2})", text.strip())
    require(m is not None, "unparseable archived timestamp")
    y, mo, d, h, mi, s = m.groups()
    return f"{int(y):04d}-{int(mo):02d}-{int(d):02d} {h}:{mi}:{s}"


def archive_author_host_blocks(text):
    """Scope to real HTML <div class=...>, never CSS/JS references or guest replies."""
    candidates = re.findall(
        r'<div\s+class=["\']divReplyIsHostTrue["\'][^>]*>(.*?)</fieldset>',
        text, re.S | re.I
    )
    result = []
    for c in candidates:
        author = re.search(r'<span\s+class=["\']author["\']\s*>(.*?)</span>', c, re.S | re.I)
        pub = re.search(r'<span\s+class=["\']pubtime["\']\s*>(.*?)</span>', c, re.S | re.I)
        require(author is not None and pub is not None, "true-host block missing author or time")
        nested = re.findall(r'<div\b[^>]*>(.*?)</div>', c, re.S | re.I)
        require(len(nested) >= 2, "true-host block missing content container")
        content = html.unescape(re.sub(r'<[^>]+>', ' ', nested[-1])).replace('\xa0', ' ')
        clean = re.sub(r'\s+', '', content)
        result.append({
            "author": html.unescape(re.sub(r'<[^>]+>', '', author.group(1))).strip(),
            "at": normalize_time(html.unescape(pub.group(1))),
            "content_compact": clean
        })
    return result


def audit(catalog, root=ROOT):
    require(catalog.get("schema_version")==1 and catalog.get("version")=="4.94.0"
            and catalog.get("id")=="CHANLUN-L42-THREE_SOURCE_REPLY_COUNT_NONSEMANTIC_DELTA_V494",
            "catalog identity")
    sites = catalog["sites"]
    require(len(sites)==3 and [x["id"] for x in sites]==["STOCKSERV","FANGJ","ECZSC"],
            "must keep three distinct source roles")
    a,b,c = sites
    require(a["kind"]=="FROZEN_THIRD_PARTY_MD_WITH_UID_AND_NICKNAME"
            and (a["repository"],a["path"],a["blob_sha"],a["lesson"],a["matching_uid_author"])
            == ("stockServ/chzhshch-108-plus",MD_PATH,MD_BLOB,42,29),
            "baseline UID archive source")
    require(b["kind"]=="FROZEN_THIRD_PARTY_HOST_MARKED_HTML"
            and (b["repository"],b["commit_sha"],b["path"],b["blob_sha"],b["lesson"],b["host_marker_count"])
            == ("fangj/chan","9a0d1d08f3455e096a7aa37adb766d8555e16253",RAW_PATH,RAW_BLOB,42,30),
            "raw-style third-party HTML archive identity")
    require(c["kind"]=="CURRENT_PUBLIC_WEBSITE_SELF_REPORTED_DOUBLE_MARKER_PLUS_EXACT_AUTHOR_NAME"
            and c["url"]=="https://eczsc.com/replies?lesson=42"
            and c["methods_url"]=="https://eczsc.com/about"
            and c["archive_url"]=="https://eczsc.com/archive"
            and c["index_url"]=="https://eczsc.com/replies"
            and (c["reported_lesson42_count"],c["reported_sitewide_count"])==(30,963)
            and c["independent_source_bytes_acquired"] is False,
            "website numbers improperly upgraded to independently verified")
    require(all(x["original_sina_server_bytes_authenticated"] is False for x in sites),
            "historical server authenticity falsely claimed")
    prior=catalog["prior_art"]
    require(prior == {
        "v490":"catalog/chanlun_108_author_uid_reply_baseline_v490.json",
        "v493":"catalog/chanlun_a087_two_center_claim_triage_v493.json",
        "no_claim_sitewide_963_vs_953_proven_to_be_10_missing":True
    }, "prior-art or count-comparability guard")
    data=json.loads((root/prior["v490"]).read_text(encoding="utf-8"))
    require(data["version"]=="4.90.0"
            and data["summary"]["matching_name_and_uid_records"]==953,
            "prior global baseline")
    row=data["records"][41]
    require(row["lesson"]==42 and row["path"]==MD_PATH and row["blob_sha"]==MD_BLOB,
            "prior lesson 42 file ref")
    x=catalog["count_reconciliation"]
    require(x["lesson"]==42 and x["strict_uid_reply_time_list"]==row["author_timestamps"]
            and x["raw_host_marked_count"]==30 and x["stockserv_uid_name_count"]==29
            and x["eczsc_site_reported_count"]==30
            and x["raw_minus_stockserv"]==1 and x["common_exact_times_count"]==29
            and x["uid_only_time_list"]==[] and x["raw_only_time_list"]==[EXTRA],
            "time crosswalk or counts")
    raw=x["raw_host_reply_time_list"]
    require(len(raw)==30 and len(set(raw))==30 and
            all(normalize_time(t)==t for t in raw), "raw time list must be 30 unique normalized timestamps")
    require(set(raw)-set(row["author_timestamps"])=={EXTRA}
            and set(row["author_timestamps"])-set(raw)==set(),
            "one and only one archived host marker outside UID edition")
    for flag in ("sitewide_delta_963_minus_953_not_comparable_as_missing_reply_count",
                 "cannot_infer_nine_other_missing_replies_from_sitewide_totals",
                 "raw_snapshot_looks_2022_HTTRACK_COPY_NOT_2007_SINA_ORIGINAL"):
        require(x[flag] is True, "source/total guard: "+flag)
    require(x["semantic_new_author_explanation_count_from_raw_only"]==0,
            "invented recoverable second-center formula")
    extra=catalog["raw_only_receipt"]
    require(extra=={
        "author_time": EXTRA, "author_label":"缠中说禅", "source":"FANGJ",
        "marker_class":"divReplyIsHostTrue", "literal_body":"??????????",
        "body_character_count":10,
        "body_category":"QUESTION_MARKS_ONLY_MEANING_UNRECOVERABLE",
        "counts_as_archived_host_marked_reply":True,
        "counts_as_readable_center_definition":False,
        "counts_as_confirmed_2007_sina_authorship":False,
        "must_not_be_promoted_to_A087_second_axiom":True,
        "reason_for_question_marks_not_known":True,
    }, "unreadable archived marker misclassified")
    answer=catalog["relevant_original_author_reply"]
    require(answer=={
        "date":H02, "questioner":"asdf", "question_at":"2007-04-04 15:55:25",
        "parent_article_title":"教你炒股票42：有些人是不适合参与市场的",
        "parent_article_published_at":"2007-04-04 15:31:30",
        "question_topic":"CAN_HIGHER_TIMEFRAME_CENTER_BE_IDENTIFIED_WITHOUT_RECURSIVELY_CONFIRMING_ALL_LOWER_TIMESCALE_SEGMENTS",
        "author_reply_short_marker":"趋势看背驰，盘整看第三类买卖点",
        "found_in_stockserv_uid_list":True,"found_in_fangj_host_list":True,
        "newly_discovered_reply":False,
        "helps_H02_theory_vs_practical_workflow":True,
        "identifies_A087_second_center_definition":False,
        "proves_two_independent_center_axioms":False,
    }, "Apr4 H02 reply mischaracterized")
    require(H02 in row["author_timestamps"], "Apr4 reply absent from v4.90 base")
    other=json.loads((root/prior["v493"]).read_text(encoding="utf-8"))
    require(other["version"]=="4.93.0" and other["frontier"]["A087"]=="OPEN"
            and other["candidate_triage"][1]["id"]=="H02", "H02 prior assertion")
    top=catalog["site_index_top_lesson_counts"]
    require([(t["lesson"],t["site_reported"]) for t in top]==EXPECTED_SITE_LESSONS,
            "do not invent external site lesson counts")
    for item in top:
        l=item["lesson"]
        require(item["stockserv"]==data["records"][l-1]["author_uid_confirmed_count"],
                "site-vs-v490 per-lesson base " + str(l))
    require(catalog["evidence_caveats"] == {
        "no_2007_sina_server_original_comment_bytes":True,
        "no_independence_of_public_mirrors_established":True,
        "no_full_site_963_record_by_record_download_or_verification":True,
        "no_lesson42_semantic_second_center_definition_from_question_marks":True,
        "no_kaixiang_A087_original_reply_identified":True,
        "no_laohu_edition_pdf_docx_acquired":True,
        "no_market_backtest_run":True,
    }, "unproven claims")
    require(catalog["state"]=={
        "A087":"OPEN","A016":"OPEN","F01":"OPEN",
        "OB38":"OPEN","OB99":"OPEN","E1_E4":"NOT_RUN"
    }, "research state")
    require(catalog["report"]=="other_views/chanlun/speaker-unknown-001/IDEA_L42_AUTHOR_REPLY_COVERAGE_DELTA_AND_A087_WORKFLOW_V494.md",
            "report path")
    report=(root/catalog["report"]).read_text(encoding="utf-8")
    require(all(q in report for q in ("953","963","2007-04-07 14:52:10",
            "2007-04-04", "??????????", "A087", "NOT_RUN")),
            "missing report coverage ambiguity explanation")
    return {"status":"L42_RAW_30_UID_29_UNREADABLE_ONE_DELTA",
            "host_marked":30,"strict_UID":29,"raw_only":[EXTRA],
            "new_interpretable_center_replies":0,"H02_prior_reply":H02,
            "A087":"OPEN","original_2007_Sina_server_authenticated":False}


def check_raw_html(catalog, file, verify_blob=False):
    data=Path(file).read_bytes()
    if verify_blob:
        require(git_blob_sha(data)==RAW_BLOB,"input bytes are not pinned Fangj blob")
    text=data.decode("utf-8-sig")
    title=re.search(r'<title>(.*?)</title>',text,re.S|re.I)
    require(title is not None and html.unescape(title.group(1)).strip()
            ==catalog["relevant_original_author_reply"]["parent_article_title"],
            "wrong source parent article")
    published=re.search(r'<span\s+class=["\']pubtime["\']\s*>(.*?)</span>',text,re.S|re.I)
    require(published is not None and normalize_time(published.group(1))=="2007-04-04 15:31:30",
            "wrong source parent publication time")
    blocks=archive_author_host_blocks(text)
    require(len(blocks)==30 and all(b["author"]=="缠中说禅" for b in blocks),
            "source host author marker count")
    require([b["at"] for b in blocks]==catalog["count_reconciliation"]["raw_host_reply_time_list"],
            "archived author time list drift")
    extra=[b for b in blocks if b["at"]==EXTRA]
    require(len(extra)==1 and extra[0]["content_compact"]=="??????????",
            "garbled/unknown-content extra reply is different")
    reply=[b for b in blocks if b["at"]==H02]
    require(len(reply)==1 and all(s in reply[0]["content_compact"] for s in (
        "asdf","2007-04-0415:55:25","不用一层一层",
        "趋势看背驰，盘整看第三类买卖点")),
        "missing original-snapshot practical-reply context")
    return {"status":"L42_THIRTY_REAL_HOST_MARKED_BLOCKS_CHECKED",
            "raw_only_garbled":EXTRA, "relevant_reply":H02,
            "exact_raw_git_blob":bool(verify_blob),
            "authentic_original_Sina_2007_bytes":False}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description="L42 source-specific archived author replies")
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--raw-html",type=Path)
    parser.add_argument("--verify-git-blob",action="store_true")
    options=parser.parse_args()
    require(not options.verify_git_blob or options.raw_html is not None,
            "--verify-git-blob needs --raw-html")
    obj=json.loads(CATALOG.read_text(encoding="utf-8"))
    result={"catalog":audit(obj)}
    if options.raw_html is not None:
        result["source"]=check_raw_html(obj,options.raw_html,options.verify_git_blob)
    print(json.dumps(result,sort_keys=True,ensure_ascii=False))
