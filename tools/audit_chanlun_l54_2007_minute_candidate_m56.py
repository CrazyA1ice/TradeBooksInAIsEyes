#!/usr/bin/env python3
"""M56: offline provenance boundary and optional CSV-shape admission only.

An OHLCV candidate can never authenticate the archived chart, exact year,
vendor identity, or subminute segment/movement completion by itself.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from datetime import datetime, time
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"catalog/chanlun_l54_600151_historical_minute_admission_m56.json"
CHART=ROOT/"catalog/chanlun_l54_cross_archive_figure_and_decision_v1.json"
M54=ROOT/"catalog/chanlun_l54_dual_policy_witness_m54.json"
M55=ROOT/"catalog/chanlun_l18_l54_completed_movement_slots_m55.json"
ID="CHANLUN-M56-L54-600151-2007-1MIN-PROVENANCE-ADMISSION"
FIELDS=["time","open","high","low","close","volume"]

def require(ok,issue):
    if not ok:
        raise ValueError("M56_REJECTED: "+issue)

def number(s):
    try:
        x=Decimal(str(s))
    except (InvalidOperation,ValueError,TypeError):
        raise ValueError("M56_REJECTED: invalid decimal")
    require(x.is_finite(),"nonfinite decimal")
    return x

def aggregate(prices):
    p=[number(x) for x in prices]
    require(len(p)>1,"insufficient synthetic ticks")
    return {"open":str(p[0].quantize(Decimal(".01"))),
            "high":str(max(p).quantize(Decimal(".01"))),
            "low":str(min(p).quantize(Decimal(".01"))),
            "close":str(p[-1].quantize(Decimal(".01"))),
            "volume":str(len(p)),
            "amount":str(sum(p).quantize(Decimal(".01")))}

def audit(doc,chart,m54,m55):
    require(doc.get("schema_version")==1 and doc.get("id")==ID,"contract ID")
    figure=chart["figure_visual_observations"]
    src=doc["source_pdf"]
    require(src["verified_image_chart_title"]==figure["printed_chart_title"]=="航天机电(1分钟)","stock chart title")
    require(src["year_printed_in_chart"] is False and figure["calendar_year_visible_in_chart"] is False,"chart year")
    require(src["month_day_printed"]==figure["printed_calendar_fragment"]=="05月18日","chart date label")
    require(src["chart_peak_annotation"]==figure["high_annotation_in_chart"]=="18.59","visual peak")
    require(src["chart_right_annotation"]==figure["rightmost_price_annotation_in_chart"]=="18.03","visual right price")
    require(src["author_prose_g0"]==figure["starts_analysis_at_price_from_author_prose"]=="18.50","g0 distinct from chart extreme")
    require(src["printed_page"]==125 and src["pdf_page_index0"]==128,"external visual page")
    require(doc["candidate_instrument"]["code"]=="600151.SH","stock identity candidate")
    require(doc["author_publication"]=="2007-05-24 01:37:31","publication date")
    require(doc["candidate_date"]=="2007-05-18" and doc["date_proof_status"]=="YEAR_NOT_VISIBLE_HYPOTHESIS_ONLY","candidate date must remain hypothetical")
    require(doc["other_years_eliminated"] is False and doc["chart_date_confirmed"] is False,"year not established")
    providers={p["id"]:p for p in doc["external_provider_candidates"]}
    require(set(providers)=={"QMT","ZHITU_FULL"},"source candidates")
    require(all(p["specific_2007_600151_coverage_confirmed"] is False and p["actual_download_performed"] is False for p in providers.values()),"no vendor-day coverage demonstrated")
    require(doc["required_canonical_csv_columns"]==FIELDS,"canonical CSV fields")
    require(doc["optional_canonical_csv_columns"]==["amount"],"CSV amount schema")
    require(doc["timestamp_convention_requires_explicit_choice"] is True and doc["candidate_market_time_zone"]=="Asia/Shanghai","time normalization must be explicit")
    require(m54["id"]=="CHANLUN-L54-TWO-R-THREE-GROUP-SOURCE-WITNESS-M54","M54 source")
    require(m55["id"]=="CHANLUN-M55-L18-L54-CENTER-VS-FINISHED-MOVEMENT-SLOTS","M55 proof slots")
    require(len(m55["group_slots"])==6,"six M55 groups")
    expected={"R_A":True,"R_B":False}
    require(m54["checkpoints"][0]["author_attested_by_policy"]==expected,"g5 author states")
    p=doc["two_synthetic_tick_order_counterexamples"]
    require(p["kind"]=="RESEARCHER_SYNTHETIC_UNIT_VOLUME_PRICE_MULTISETS_NO_REAL_MARKET","synthetic witness disclosure")
    left,right=p["path_H_then_L"],p["path_L_then_H"]
    require(aggregate(left)==aggregate(right)==p["expected_1m"],"identical full 1m aggregates")
    require(left.index("18.50")<left.index("18.20") and right.index("18.50")>right.index("18.20"),"different internal high-low sequence")
    require(doc["catalog_data_status"]=="NOT_ACQUIRED" and doc["year_specific_source_file_digest"] is None,"raw source not acquired")
    require(doc["real_600151_2007_1m_rows_ingested"]==0 and doc["actual_subminute_data_ingested"]==0,"no raw rows")
    require(doc["author_market_ends_achieved"]==0 and doc["phi20_verified"] is False,"no completed market movement")
    require(all(value is False for value in doc["forbidden_upgrade_flags"].values()),"forbidden claim raised")
    return {"status":"NOT_ACQUIRED_YEAR_UNCONFIRMED","stock":"600151.SH",
            "preferred_date_hypothesis":"2007-05-18",
            "chart_year_independently_confirmed":False,
            "source_specific_2007_1m_coverage_confirmed":False,
            "minute_data_retrieved":False,
            "intraminute_HL_order_identifiable_from_OHLCVA":False,
            "completed_market_movement_proved":False,
            "phi20_proved":False}

def inspect_candidate_csv(path, date_label, timestamp_convention):
    require(date_label in ("2007-05-18","2006-05-18"),"only explicit May18 year candidates")
    require(timestamp_convention in ("bar_start","bar_end"),"timestamp convention explicitly required")
    binary=Path(path).read_bytes()
    require(len(binary)>0,"empty file")
    try:
        decoded=binary.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("M56_REJECTED: canonical input must be UTF-8") from None
    from io import StringIO
    reader=csv.DictReader(StringIO(decoded))
    require(reader.fieldnames is not None and all(f in reader.fieldnames for f in FIELDS),"canonical CSV missing fields")
    require(set(reader.fieldnames).issubset(set(FIELDS+["amount"])),"unknown canonical CSV fields")
    seen=set()
    first=None
    last=None
    rows=0
    afternoon=[]
    for rec in reader:
        require(all(rec.get(f) is not None for f in FIELDS),"incomplete CSV row")
        try:
            dt=datetime.strptime(rec["time"].strip(),"%Y-%m-%d %H:%M:%S")
        except (ValueError,AttributeError):
            raise ValueError("M56_REJECTED: time must use YYYY-MM-DD HH:MM:SS") from None
        require(dt.strftime("%Y-%m-%d")==date_label,"another calendar day mixed in")
        require(dt.second==0 and dt.microsecond==0,"minute bars only")
        tm=dt.time()
        require((time(9,30)<=tm<=time(11,30)) or (time(13,0)<=tm<=time(15,0)),"not Shanghai regular session")
        require(first is None or dt>last,"time must be strictly increasing with no duplicates")
        require(dt not in seen,"duplicate minute timestamp")
        seen.add(dt)
        last=dt
        if first is None:
            first=dt
        op,hi,lo,cl=(number(rec[k]) for k in ("open","high","low","close"))
        v=number(rec["volume"])
        require(lo>0 and lo<=op<=hi and lo<=cl<=hi and v>=0,"OHLCV invariant or nonpositive price")
        if "amount" in reader.fieldnames and rec["amount"] not in ("",None):
            require(number(rec["amount"])>=0,"negative traded amount")
        if time(13,21)<=tm<=time(15,0):
            afternoon.append((lo,hi,dt))
        rows+=1
    require(rows>0,"no rows")
    lo=min((r[0] for r in afternoon),default=None)
    hi=max((r[1] for r in afternoon),default=None)
    anchors={"18.59":None,"18.50":None,"18.03":None}
    if lo is not None:
        anchors={key:lo<=Decimal(key)<=hi for key in anchors}
    return {
       "status":"CANDIDATE_CSV_SCHEMA_ONLY_UNAUTHENTICATED",
       "candidate_date":date_label,
       "candidate_year_proved":False,
       "claimed_instrument":"600151.SH_NOT_AUTHENTICATED_FROM_CSV",
       "local_file_sha256":hashlib.sha256(binary).hexdigest(),
       "file_hash_is_vendor_authentication":False,
       "timestamp_zone_declared":"Asia/Shanghai",
       "timestamp_convention":timestamp_convention,
       "rows":rows,
       "first_time":first.isoformat(sep=" "),
       "last_time":last.isoformat(sep=" "),
       "chart_afternoon_bar_count":len(afternoon),
       "chart_afternoon_price_range":[str(lo),str(hi)] if lo is not None else None,
       "chart_price_anchors_within_range_necessary_only":anchors,
       "chart_identity_matched":False,
       "subminute_path_reconstructed":False,
       "completed_market_movement_proved":False,
       "phi20_proved":False
    }

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--candidate-csv")
    a.add_argument("--candidate-date",default="2007-05-18",choices=["2007-05-18","2006-05-18"])
    a.add_argument("--timestamp-convention",choices=["bar_start","bar_end"])
    args=a.parse_args()
    doc=json.loads(CONTRACT.read_text(encoding="utf-8"))
    meta= audit(doc,json.loads(CHART.read_text(encoding="utf-8")),
                json.loads(M54.read_text(encoding="utf-8")),
                json.loads(M55.read_text(encoding="utf-8")))
    if args.candidate_csv:
        require(args.timestamp_convention is not None,"CSV timestamp convention required")
        meta["candidate_csv"]=inspect_candidate_csv(args.candidate_csv,args.candidate_date,args.timestamp_convention)
    print(json.dumps(meta,ensure_ascii=False,indent=2))
