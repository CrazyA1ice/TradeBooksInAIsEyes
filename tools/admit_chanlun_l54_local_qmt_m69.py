#!/usr/bin/env python3
"""M69: local-only QMT 600151 candidate 1m source -> M56 pure bytes audit -> grid.

Native XtData read uses M57 frozen **single stock/date**, fill_data=False,
dividend_type=none; DOES NOT download/subscribe/trade. Default NO file writes.
Optional private export is outside the Git repository and never overwritten.
A candidate historical cache observation cannot authenticate 2007 chart year,
original-market first-known, subminute order, F01 completion, or trading returns.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools import audit_chanlun_l54_2007_minute_candidate_m56 as m56
from tools import probe_chanlun_l54_qmt_local_1m_m57 as m57

SPEC=ROOT/"catalog/chanlun_l54_local_qmt_market_envelope_m69.json"
CODE=m57.CODE
DAY=m57.DAY
FIELDS=m56.FIELDS+["amount"]

def require(ok,msg):
    if not ok:
        raise ValueError("M69_REJECTED: "+msg)

def expected_minutes(date_label,convention):
    require(convention in ("bar_start","bar_end"),"explicit bar timestamp convention required")
    base=datetime.strptime(date_label,"%Y-%m-%d")
    shift=0 if convention=="bar_start" else 1
    return [base.replace(hour=h,minute=m)+timedelta(minutes=i+shift)
            for h,m in ((9,30),(13,0)) for i in range(120)]

def inspect_grid(csv_bytes,date_label,convention):
    require(isinstance(csv_bytes,bytes),"require original candidate bytes")
    rows=list(csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig"))))
    observed=[datetime.strptime(x["time"],"%Y-%m-%d %H:%M:%S") for x in rows]
    expected=expected_minutes(date_label,convention)
    want=set(expected)
    got=set(observed)
    missing=sorted(want-got)
    extra=sorted(got-want)
    if extra:
        state="TIMESTAMP_CONVENTION_CONFLICT_OR_SPECIAL_PROVIDER_BAR"
    elif missing:
        state="PARTIAL_1M_GRID_OR_VALID_NONTRADING"
    else:
        state="FULL_240_DECLARED_GRID_ONLY"
    return {
      "grid_status":state,"expected_slots":240,"observed_rows":len(rows),
      "missing_slot_count":len(missing),"off_declared_grid_count":len(extra),
      "missing_first_8":[x.isoformat(sep=" ") for x in missing[:8]],
      "off_grid_first_8":[x.isoformat(sep=" ") for x in extra[:8]],
      "grid_matches_under_declared_convention":not missing and not extra,
      "provider_2007_coverage_verified":False,
      "bar_close_historical_first_known_verified":False,
      "listed_candidate_date_chart_year_authenticated":False
    }

def inspect_blob(csv_bytes,date_label,convention,origin):
    require(origin in ("QMT_NATIVE_LOCAL_CACHE_READ","USER_PROVIDED_CSV"),"source origin grade")
    # M56 central parser, including chronological, OHLCV, source-window checks.
    base=m56.inspect_candidate_csv_bytes(csv_bytes,date_label,convention)
    grid=inspect_grid(csv_bytes,date_label,convention)
    return {
      "status":"LOCAL_MINUTE_CANDIDATE_SHAPE_ONLY_NOT_AUTHOR_CHART_AUTHENTICATED",
      "read_origin":origin,
      "instrument":CODE if origin=="QMT_NATIVE_LOCAL_CACHE_READ" else "600151.SH_CSV_SELF_DECLARED",
      "candidate_date":date_label,
      "candidate_year_proved":False,
      "byte_sha256":hashlib.sha256(csv_bytes).hexdigest(),
      "byte_digest_is_provider_authentication":False,
      "timestamp_convention_assumed_not_vendor_attested":convention,
      "timezone_declared":"Asia/Shanghai",
      "schema":base,
      "minute_grid":grid,
      "historical_bar_close_first_known_at":"UNKNOWN_NOT_DERIVABLE_FROM_CACHED_1M",
      "real_tick_path":"NOT_ACQUIRED",
      "intraminute_high_low_order_known":False,
      "M68_L17_asof_bar_close_certified":False,
      "M68_L35_3_equal_trades_certified":False,
      "M68_L60_segment_finished_certified":False,
      "F01":"OPEN","Phi20":"OPEN","chart_identity_authenticated":False,
      "real_market_experiments":"NOT_RUN","orders_sent":0,"actual_pnl":"NOT_RUN"
    }

def native_qmt_bytes(xtdata):
    """One local native-cache read; capture exact returned bars in memory only."""
    result=xtdata.get_market_data_ex(**m57.ARGS)
    require(isinstance(result,dict),"native QMT response must be stock->frame mapping")
    frame=result.get(CODE)
    if frame is None:
        return None
    require(hasattr(frame,"iterrows"),"native QMT did not return a DataFrame-like frame")
    raw_rows=list(frame.iterrows())
    # Existing M57 checker refuses out-of-session, duplicates, invalid OHLCV.
    class ReplayFrame:
        def iterrows(self):
            return iter(raw_rows)
    m57.scan_frame(ReplayFrame())
    if not raw_rows:
        return None
    sink=io.StringIO(newline="")
    writer=csv.writer(sink,lineterminator="\n")
    writer.writerow(FIELDS)
    for idx,row in raw_rows:
        t=m57.parse_index(idx)
        def val(k):
            try:
                return str(m57.as_decimal(row[k],k))
            except (KeyError,IndexError,TypeError):
                raise ValueError("M69_REJECTED: QMT missing "+k) from None
        amount=""
        try:
            if "amount" in row and row["amount"] is not None:
                amount=val("amount")
        except (KeyError,IndexError,TypeError):
            pass
        writer.writerow([t.strftime("%Y-%m-%d %H:%M:%S"),
                         val("open"),val("high"),val("low"),val("close"),val("volume"),amount])
    return sink.getvalue().encode("utf-8")

def save_private(csv_bytes,report,private_dir):
    """Opt-in local retention, refuses to write anywhere under this repository."""
    require(report["read_origin"]=="QMT_NATIVE_LOCAL_CACHE_READ","no source-copy for supplied CSV")
    folder=Path(private_dir).expanduser().resolve()
    require(folder!=ROOT and ROOT not in folder.parents,
            "private evidence directory must be outside git repository")
    filename=f"{CODE}_{DAY}_1m_{report['byte_sha256'][:12]}"
    folder.mkdir(parents=True,exist_ok=True)
    receipt=dict(report)
    receipt["private_data_no_git_upload"]=True
    data=json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2).encode("utf-8")+b"\n"
    files=[(folder/(filename+".csv"),csv_bytes),(folder/(filename+".receipt.json"),data)]
    for path,blob in files:
        if path.exists():
            require(path.is_file() and path.read_bytes()==blob,"existing private evidence must not be overwritten")
        else:
            with path.open("xb") as f:
                f.write(blob)
    return {"local_evidence_csv":str(files[0][0]),
            "local_evidence_receipt":str(files[1][0]),
            "private_files_only":True}

def preflight(contract=None):
    d=contract or json.loads(SPEC.read_text(encoding="utf-8"))
    require(d.get("id")=="CHANLUN-M69-L54-LOCAL-QMT-REAL-SOURCE-CANDIDATE-INTAKE"
            and d.get("schema_version")==1,"M69 pinned contract")
    require(d["native_QMT_readonly_kwargs"]==m57.ARGS
            and d["instrument"]==CODE and d["primary_candidate_date"]==DAY,
            "M57 single stock/day must remain pinned")
    require(d["read_modes"]==["preflight","qmt-local","csv"]
            and d["bar_timestamp_declaration_required"]==["bar_start","bar_end"],
            "known explicit modes/conventions only")
    require(d["privacy"]["default_no_file_writes"] is True
            and d["privacy"]["optional_private_export_only_outside_repo"] is True,
            "raw user files must stay private")
    require(d["minute_grid"]["expected_declared_minutes"]==240
            and d["minute_grid"]["historical_provider_convention_proven"] is False,
            "do not assert historic QMT convention")
    states=d["current_status"]
    require(states["local_2007_600151_qmt_call_performed_by_assistant"] is False
            and states["chart_year_proven"] is False
            and states["real_market_experiments"]=="NOT_RUN"
            and states["F01"]==states["OB38"]==states["OB99"]==states["Phi20"]=="OPEN"
            and states["orders"]==0,"cannot forge market or proof completion")
    old=json.loads(m57.CONTRACT.read_text(encoding="utf-8"))
    older=json.loads(m57.PRIOR.read_text(encoding="utf-8"))
    m57.preflight(old,older)
    return {"status":"M69_LOCAL_SOURCE_READ_NOT_YET_RUN",
            "native_kwargs":m57.ARGS,"chart_year_authenticated":False,
            "user_local_cache_inspected":False,"market_experiments":"NOT_RUN"}

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode",choices=("preflight","qmt-local","csv"),default="preflight")
    ap.add_argument("--input-csv",type=Path)
    ap.add_argument("--candidate-date",choices=("2007-05-18","2006-05-18"),default=DAY)
    ap.add_argument("--timestamp-convention",choices=("bar_start","bar_end"))
    ap.add_argument("--private-evidence-dir",type=Path)
    a=ap.parse_args(argv)
    if a.mode=="preflight":
        print(json.dumps(preflight(),ensure_ascii=False,indent=2))
        return 0
    require(a.timestamp_convention is not None,"--timestamp-convention required for real candidate")
    if a.mode=="csv":
        require(a.input_csv is not None and a.private_evidence_dir is None,
                "csv mode reads existing file; no redundant copy/output")
        raw=a.input_csv.read_bytes()
        report=inspect_blob(raw,a.candidate_date,a.timestamp_convention,"USER_PROVIDED_CSV")
    else:
        require(a.input_csv is None and a.candidate_date==DAY,
                "M57 native QMT query pinned to 2007-05-18 only")
        try:
            from xtquant import xtdata
        except (ImportError,ModuleNotFoundError):
            print(json.dumps({"status":"QMT_NATIVE_RUNTIME_NOT_AVAILABLE",
                              "provider_data_absence_proven":False},ensure_ascii=False))
            return 2
        try:
            raw=native_qmt_bytes(xtdata)
        except Exception as e:
            print(json.dumps({"status":"LOCAL_QMT_READ_FAILED_NOT_PROVIDER_ABSENCE",
                              "error_type":type(e).__name__,"provider_data_absence_proven":False},ensure_ascii=False))
            return 3
        if raw is None:
            print(json.dumps({"status":"QMT_LOCAL_CACHE_EMPTY_NOT_PROVIDER_ABSENCE",
                              "source_stock":CODE,"candidate_date":DAY,
                              "chart_year_confirmed":False,"real_market_experiments":"NOT_RUN"},ensure_ascii=False,indent=2))
            return 0
        report=inspect_blob(raw,DAY,a.timestamp_convention,"QMT_NATIVE_LOCAL_CACHE_READ")
        if a.private_evidence_dir is not None:
            report["local_private_export"]=save_private(raw,report,a.private_evidence_dir)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
