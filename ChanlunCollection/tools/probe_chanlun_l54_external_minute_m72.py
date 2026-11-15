#!/usr/bin/env python3
"""M72: deliberately bounded external provider 600151 2006/2007 1m samples.

Default/preflight and access-check are OFFLINE. rqdata-once or ardata-once
requires the user's EXPLICIT CLI choice and their existing local credential.
Only one symbol, one chosen day, one 1m data query per invocation.
No Git uploads or data-file modifications. No vendor data in stdout.
Provider response/date/time/price shapes enter the M56 prior gate; no tick,
original chart identity, real-time first-known, F01, or PnL is inferred.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib import error as urlerror, parse, request
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools import audit_chanlun_l54_2007_minute_candidate_m56 as m56
from tools import admit_chanlun_l54_local_qmt_m69 as m69

SPEC=ROOT/"catalog/chanlun_l54_external_minute_single_day_m72.json"
CANDIDATES=("2007-05-18","2006-05-18")
STOCK_RQ="600151.XSHG"
STOCK_ARDATA="600151.XSHG"
FIELDS=("open","high","low","close","volume")
CANONICAL=("time",*FIELDS,"amount")
API_HOST="https://api.followquant.cn/api/v1"
RESPONSE_MAX=2000000
MAX_BARS=300

def need(ok,reason):
    if not ok:
        raise ValueError("M72_REJECTED: "+reason)

def parse_time(value):
    if isinstance(value,datetime):
        d=value
    elif hasattr(value,"to_pydatetime"):
        d=value.to_pydatetime()
    else:
        try:
            d=datetime.fromisoformat(str(value).replace("Z","+00:00"))
        except (TypeError,ValueError):
            raise ValueError("M72_REJECTED: invalid provider bar timestamp") from None
    if d.tzinfo is not None:
        d=d.astimezone(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None)
    need(d.second==0 and d.microsecond==0,"bar must be aligned to minute")
    return d

def numeric(value,name):
    """Use the old M56 decimal validator; reject NaN/inf and coercion surprises."""
    d=m56.number(value)
    need(d.is_finite(),"invalid "+name)
    return str(d)

def encode_rows(rows,day):
    """In-memory CSV only; deterministic SHA, never submitted or written."""
    need(day in CANDIDATES,"one of the two L54 candidate dates required")
    need(isinstance(rows,list) and len(rows)<=MAX_BARS,"one-day minute row cap")
    if not rows:
        return None
    sink=io.StringIO(newline="")
    writer=csv.writer(sink,lineterminator="\n")
    writer.writerow(CANONICAL)
    prev=None
    for row in rows:
        need(isinstance(row,dict),"provider rows must be dict records")
        at=parse_time(row["time"])
        need(at.date().isoformat()==day,"another year or day in source return")
        need(prev is None or at>prev,"minute timestamps must increase without duplicates")
        prev=at
        values=[numeric(row[name],name) for name in FIELDS]
        amount="" if row.get("amount") is None else numeric(row["amount"],"amount")
        writer.writerow([at.strftime("%Y-%m-%d %H:%M:%S"),*values,amount])
    return sink.getvalue().encode("utf-8")

def from_rq_dataframe(frame,day):
    """RQData: expected MultiIndex(order_book_id,datetime) or datetime index."""
    need(hasattr(frame,"iterrows"),"RQData must return DataFrame-like value")
    result=[]
    for index,series in frame.iterrows():
        if isinstance(index,tuple):
            need(len(index)==2 and str(index[0])==STOCK_RQ,
                 "RQData index symbol must equal requested single stock")
            time=index[1]
        else:
            time=index
        if "order_book_id" in series and series["order_book_id"] is not None:
            need(str(series["order_book_id"])==STOCK_RQ,"returned symbol mismatch")
        row={"time":time}
        for name in FIELDS:
            try:
                row[name]=series[name]
            except (KeyError,IndexError,TypeError):
                raise ValueError("M72_REJECTED: missing RQData "+name) from None
        if "total_turnover" in series:
            row["amount"]=series["total_turnover"]
        result.append(row)
        need(len(result)<=MAX_BARS,"RQData result exceeds one-day cap")
    return encode_rows(result,day)

def query_rq_once(client,day):
    """Exactly one get_price request; never schedules or downloads a range."""
    need(day in CANDIDATES,"unapproved calendar day")
    frame=client.get_price(
        STOCK_RQ,start_date=day,end_date=day,frequency="1m",
        fields=["open","high","low","close","volume","total_turnover"],
        adjust_type="none",skip_suspended=True,expect_df=True,market="cn")
    return from_rq_dataframe(frame,day)

def from_ardata_json(data,day):
    need(isinstance(data,list) and len(data)<=MAX_BARS,"bounded JSON list required")
    rows=[]
    for entry in data:
        need(isinstance(entry,dict),"ARData row must be JSON object")
        symbol=entry.get("code",entry.get("security"))
        need(symbol==STOCK_ARDATA,"ARData return symbol must match requested stock")
        row={"time":entry.get("time")}
        for k in FIELDS:
            need(k in entry,"missing ARData "+k)
            row[k]=entry[k]
        if "money" in entry:
            row["amount"]=entry["money"]
        rows.append(row)
    return encode_rows(rows,day)

def call_ardata_once(api_key,day,opener=None):
    """No SDK dependency; HTTPS pinned, no redirects to arbitrary hosts.

    Login only with a local environment API key. Token and key never logged.
    Explicit ardata-once mode is required; may consume account credits.
    """
    need(day in CANDIDATES and isinstance(api_key,str) and bool(api_key),
         "valid date and locally supplied key required")
    if opener is None:
        # Reject all 3xx redirects before forwarding credentials or Bearer.
        class NoRedirect(request.HTTPRedirectHandler):
            def redirect_request(self,req,fp,code,msg,headers,newurl):
                return None
        opener=request.build_opener(NoRedirect()).open
    auth_data=json.dumps({"api_key":api_key,"expire_days":1}).encode("utf-8")
    login=request.Request(API_HOST+"/auth/login",data=auth_data,
                          headers={"Content-Type":"application/json"},
                          method="POST")
    def read_json(req):
        with opener(req,timeout=20) as response:
            need(response.geturl().startswith(API_HOST+"/"),
                 "redirect outside pinned provider blocked")
            data=response.read(RESPONSE_MAX+1)
        need(len(data)<=RESPONSE_MAX,"provider response over 2MB cap")
        return json.loads(data.decode("utf-8"))
    auth=read_json(login)
    need(isinstance(auth,dict) and isinstance(auth.get("token"),str)
         and bool(auth["token"]),"missing login token")
    query=parse.urlencode({"security":STOCK_ARDATA,"start_date":day,
                           "end_date":day,"frequency":"1m"})
    url=API_HOST+"/get_price?"+query
    req=request.Request(url,headers={"Authorization":"Bearer "+auth["token"]},
                        method="GET")
    # No fq param = no adjustment per ARData's published contract.
    return from_ardata_json(read_json(req),day)

def anchor_summary(csv_bytes):
    reader=csv.DictReader(io.StringIO(csv_bytes.decode("utf-8")))
    total=0
    afternoons=0
    h1859=l1803=c1803=c1850=0
    for r in reader:
        total+=1
        if r["time"][11:16]>="13:21":
            afternoons+=1
            if m56.number(r["high"])==m56.number("18.59"): h1859+=1
            if m56.number(r["low"])==m56.number("18.03"): l1803+=1
            if m56.number(r["close"])==m56.number("18.03"): c1803+=1
            if m56.number(r["close"])==m56.number("18.50"): c1850+=1
    return {"afternoon_1321_to_1500_rows":afternoons,
            "bar_high_exact_18_59_hits_necessary_only":h1859,
            "bar_low_exact_18_03_hits_necessary_only":l1803,
            "bar_close_exact_18_03_hits_necessary_only":c1803,
            "bar_close_exact_g0_18_50_hits_necessary_only":c1850,
            "price_annotation_is_not_precise_author_chart_bar_id":True}

def admit(csv_bytes,provider,day,convention):
    need(provider in ("RQDATA","ARDATA"),"known external source labels")
    need(day in CANDIDATES and convention in ("bar_start","bar_end"),
         "candidate/date/time convention must be explicit")
    if csv_bytes is None:
        return {"status":"PROVIDER_RETURNED_ZERO_ROWS_NOT_COVERAGE_PROOF",
                "provider":provider,"candidate_date":day,
                "vendor_historical_coverage_absent_proven":False,
                "chart_date_authenticated":False,"F01":"OPEN",
                "E1_E4":"NOT_RUN","orders":0}
    # Reuse M56's original strict OHLCV, session and chronologic gate.
    old=m56.inspect_candidate_csv_bytes(csv_bytes,day,convention)
    grid=m69.inspect_grid(csv_bytes,day,convention)
    return {"status":"EXTERNAL_SINGLE_DAY_MINUTE_CANDIDATE_ADMITTED_NOT_CHART_AUTHENTICATED",
            "provider":provider,"requested_stock":"600151.XSHG",
            "candidate_date":day,"frequency":"1m","adjustment":"none_requested",
            "skip_suspended_rqdata":True if provider=="RQDATA" else None,
            "declared_time_zone":"Asia/Shanghai",
            "declared_bar_label_not_authoritative":convention,
            "normalized_csv_sha256":hashlib.sha256(csv_bytes).hexdigest(),
            "hash_is_provider_signature":False,
            "rows":old["rows"],"first_time":old["first_time"],"last_time":old["last_time"],
            "grid":grid,"anchors":anchor_summary(csv_bytes),
            "chart_year_authenticated":False,
            "author_chart_identity_authenticated":False,
            "historical_first_known_available":False,
            "tick_price_order_recovered":False,
            "F01":"OPEN","OB38":"OPEN","OB99":"OPEN","Phi20":"OPEN",
            "E1_E4":"NOT_RUN","orders":0,"trading_performance":"NOT_RUN"}

def access_check():
    return {"status":"OFFLINE_PROVIDER_READINESS_CHECK",
            "rqdatac_installed":importlib.util.find_spec("rqdatac") is not None,
            "ardata_key_environment_present":bool(os.environ.get("ARDATA_API_KEY")),
            "provider_network_queries":0,
            "account_authorized":False,"data_2007_observed":False,
            "no_credentials_printed":True}

def preflight(spec=None):
    doc=spec if spec is not None else json.loads(SPEC.read_text(encoding="utf-8"))
    need(doc.get("schema_version")==1 and doc.get("id")==
         "CHANLUN-M72-2006-2007-EXTERNAL-MINUTE-ONE-DAY-PROVENANCE-GATE",
         "contract ID")
    need(doc["single_stock"]=="600151.XSHG"
         and doc["candidate_dates"]==list(CANDIDATES),
         "stock or candidate dates changed")
    need(doc["rqdata"]["adjust_type"]=="none"
         and doc["rqdata"]["skip_suspended"] is True,
         "RQData adjusted or imputed suspended bars not allowed")
    need(doc["ardata"]["base_url"]==API_HOST
         and doc["ardata"]["fq_absent_means_none"] is True,
         "ARData request semantics changed")
    need(doc["privacy"]["default_no_provider_query"] is True
         and doc["privacy"]["no_raw_market_rows_stdout_or_repo"] is True
         and doc["privacy"]["do_not_print_credentials"] is True,
         "secrets/source protection")
    s=doc["status"]
    need(s["provider_day_source_acquired"] is False and
         s["F01"]==s["OB38"]==s["OB99"]==s["Phi20"]=="OPEN"
         and s["E1_E4"]=="NOT_RUN",
         "cannot claim market acquisition on unrun provider")
    need(m69.preflight()["market_experiments"]=="NOT_RUN","M69 must remain frozen")
    return {"status":"M72_EXTERNAL_ONE_DAY_SOURCE_GATE_READY_NOT_QUERIED",
            "real_2007_minute_rows_received":0,
            "provider_access_rights_verified":False,
            "author_chart_year_authenticated":False,
            "market_experiments":"NOT_RUN"}

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode",choices=("preflight","access-check","rqdata-once","ardata-once"),
                    default="preflight")
    ap.add_argument("--candidate-date",choices=CANDIDATES,default="2007-05-18")
    ap.add_argument("--timestamp-convention",choices=("bar_start","bar_end"))
    a=ap.parse_args(argv)
    if a.mode=="preflight":
        print(json.dumps(preflight(),ensure_ascii=False,indent=2))
        return 0
    if a.mode=="access-check":
        print(json.dumps(access_check(),ensure_ascii=False,indent=2))
        return 0
    need(a.timestamp_convention is not None,
         "explicit bar-start/bar-end assumption required for paid request")
    if a.mode=="rqdata-once":
        try:
            import rqdatac
        except (ImportError,ModuleNotFoundError):
            print(json.dumps({"status":"RQDATAC_NOT_INSTALLED",
                              "provider_2007_history_unavailable_proven":False}))
            return 2
        try:
            # Per official RQData manual: uses user's own local credential profile.
            rqdatac.init()
            raw=query_rq_once(rqdatac,a.candidate_date)
        except Exception as err:
            print(json.dumps({"status":"RQDATA_INIT_OR_QUERY_FAILED",
                              "error_class":type(err).__name__,
                              "details_redacted":True,
                              "vendor_history_absence_proven":False}))
            return 3
        provider="RQDATA"
    else:
        key=os.environ.get("ARDATA_API_KEY")
        if not key:
            print(json.dumps({"status":"ARDATA_KEY_ENVIRONMENT_MISSING",
                              "network_queries":0,"no_key_printed":True}))
            return 2
        try:
            raw=call_ardata_once(key,a.candidate_date)
        except Exception as err:
            code=getattr(err,"code",None)
            print(json.dumps({"status":"ARDATA_AUTH_OR_QUERY_FAILED",
                              "http_status":code if type(code) is int else None,
                              "error_class":type(err).__name__,
                              "details_redacted":True,
                              "vendor_history_absence_proven":False}))
            return 3
        provider="ARDATA"
    # No file ever written; provider return is admitted to the old M56.
    result=admit(raw,provider,a.candidate_date,a.timestamp_convention)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
