"""Audit July 19/20 author Sina original-post identity, type boundaries and a0 semantics."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/"catalog/chanlun_20070720_dual_a0_original_post_v441.json"
REPORT=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_PRIMARY_SINA_DUAL_A0_THEORY_V441.md"
def audit(data,report,root=ROOT):
    def req(test,why):
        if not test: raise ValueError("AUTHOR_PRIMARY_DUAL_A0_FAIL: "+why)
    req(data["id"]=="CHANLUN-AUTHOR-20070720-DUAL-A0-INITIALIZATION-V441" and
        data["version"]=="4.41.0","id/version")
    req(data["source_role"]=="PRIMARY_SINA_DOMAIN_AUTHOR_MAIN_POST_VISIBLE_NOT_AUTHENTICATED_2007_BYTES","main source status")
    posts={p["id"]:p for p in data["primary_posts"]}
    req(set(posts)=={"JUL19","JUL20"} and
        posts["JUL19"]["url"]=="https://blog.sina.com.cn/s/blog_486e105c01000brc.html" and
        posts["JUL20"]["url"]=="https://blog.sina.com.cn/s/blog_486e105c01000bs4.html" and
        posts["JUL19"]["date"]=="2007-07-19 15:29:28" and
        posts["JUL20"]["date"]=="2007-07-20 08:26:20" and
        all(p["role"]=="AUTHOR_MAIN_POST" for p in posts.values()),"correct original blog main posts/timestamps")
    props=data["propositions"]
    req(len(props)==6 and set(x["id"] for x in props)=={"D"+str(i) for i in range(1,7)},"six claims")
    req(all(x["source"] in posts for x in props),"claim source role")
    anchors=data["course_anchors"]
    req(len(anchors)==14 and len({(x["lesson"],x["id"]) for x in anchors})==14,"original course anchors count")
    for a in anchors:
        source=root/("knowledge/evidence/chanlun_lesson%03d.json"%a["lesson"])
        card=json.loads(source.read_text(encoding="utf-8"))
        matches=[x for x in card["claims"] if x["id"]==a["id"] and x["kind"]=="SOURCE"]
        req(len(matches)==1 and set(a["pages"]).issubset(set(matches[0]["pdf_pages"])), "invalid claim/source/page: "+a["id"])
    t=data["type_contract"]
    req(t["strict_a0_source"]=="INDIVIDUAL_TRANSACTION_EXECUTIONS" and
        t["practical_a0_source"]=="FRACTAL_PEN_SEGMENT_CONSTRUCTION" and
        t["shared_recurrence_form"]=="a_n=f(a_(n-1))","two different a0, one recursive shape")
    req(not t["universal_equal_center_outputs_from_same_recurrence"]
        and not t["strict_segment_is_subordinate_finished_movement"] and
        not t["actual_trade_is_subordinate_finished_movement"] and
        not t["a_segment_finish_proves_movement_finish"]
        and t["practical_segments_may_build_lowest_center"]
        and t["requires_legal_member_and_completed_movement_before_next_recursive_center"]
        and not t["source_author_proved_a_complete_asof_market_parser"],
        "do not invent strict casts, output equality, or a parser")
    req(t["strict_initial_trade_axiom_lesson35"]=="THREE_CONSECUTIVE_SAME_PRICE_TRADES","lowest theoretical base")
    toy=data["toy_logic"]
    req(toy["scope"]=="ARTIFICIAL_INTEGER_FUNCTION_NOT_A_CHANLUN_MARKET_OR_CENTER" and
        toy["f"]=="f(x)=x+1" and
        toy["strict_a0"]+1==toy["strict_a1"] and
        toy["practical_a0"]+1==toy["practical_a1"] and
        toy["strict_a1"]!=toy["practical_a1"],"different a0 same f not equal output")
    mapping=data["prior_relations"]
    req(mapping["new_v441"]=="AUTHOR_MAIN_POST_THEORY_VS_PRACTICE_DIFFERENT_A0" and
        mapping["expert_identity_of_second_method"]=="STRONGLY_MATCHES_BUT_EXPERT_ORIGINAL_PUBLIC_QUOTE_NOT_VERIFIED",
        "expert provenance not definitive")
    scope=data["scope_limits"]
    req(scope and all(v is False for v in scope.values()),"do not make unverified claims")
    req({"F01_OPEN","OB38_OPEN","OB99_OPEN","COMPLETE_PRACTICAL_A0_TO_FINISHED_MOVEMENT_BRIDGE_OPEN",
         "CROSS_A0_OUTPUT_EQUIVALENCE_NOT_PROVEN","NOT_RUN_REAL_MARKET"}.issubset(set(data["open"])),"open gates preserved")
    req(data["status"]=="ORIGINAL_SINA_MAIN_POST_DUAL_A0_AUTHOR_EXPLICIT_EXPERT_MATCH_HIGH_BUT_NOT_IDENTIFIED","research classification")
    for token in ("2007-07-19 15:29:28","2007-07-20 08:26:20","a0","第35课","第65课","第83课","第84课","NOT_RUN"):
        req(token in report,"explanation missing "+token)
    return {"status":"SINA_MAIN_POST_TWO_A0_SOURCE_SCOPE_AUDIT_SUCCESS","author_main_posts":2,
            "course_source_anchors":len(anchors),"distinct_a0_types":2,
            "cross_a0_full_equivalence_claimed":False}
if __name__=="__main__":
    print(json.dumps(audit(json.loads(SPEC.read_text(encoding="utf-8")),
                           REPORT.read_text(encoding="utf-8")),ensure_ascii=False))
