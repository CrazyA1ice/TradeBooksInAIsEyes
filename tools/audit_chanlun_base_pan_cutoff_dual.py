"""v4.44: distinguish absolute trade-event base from operable segment cutoff.

Checks synthetic non-forward-looking interface states and source/provenance constraints.
NEVER certifies raw market events, segment validity, completion, trading value or
author's full theory; no data/network used during execution.
"""
from __future__ import annotations
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/"catalog/chanlun_strict_vs_operable_bottom_pan_v444.json"
REPORT=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/ABSOLUTE_PAN_BASE_VS_OPERABLE_SEGMENT_CUTOFF_V444.md"

def require(ok, msg):
    if not ok: raise ValueError("STRICT_OPERABLE_BASE_GUARD: "+msg)

def index(v):
    require(type(v) is int and v>=0, "nonnegative integer observation index")
    return v

def dec(v):
    require(isinstance(v,str), "decimal text prices required")
    try: out=Decimal(v)
    except InvalidOperation: raise ValueError("STRICT_OPERABLE_BASE_GUARD: invalid price") from None
    require(out.is_finite(), "finite price")
    return out

def verdict(state,base,first_known=None):
    return {
        "state":state,"base_id":base,
        "conditionally_first_known_at":first_known,
        "market_or_author_exit_authenticated":False,
        "finite_source_proof_completed":False
    }

def inspect_case(contract,case,spec):
    bases={b["id"]:b for b in spec["base_contracts"]}
    require(set(bases)=={"STRICT_TRANSACTION_BASE","OPERABLE_SEGMENT_CUTOFF"},
            "two independent base types")
    base=case["base"]
    require(base in bases,"known initialized base")
    idx=index(case["asof"])
    require(contract["source_class"]=="EXTERNAL_SYNTHETIC_UNVERIFIED",
            "never market-authenticated")
    center_seen=None
    if base=="STRICT_TRANSACTION_BASE":
        raw=spec["prefix_nonidentifiability"]["shared_raw_prefix"]
        prices=case.get("amended_prices",[x["price"] for x in raw])
        require(len(prices)==3, "three actual-trade-shaped values in illustrative prefix")
        px=[dec(x) for x in prices]
        require([x["seq"] for x in raw]==[0,1,2],"continuous base event indices")
        if idx<2: return verdict("AWAITING_BASE_CENTER",base)
        if not(px[0]==px[1]==px[2]):
            return verdict("NO_THREE_EQUAL_PRICE_CENTER",base)
        center_seen=2
    else:
        center_seen=case.get("practical_center_first_known")
        require(center_seen is None or type(center_seen) is int and center_seen>=0,
                "practical center source ordinal or absent")
        if center_seen is None or center_seen>idx:
            return verdict("AWAITING_PRACTICAL_CENTER_SOURCE",base)
    receipt=case.get("exit")
    if receipt is None:
        if base=="STRICT_TRANSACTION_BASE":
            return verdict("CENTER_EXISTS_PAN_TERMINAL_UNKNOWN",base)
        return verdict("PRACTICAL_CENTER_CONDITIONAL_PAN_TERMINAL_UNKNOWN",base)
    require(isinstance(receipt,dict),"external receipt object")
    permitted={
        "STRICT_TRANSACTION_BASE":"EXTERNAL_UNVERIFIED_AUTHOR_END",
        "OPERABLE_SEGMENT_CUTOFF":"EXTERNAL_UNVERIFIED_RESEARCH_POLICY_EXIT"
    }
    require(receipt.get("kind")==permitted[base],
            "must not conflate author-claim and researcher exit policy")
    end=index(receipt.get("first_known"))
    require(end>=center_seen, "exit cannot be known before source center")
    if end>idx: return verdict("AWAITING_EXTERNAL_EXIT",base)
    if base=="STRICT_TRANSACTION_BASE":
        return verdict("CONDITIONAL_EXIT_UNVERIFIED",base,end)
    return verdict("PRACTICAL_CONDITIONAL_EXIT_UNVERIFIED_NOT_AUTHOR",base,end)

