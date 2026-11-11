"""Provenance-sensitive adjudication of six non-equivalent Chanlun 'two methods'."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/"catalog/chanlun_second_method_disambiguation_v439.json"
REPORT=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_SECOND_CENTER_METHOD_DISAMBIGUATION_V439.md"
REQUIRED={"S1":"ALTERNATIVE_PARTITION","S2":"OBSERVATIONAL_VIEWPOINT",
          "S3":"INPUT_POLICY","S4":"RECURSIVE_BASE_CHOICE",
          "S5":"COMPETING_INTERVAL_FORMULA","S6":"MIRROR_DIRECTION_CASES"}
def ordered_intersection(intervals):
    if not intervals or any(len(x)!=2 or x[0]>x[1] for x in intervals):
        raise ValueError("only nonempty valid numeric intervals")
    lo=max(x[0] for x in intervals);hi=min(x[1] for x in intervals)
    return [lo,hi] if lo<=hi else None
def envelope(intervals):
    if not intervals or any(len(x)!=2 or x[0]>x[1] for x in intervals):
        raise ValueError("only nonempty valid intervals")
    return [min(x[0] for x in intervals),max(x[1] for x in intervals)]
def audit(s,r,root=ROOT):
    def req(test,why):
        if not test:raise ValueError("SECOND_METHOD_SCOPE_REJECTED: "+why)
    req(s.get("id")=="CHANLUN-EXPERT-SECOND-METHOD-SOURCE-DISAMBIGUATION-V439"
        and s.get("version")=="4.39.0","identity")
    p=s["provenance"]
    req(p["expert_passage_received_in_chat"] and not p["expert_author_public_post_verified"] and
        not p["second_method_unique_identity_confirmed"] and not p["original_sina_comment_bytes_verified"]
        and not p["laohu_edition_bytes_reviewed"] and not p["full_108_verbatim_reread_this_round"]
        and not p["market_data_or_backtest_run"],"unverified evidence remains bounded")
    anchors=s["original_author_evidence"]
    req(len(anchors)==16 and len({(a["lesson"],a["id"]) for a in anchors})==16,
        "author source pin inventory")
    for a in anchors:
        card=json.loads((root/("knowledge/evidence/chanlun_lesson%03d.json"%a["lesson"])).read_text(encoding="utf-8"))
        matches=[c for c in card["claims"] if c["id"]==a["id"] and c["kind"]=="SOURCE"]
        req(len(matches)==1 and set(a["pages"]).issubset(set(matches[0]["pdf_pages"])),
            "original author source or physical page")
    cand={x["id"]:x for x in s["candidate_referents"]}
    req(len(cand)==6 and {k:v["role"] for k,v in cand.items()}==REQUIRED,"six distinct candidate object types")
    req(cand["S1"]["exact_practical_comparison_in_author_body"] is True
        and cand["S1"]["author_declares_second_pure_center_definition_universally_superior"] is False,
        "lesson54 local choice not universal axiom")
    req(all(x["author_declares_second_pure_center_definition_universally_superior"] is False for x in cand.values()),
        "no substantiated global second center axiom")
    gates=s["lesson54_author_chart_checkpoints"]
    req([x["id"] for x in gates]==["D4","G5","G6","G7"] and
        all(x["future_confirmation_used"] is False for x in gates),"chronological checkpoints")
    req(gates[1]["second_cut_higher_center"]=="NOT_YET_COMPLETED" and
        gates[3]["first_cut_g7_tag"]=="THIRD_SELL" and
        gates[3]["second_cut_g7_tag"]=="CENTER_OSCILLATION_NOT_THIRD_SELL",
        "author chart labels differ at specific times")
    e=s["interval_semantic_example"]
    req(e["type"]=="INDEPENDENT_ARTIFICIAL_INTERVALS_NOT_A_LEGAL_CHANLUN_MOVEMENT_SEQUENCE",
        "toy intervals not legal author movements")
    req(ordered_intersection(e["intervals"][:3])==e["first_three_core"] and
        ordered_intersection(e["intervals"])==e["rolling_all_intersection"] and
        envelope(e["intervals"])==e["all_member_envelope"],"three interval functions")
    req(len(set(map(tuple,[e["first_three_core"],e["rolling_all_intersection"],e["all_member_envelope"]])))==3,
        "functions must visibly differ")
    req({"EXPERT_INTENDED_REFERENT_OPEN","NO_SECOND_GLOBAL_CENTER_AXIOM_PROVED",
         "F01_OPEN","OB38_OPEN","OB99_OPEN","MARKET_NOT_RUN"}.issubset(set(s["special_limits"])),"limits preserved")
    req(s["status"]=="MULTI_CANDIDATE_ADJUDICATION_NO_UNIQUE_EXPERT_REFERENT_OR_AUTHOR_SECOND_FORMULA","scope")
    for item in ("第54课","第38课","第20课","S1","S5","g7","[6,11]","[8,10]","NOT_RUN"):
        req(item in r,"report missing "+item)
    return {"status":"SIX_CANDIDATES_WITH_LESSON54_LOCAL_PREFERENCE_PINNED_NOT_GLOBAL_AXIOM",
            "author_source_anchors":len(anchors),"candidate_interpretations":len(cand),
            "lesson54_asof_checkpoints":len(gates)}
if __name__=="__main__":
    print(json.dumps(audit(json.loads(SPEC.read_text(encoding="utf-8")),
                           REPORT.read_text(encoding="utf-8")),ensure_ascii=False))
