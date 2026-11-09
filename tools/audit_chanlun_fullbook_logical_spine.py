#!/usr/bin/env python3
"""Rebuild a 108-lesson *interpretive* dependency atlas from original SOURCE cards.

Never accepts an AI reading-order / conceptual bridge as a proven logical edge.
The separate OPEN proof-frontier ledger is checked against the original
canonical OB38/OB99 readiness report. No PDF figures, OCR or market data read.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict, deque
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/"catalog/chanlun_108_fullbook_logical_spine_v1.json"
INDEX=ROOT/"catalog/chanlun_lesson_index.json"
INVENTORY=ROOT/"reports/source_inventory/chanlun_20261107_verified.json"
FORMAL=ROOT/"reports/source_inventory/chanlun_formal_proof_readiness_v1.json"
ARGUMENTS=ROOT/"catalog/chanlun_theory_argument_links_v1.json"
CONFLICTS=ROOT/"catalog/chanlun_crosslesson_consistency_v1.json"
VERSIONS=ROOT/"catalog/chanlun_rule_history_v1.json"
MANUSCRIPT=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_LOGICAL_CONTINUITY.md"
ATLAS=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_108_LOGIC_MAP.md"
README=ROOT/"deliverables/chanlun_108_acceptance/README.md"
EXPECTED_ID="CL108-READING_LOGIC-SPINE-AND-PROOF-FRONTIER-V1"
PERMITTED_GOALS={"OB38-EXIST","OB38-UNIQUE","OB38-ASOF","OB99-EXIST","OB99-LOCATION"}
PROOF_REQUIRED={"F04":"OB38-UNIQUE","F05":"OB38-ASOF",
                "F06":"OB99-EXIST","F07":"OB99-LOCATION"}
PRIMARY_ARCS=((1,11),(11,15),(15,17),(17,18),(18,20),
              (20,21),(21,53),(53,101),(101,108))
GEOMETRY_ARCS=((62,65),(65,67),(67,71),(71,78),(78,81),
               (81,84),(84,91),(91,93),(93,99),(99,108))
INDICATOR_ARCS=((15,24),(24,25),(25,50),(50,61))
SCOPES={"AI_CONCEPTUAL_READING_BRIDGE_NOT_DEDUCTIVE_PROOF"}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inline(value):
    require(type(value) is str and bool(value.strip()),"Missing textual research value")
    return re.sub(r"\s+"," ",value).replace("|","／").strip()


def verify_and_collect():
    config=load(CONFIG)
    require(config.get("schema_version")==1 and config.get("id")==EXPECTED_ID and
            config.get("scope")=="CURATED_108_CHAPTER_RESEARCH_ROLES_AND_INTERPRETIVE_BRIDGES_NOT_PROVEN_THEORY" and
            config.get("original_lesson_index")=="catalog/chanlun_lesson_index.json",
            "Original-index dependency or interpretation-only scope changed")
    for key,value in (("reading_order_only_not_logical_proof",True),
                      ("all_108_original_author_pages_fully_manually_reviewed",False),
                      ("all_figure_claims_verified",False),("all_theorems_proven",False),
                      ("all_historical_rules_frozen",False),
                      ("real_market_data_accessed",False),("market_backtesting","NOT_RUN")):
        require(config.get(key)==value,"An unsupported proof/empirical conclusion was promoted: "+key)
    original=load(INDEX)
    inv={v["path"]:v for v in load(INVENTORY)["volumes"]}
    chapters={}
    for vol in original["volumes"]:
        require(vol["path"] in inv and vol["sha256"]==inv[vol["path"]]["sha256"] and
                vol["pdf_page_count"]==inv[vol["path"]]["page_count"],
                "Original five-volume PDF SHA/page index changed")
        for item in vol["lessons"]:
            n=item["lesson"]
            require(type(n) is int and n not in chapters,"Duplicate original chapter")
            evidence=ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json"
            chapter=ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md"
            require(evidence.is_file() and chapter.is_file(),"Missing primary chapter/evidence")
            card_bytes=evidence.read_bytes()
            card=json.loads(card_bytes)
            require(card["source"]["path"]==vol["path"] and
                    card["source"]["sha256"]==vol["sha256"] and
                    item["start_pdf_page"] in card["source"]["pdf_pages"],
                    "Chapter evidence SHA/path/title physical PDF page mismatch")
            source=[x for x in card["claims"] if x.get("kind")=="SOURCE"]
            require(source and len({x["id"] for x in card["claims"]})==len(card["claims"]),
                    "Chapter missing original SOURCE anchors / duplicate claim IDs")
            first=source[0]
            first_pages=first.get("pdf_pages") or first.get("pages") or []
            require(type(first_pages) is list and first_pages and
                    all(type(p) is int and 1<=p<=vol["pdf_page_count"]
                        for p in first_pages),
                    "Original claim lacks legal physical page")
            require(len(chapter.read_text(encoding="utf-8"))>300,
                    "Chapter has no first-pass research")
            chapters[n]={
                "lesson":n,"title":inline(item["title"]),"volume":vol["volume"],
                "page":item["start_pdf_page"],"pdf_path":vol["path"],
                "pdf_sha256":vol["sha256"],"first_claim":first["id"],
                "first_summary":inline(first.get("summary") or first.get("statement") or first.get("claim")),
                "first_claim_pages":first_pages,
                "source_claim_count":len(source),
                "card_sha256":hashlib.sha256(card_bytes).hexdigest(),
            }
    require(list(sorted(chapters))==list(range(1,109)),
            "Exactly 108 source chapters required")
    phases=config.get("phases")
    require(type(phases) is list and len(phases)==11 and
            [p["id"] for p in phases]==[f"P{i:02d}" for i in range(1,12)],
            "Exactly 11 ordered research reading stages required")
    used=[]
    for p in phases:
        require(type(p["start"]) is int and type(p["end"]) is int and
                1<=p["start"]<=p["end"]<=108 and
                len(inline(p["name"]))>=4 and
                len(inline(p["interpretive_limit"]))>=12,
                "Invalid reading stage or missing source interpretation caveat")
        used.extend(range(p["start"],p["end"]+1))
    require(used==list(range(1,109)),"Every lesson must occur once and in order in a phase")
    roles=config.get("chapter_roles")
    require(type(roles) is list and len(roles)==108 and
            all(type(x) is str and len(inline(x))>=12 for x in roles),
            "108 distinct chapter interpretations are required")
    for n in range(1,109):
        chapters[n]["role"]=inline(roles[n-1])
        chapters[n]["phase"]=next(p["id"] for p in phases if p["start"]<=n<=p["end"])
    links=config.get("conceptual_links")
    require(type(links) is list and len(links)>=100,
            "Whole-book conceptual bridges do not cover core course relationships")
    pairs=set()
    forward=defaultdict(list);incoming=defaultdict(list)
    cross_phase=0
    for i,e in enumerate(links,1):
        a,b=e["from"],e["to"]
        require(e["id"]==f"L{i:03d}" and type(a) is int and type(b) is int and
                1<=a<b<=108 and e["type"] in SCOPES,
                "A conceptual edge is wrongly presented as formal author deduction")
        require((a,b) not in pairs,"Duplicate conceptual edge")
        pairs.add((a,b));forward[a].append(b);incoming[b].append(a)
        cross_phase+=int(chapters[a]["phase"]!=chapters[b]["phase"])
    require(all(pair in pairs for pair in PRIMARY_ARCS+GEOMETRY_ARCS+INDICATOR_ARCS),
            "Primary whole-book theoretical reading chain was severed")
    require(cross_phase>=20,
            "Too few conceptual cross-stage bridges to connect the whole book")
    # Readability is a graph/navigation property; it DOES NOT establish
    # the truth of any original theorem/causal edge.
    def reachable(start,end):
        seen={start};q=deque([start])
        while q:
            n=q.popleft()
            for x in forward[n]:
                if x not in seen:seen.add(x);q.append(x)
        return end in seen
    require(reachable(1,108) and reachable(62,108) and reachable(15,61),
            "No continuous conceptual path from earliest source to ending")
    frontier=config.get("proof_frontier")
    require(type(frontier) is list and len(frontier)==8 and
            [f["id"] for f in frontier]==[f"F{i:02d}" for i in range(1,9)],
            "Eight explicit proof bottlenecks required")
    readiness=load(FORMAL)
    goals={g["id"]:g for g in readiness["goals"]}
    require(set(goals)==PERMITTED_GOALS and
            readiness["certifies_theorem"] is False and
            readiness["complete_frozen_rule_ref"] is None,
            "Original OB38/OB99 blocked proof policy changed")
    for id_,goal in goals.items():
        require(goal["status"]=="BLOCKED_NOT_CERTIFIED" and
                goal["complete_frozen_rule_ref"] is None and
                all(x["status"]=="OPEN" for x in goal["proof_slots"]),
                "A formal proof slot unexpectedly marked certified: "+id_)
    for f in frontier:
        require(type(f["lessons"]) is list and len(f["lessons"])>=3 and
                all(type(n) is int and n in chapters for n in f["lessons"]) and
                len(set(f["lessons"]))==len(f["lessons"]) and
                len(f["preconditions"])>=2 and
                all(len(inline(x))>=12 for x in f["preconditions"]) and
                f["resolved"] is False,
                "Missing proof dependencies or falsely resolved frontier: "+f["id"])
        if f["id"] in PROOF_REQUIRED:
            require(f["status"]==PROOF_REQUIRED[f["id"]] and
                    f["status"] in goals,
                    "False original OB38/OB99 proof completion")
        else:
            require(f["status"].startswith("open_"),
                    "Unsupported root theorem linkage in non-formal frontier")
    arguments=load(ARGUMENTS)
    conflicts=load(CONFLICTS)
    require(len(arguments["arguments"])==16 and
            len(conflicts["entries"])==16 and
            all(x["formal_proof_completed"] is False for x in arguments["arguments"]) and
            conflicts["global_author_theory_consistent_proven"] is False and
            conflicts["global_author_theory_inconsistent_proven"] is False,
            "Whole-book logical spine must not erase prior source-controversy boundaries")
    versions=load(VERSIONS)
    require(len(versions["entries"])>=16 and
            all(x["source_displayed_at"] is None for x in versions["entries"]
                if x["role"] in ("editor_later_undated","appendix_provenance_unresolved")),
            "Undated editorial appendix cannot be backdated by this crosswalk")
    report={
        "status":"ALL_108_CHAPTER_ROLES_AND_CONCEPTUAL_BRIDGES_CONNECTED_NOT_FORMAL_THEORY_CLOSURE",
        "original_book_volumes":5,
        "source_anchored_chapters":len(chapters),
        "source_claims":sum(x["source_claim_count"] for x in chapters.values()),
        "phases":len(phases),"conceptual_bridges":len(links),
        "cross_stage_bridges":cross_phase,"unresolved_proof_frontiers":len(frontier),
        "formal_OB38_OB99_goals_still_blocked":len(goals),
        "all_research_lemmas_proven":False,"market_backtesting":"NOT_RUN"
    }
    return config,chapters,forward,incoming,report


def markdown(config,chapters,forward,incoming,report):
    out=[
        "# 《缠论》108课｜前后逻辑贯通的逐课地图",
        "",
        "> **使用方法**：每一行把原书课次、第一条既有`SOURCE`证据卡、AI对该课的理论角色和跨课研究连接放在一起。",
        "> `前驱/后继`中的编号只表示**AI研究者建议的概念阅读路径**，不是原作者认证的正式证明蕴涵。",
        "> 每一行的原PDF标题与物理起页来自自动标题索引，尚未完成全部图片/原发日期逐项终审。",
        "> **图的连通性不等于理论已经自洽、完整、可实时执行或已证明盈利**；阻断环节单列为下方八道证明关口。",
        "> 延展论证见[全书逻辑主脊](WHOLE_BOOK_LOGICAL_CONTINUITY.md)、[来源首轮索引](WHOLE_BOOK_108_SOURCE_ATLAS.md)及[跨课一致性报告](WHOLE_BOOK_THEORY_CONSISTENCY.md)。",
        "",
    ]
    for p in config["phases"]:
        out+=["",f"## {p['id']}｜{p['name']}（第{p['start']}—{p['end']}课）","",
              f"**本阶段解释限制**：{p['interpretive_limit']}","",
              "| 课及PDF原文起页 | 本课原作者SOURCE首条摘要 | 在全书中的AI研究角色 | 概念前驱 → 后继 |",
              "|---|---|---|---|"]
        for n in range(p["start"],p["end"]+1):
            x=chapters[n]
            orig=f"../../../{x['pdf_path']}#page={x['page']}"
            card=f"../../../knowledge/evidence/chanlun_lesson{n:03d}.json"
            prev="、".join(map(str,incoming[n])) if incoming[n] else "无显式前驱"
            later="、".join(map(str,forward[n])) if forward[n] else "无显式后继"
            summary=x["first_summary"][:130]
            out.append(f"| **[{n:03d} {x['title']}]({orig})**（卷{x['volume']} p.{x['page']}） | [`{x['first_claim']}`]({card})：{summary} | {x['role']} | {prev} → {later} |")
    out+=["","## 八道仍未打通的证明/来源关口（不是课程缺席）","",
          "| 关口 | 关系到的课次 | 要求额外证明的内容 | 当前状态 |",
          "|---|---|---|---|"]
    for item in config["proof_frontier"]:
        out.append(f"| `{item['id']}` {item['topic']} | "+ "、".join(map(str,item["lessons"]))+
                   " | "+"；".join(item["preconditions"])+
                   f" | **OPEN**：`{item['status']}` |")
    out+=["","## 读完整本书以后可以宣称什么？","",
         f"- 可以宣称：**第1—108课均已建立可回溯的来源卡、一个非空AI角色及明确的阶段归属**，共{report['phases']}个研究阶段、{report['conceptual_bridges']}条**解释性概念连接**；所有原始PDF卷次/页面SHA接受代码检查。",
         "- 不可以宣称：这些连接已经构成原作者完成的因果/数学证明图，或从第一课已经严格推出第108课；它们只揭示哪些对象需要连接。",
         "- 如果用户要进入真正的完整证明，首先补齐下表八道`OPEN`关口，特别是`OB38-UNIQUE`、`OB38-ASOF`、`OB99-EXIST`、`OB99-LOCATION`；数学联系不能由概念图有路可走替代。",
         "- 没有独立核实所有图像/后附出版时间，没有调用真实行情，没有回测或交易，`NOT_RUN`。",
         "- 本文由`python -B tools/audit_chanlun_fullbook_logical_spine.py --render`确定性生成；`--check-atlas`将对仓库文件进行严格字节核验。",
         ""]
    return "\n".join(out)


def verify_manuscript(config,report):
    require(MANUSCRIPT.is_file() and len(MANUSCRIPT.read_text(encoding="utf-8"))>13000,
            "Missing substantive full-book argument connecting beginning to end")
    s=MANUSCRIPT.read_text(encoding="utf-8")
    for p in config["phases"]:
        require(p["id"] in s,"Missing fully articulated reading phase "+p["id"])
    for f in config["proof_frontier"]:
        require(f["id"] in s,"Missing source proof frontier "+f["id"])
    for text in ("第1课","第108课","第38课","第99课","原文","推导",
                 "SOURCE","NOT_RUN","概念连通不等于证明连通",
                 "第三类买卖点","自同构","中枢"):
        require(text in s,"Missing essential integrated theory provenance: "+text)
    require(MANUSCRIPT.name in README.read_text(encoding="utf-8"),
            "Main 108 lesson guide must link to whole-book logical spine")
    return s


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--render",action="store_true")
    ap.add_argument("--check-atlas",action="store_true")
    opts=ap.parse_args()
    config,chapters,forward,incoming,report=verify_and_collect()
    verify_manuscript(config,report)
    atlas=markdown(config,chapters,forward,incoming,report)
    if opts.render:
        print("WHOLE_BOOK_LOGICAL_ATLAS_BEGIN")
        print(atlas)
        print("WHOLE_BOOK_LOGICAL_ATLAS_END")
    if opts.check_atlas:
        require(ATLAS.is_file() and ATLAS.read_text(encoding="utf-8")==atlas,
                "Committed 108 lesson logical atlas differs from recomputed original source cards")
    print("WHOLE_BOOK_LOGICAL_VERIFIED_JSON="+json.dumps(report,ensure_ascii=False,sort_keys=True))


if __name__=="__main__":
    main()
