#!/usr/bin/env python3
"""Deterministic whole-108-lesson provenance crosswalk for the unified book study.

Reads all 108 canonical first-pass analyses and evidence cards, reconciles
volume PDF SHA and physical-page source index, then emits an all-lesson
SOURCE-summary atlas. No PDF pages/images, OCR, market or external APIs are read.
An atlas row documents existing research, NEVER independently authenticates
authorship, figures, real returns or a formal proof.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"catalog/chanlun_lesson_index.json"
INVENTORY=ROOT/"reports/source_inventory/chanlun_20261107_verified.json"
MANUSCRIPT=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_INTEGRATED_STUDY.md"
ATLAS=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_108_SOURCE_ATLAS.md"
FIRST_PASS="SOURCE_CARD_FIRST_PASS_NOT_FULL_TEXT_OR_IMAGE_AUDIT"
TOPIC_MARKERS=("原文的论证主线","定义与递归","时间与因果","规则版本",
               "可操作性与风险","全书结论与未决事项")
MAX_SUMMARY=140


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check(ok,message):
    if not ok:
        raise ValueError(message)


def cleaned(s):
    check(type(s) is str and bool(s.strip()),"Missing source summary")
    return re.sub(r"\s+"," ",s).replace("|","／").replace("【","〔").replace("】","〕").strip()


def records():
    idx=load(INDEX)
    inv=load(INVENTORY)
    check(idx["lesson_count"]==108 and idx["volume_count"]==5 and
          len(idx["volumes"])==5,"Expected five PDF volumes and 108 lessons")
    invfiles={x["path"]:x for x in inv["volumes"]}
    used=set()
    found=[]
    for vol in idx["volumes"]:
        check(vol["path"] in invfiles and
              invfiles[vol["path"]]["sha256"]==vol["sha256"] and
              invfiles[vol["path"]]["page_count"]==vol["pdf_page_count"],
              "PDF source inventory SHA/page count does not match original index")
        current=vol["volume"]
        for item in vol["lessons"]:
            n=item["lesson"]
            check(type(n) is int and n not in used and
                  1<=n<=108,"Duplicate or invalid lesson source identity")
            used.add(n)
            sourcepath=ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json"
            chapter=ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md"
            check(sourcepath.is_file() and chapter.is_file(),
                  f"Missing canonical evidence/analysis lesson {n}")
            raw=sourcepath.read_bytes()
            evidence=json.loads(raw)
            src=evidence["source"]
            check(src.get("path")==vol["path"] and
                  src.get("sha256")==vol["sha256"],
                  f"Lesson {n} evidence original PDF SHA/path mismatch")
            evidence_pages=src.get("pdf_pages") or []
            check(type(evidence_pages) is list and
                  len(evidence_pages)>0 and
                  item["start_pdf_page"] in evidence_pages,
                  f"Lesson {n} source page interval lacks title start")
            claims=evidence.get("claims")
            check(type(claims) is list and len(claims)>0,
                  f"Lesson {n} lacks an evidence claim ledger")
            ids=[x["id"] for x in claims]
            check(len(ids)==len(set(ids)),f"Lesson {n} duplicate claim identifiers")
            author=[x for x in claims if str(x.get("kind",x.get("type",""))).upper()=="SOURCE"]
            check(author,f"Lesson {n} has no SOURCE-type first pass claim")
            first=author[0]
            pages=first.get("pdf_pages") or first.get("pages") or []
            check(type(pages) is list and len(pages)>0 and
                  all(type(p) is int and 1<=p<=vol["pdf_page_count"] for p in pages),
                  f"Lesson {n} first source claim invalid physical-page reference")
            summary=cleaned(first.get("summary") or first.get("statement") or first.get("claim"))
            check(len(chapter.read_text(encoding="utf-8"))>300,
                  f"Lesson {n} is not a usable first-pass chapter")
            hypotheses=[x for x in claims if "HYPOTHESIS" in
                        str(x.get("kind",x.get("type",""))).upper()]
            found.append({"lesson":n,"title":cleaned(item["title"]),
                "volume":current,"page":item["start_pdf_page"],
                "pdf_path":vol["path"],"pdf_sha256":vol["sha256"],
                "claim_id":first["id"],"claim_pages":pages,
                "claim_summary":summary,"source_claims":len(author),
                "hypothesis_claims":len(hypotheses),
                "source_card_sha256":hashlib.sha256(raw).hexdigest(),
                "status":FIRST_PASS})
    check(used==set(range(1,109)) and len(found)==108,
          "Original lesson sequence incomplete, repeated or out of order")
    found.sort(key=lambda x:x["lesson"])
    check([x["lesson"] for x in found]==list(range(1,109)),
          "Original chapter order inconsistent")
    return found


def atlas(rows):
    s=["# 《缠论》108课｜全文统一研究的逐课原文证据索引",
       "",
       "> **研究性质**：以下108行来自仓库现有原PDF目录与108张首轮证据卡的首条 `SOURCE` 摘要；",
       "> 逐课都有对应研究稿、PDF物理起始页、来源卷SHA和证据卡内容哈希。",
       "> `SOURCE` 是既有证据卡的标签，**不代表首次发表已独立认证、逐字校勘完整，亦不等于该主张是真实市场事实或数学定理**。",
       "> 图像细价、后附问答/编注与完成证明仍受[全书一体化研究](WHOLE_BOOK_INTEGRATED_STUDY.md)列出的缺口限制。",
       "",
       "| 课 | 原书自动提取标题 | 卷 / PDF起始页 | 本课既有SOURCE证据（首条；首轮） | 逐课研究 / 证据 |",
       "|---:|---|---|---|---|"]
    for row in rows:
        n=row["lesson"]
        p="，".join(map(str,row["claim_pages"]))
        short=row["claim_summary"][:MAX_SUMMARY]
        source_rel=f"../../../{row['pdf_path']}"
        chapter=f"../../../analyses/books/chanlun/chapters/lesson_{n:03d}.md"
        card=f"../../../knowledge/evidence/chanlun_lesson{n:03d}.json"
        s.append(f"| {n} | {row['title']} | [卷{row['volume']} p.{row['page']}]({source_rel}#page={row['page']}) | `{row['claim_id']}`（p.{p}）{short} | [逐课]({chapter}) / [原证据]({card}) |")
    s+=["",
        "## 统一验收限定",
        "",
        f"- 已登记 {len(rows)}/108 课的**首轮原文证据索引**；合计原证据卡内 `SOURCE` 标签 {sum(r['source_claims'] for r in rows)} 条、`HYPOTHESIS` 标签 {sum(r['hypothesis_claims'] for r in rows)} 条（本表不复制所有主张）。",
        "- **首轮研究≠全文逐字复核终审**；自动标题/首发边界、低文本图页、后期编注、图中数值仍可有局限。",
        "- 不能从首个SOURCE摘要推断该课所有来源片段都经作者身份与发表时间验证；不由源码标签推出作者定理已获证明。",
        "- 未读取真实行情，未进行真实回测，任何盈利或系统普适性命题均为未验证主张。",
        "- 此文件由 `python -B tools/audit_chanlun_whole_book_integrated.py --render` 确定性生成；生成时会逐条重新验证108课源SHA与连续课号。",
        ""]
    return "\n".join(s)


def verify_manuscript(rows):
    check(MANUSCRIPT.is_file(),"Missing unified whole-book manuscript")
    body=MANUSCRIPT.read_text(encoding="utf-8")
    for mark in TOPIC_MARKERS:
        check(mark in body,"Missing a full-book synthesis topic: "+mark)
    for word in ("第1—108课","SOURCE","EDITORIAL","INFERENCE",
                 "HYPOTHESIS","NOT_RUN","第108课","第35课",
                 "第38课","第99课","逐课证据索引"):
        check(word in body,"Whole-book manuscript missing claim/gap label: "+word)
    check("收益已证明" not in body and
          "所有图像已逐项核准" not in body,
          "Unsupported full-book certification")
    check(len(body)>12000,"Unified manuscript insufficiently developed")
    return len(body)


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--render",action="store_true",
                     help="Print the complete reproducible Markdown 108-source atlas")
    cli.add_argument("--check-atlas",action="store_true",
                     help="Compare committed atlas verbatim to re-derived 108 cards")
    args=cli.parse_args()
    rows=records()
    generated=atlas(rows)
    if args.render:
        print("WHOLE_BOOK_ATLAS_BEGIN")
        print(generated)
        print("WHOLE_BOOK_ATLAS_END")
    if args.check_atlas:
        check(ATLAS.is_file() and ATLAS.read_text(encoding="utf-8")==generated,
              "Committed whole-book 108-source atlas differs from evidence/source index")
    manuscript_chars=verify_manuscript(rows)
    print("WHOLE_BOOK_VERIFIED_JSON="+json.dumps({
        "status":"108_OF_108_FIRST_PASS_SOURCE_CARD_COVERAGE_VERIFIED_NOT_FULL_TEXT_PROOF",
        "lessons":len(rows),"volumes":len(set(x["volume"] for x in rows)),
        "source_claims":sum(x["source_claims"] for x in rows),
        "hypothesis_claims":sum(x["hypothesis_claims"] for x in rows),
        "source_index_atlas_rows":len(rows),
        "unified_manuscript_characters":manuscript_chars,
        "real_market_data_read":False,"source_pdf_images_read":False,
        "formal_uniqueness_or_profit_proven":False,
        "empirical_status":"NOT_RUN"
    },ensure_ascii=False,sort_keys=True))


if __name__=="__main__":
    main()
