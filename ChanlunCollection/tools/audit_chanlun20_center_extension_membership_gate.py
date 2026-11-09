#!/usr/bin/env python3
"""Source-locked lesson20 Zn extension barrier; never certify completed centers.

Two distinct input types are intentionally incompatible: genuine *synthetic*
raw trade event packets from PR58 have NO author-validated Zn membership, so
center identity remains unresolved; separately supplied symbolic Zn intervals
can be tested only for the authored numerical extension predicate.
"""
from __future__ import annotations
import importlib.util
import json
import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"catalog/chanlun20_center_extension_membership_gate_v1.json"
FIXTURES=ROOT/"tests/fixtures/chanlun20_center_extension_membership_cases_v1.json"
SOURCE_PINS=ROOT/"reports/source_inventory/chanlun_center_order_completion_native_text_sha256.json"
SOURCE_INVENTORY=ROOT/"reports/source_inventory/chanlun_20261107_verified.json"
RANK_SCRIPT=ROOT/"tools/audit_chanlun35_event_center_price_order.py"
ID="CL20-CENTER-EXTENSION-ZN-MEMBERSHIP-GATE-V1"
PDF_SHA="0a402e19bbcabc24a5d031b047aeebcf96cdb7f777d2462cc7e5b28ed121b865"
PAGES={"234":"69121d9a964de1298165d08291f802d4263be12adaabdd8f5e5353b396aca86f",
       "235":"d4f06d4d8395748f7b38307ccdc83436fdf9480a729fad413c45f772ae7023d4",
       "245":"b699993c6d57238640eb94844f53d5391fcb1572659cae08fb2248139ca74ea3",
       "246":"441f33589318f29d539f01124a9be0ecf8fd98e372b2340cb2367a785a5397f9"}
SOURCE=(("CL020-S01",1,[245,246]),("CL020-S02",1,[246]),
        ("CL018-S01",1,[234]),("CL018-S07",1,[235]))
OPEN=("author_z_member_legality_and_direction",
      "origin_and_completed_status_of_child_types",
      "exact_same_level_center_continuity",
      "author_core_point_touch_boundary_semantics",
      "original_rule_version_at_event_time",
      "center_finished_and_new_center_origin",
      "real_trade_execution_provenance")
CLAIMS=("author_completed_center","author_distinct_center",
        "author_center_extension_certified","author_trend_completed",
        "higher_level_center_certified","lesson38_uniqueness_proven",
        "lesson99_universal_center_proven")
RANK_ID="CL35-EVENT-DERIVED-LOWEST-CENTER-PRICE-ORDER-V1"
RAW_KEYS={"mode","trade_packet"}
ZN_KEYS={"mode","as_of","members"}
MEMBER_KEYS={"ordinal","interval","seen_at","confirmed_at","child_completed_declared",
             "rule_version","kind"}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def guard(condition, message):
    if not condition:
        raise ValueError(message)


def load_rank():
    spec=importlib.util.spec_from_file_location("lesson35_event_derived_rank",RANK_SCRIPT)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_contract(doc, pins, inventory, cards, rank_doc):
    guard(doc.get("schema_version")==1 and doc.get("id")==ID and
          doc.get("scope")=="AUTHOR_ZN_EXTENSION_NUMERIC_TEST_NOT_VALID_CENTER_IDENTITY",
          "Unknown center-extension source-gate version or scope")
    guard(doc.get("volume1_pdf_sha256")==PDF_SHA and
          pins.get("source_pdf_sha256")==PDF_SHA and
          pins.get("reader")=="pymupdf_1.26.7_get_text_sort_true" and
          all(pins["page_native_text_sha256"].get(p)==v for p,v in PAGES.items()) and
          doc.get("native_pages_sha256")==PAGES and
          any(v["path"]=="ChineseBooks/缠论/缠论_卷1.pdf" and
              v["sha256"]==PDF_SHA for v in inventory["volumes"]),
          "Original chapter18/20 native-text SHA / PDF provenance drift")
    claims=doc.get("original_sources")
    guard(isinstance(claims,list) and len(claims)==len(SOURCE),
          "Missing authored center source claims")
    for item,(claim,vol,pages) in zip(claims,SOURCE):
        guard(item=={"claim":claim,"volume":vol,"pages":pages,"role":"SOURCE"},
              "Source identity, page attribution or role altered")
        card=cards[20 if claim.startswith("CL020") else 18]
        source=[x for x in card["claims"] if x["id"]==claim]
        guard(len(source)==1 and source[0]["kind"]=="SOURCE" and
              all(p in source[0]["pdf_pages"] for p in pages) and
              card["source"]["sha256"]==PDF_SHA,
              "Original author card was removed, retyped or re-attributed")
    guard(doc.get("zn_core_definition")=="ZG=min(g1,g2),ZD=max(d1,d2)" and
          doc.get("extension_condition")==
             "EVERY_SUBSEQUENT_AUTHOR_QUALIFIED_ZN_INTERVAL_OVERLAPS_FROZEN_CORE" and
          doc.get("extension_break_condition")==
             "ANY_SUBSEQUENT_AUTHOR_QUALIFIED_ZN_INTERVAL_STRICTLY_DISJOINT_FROM_CORE" and
          doc.get("touch_policy")==
             "POINT_TOUCH_NOT_AUTOMATICALLY_PROMOTED_TO_AUTHOR_EXTENSION_PROOF",
          "Original center-extension formula or strict boundary changed")
    guard(doc.get("raw_mode_upstream_contract")==RANK_ID and
          rank_doc["id"]==RANK_ID and
          rank_doc["raw_run_distinctness_status"]==
              "DIFFERENT_PRICE_RUNS_ARE_NOT_AUTHOR_VERIFIED_DISTINCT_CENTERS" and
          doc.get("raw_mode_result")=="RAW_TRADE_RUN_CENTER_IDENTITY_UNRESOLVED_NO_ZN",
          "Raw trade runs were illegally promoted to independent center groups")
    guard(doc.get("unverified")==list(OPEN) and
          doc.get("certificates")=={x:False for x in CLAIMS} and
          doc.get("market_inputs_read") is False and
          doc.get("pdf_images_read") is False and
          doc.get("original_first_publication_proven") is False and
          doc.get("backtest_status")=="NOT_RUN",
          "Missing unverified center members or false completion proof")