def audit(spec,report,root=ROOT):
    require(spec["schema_version"]==1 and
            spec["id"]=="CHANLUN-V444-BOTTOM-PAN-STRICT-AND-OPERABLE-CUTOFF-DISTINCTION" and
            spec["version"]=="4.44.0","identity/version")
    sources={x["id"]:x for x in spec["source_layers"]}
    require(set(sources)=={"L18","L19_REPLY","L35","L60","L65","L81","L84"},
            "source layers")
    require(sources["L19_REPLY"]["kind"]==
            "SECONDARY_ARCHIVED_AUTHOR_ATTRIBUTED_REPLY_NOT_2006_SINA_COMMENT_BYTES" and
            sources["L19_REPLY"]["reply_at"]=="2006-12-27 21:05:20" and
            sources["L19_REPLY"]["question_at"]=="2006-12-27 20:21:58" and
            sources["L19_REPLY"]["url"]=="https://chzhshch.blog/stocks/019/",
            "early comment cannot be silently upgraded to original posted lesson")
    require(sources["L60"]["kind"]=="AUTHOR_LESSON_BODY_REPUBLISHED" and
            sources["L60"]["original_at"]=="2007-06-19 08:04:06" and
            sources["L60"]["url"]=="https://eczsc.com/originals/60",
            "correct authored lesson60 practical cutoff")
    assert_names={"L18":"2006-12-26 15:05:58",
                  "L35":"2007-03-09 11:51:34",
                  "L81":"2007-09-17 22:57:16",
                  "L84":"2007-10-07 16:09:06"}
    for key,value in assert_names.items():
        require(sources[key]["original_at"]==value,
                "source main-body dates "+key)
    detail=spec["important_attribution_clarification"]
    require(detail["lesson19_article_claim_card_source_is_not_author_reply"] and
            detail["lesson19_archive_reply_timestamp"]=="2006-12-27 21:05:20" and
            detail["lesson19_early_value_center_identical_to_lesson35_three_transaction_center"]=="NOT_ESTABLISHED",
            "early reply is not 2007 formal a0 proof")
    require(detail["lesson60_operational_cutoff_original_date"]=="2007-06-19 08:04:06"
            and detail["lesson81_20070917_precision_correction_not_source_of_cutoff"]
            and not detail["lesson60_images_reconstructed_from_pixels_in_this_round"]
            and not detail["source_bytes_original_post_time_authenticated"],"cutoff provenance")
    pins=spec["original_pdf_source_claim_pins"]
    require(len(pins)==16 and len({(x["lesson"],x["id"]) for x in pins})==16,
            "exact 16 authored lesson-source pins")
    for claim in pins:
        file=root/("knowledge/evidence/chanlun_lesson%03d.json"%claim["lesson"])
        card=json.loads(file.read_text(encoding="utf-8"))
        matches=[c for c in card["claims"]
                 if c["id"]==claim["id"] and c["kind"]=="SOURCE"]
        require(len(matches)==1 and
                set(claim["pages"]).issubset(set(matches[0]["pdf_pages"])) and
                claim["kind"]=="SOURCE_IN_COMPILED_LESSON_NOT_ORIGINAL_SERVER_SIGNATURE",
                "anchored original claim/page "+claim["id"])
    bs={x["id"]:x for x in spec["base_contracts"]}
    require(set(bs)=={"STRICT_TRANSACTION_BASE","OPERABLE_SEGMENT_CUTOFF"},
            "distinct base contracts")
    require(bs["STRICT_TRANSACTION_BASE"]["a0_kind"]=="CONSECUTIVE_REAL_EXECUTION_EVENTS" and
            bs["STRICT_TRANSACTION_BASE"]["price_minimum"]=="THREE_EQUAL_PRICE_EXECUTIONS" and
            bs["STRICT_TRANSACTION_BASE"]["base_pan_finished"]==
            "OPEN_NO_AUTHOR_NONRECURSIVE_TERMINAL_RULE" and
            bs["STRICT_TRANSACTION_BASE"]["negative_level_child_movement"]==
            "NOT_DEFINED_IN_CURRENT_STRICT_BASE_CONTRACT",
            "absolute trade base not its pan exit")
    require(bs["OPERABLE_SEGMENT_CUTOFF"]["a0_kind"]==
            "FROZEN_OPERATIONAL_FRACTAL_PEN_SEGMENT_INITIALIZER" and
            bs["OPERABLE_SEGMENT_CUTOFF"]["cutoff_policy"]==
            "AUTHOR_L60_INTENTIONALLY_IGNORE_SUBCUTOFF_MOVEMENTS" and
            bs["OPERABLE_SEGMENT_CUTOFF"]["negative_level_child_movement"]==
            "INTENTIONALLY_ABSTRACTED_NOT_PROVED_NONEXISTENT" and
            bs["OPERABLE_SEGMENT_CUTOFF"]["base_pan_finished"]==
            "OPEN_NEEDS_AUTHORED_EXIT_OR_EXPLICIT_RESEARCH_POLICY",
            "practical cutoff not nonexistence/no exit")
    pairs=spec["separated_propositions"]
    require(len(pairs)==6 and set(x["id"] for x in pairs)=={"P1","P2","P3","P4","P5","P6"},
            "six source/logical distinctions")
    require({x["label"]:x["not_implies"] for x in pairs}["CENTER_PRESENT"]=="FINISHED_LOWEST_PAN",
            "no automatic completion")
    prefix=spec["prefix_nonidentifiability"]
    require(prefix["type"]==
            "CONDITIONAL_TWO_POSSIBLE_FUTURES_SAME_PRICE_OBSERVATIONS_NOT_LEGAL_MARKET_COUNTEREXAMPLE"
            and prefix["shared_raw_prefix"]==[
              {"seq":0,"price":"8.00"},{"seq":1,"price":"8.00"},{"seq":2,"price":"8.00"}]
            and prefix["common_asof"]==2 and
            prefix["possible_future_A"]["observed_at"]>prefix["common_asof"]
            and prefix["possible_future_B"]["observed_at"]>prefix["common_asof"]
            and prefix["source_existence_of_future_B_not_established"] and
            not prefix["is_a_market_valid_chanlun_counterexample"]
            and not prefix["is_a_proof_author_theory_inconsistent"],
            "conditional prefix argument not a false market countermodel")
    scenarios=spec["synthetic_receipt_cases"]
    require(len(scenarios)==10 and len({x["id"] for x in scenarios})==10,
            "10 synthetic abstract prefixes")
    op={"source_class":"EXTERNAL_SYNTHETIC_UNVERIFIED"}
    for s in scenarios:
        r=inspect_case(op,s,spec)
        require(r["state"]==s["expected"] and
                r["market_or_author_exit_authenticated"] is False and
                r["finite_source_proof_completed"] is False,
                "case mismatch "+s["id"])
    root_only=[x for x in scenarios if x["id"]=="STRICT_THREE_EQUAL_CENTER_ONLY"][0]
    require(inspect_case(op,root_only,spec)["state"]==
            "CENTER_EXISTS_PAN_TERMINAL_UNKNOWN",
            "three same trades never self-validate pan completion")
    require(spec["proof_frontier"]=={
            "F01":"OPEN","OB38":"OPEN","OB99":"OPEN",
            "strict_base_pan":"UNSOURCED_TERMINAL_ORACLE",
            "practical_cutoff_exit":"AUTHOR_PARTITION_POLICY_NOT_A_FINISHING_ORACLE",
            "real_market":"NOT_RUN"}, "proof not closed")
    require(len(spec["unverified"])==8 and all(x is False for x in spec["unverified"].values()),
            "unverified source/market status never upgraded")
    require(spec["status"]==
            "STRICT_VS_OPERABLE_BOTTOM_CUTOFF_DISTINCT_WITH_OPEN_TERMINAL_RULE_AND_CONDITIONAL_PREFIX_LIMIT",
            "conclusion scope")
    for term in ("2006-12-27 21:05:20","2007-06-19 08:04:06",
                 "第35课","第60课","第84课","可以结束","已经结束","负一级",
                 "F01","NOT_RUN"):
        require(term in report,"report missing "+term)
    return {"status":"TWO_AUTHOR_SUPPORTED_BASE_MEANINGS_WITHOUT_A_TOTAL_PAN_STOP_ORACLE",
            "archived_2006_reply_not_primary_source":True,
            "original_lesson_source_pins":len(pins),
            "synthetic_prefix_cases":len(scenarios),
            "author_total_bottom_exit_proven":False,
            "market_data":"NOT_RUN"}

if __name__=="__main__":
    print(json.dumps(audit(json.loads(SPEC.read_text(encoding="utf-8")),
                          REPORT.read_text(encoding="utf-8")),ensure_ascii=False))
