#!/usr/bin/env python3
"""Lesson18/20/35: source-locked third point boundary versus structural return.

This is a *conditional* operator on synthetic DECLARED completed lower types,
not a Chanlun legal trend parser, proof of original author center destruction,
or a market-data/return simulator. Touch equals the weak third-point boundary
while strict nonreturn is a *different predicate*. This is the substantive
textual distinction, not a market prediction.
"""
from __future__ import annotations
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"catalog/chanlun_f01_f02_third_point_boundary_v1.json"
CASES=ROOT/"tests/fixtures/chanlun_f01_f02_boundary_cases_v1.json"
PIN1=ROOT/"reports/source_inventory/chanlun_center_order_completion_native_text_sha256.json"
BASE35=ROOT/"catalog/chanlun35_author_base_center_axiom_v1.json"
ID="CL18-20-35-THIRD-POINT-BOUNDARY-NONIDENTITY-V1"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def ensure(x,message):
    if not x:raise ValueError(message)

def source_guard(contract):
    pins=load(PIN1); base=load(BASE35)
    expected=[
        (18,"CL018-S01",234),(18,"CL018-S07",235),
        (18,"CL018-S03",236),(20,"CL020-S02",246),
        (20,"CL020-S03",247),(35,"CL35-SO-2",291)
    ]
    ensure(contract.get("schema_version")==1 and contract.get("id")==ID and
      contract.get("scope")==
      "AUTHOR_TEXT_BOUNDARY_DIFFERENT_PREDICATES_CONDITIONAL_TO_SYNTHETIC_DECLARED_FINISHED_TYPES" and
      contract.get("existing_native_text_pins")==
      "reports/source_inventory/chanlun_center_order_completion_native_text_sha256.json" and
      contract.get("lowest_level_native_sha_file")==
      "catalog/chanlun35_author_base_center_axiom_v1.json",
      "Boundaries or source-provenance scope changed")
    ensure(len(contract.get("claims",[]))==len(expected) and
           contract["original_pdf_sha256"]["1"]==pins["source_pdf_sha256"] and
           contract["original_pdf_sha256"]["2"]==base["original_pdf_sha256"],
           "Original volume SHA or source claim list altered")
    for row,(n,claim,page) in zip(contract["claims"],expected):
        ensure((row["lesson"],row["id"],row["original_page"])==(n,claim,page),
               "Original lesson and native page source changed")
        doc=load(ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json")
        matches=[x for x in doc["claims"] if x["id"]==claim]
        ensure(len(matches)==1 and matches[0]["kind"]=="SOURCE" and
               page in matches[0]["pdf_pages"] and
               doc["source"]["sha256"]==contract["original_pdf_sha256"][str(1 if n<35 else 2)],
               "Claim source role, page or volume changed")
        expected_sha=(pins["page_native_text_sha256"][str(page)] if n<35
                      else base["native_text_sha256"])
        ensure(row["native_sha256"]==expected_sha,
               "Pinned original native PDF page text changed")
    ensure(contract["numeric_truths"]=={
      "third_buy_no_break":"retest_low >= center_ZG",
      "strict_above":"retest_low > center_ZG",
      "third_sell_no_break":"retest_high <= center_ZD",
      "strict_below":"retest_high < center_ZD",
      "closed_interval_touch":"retest_low == center_ZG OR retest_high == center_ZD"
    }, "Weak and strict predicates illegally conflated")
    require_false=("author_third_point_certified","author_center_destroyed_certified",
      "author_center_distinct_certified","author_completed_trend_certified",
      "full_author_rule_version_frozen","historical_original_first_publication_verified",
      "real_market_accessed","original_images_read")
    ensure(all(contract.get(k) is False for k in require_false) and
           contract.get("backtesting")=="NOT_RUN" and
           contract.get("assumed_input")==
           "SYNTHETIC_DECLARED_FIRST_RETEST_AND_COMPLETION_NOT_AUTHOR_AUTHENTICATED" and
           len(contract.get("blocked_proof_slots",[]))==5 and
           len(contract.get("interpretive_separations",[]))==7,
           "Unverified Chanlun/market certificates illegally promoted")

def time(value):
    ensure(type(value) is str,"Synthetic datetime must be string")
    try:t=datetime.fromisoformat(value)
    except ValueError as e:raise ValueError("Invalid as-of timestamp") from e
    ensure(t.tzinfo is not None and t.utcoffset() is not None,
           "Explicit timezone required")
    return t

def decimal(value):
    ensure(type(value) is str and value,
           "Exact numeric input must be a decimal string")
    try:d=Decimal(value)
    except InvalidOperation as e:raise ValueError("Invalid numeric input") from e
    ensure(d.is_finite(),"NaN and Infinity are not valid prices")
    return d

def evaluate(item):
    require={"id","direction","center","retest","observed_at",
             "confirmed_at","as_of","first_retest_declared","member_provenance"}
    ensure(set(item)==require and item["direction"] in {"BUY","SELL"} and
           item["member_provenance"]=="SYNTHETIC_DECLARED_NOT_AUTHOR_CERTIFIED" and
           type(item["first_retest_declared"]) is bool,
           "Input cannot claim actual author-validated first retest")
    z=item["center"];r=item["retest"]
    ensure(type(z) is dict and set(z)=={"ZD","ZG"} and
           type(r) is dict and set(r)=={"low","high"},
           "Strict center / retest schema required")
    zd,zg=decimal(z["ZD"]),decimal(z["ZG"])
    low,high=decimal(r["low"]),decimal(r["high"])
    ensure(zd<=zg and low<=high,
           "Center/retest interval invalid")
    obs,conf,now=(time(item[x]) for x in ("observed_at","confirmed_at","as_of"))
    ensure(obs<=conf,"Impossible observation/completion ordering")
    # The retest range contains information whose final low/high can require
    # future observations. Even numeric evidence is invisible before confirmed_at.
    result={"id":item["id"],"direction":item["direction"],"as_of":item["as_of"],
       "author_declared_first_retest_authenticated":False,
       "author_finished_child_verified":False,
       "author_third_point_certified":False,
       "author_center_destroyed_certified":False,
       "author_new_independent_center_certified":False,
       "completed_trajectory_certified":False,
       "actual_market_backtest":"NOT_RUN"}
    if now<conf:
        result.update(status="PENDING_CHILD_COMPLETION_ASOF",
                      third_point_weak_price_condition=None,
                      strict_nonreturn_numeric=None,point_touch=None)
        return result
    if not item["first_retest_declared"]:
        result.update(status="NOT_FIRST_RETEST_DECLARED",
                      third_point_weak_price_condition=None,
                      strict_nonreturn_numeric=None,point_touch=None)
        return result
    if item["direction"]=="BUY":
        weak=low>=zg;strict=low>zg;touch=low==zg
    else:
        weak=high<=zd;strict=high<zd;touch=high==zd
    status=("THIRD_POINT_PRICE_THRESHOLD_FAILS" if not weak else
            "WEAK_THIRD_POINT_THRESHOLD_ONLY_POINT_TOUCH_STRUCTURAL_NONRETURN_UNRESOLVED" if touch else
            "WEAK_THIRD_POINT_THRESHOLD_ONLY_STRICT_NONRETURN_NUMERIC")
    result.update(status=status,third_point_weak_price_condition=weak,
                  strict_nonreturn_numeric=strict,point_touch=touch)
    return result

def verify():
    contract=load(CONTRACT)
    source_guard(contract)
    cases=load(CASES)
    ensure(cases.get("schema_version")==1 and len(cases.get("cases",[]))==8,
           "Expected eight bounded synthetic boundary cases")
    outcomes=[]
    for item in cases["cases"]:
        actual=evaluate(item["input"])
        ensure(actual["status"]==item["expected_status"] and
               actual["third_point_weak_price_condition"]==item["expected_weak"] and
               actual["strict_nonreturn_numeric"]==item["expected_strict"] and
               actual["point_touch"]==item["expected_touch"],
               "Text boundary case did not preserve weak/strict difference: "+item["input"]["id"])
        ensure(all(actual[x] is False for x in (
            "author_third_point_certified","author_center_destroyed_certified",
            "author_new_independent_center_certified","completed_trajectory_certified")),
            "Toy numerical predicate was promoted to Chanlun center/trajectory proof")
        outcomes.append(actual)
    ensure({x["direction"] for x in outcomes}=={"BUY","SELL"} and
           sum(x["point_touch"] is True for x in outcomes)==2 and
           sum(x["third_point_weak_price_condition"] is True for x in outcomes)==4 and
           sum(x["status"]=="PENDING_CHILD_COMPLETION_ASOF" for x in outcomes)==1,
           "Bilateral boundary/as-of evidence lost")
    return {"status":"WEAK_PRICE_BOUNDARY_CHECKED_STRUCTURAL_COMPLETION_OPEN",
            "cases":len(outcomes),"boundary_touch_numeric_passes":2,
            "weak_third_point_numeric_passes":4,
            "original_pdf_claims":len(contract["claims"]),
            "actual_author_third_points_certified":0,
            "actual_centers_destroyed_certified":0,
            "real_market":"NOT_RUN"}

if __name__=="__main__":
    print(json.dumps(verify(),ensure_ascii=False,sort_keys=True))
