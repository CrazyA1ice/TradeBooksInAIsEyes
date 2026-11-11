"""V4.43: finite-prefix type and clock audit for nested micro retraces and bottom pan.

UNVERIFIED synthetic/declared structure ONLY. No real-market or author-exit oracle.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/"catalog/chanlun_minimum_pan_exit_nested_retrace_v443.json"
REPORT=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/MINIMUM_PAN_END_NESTED_RETRACE_AND_BASE_GAP_V443.md"

def req(ok, reason):
    if not ok:
        raise ValueError("V443_NESTED_PAN_REJECTED: "+reason)

def ordinal(x):
    req(type(x) is int and x>=0, "time/level must be nonnegative integer")
    return x

def inspect_nested(spec, scenario):
    op=spec["bounded_research_model"]
    req(op["source_class"]=="ONLY_SYNTHETIC_EXTERNAL_DECLARATIONS_NOT_MARKET_AUTHENTICATION",
        "unverified source boundary")
    req(op["one_parent_level"]==1 and op["child_level"]==0,
        "only one synthetic L1/L0 example")
    req(op["one_parent_id"]=="PARENT_RETRACE_001" and
        op["frozen_policy"]=="SYNTHETIC_RANK_POLICY_V443", "frozen parse scope")
    asof=ordinal(scenario["asof"])
    count=ordinal(scenario["include_count"])
    req(count<=len(spec["synthetic_events"]),"prefix length")
    events=[dict(x) for x in spec["synthetic_events"][:count]]
    change=scenario.get("amend")
    if change:
        i=ordinal(change["index"])
        req(i<len(events),"amend reference")
        events[i]["declared_complete"]=change["declared_complete"]
    ids=set()
    last_end=last_known=-1
    visible=[]
    for x in events:
        req(x["id"] not in ids and isinstance(x["id"],str),"duplicate micro id")
        ids.add(x["id"])
        req(x["parent_id"]==op["one_parent_id"] and x["level"]==op["child_level"]
            and x["source"]=="SYNTHETIC_UNVERIFIED_MICRO", "parent/level/source identity")
        req(x["role"] in ("MICRO_COMPONENT","MICRO_RETRACE"), "micro role")
        req(type(x["declared_complete"]) is bool,"boolean declared only")
        ended=ordinal(x["history_end"])
        known=ordinal(x["first_known"])
        req(ended>last_end and known>last_known and known>=ended,
            "strictly monotone physical and first-known time")
        last_end,last_known=ended,known
        if known<=asof:
            visible.append(x)
    if any(x["declared_complete"] is False for x in visible):
        return result("LOWER_COMPONENT_UNFINISHED", visible)
    if len(visible)<3:
        return result("WAITING_MINIMUM_THREE_COMPONENTS", visible)
    receipt=scenario.get("finish_receipt")
    if receipt is None:
        return result("CAN_FINISH_NOT_ACTUALLY_CERTIFIED",visible)
    req(receipt["parent_id"]==op["one_parent_id"] and
        receipt["role"]=="UNVERIFIED_EXTERNAL_PARENT_EXIT",
        "caller cannot forge verified author source")
    first=ordinal(receipt["first_known"])
    req(first>=max(x["first_known"] for x in visible),
        "parent finish cannot arrive before its used child evidence")
    if first>asof:
        return result("AWAITING_EXTERNAL_PARENT_FINISH",visible)
    return result("ONE_PARENT_FINISH_CONDITIONAL_NOT_AUTHENTICATED",visible,first)

def result(state,visible,first=None):
    return {"state":state,"observed_micro_components":len(visible),
            "observed_micro_retraces":sum(x["role"]=="MICRO_RETRACE" for x in visible),
            "represented_parent_movements":1 if visible else 0,
            "conditional_parent_first_known":first,
            "market_authenticated":False,"author_theorem_proved":False}

def bottom_pan_blocked(spec):
    d=spec["root_panzheng"]
    req(d["parent_level"]==0 and d["would_require_child_level"]==-1 and
        not d["negative_level_author_initializer_supplied"] and
        d["center_exists_after_third_identical_trade"] and
        d["center_does_not_force_reversal"] and
        d["no_claim_of_theory_inconsistency"],"lowest strictly typed frontier")
    req(d["only_general_exit_rule"]==
        "PAN_FINISH_DEPENDS_ON_THIRD_POINT_WITH_COMPLETE_CHILD_AT_LEVEL_MINUS_ONE",
        "no invented base exit")
    return d["result"]

def audit(spec, report,root=ROOT):
    req(spec["id"]=="CHANLUN-MINIMUM-PAN-EXIT-NESTED-RETRACE-20070320-21-V443"
        and spec["version"]=="4.43.0","identity")
    replies=spec["reply_evidence"]
    req(len(replies)==4 and [x["reply_at"] for x in replies]==[
        "2007-03-20 17:39:28","2007-03-20 18:16:44",
        "2007-03-20 18:55:11","2007-03-21 16:56:34"
        ],"different primary reply timestamps / chronological order")
    req([x["question_at"] for x in replies]==[
        "2007-03-20 16:02:35","2007-03-20 17:35:58",
        "2007-03-20 18:49:09","2007-03-21 16:49:31"
        ] and all(x["reply_at"]>x["question_at"] for x in replies),
        "question / answer provenance order")
    req(all(x["role"]=="SECONDARY_ARCHIVED_AUTHOR_ATTRIBUTED_REPLY_NOT_ORIGINAL_SINA_BYTES"
            for x in replies) and
        [x["page"] for x in replies]==[
            "https://chzhshch.blog/confucius/58/"]*3+[
            "https://chzhshch.blog/stocks/038/"],
        "provenance sources not primary 2007 bytes")
    author=spec["other_primary_source"]
    req(author["kind"]=="DIRECT_AUTHOR_SINA_LESSON38_MAIN_BODY_ONLY"
        and not author["comments_from_2007_original_sina_bytes_verified"],
        "visible Sina lesson body is not original comments")
    anchors=spec["original_author_lessons"]
    req(len(anchors)==13 and len({(x["lesson"],x["id"]) for x in anchors})==13,
        "13 distinct lesson author-source claim anchors")
    for a in anchors:
        f=root/("knowledge/evidence/chanlun_lesson%03d.json"%a["lesson"])
        claim=json.loads(f.read_text(encoding="utf-8"))
        selected=[x for x in claim["claims"] if x["kind"]=="SOURCE" and x["id"]==a["id"]]
        req(len(selected)==1 and set(a["pages"]).issubset(set(selected[0]["pdf_pages"])),
            "PDF source pin missing "+a["id"])
    typed={x["code"]:x for x in spec["typed_distinctions"]}
    req(len(typed)==6 and set(typed)=={"B0","C1","C2","C3","C4","C5"},
        "six distinct source type distinctions")
    req(typed["B0"]["does_not_imply"]=="LOWEST_PAN_FINAL_END"
        and typed["C1"]["does_not_imply"]=="PAN_FINISHED_NOW"
        and typed["C4"]["does_not_imply"]=="AUTOMATIC_PARENT_FINISH_CLOCK",
        "do not turn construction permission into completion")
    op=spec["bounded_research_model"]
    req(all(op[x] is True for x in (
        "minimum_three_lower_components_for_eligibility",
        "two_micro_observations_not_two_parent_complete_retraces",
        "external_parent_finish_receipt_is_unverified",
        "first_confirm_time_cannot_precede_children_or_declared_exit",
        "automatic_movement_completion_from_center_present",
        "strict_bottom_third_point_with_child_level_negative_is_undefined",
        "no_complete_f01_oracle_available"
        ) if x!="automatic_movement_completion_from_center_present")
        and op["automatic_movement_completion_from_center_present"] is False,
        "missing scope and no-false-completion gates")
    cases=spec["example_receipts"]
    req(len(cases)==8 and len({x["id"] for x in cases})==8, "8 adversarial prefixes")
    for c in cases:
        if c["expected"]=="REJECT_TEMPORAL_CERTIFICATE":
            try:
                inspect_nested(spec,c)
            except ValueError:
                pass
            else:
                raise ValueError("V443_NESTED_PAN_REJECTED: accepted early exit evidence")
        else:
            res=inspect_nested(spec,c)
            req(res["state"]==c["expected"] and not res["market_authenticated"]
                and not res["author_theorem_proved"],
                "synthetic prefix result "+c["id"])
    five=inspect_nested(spec,cases[2])
    req(five["observed_micro_components"]==5 and
        five["observed_micro_retraces"]==2 and
        five["represented_parent_movements"]==1,
        "micro twice remains one parent in chosen synthetic trace")
    known=inspect_nested(spec,cases[4])
    req(known["conditional_parent_first_known"]==12,
        "do not predate micro-to-parent certification")
    req(bottom_pan_blocked(spec)==
        "BLOCKED_GENERIC_THIRD_POINT_AT_ABSOLUTE_F1_BASE_NO_FINISHED_NEGATIVE_LEVEL_CHILD",
        "lowest level must not invent negative level")
    flags=spec["provenance_flags"]
    req(len(flags)==7 and all(x is False for x in flags.values()),
        "unverified sources not auto-upgraded")
    req(spec["proof_status"]=={"F01":"OPEN","OB38":"OPEN","OB99":"OPEN",
        "market":"NOT_RUN"},"never close global proof without full oracle")
    req(spec["status"]==
        "NESTED_MICRO_RETRACE_DISTINGUISHED_FROM_PARENT_FINISH_AND_BASE_PAN_GAP_LOCALIZED",
        "research conclusion scope")
    for word in ("2007-03-20 18:16:44","2007-03-20 18:55:11",
                 "2007-03-21 16:56:34","次次级别","a0","第35课",
                 "最低盘整","负一级","F01","NOT_RUN"):
        req(word in report,"reader report missing "+word)
    return {"status":"NESTED_RETRACE_AND_ABSOLUTE_BASE_EXIT_GAP_AUDITED",
            "dated_author_attributed_replies":len(replies),
            "source_claim_pins":len(anchors),
            "synthetic_prefix_checks":len(cases),
            "bottom_pan":"OPEN_NO_NEGATIVE_LEVEL_CHILD_AUTHORIZATION",
            "real_market":"NOT_RUN"}

if __name__=="__main__":
    print(json.dumps(audit(json.loads(SPEC.read_text(encoding="utf-8")),
                          REPORT.read_text(encoding="utf-8")),ensure_ascii=False))