def ts(value):
    guard(type(value) is str and value.strip(),"Empty or forged synthetic time")
    try: d=datetime.fromisoformat(value)
    except ValueError as err: raise ValueError("Malformed synthetic time") from err
    guard(d.tzinfo is not None and d.utcoffset() is not None,
          "Timezone-aware clock required")
    return d


def decimal(s):
    guard(type(s) is str and bool(re.fullmatch(r"[+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)",s)),
          "Only finite exact positive decimal strings accepted")
    x=Decimal(s)
    guard(x.is_finite(),"Non-finite interval")
    return x


def verdict(status, visible_count, core=None, first_outside=None,
            raw_center_count=0, raw_price_order=None):
    return {"status":status,"visible_zn":visible_count,
            "frozen_core":core,"first_strictly_disjoint_zn":first_outside,
            "raw_conditional_base_centers":raw_center_count,
            "raw_price_condition":raw_price_order,
            "author_z_membership_verified":False,
            "author_independent_center_certified":False,
            "author_center_extension_certified":False,
            "trajectory_completed":False,
            "higher_center_can_be_constructed":False}


def evaluate(item, doc, rank_tool=None):
    guard(doc["id"]==ID,"Source center-extension proof scope mismatch")
    guard(type(item) is dict,"Expected typed conditional evidence")
    if item.get("mode")=="RAW_TRADE_EVENTS":
        guard(set(item)==RAW_KEYS,"Unexpected manual Zn or legal certificate on raw trade data")
        rank_tool=rank_tool or load_rank()
        result=rank_tool.inspect(item["trade_packet"],
                                 read(rank_tool.CONTRACT))
        if result["status"]=="VERSION_MISMATCH_NO_ORDER":
            return verdict("RAW_TRADE_SOURCE_RULE_MISMATCH_NO_CENTER_GROUPING",0)
        return verdict("RAW_TRADE_RUN_CENTER_IDENTITY_UNRESOLVED_NO_ZN",0,
                       raw_center_count=result["center_count"],
                       raw_price_order=result["status"])
    guard(item.get("mode")=="SYNTHETIC_DECLARED_ZN_NOT_AUTHOR_CERTIFIED" and
          set(item)==ZN_KEYS,"Only explicitly unverified Zn membership may be inspected")
    asof=ts(item["as_of"])
    members=item["members"]
    guard(type(members) is list and 2<=len(members)<=20,
          "Finite two-or-more declared Zn members required")
    parsed=[]
    previous_seen=None
    confirmed_prev=None
    for index,z in enumerate(members,1):
        guard(type(z) is dict and set(z)==MEMBER_KEYS,
              "Zn member cannot contain legal certificate fields")
        guard(type(z["ordinal"]) is int and z["ordinal"]==index and
              z["kind"]=="SYNTHETIC_ZN_NOT_AUTHOR_VALIDATED" and
              type(z["child_completed_declared"]) is bool and
              type(z["rule_version"]) is str and z["rule_version"].strip(),
              "Invalid ordinal, membership kind, completion field or version")
        bounds=z["interval"]
        guard(type(bounds) is list and len(bounds)==2,
              "Two exact numeric bounds per Zn required")
        lo,hi=map(decimal,bounds)
        guard(lo<=hi,"Zn high below low")
        seen=ts(z["seen_at"])
        confirmed=ts(z["confirmed_at"]) if z["confirmed_at"] is not None else None
        guard(previous_seen is None or seen>previous_seen,
              "Zn events need a strictly increasing observation order")
        previous_seen=seen
        if confirmed is not None:
            guard(confirmed>=seen and
                  (confirmed_prev is None or confirmed>confirmed_prev),
                  "Zn confirmation cannot precede seen time or prior confirmation")
            confirmed_prev=confirmed
        guard(z["child_completed_declared"] or confirmed is None,
              "Incomplete child cannot have completed confirmation clock")
        parsed.append((index,lo,hi,seen,confirmed,
                       z["child_completed_declared"],z["rule_version"]))
    visible=[x for x in parsed if x[3]<=asof]
    if len({x[6] for x in visible})>1:
        return verdict("DECLARED_ZN_RULE_VERSION_MISMATCH",len(visible))
    if len(visible)<2:
        return verdict("TOO_FEW_VISIBLE_ZN_FOR_CORE",len(visible))
    if any(not x[5] or x[4] is None or x[4]>asof for x in visible):
        return verdict("UNCONFIRMED_ZN_NOT_EVALUATED",len(visible))
    zd=max(visible[0][1],visible[1][1])
    zg=min(visible[0][2],visible[1][2])
    core={"ZD":str(zd.normalize()),"ZG":str(zg.normalize())}
    if zd>zg:
        return verdict("DECLARED_ZN_CORE_EMPTY",len(visible),core)
    if zd==zg:
        return verdict("CORE_POINT_TOUCH_BOUNDARY_UNRESOLVED",len(visible),core)
    if len(visible)==2:
        return verdict("NO_SUBSEQUENT_ZN_EXTENSION_EVENT",len(visible),core)
    for n,lo,hi,*_ in visible[2:]:
        if hi<zd or lo>zg:
            return verdict("AUTHOR_ZN_EXTENSION_STRICT_DISJOINTNESS_CONDITION_ONLY",
                           len(visible),core,n)
        if hi==zd or lo==zg:
            return verdict("ZN_POINT_TOUCH_BOUNDARY_UNRESOLVED",len(visible),core)
    return verdict("AUTHOR_ZN_EXTENSION_OVERLAP_CONDITION_ONLY",
                   len(visible),core)


