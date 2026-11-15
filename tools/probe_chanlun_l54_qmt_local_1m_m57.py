#!/usr/bin/env python3
"""M57: bounded XtQuant native LOCAL read of 600151.SH on one unverified day.

No calls to download_history_data, subscribe_quote or file writes. This tool
does not run against a user's Windows QMT merely by running in cloud CI.
"""
from __future__ import annotations
import argparse
import json
import numbers
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"catalog/chanlun_l54_qmt_tdx_local_1m_m57.json"
PRIOR=ROOT/"catalog/chanlun_l54_600151_historical_minute_admission_m56.json"
CODE="600151.SH"
DAY="2007-05-18"
BEIJING=timezone(timedelta(hours=8))
ARGS=dict(field_list=["open","high","low","close","volume","amount"],
          stock_list=[CODE],period="1m",start_time="20070518093000",
          end_time="20070518150000",count=-1,dividend_type="none",fill_data=False)

def need(ok,why):
    if not ok:
        raise ValueError("M57_REJECTED: "+why)

def preflight(doc,prior):
    need(doc.get("schema_version")==1 and
         doc.get("id")=="CHANLUN-M57-L54-600151-LOCAL-QMT-TDX-READONLY-PROBE",
         "contract identity")
    need(prior.get("id")=="CHANLUN-M56-L54-600151-2007-1MIN-PROVENANCE-ADMISSION",
         "M56 document identity")
    need(prior.get("date_proof_status")=="YEAR_NOT_VISIBLE_HYPOTHESIS_ONLY",
         "the chart year remains unverified")
    need(doc.get("instrument")==CODE and doc.get("candidate_date")==DAY,
         "one stock and one candidate day")
    need(doc.get("xtdata_native_args")==ARGS,"native XtData argument contract")
    need(doc.get("native_interface_has_subscribe_keyword") is False and
         doc.get("builtin_qmt_interface_has_subscribe_keyword") is True and
         doc.get("builtin_qmt_readonly_subscribe_value") is False,
         "QMT native/built-in are different APIs")
    need(doc.get("read_modes")==["preflight","xtdata-local"],"bounded read modes")
    tdx=doc.get("tdx_reuse",{})
    need(tdx.get("repository")=="CrazyA1ice/AStockDataTools" and
         tdx.get("path")=="H5ParquetReconciler/tools/probe-tdx-native-readonly.py",
         "TDX existing decoder must be reused")
    need(tdx.get("exists_on_user_machine")=="UNKNOWN" and
         tdx.get("contains_requested_day")=="UNKNOWN","no TDX inspection made")
    need(doc.get("year_independently_confirmed") is False,"year unproven")
    need(all(v is False for v in doc.get("forbidden_outcome_claims",{}).values()),
         "an unauthorized data claim was inserted")
    return {"status":"LOCAL_QMT_NOT_PROBED","instrument":CODE,
            "candidate_date":DAY,"chart_year_confirmed":False,
            "real_market_rows_observed":0,"market_movement_complete":False}

def parse_index(value):
    if isinstance(value,datetime):
        d=value
    elif isinstance(value,numbers.Integral):
        s=str(int(value))
        if len(s)==13:
            d=datetime.fromtimestamp(int(s)/1000,tz=BEIJING)
        elif len(s)==14:
            d=datetime.strptime(s,"%Y%m%d%H%M%S")
        else:
            raise ValueError("M57_REJECTED: unknown numeric QMT time index")
    else:
        s=str(value).strip()
        if len(s)==14 and s.isdigit():
            d=datetime.strptime(s,"%Y%m%d%H%M%S")
        else:
            try:
                d=datetime.fromisoformat(s[:19].replace("T"," "))
            except ValueError:
                raise ValueError("M57_REJECTED: unrecognized QMT index") from None
    return d.astimezone(BEIJING).replace(tzinfo=None) if d.tzinfo else d

def as_decimal(val,key):
    try:
        d=Decimal(str(val))
    except (InvalidOperation,ValueError,TypeError):
        raise ValueError("M57_REJECTED: invalid "+key) from None
    need(d.is_finite(),"nonfinite "+key)
    return d

def scan_frame(df):
    need(hasattr(df,"iterrows"),"requires a DataFrame-like value")
    count=0;first=None;last=None;minimum=None;maximum=None
    for index,bar in df.iterrows():
        at=parse_index(index)
        need(at.date().isoformat()==DAY,"bar outside candidate day")
        need(at.second==0 and at.microsecond==0,"nonminute timestamp")
        mins=at.hour*60+at.minute
        need(570<=mins<=690 or 780<=mins<=900,"bar outside session")
        need(last is None or last<at,"duplicate or reverse timestamp")
        try:
            o=as_decimal(bar["open"],"open")
            h=as_decimal(bar["high"],"high")
            l=as_decimal(bar["low"],"low")
            c=as_decimal(bar["close"],"close")
            v=as_decimal(bar["volume"],"volume")
        except (KeyError,IndexError,TypeError):
            raise ValueError("M57_REJECTED: required OHLCV missing") from None
        need(l>0 and l<=o<=h and l<=c<=h and v>=0,"invalid OHLCV")
        if "amount" in bar and bar["amount"] is not None:
            need(as_decimal(bar["amount"],"amount")>=0,"negative amount")
        minimum=l if minimum is None else min(minimum,l)
        maximum=h if maximum is None else max(maximum,h)
        first=at if first is None else first
        last=at
        count+=1
        need(count<=300,"too many minute rows for one day")
    if not count:
        return {"status":"QMT_LOCAL_DATA_ABSENT_NOT_PROVIDER_PROOF",
                "rows":0,"provider_history_absence_proven":False,
                "chart_date_authenticated":False,"movement_complete":False}
    return {"status":"LOCAL_QMT_CANDIDATE_BARS_FOUND_UNAUTHENTICATED",
            "rows":count,"first_shanghai_time":first.isoformat(sep=" "),
            "last_shanghai_time":last.isoformat(sep=" "),
            "min_max_price":[str(minimum),str(maximum)],
            "chart_18_59_within_full_day_range_necessary_not_sufficient":
               minimum<=Decimal("18.59")<=maximum,
            "chart_date_authenticated":False,"provider_origin_authenticated":False,
            "market_movement_complete":False,"subminute_order_recovered":False,
            "phi20_proven":False}

def query_local_native(xtdata):
    # Native xtdata.get_market_data_ex has no subscribe= keyword.
    result=xtdata.get_market_data_ex(**ARGS)
    need(isinstance(result,dict),"native response must be a stock->frame dict")
    frame=result.get(CODE)
    return scan_frame(frame) if frame is not None else scan_frame(EmptyFrame())

class EmptyFrame:
    def iterrows(self):
        return iter(())

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode",choices=("preflight","xtdata-local"),default="preflight")
    args=parser.parse_args(argv)
    state=preflight(json.loads(CONTRACT.read_text(encoding="utf-8")),
                    json.loads(PRIOR.read_text(encoding="utf-8")))
    if args.mode=="preflight":
        print(json.dumps(state,ensure_ascii=False,indent=2))
        return 0
    try:
        from xtquant import xtdata
    except (ImportError,ModuleNotFoundError):
        print(json.dumps({"status":"QMT_NATIVE_RUNTIME_NOT_AVAILABLE",
                          "market_history_absence_proven":False}))
        return 2
    try:
        result=query_local_native(xtdata)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status":"QMT_LOCAL_READ_OR_VALIDATION_FAILED",
                          "error_type":type(exc).__name__,
                          "market_history_absence_proven":False}))
        return 3

if __name__=="__main__":
    raise SystemExit(main())
