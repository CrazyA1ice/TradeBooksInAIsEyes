"""Audit archived 2007 author replies about nine components versus three triple groups."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/"catalog/chanlun_recursive_center_333_author_reply_v440.json"
REPORT=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_NINEFOLD_CENTER_333_AUTHOR_REPLIES_V440.md"
def overlap(intervals):
    if not intervals or any(len(x)!=2 or x[0]>x[1] for x in intervals):
        raise ValueError("invalid ranges")
    lo=max(x[0] for x in intervals)
    hi=min(x[1] for x in intervals)
    return [lo,hi] if lo<=hi else None
def envelope(intervals):
    if not intervals or any(len(x)!=2 or x[0]>x[1] for x in intervals):
        raise ValueError("invalid ranges")
    return [min(x[0] for x in intervals),max(x[1] for x in intervals)]
def audit(s,report,root=ROOT):
    def req(cond,reason):
        if not cond: raise ValueError("AUTHOR_333_SCOPE_ERROR: "+reason)
    req(s["id"]=="CHANLUN-NINEFOLD-THREE-PLUS-THREE-PLUS-THREE-AUTHOR-REPLY-V440" and
        s["version"]=="4.40.0","identity")
    p=s["provenance"]
    req(p["expert_text_provided_by_user"] and p["archive_public_page_and_early_compilation_crosschecked"] and
        p["early_compilation_actual_pdf_pages_visually_inspected"],"visible evidence")
    for flag in ("expert_original_post_authenticated","original_sina_comments_cryptographically_authenticated",
                 "early_compilation_copyright_text_or_pdf_redistributed","laohu_pdf_or_docx_examined",
                 "new_original_108_lesson_full_verbatim_reread","actual_market_data_backtested"):
        req(p[flag] is False,"cannot upgrade unavailable "+flag)
    replies={x["id"]:x for x in s["new_author_reply_chronology"]}
    req(set(replies)=={"R0521","R0711","R0731A","R0731B","R0731C"},"reply identity set")
    req(replies["R0521"]["posted_at"]=="2007-05-21 16:41:03" and
        replies["R0711"]["posted_at"]=="2007-07-11 16:32:08" and
        replies["R0731A"]["posted_at"]=="2007-07-31 16:43:17" and
        replies["R0731B"]["posted_at"]=="2007-07-31 16:50:47" and
        replies["R0731C"]["posted_at"]=="2007-07-31 16:55:59","dated separate replies")
    req(all(x["attributed_role"]=="AUTHOR_ATTRIBUTED_ARCHIVED_REPLY_NOT_ORIGINAL_SINA_BYTES" and
             x["page_url"].startswith("https://chzhshch.blog/") and
             x["posted_at"]>x["question_at"] for x in replies.values()),
        "archive source and question times")
    witnesses={x["id"]:x for x in s["corroborating_source_layers"]}
    req(set(witnesses)=={"W1","W2","W3","W4","W5"},"witness diversity")
    pdf=witnesses["W2"]
    req(pdf["kind"]=="OLDER_EDITORIAL_PDF_COMPILATION_RESTRICTED_REDISSEMINATION" and
        pdf["physical_printed_pages"]==[164,165] and pdf["viewed_zero_index_pages"]==[162,163],
        "actual older compilation page inspection")
    req(witnesses["W5"]["kind"]=="LATER_THIRD_PARTY_INTERPRETATION_NOT_AUTHOR",
        "2025 interpreter not original author")
    req(len(s["additional_original_course_anchors"])==13,"original lessons count")
    for a in s["additional_original_course_anchors"]:
        f=root/("knowledge/evidence/chanlun_lesson%03d.json"%a["lesson"])
        card=json.loads(f.read_text(encoding="utf-8"))
        claims=[x for x in card["claims"] if x["id"]==a["id"] and x["kind"]=="SOURCE"]
        req(len(claims)==1 and set(a["pages"]).issubset(set(claims[0]["pdf_pages"])),
            "original PDF page source "+a["id"])
    o=s["operator_contract"]
    req(o["equal_output_guaranteed"] is False and
        o["author_claims_two_equally_valid_competing_center_axioms"] is False and
        o["completed_submovement_gate_required"] and o["fixed_grouping_policy_required"] and
        o["center_core_from_first_three_of_eligible_next_level_movements"] and
        o["unknown_full_algorithm_for_valid_three_group_completion"] and
        o["chart_bar_interval_never_replaces_structural_level"],"operator qualification")
    e=s["illustrative_math"]
    req(e["kind"]=="ARTIFICIAL_INTERVAL_OPERATOR_COUNTEREXAMPLE_NOT_A_CHANLUN_MARKET_SEQUENCE","toy scope")
    xs=e["raw_lower_unit_ranges"]
    req(len(xs)==9 and overlap(xs)==e["flat_nine_interval_intersection"],"raw 9-fold")
    groups=[envelope(xs[i:i+3]) for i in (0,3,6)]
    req(groups==e["three_consecutive_triple_range_envelopes"] and
        overlap(groups)==e["intersection_of_three_triple_envelopes"],"grouped schematic")
    req(e["flat_nine_interval_intersection"]!=e["intersection_of_three_triple_envelopes"],
        "operator order example")
    update=s["interpretation_update"]
    req(update["expert_identity_of_second_method"]=="STILL_UNDETERMINED" and
        update["author_discards_flat_shortcut_as_exact_general_higher_center_locator"] and
        update["second_formal_axiom_with_same_status_as_three_completed_lower_movements"]=="NOT_ESTABLISHED",
        "cannot certify second axiom")
    req({"F01_OPEN","OB38_OPEN","OB99_OPEN","REAL_MARKET_NOT_RUN",
         "COMPLETE_3PLUS3PLUS3_ENDING_POLICY_NOT_PROVED"}.issubset(s["open"]),"open proof")
    for phrase in ("2007-05-21 16:41:03","2007-07-11 16:32:08","2007-07-31 16:43:17",
                   "2007-07-31 16:50:47","[6,8]","[2,12]","老虎版","NOT_RUN"):
        req(phrase in report,"required report content "+phrase)
    return {"status":"AUTHOR_333_ARCHIVE_AND_EARLY_PDF_CONCORDANT_WITH_SCOPE_LIMITS",
            "replies":len(replies),"source_witnesses":len(witnesses),
            "course_source_pages":len(s["additional_original_course_anchors"])}
if __name__=="__main__":
    print(json.dumps(audit(json.loads(SPEC.read_text(encoding="utf-8")),
                           REPORT.read_text(encoding="utf-8")),ensure_ascii=False))
