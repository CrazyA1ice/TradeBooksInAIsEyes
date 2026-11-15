#!/usr/bin/env python3
"""M55 source-typed completion slot audit; no historical OHLC or proof oracle."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"catalog/chanlun_l18_l54_completed_movement_slots_m55.json"
SOURCE=ROOT/"catalog/chanlun_l54_dual_policy_witness_m54.json"
ID="CHANLUN-M55-L18-L54-CENTER-VS-FINISHED-MOVEMENT-SLOTS"
SOURCE_ID="CHANLUN-L54-TWO-R-THREE-GROUP-SOURCE-WITNESS-M54"
FIELDS=("independent_movement_completion_receipt","raw_source_digest","market_first_known","strict_f1_f2_R_receipt")

def check(ok,reason):
    if not ok:
        raise ValueError("M55_REJECTED: "+reason)

def audit(spec,source):
    check(spec.get("schema_version")==1 and spec.get("id")==ID,"schema")
    check(spec.get("source_m54_id")==SOURCE_ID and source.get("id")==SOURCE_ID,"M54 identity")
    check(spec.get("source_m54_path")=="catalog/chanlun_l54_dual_policy_witness_m54.json","canonical source")
    check(spec.get("required_independent_fields")==list(FIELDS),"source receipt field requirement")
    theory=spec["lesson18_semantics"]
    check(theory["formed_center_implies_containing_movement_finished_now"] is False,"center vs movement type")
    check(theory["model_is_hypothetical_not_market"] is True,"countermodels not market")
    world=theory["countermodels"]
    check(len(world)==2 and
          all(w["center_exists"] is True for w in world) and
          {w["containing_g_movement_finished_at_t"] for w in world}=={True,False},
          "both author-allowed completion/extension possibilities")
    scope=spec["full_chart_vs_prefix"]
    check(scope["author_assumption"]=="FULL_AUTHOR_CHART_ALL_EXCEPT_FINAL","full chart evidence scope")
    check(scope["not_implied"]=="PREFIX_RIGHTMOST_LEG_ALREADY_COMPLETED_FIRST_KNOWN","full chart is not historical prefix")
    check(scope["full_market_raw_data_unavailable"] is True,"market provenance absent")
    originals={x["id"]:x for x in source["policies"]}
    check(set(originals)=={"R_A","R_B"},"M54 policy drift")
    expected={f"{pid}:G{i}" for pid in originals for i in (1,2,3)}
    seen=set()
    slots=spec["group_slots"]
    check(len(slots)==6,"six typed policy-qualified slots")
    for s in slots:
        pid=s.get("policy_id")
        k=s.get("ordinal")
        check(pid in originals and type(k) is int and k in (1,2,3),"policy/ordinal")
        ident=f"{pid}:G{k}"
        check(s.get("slot_id")==ident and ident not in seen,"slot identity")
        seen.add(ident)
        check(s.get("source_group_members")==originals[pid]["groups"][k-1],"source member symbols changed")
        check(s.get("source_typed_role")=="AUTHOR_BRACKETED_1MIN_CENTER_GROUP","center retyped as finished movement")
        check(s.get("coarse_segmentation_grade")=="SOURCE_ILLUSTRATION_NOT_FINISHED_MOVEMENT","source coarse line mis-certified")
        check(s.get("proof_status")=="AUTHOR_TEXT_GROUP_KNOWN_INDEPENDENT_MOVEMENT_COMPLETION_UNKNOWN","completion not independently checked")
        for f in FIELDS:
            check(s.get(f) is None,"forged independent evidence: "+f)
    check(seen==expected,"missing or reused group slot")
    checkpoint={c["id"]:c for c in spec["checkpoints"]}
    check(set(checkpoint)=={"g5","g6"},"checkpoint identity")
    original_ch={c["id"]:c for c in source["checkpoints"]}
    for at,author in (("g5",{"R_A":True,"R_B":False}),("g6",{"R_A":True,"R_B":True})):
        check(checkpoint[at]["author_attested"]==author and original_ch[at]["author_attested_by_policy"]==author,
              "author attestation may not be rewritten")
        market={"R_A":"UNKNOWN","R_B":"NOT_SOURCE_ELIGIBLE_AT_G5" if at=="g5" else "UNKNOWN"}
        check(checkpoint[at]["market_verified"]==market,"actual first-known is not source-attested")
    check(set(spec["phi20_proof_missing"])=={"TWO_INDEPENDENT_CONSECUTIVE_VALID_G_CENTERS","LEGAL_CONNECTOR_AS_REQUIRED",
      "SOURCE_PERIPHERAL_MEMBER_IDENTITY","THREE_COMPLETED_G_MOVEMENT_RECEIPTS",
      "SAME_HIGHER_CENTER_ID","MARKET_FIRST_KNOWN_TIMES"},"Phi20 proof obligations")
    flags=spec["guard_flags"]
    check(flags.get("preserve_author_higher_center_attestation") is True,"author claim must be preserved")
    for f in ("market_completion_claim","full_f01_solution","phi20_solution","real_market_backtest","a087_second_formula_identified"):
        check(flags.get(f) is False,"false global proof: "+f)
    return {"status":"AUTHOR_CENTER_ATTESTED_SIX_COMPLETED_MOVEMENT_SLOTS_OPEN",
            "six_policy_qualified_slots":len(slots),
            "m54_symbol_lineage_intact":True,
            "author_g5":{"R_A":True,"R_B":False},
            "author_g6":{"R_A":True,"R_B":True},
            "market_movement_certifications":0,
            "phi20_complete":False,
            "used_real_market_data":False}

if __name__=="__main__":
    print(json.dumps(audit(json.loads(CONTRACT.read_text(encoding="utf-8")),
                           json.loads(SOURCE.read_text(encoding="utf-8"))),
                     ensure_ascii=False,indent=2))