def fixtures_check(fixtures,doc):
    guard(fixtures.get("schema_version")==1 and fixtures.get("contract_id")==ID
          and fixtures.get("synthetic_only") is True,
          "Typed fixture source/version mismatch")
    rows=fixtures.get("cases")
    guard(type(rows) is list and len(rows)==12 and
          len({x["id"] for x in rows})==12,
          "12 distinct Zn and raw event evidence cases expected")
    counts={}
    for row in rows:
        output=evaluate(row["input"],doc)
        want=row["expected"]
        guard(output["status"]==want["status"] and
              output["visible_zn"]==want["visible_zn"] and
              output["first_strictly_disjoint_zn"]==want["first_outside"] and
              output["raw_conditional_base_centers"]==want["raw_centers"],
              "Source interval/member classification drift: "+row["id"])
        guard(not any(output[f] for f in
                  ("author_z_membership_verified","author_independent_center_certified",
                   "author_center_extension_certified","trajectory_completed",
                   "higher_center_can_be_constructed")),
              "Falsely conferred author source or downstream certificate")
        counts[output["status"]]=counts.get(output["status"],0)+1
    guard(counts.get("RAW_TRADE_RUN_CENTER_IDENTITY_UNRESOLVED_NO_ZN",0)>=2 and
          counts.get("AUTHOR_ZN_EXTENSION_OVERLAP_CONDITION_ONLY",0)>=1 and
          counts.get("AUTHOR_ZN_EXTENSION_STRICT_DISJOINTNESS_CONDITION_ONLY",0)>=1,
          "Raw identity and both overlap verdicts must be covered")
    return {"status":"SOURCE_LOCKED_ZN_EXTENSION_NUMERIC_ONLY_CENTER_IDENTITY_UNRESOLVED",
            "source_claims":len(SOURCE),"synthetic_cases":len(rows),
            "unverified_premises":len(OPEN),"outcomes":counts,
            "genuine_independent_centers_certified":0,
            "genuine_completed_types_certified":0,
            "market_data_read":False,"pdf_images_read":False}


def main():
    doc=read(CONTRACT)
    cards={n:read(ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json") for n in (18,20)}
    validate_contract(doc,read(SOURCE_PINS),read(SOURCE_INVENTORY),cards,
                      read(ROOT/"catalog/chanlun35_event_derived_center_price_order_v1.json"))
    print(json.dumps(fixtures_check(read(FIXTURES),doc),ensure_ascii=False))


if __name__=="__main__":
    main()
