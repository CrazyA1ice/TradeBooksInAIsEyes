#!/usr/bin/env python3
"""M70: bounded local TDX .lc1 minute keys vs M69 native QMT minute keys.

Only date and minute are decoded from the TDX 32-byte records; no TDX price,
amount or volume interpretation. No network, file writes, uploads, or orders
are initiated by this code. Native QMT branch reuses frozen M69 local read.
Clock overlap NEVER authenticates historical prices, original chart or F01.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import struct
import sys
from datetime import date, datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from tools import admit_chanlun_l54_local_qmt_m69 as m69

SPEC=ROOT/"catalog/chanlun_l54_tdx_qmt_clock_intersection_m70.json"
DEFAULT_TDX=Path(r"D:\software\TDX\vipdoc\sh\minline\sh600151.lc1")
RECORD_SIZE=32
MAX_BYTES=64*1024*1024
HEADER=struct.Struct("<HH")
DAYS=("2006-05-18","2007-05-18")
GRID={
 "TDX_1MIN_START_240":tuple(list(range(570,690))+list(range(780,900))),
 "TDX_1MIN_END_240":tuple(list(range(571,691))+list(range(781,901))),
 "TDX_OPENING_PLUS_END_241":tuple(list(range(570,691))+list(range(781,901)))
}

def need(ok,reason):
    if not ok:
        raise ValueError("M70_REJECTED: "+reason)

def decode_key(raw):
    need(type(raw) is bytes and len(raw)==32,"native record must have 32 bytes")
    packed,minute=HEADER.unpack_from(raw)
    year=2004+packed//2048
    fragment=packed%2048
    try:
        day=date(year,fragment//100,fragment%100)
    except ValueError:
        raise ValueError("M70_REJECTED: invalid compressed TDX calendar date") from None
    need(2004<=year<=2100 and 0<=minute<1440,"TDX date/minute bounds")
    return day.isoformat(),minute

def scan_tdx(path,max_bytes=MAX_BYTES):
    """No side effects; file digest and all-order check, two candidate days held."""
    path=Path(path)
    need(path.name.lower()=="sh600151.lc1","only sh600151.lc1 target supported")
    need(type(max_bytes) is int and 32<=max_bytes<=MAX_BYTES,"bounded source budget")
    need(path.is_file() and not path.is_symlink(),"native source must be regular not symlink")
    stat_before=path.stat()
    need(0<stat_before.st_size<=max_bytes and stat_before.st_size%32==0,
         "TDX must be nonempty bounded 32-byte aligned")
    digest=hashlib.sha256()
    first=None
    last=None
    previous=None
    keys={d:[] for d in DAYS}
    total=0
    with path.open("rb") as handle:
        for _ in range(stat_before.st_size//32):
            record=handle.read(32)
            need(len(record)==32,"native file truncated during read")
            digest.update(record)
            d,minute=decode_key(record)
            key=(d,minute)
            need(previous is None or key>previous,"source minute keys not increasing")
            previous=key
            first=first or d
            last=d
            total+=1
            if d in keys:
                keys[d].append(minute)
        need(not handle.read(1),"source appended during read")
    stat_after=path.stat()
    need(stat_before.st_size==stat_after.st_size and
         stat_before.st_mtime_ns==stat_after.st_mtime_ns,
         "source stat changed while reading")
    dates={}
    for day,minutes in keys.items():
        profile=next((k for k,v in GRID.items() if tuple(minutes)==v),None)
        dates[day]={
          "rows":len(minutes),"profile":profile,
          "status":("DATE_NOT_IN_LOCAL_FILE" if not minutes
                    else "RECOGNIZED_NATIVE_MINUTE_PROFILE" if profile
                    else "PARTIAL_OR_UNRECOGNIZED_NATIVE_GRID"),
          "vendor_history_absence_proven":False
        }
    report={
      "status":"LOCAL_TDX_DATE_CLOCK_OBSERVED_NOT_AUTHOR_CHART_AUTHENTICATED",
      "source_basename":path.name,"source_bytes":stat_before.st_size,
      "source_total_records":total,"source_first_date":first,"source_last_date":last,
      "source_sha256":digest.hexdigest(),
      "digest_is_vendor_signature":False,"source_stable_during_read":True,
      "date_minute_layout":"ASSUMED_COMMON_TDX_32BYTE_HEADER",
      "stock_identity":"600151.SH_FILENAME_ONLY",
      "tdx_prices_or_volumes_decoded":False,
      "source_bars_exported":False,"individual_minutes_exported":False,
      "dates":dates,"chart_year_authenticated":False,
      "F01":"OPEN","E1_E4":"NOT_RUN"
    }
    return report,keys

def qmt_minutes(raw):
    need(isinstance(raw,bytes) and raw,"QMT bytes needed")
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8")))
    times=[datetime.strptime(row["time"],"%Y-%m-%d %H:%M:%S") for row in reader]
    need(all(t.date().isoformat()==m69.DAY for t in times),
         "QMT snapshot must be frozen candidate day")
    need(len(times)==len(set(times)),"QMT times cannot repeat")
    return [t.hour*60+t.minute for t in times]

def compare(qmt_keys,tdx_keys,qmt_convention,tdx_convention,tdx_profile=None):
    need(qmt_convention in ("bar_start","bar_end") and
         tdx_convention in ("bar_start","bar_end"),
         "both time-label conventions must be explicit")
    base={"price_equal_proven":False,"chart_year_authenticated":False,
          "provider_authenticated":False,"historical_first_known_verified":False,
          "subminute_path_reconstructed":False,"F01":"OPEN","E1_E4":"NOT_RUN"}
    if qmt_keys is None or tdx_keys is None:
        return dict(base,status="ONE_LOCAL_SOURCE_MISSING_NOT_COMPARABLE")
    if tdx_profile in ("TDX_1MIN_START_240","TDX_1MIN_END_240"):
        observed="bar_start" if tdx_profile=="TDX_1MIN_START_240" else "bar_end"
        if observed!=tdx_convention:
            return dict(base,status="TDX_DECLARED_CONVENTION_CONFLICTS_WITH_FULL_GRID",
                        detected=tdx_profile)
    def normalized(values,convention):
        return [int(x)-(1 if convention=="bar_end" else 0) for x in values]
    a=normalized(qmt_keys,qmt_convention)
    b=normalized(tdx_keys,tdx_convention)
    need(len(a)==len(set(a)) and len(b)==len(set(b)),
         "normalization produced duplicate minute intervals")
    sa,sb=set(a),set(b)
    status=("LOCAL_INTERVAL_KEYS_AGREE_ONLY" if sa==sb and sa
            else "LOCAL_TIME_KEYS_DIFFER" if sa or sb
            else "BOTH_LOCAL_SOURCES_MISSING_CANDIDATE_DAY")
    return dict(base,status=status,local_qmt_minutes=len(sa),
                local_tdx_minutes=len(sb),common_minutes=len(sa&sb),
                qmt_only_minutes=len(sa-sb),tdx_only_minutes=len(sb-sa),
                qmt_convention=qmt_convention,tdx_convention=tdx_convention,
                tdx_recognized_profile=tdx_profile)

def get_local_qmt(convention):
    need(convention in ("bar_start","bar_end"),"explicit QMT convention")
    try:
        from xtquant import xtdata
    except (ModuleNotFoundError,ImportError):
        return {"status":"QMT_RUNTIME_MISSING_NOT_PROVIDER_ABSENCE"},None
    try:
        raw=m69.native_qmt_bytes(xtdata)
    except (ValueError,KeyError,RuntimeError,TypeError):
        return {"status":"QMT_LOCAL_READ_FAILED_NOT_PROVIDER_ABSENCE"},None
    if raw is None:
        return {"status":"QMT_LOCAL_CACHE_EMPTY_NOT_PROVIDER_ABSENCE"},None
    report=m69.inspect_blob(raw,m69.DAY,convention,"QMT_NATIVE_LOCAL_CACHE_READ")
    return {
       "status":"QMT_LOCAL_CANDIDATE_SHAPE_ONLY",
       "rows":report["schema"]["rows"],"normalized_bytes_sha256":report["byte_sha256"],
       "time_grid_status":report["minute_grid"]["grid_status"],
       "missing_grid_slots":report["minute_grid"]["missing_slot_count"],
       "off_grid_slots":report["minute_grid"]["off_declared_grid_count"],
       "source_prices_exported":False,
       "historical_first_known_at":"UNKNOWN",
       "chart_identity_authenticated":False
    },qmt_minutes(raw)

def preflight(doc=None):
    d=doc if doc is not None else json.loads(SPEC.read_text(encoding="utf-8"))
    need(d.get("schema_version")==1 and
         d.get("id")=="CHANLUN-M70-TDX-QMT-LOCAL-NATIVE-CLOCK-INTERSECTION",
         "contract identity")
    need(d["instrument"]=="600151.SH" and d["candidate_dates"]==list(DAYS)
         and d["qmt_day"]==m69.DAY,"fixed stock/day candidates")
    layout=d["tdx_native_layout"]
    need(layout["record_bytes"]==32 and layout["header"]=="<HH"
         and layout["max_bytes"]==MAX_BYTES,"bounded TDX time decoder")
    privacy=d["privacy"]
    need(all(privacy[x] is True for x in ("default_no_file_writes",
         "not_upload_paid_bars","never_write_local_market_file")),"raw data privacy")
    state=d["status"]
    need(state["real_tdx_or_qmt_windows_inspected_by_assistant"] is False
         and state["chart_year_confirmed"] is False
         and state["F01"]=="OPEN" and state["E1_E4"]=="NOT_RUN",
         "cannot forge completed market evidence")
    need(m69.preflight()["status"]=="M69_LOCAL_SOURCE_READ_NOT_YET_RUN",
         "prior M69 local source contract")
    return {"status":"M70_LOCAL_DUAL_SOURCE_GATE_READY_BUT_NOT_RUN_ON_WINDOWS",
            "candidate_dates":list(DAYS),"user_local_files_inspected":False,
            "market_experiments":"NOT_RUN"}

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode",choices=("preflight","tdx-local","dual-local"),default="preflight")
    ap.add_argument("--tdx-file",type=Path,default=DEFAULT_TDX)
    ap.add_argument("--qmt-convention",choices=("bar_start","bar_end"))
    ap.add_argument("--tdx-convention",choices=("bar_start","bar_end"))
    args=ap.parse_args(argv)
    if args.mode=="preflight":
        print(json.dumps(preflight(),ensure_ascii=False,indent=2))
        return 0
    need(args.tdx_convention is not None,"TDX convention required")
    report={"mode":args.mode,"candidate_dates":list(DAYS),
            "chart_year_authenticated":False,"market_experiments":"NOT_RUN",
            "raw_data_exported":False}
    keys=None
    need(not args.tdx_file.is_symlink(),"symlink TDX input refused")
    if args.tdx_file.is_file():
        report["tdx"],keys=scan_tdx(args.tdx_file)
    else:
        report["tdx"]={"status":"TDX_LOCAL_FILE_MISSING_NOT_PROVIDER_ABSENCE",
                       "candidate_basename":args.tdx_file.name}
    if args.mode=="dual-local":
        need(args.qmt_convention is not None,"QMT convention required")
        report["qmt"],qkeys=get_local_qmt(args.qmt_convention)
        tkeys=keys[m69.DAY] if keys is not None else None
        profile=report["tdx"]["dates"][m69.DAY]["profile"] if keys is not None else None
        report["comparison"]=compare(qkeys,tkeys,args.qmt_convention,
                                     args.tdx_convention,profile)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
