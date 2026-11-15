#!/usr/bin/env python3
"""M73: bounded public historical A-share 1m archive source check.

No account, paid API, installer, persistent data writes, or trading.
Default --mode preflight uses NO network. Real public queries require explicit
--mode hf-once or zzshare-once. Only 600151 and 2007/2006-05-18 admissible.
Never echo original OHLCV rows; assert source identity and time before M56/M69.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib import error as urlerror, parse, request

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from tools import probe_chanlun_l54_external_minute_m72 as m72

HF_DATASET="OxFengyuan/stock_dataset"
HF_HOST="https://huggingface.co"
HF_DIRECTORY="A股分钟/2000-2024/{year}/1分钟"
ZZ_HOST="https://api.zizizaizai.com"
ZZ_ROUTE="/v3/market/kline/minute/600151.SH"
CANDIDATES=m72.CANDIDATES
MAX_HF_FILE=30*1024*1024
MAX_JSON=3*1024*1024
MAX_PAGES=12
MAX_ROWS_IN_YEAR=140000
ALLOWED_FILENAMES={"600151csv","sh600151csv","600151shcsv",
                   "xshg600151csv","600151xshgcsv"}
SPEC=ROOT/"catalog/chanlun_l54_github_public_minute_2007_m73.json"

def require(value,reason):
    if not value:
        raise ValueError("M73_REJECTED: "+reason)

def http_read(url,cap,opener=None):
    require(url.startswith(HF_HOST+"/") or url.startswith(ZZ_HOST+"/"),
            "unexpected remote URL")
    opener=opener or request.urlopen
    req=request.Request(url,headers={"User-Agent":"Chanlun-L54-M73-public-single-day-source-probe/1.0",
                                    "Accept":"application/json,text/csv,*/*",
                                    **({"sdk-key":"anonymous"} if url.startswith(ZZ_HOST) else {})})
    with opener(req,timeout=25) as resp:
        # Repository LFS uses trusted HF/Xet storage redirectors; no account
        # token is ever attached. Never forward a user credential.
        status=getattr(resp,"status",200)
        require(status==200,"HTTP non-200 response")
        final=resp.geturl()
        host=parse.urlparse(final).hostname or ""
        require(host in ("huggingface.co","cdn-lfs.hf.co","cas-bridge.xethub.hf.co",
                          "cas-server.xethub.hf.co","api.zizizaizai.com")
                or host.endswith(".xethub.hf.co"),
                "redirect to unexpected host")
        data=resp.read(cap+1)
        require(len(data)<=cap,"response exceeds bounded byte limit")
        return data,dict(resp.headers)

def get_json(url,opener=None):
    raw,headers=http_read(url,MAX_JSON,opener=opener)
    return json.loads(raw.decode("utf-8")),headers

def normalize_name(name):
    return re.sub("[^a-z0-9]","",name.lower())

def hf_directory_file(day,getter=None):
    """List one year/period directory, not all 201,000 MiB of dataset."""
    require(day in CANDIDATES,"unsupported candidate date")
    getter=getter or get_json
    directory=HF_DIRECTORY.format(year=day[:4])
    prefix=f"{HF_HOST}/api/datasets/{HF_DATASET}/tree/main/"
    url=prefix+parse.quote(directory,safe="/")+"?limit=100"
    visited=set()
    for page in range(MAX_PAGES):
        require(url not in visited,"pagination loop")
        require(url.startswith(prefix),"HF pagination crossed fixed repository")
        visited.add(url)
        entries,headers=getter(url)
        require(isinstance(entries,list) and len(entries)<=100,"HF directory listing shape")
        for entry in entries:
            require(isinstance(entry,dict),"HF entry shape")
            path=entry.get("path","")
            require(isinstance(path,str),"HF entry path type")
            if (entry.get("type")=="file" and path.startswith(directory+"/")
                and normalize_name(Path(path).name) in ALLOWED_FILENAMES):
                size=entry.get("size")
                require(isinstance(size,int) and 0<size<=MAX_HF_FILE,
                        "annual file must fit 30 MiB cap")
                return {"path":path,"size":size,"lfs":entry.get("lfs"),
                        "directory_verified":True,"pages_scanned":page+1}
        link=headers.get("Link") or headers.get("link") or ""
        m=re.search(r'<([^>]+)>;\s*rel="next"',link)
        if not m:
            return {"status":"HF_TARGET_NOT_FOUND_IN_LISTED_DIRECTORY",
                    "year":day[:4],"pages_scanned":page+1,
                    "dataset_absence_proven":False,
                    "directory":directory}
        url=m.group(1)
        require(url.startswith(prefix),"HF pagination redirected outside repository")
    return {"status":"HF_DIRECTORY_PAGINATION_LIMIT_NOT_ABSENCE",
            "year":day[:4],"pages_scanned":MAX_PAGES,
            "directory":directory,"dataset_absence_proven":False}

def parse_time_parts(row):
    lower={str(k).strip().lower():v for k,v in row.items() if k is not None}
    date=next((lower[k] for k in ("datetime","date_time","trade_time",
                                 "date","交易日期","日期","时间","timestamp")
               if k in lower and str(lower[k]).strip()),None)
    time=next((lower[k] for k in ("time","交易时间","时间","minute","分钟")
               if k in lower and str(lower[k]).strip()),None)
    if date is None:
        return None
    s=str(date).strip().replace("/","-").replace("T"," ")
    if re.fullmatch(r"\d{8}",s):
        s=f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    elif re.fullmatch(r"\d{12}(\d{2})?",s):
        # YYYYMMDDHHMM[SS]
        s=f"{s[:4]}-{s[4:6]}-{s[6:8]} {s[8:10]}:{s[10:12]}:00"
    if len(s)==10 and time is None:
        # A date-only minute row is not a valid 00:00 bar.
        return None
    if len(s)==10 and time is not None:
        t=str(time).strip()
        if re.fullmatch(r"\d{3,4}",t):
            t=t.zfill(4)
            t=f"{t[:2]}:{t[2:]}:00"
        s=s+" "+t
    if len(s)==16 and s[10]==" ":
        s+=":00"
    try:
        d=datetime.fromisoformat(s)
    except (ValueError,TypeError):
        return None
    if d.tzinfo is not None or d.second!=0 or d.microsecond!=0:
        return None
    return d

def first(row,keys):
    idx={str(k).strip().lower():v for k,v in row.items() if k is not None}
    for k in keys:
        if k in idx and idx[k] not in ("",None):
            return idx[k]
    raise ValueError("M73_REJECTED: required OHLCV field not found")

def csv_annual_day_rows(raw,day):
    require(day in CANDIDATES,"unapproved date")
    try:
        s=raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        s=raw.decode("gb18030")
    reader=csv.DictReader(io.StringIO(s))
    cols=list(reader.fieldnames or [])
    require(len(cols)>=5 and len(cols)<=40,"unexpected annual CSV columns")
    out=[]
    total=0
    malformed_target=0
    sample_time_column=False
    for row in reader:
        total+=1
        require(total<=MAX_ROWS_IN_YEAR,"annual record cap")
        ts=parse_time_parts(row)
        if ts is None:
            # Do not skip corrupt rows that visibly belong to the target day.
            if day in " ".join(str(v) for v in row.values()):
                malformed_target+=1
            continue
        sample_time_column=True
        if ts.date().isoformat()!=day:
            continue
        obj={"time":ts,
             "open":first(row,("open","开盘","开盘价")),
             "high":first(row,("high","最高","最高价")),
             "low":first(row,("low","最低","最低价")),
             "close":first(row,("close","收盘","收盘价")),
             "volume":first(row,("volume","vol","成交量"))}
        for k in ("amount","money","成交额"):
            if k in {str(x).strip().lower() for x in row}:
                obj["amount"]=first(row,("amount","money","成交额"))
                break
        out.append(obj)
        require(len(out)<=300,"target day exceeds maximum minute bars")
    require(malformed_target==0,"target date present but timestamp parsing failed")
    return {"rows":sorted(out,key=lambda r:r["time"]),
            "annual_rows":total,"headers":cols,
            "any_valid_year_timestamp":sample_time_column,
            "date_present":bool(out)}

def hf_once(day,convention,listing=None,fetcher=None):
    require(day in CANDIDATES and convention in ("bar_start","bar_end"),
            "explicit day and timestamp label convention")
    listing=listing or hf_directory_file
    fetcher=fetcher or http_read
    try:
        evidence=listing(day)
    except urlerror.HTTPError as err:
        if err.code!=401:
            raise
        # HF free tree listing can be 401 when asking for many entries.
        # A 2007 directory with sh6000xx CSVs was independently observed.
        # Try precisely one guessed stock-year object, never an entire archive.
        evidence={"path":HF_DIRECTORY.format(year=day[:4])+"/sh600151.csv",
                  "size":None,"lfs":None,"directory_metadata_http_status":401,
                  "direct_filename_guess_not_metadata_authenticated":True}
    if "path" not in evidence:
        return {"provider":"HF_PUBLIC_ARCHIVE","candidate_date":day,**evidence,
                "market_experiments":"NOT_RUN"}
    path=evidence["path"]
    require(path.startswith(HF_DIRECTORY.format(year=day[:4])+"/"),
            "path escaped fixed year directory")
    url=f"{HF_HOST}/datasets/{HF_DATASET}/resolve/main/"+parse.quote(path,safe="/")
    raw,_=fetcher(url,MAX_HF_FILE)
    size=len(raw)
    if evidence["size"] is not None:
        require(size==evidence["size"],"HF listing size disagrees with downloaded file")
    digest=hashlib.sha256(raw).hexdigest()
    lfs=evidence.get("lfs") or {}
    lfs_oid=lfs.get("oid") if isinstance(lfs,dict) else None
    if lfs_oid:
        require(digest==lfs_oid.replace("sha256:",""),"LFS blob sha256 mismatch")
    parsed=csv_annual_day_rows(raw,day)
    report={"provider":"HF_PUBLIC_ARCHIVE","candidate_date":day,
            "dataset":HF_DATASET,"archive_file":path,
            "annual_file_bytes":size,"annual_file_sha256":digest,
            "hf_repository_lfs_sha256_matches_download":bool(lfs_oid),
            "annual_csv_total_rows":parsed["annual_rows"],
            "csv_headers":parsed["headers"],
            "annual_csv_has_valid_datetime":parsed["any_valid_year_timestamp"],
            "declared_adjustment":"NOT_VERIFIED",
            "direct_filename_guess_not_metadata_authenticated":evidence.get("direct_filename_guess_not_metadata_authenticated",False),
            "dataset_source_rights":"NOT_VERIFIED",
            "original_chart_year_authenticated":False}
    if not parsed["rows"]:
        return {**report,"status":"HF_ANNUAL_FILE_HAS_NO_TARGET_DAY_OR_UNKNOWN_TIME_FORMAT",
                "day_bars":0,"provider_coverage_proven":False,
                "market_experiments":"NOT_RUN"}
    csv_bytes=m72.encode_rows(parsed["rows"],day)
    admitted=m72.admit(csv_bytes,"RQDATA",day,convention)
    # RQDATA is only the M72 schema adapter label; change it back to the
    # actual independently identified HF archive source in the public report.
    admitted["provider"]="HF_PUBLIC_ARCHIVE"
    admitted["source_adapter"]="M72_CANONICAL_CSV_GATE_NOT_RQDATA_AUTH"
    admitted["adjustment_status"]="UNVERIFIED_NO_AUTOMATIC_RAW_PRICE_CLAIM"
    admitted["adjustment"]="UNVERIFIED_NOT_RQDATA_REQUEST"
    admitted["skip_suspended_rqdata"]=None
    return {**report,"status":"HF_PUBLIC_ANNUAL_CSV_TARGET_DAY_ADMITTED_NOT_AUTHOR_AUTHENTICATED",
            "admission":admitted,"market_experiments":"NOT_RUN"}

def zzshare_once(day,convention,getter=None):
    require(day in CANDIDATES and convention in ("bar_start","bar_end"),
            "explicit day and minute convention")
    getter=getter or get_json
    url=ZZ_HOST+ZZ_ROUTE+"?"+parse.urlencode({"freq":"1min",
                                             "trade_time":day.replace("-","")})
    body,_=getter(url)
    require(isinstance(body,dict),"zzshare JSON top-level dict")
    code=body.get("code")
    if code not in (200,20000):
        return {"status":"ZZSHARE_API_NON_SUCCESS_NOT_HISTORY_ABSENCE",
                "api_code":code if isinstance(code,int) else None,
                "candidate_date":day,"provider":"ZZSHARE",
                "provider_history_absence_proven":False,"E1_E4":"NOT_RUN"}
    data=body.get("data")
    rows=data if isinstance(data,list) else (data.get("list") if isinstance(data,dict) else None)
    if rows is None:
        rows=[]
    require(isinstance(rows,list) and len(rows)<=300,"zzshare one-day limit")
    candidate=[]
    for row in rows:
        require(isinstance(row,dict),"zzshare bar must be dict")
        stock=row.get("code",row.get("ts_code","600151.SH"))
        require(str(stock).upper().replace(".","") in ("600151SH","SH600151","600151"),
                "zzshare returned another stock")
        d=parse_time_parts({"trade_time":row.get("trade_time")})
        require(d is not None and d.date().isoformat()==day,
                "zzshare result must be same day and minute timestamp")
        candidate.append({"time":d,"open":first(row,("open",)),
                          "high":first(row,("high",)),"low":first(row,("low",)),
                          "close":first(row,("close",)),
                          "volume":first(row,("vol","volume")),
                          "amount":row.get("amount")})
    if not candidate:
        return {"status":"ZZSHARE_ZERO_ROWS_NOT_HISTORICAL_COVERAGE_PROOF",
                "provider":"ZZSHARE","candidate_date":day,
                "provider_history_absence_proven":False,"F01":"OPEN",
                "E1_E4":"NOT_RUN"}
    candidate.sort(key=lambda r:r["time"])
    result=m72.admit(m72.encode_rows(candidate,day),"RQDATA",day,convention)
    result["provider"]="ZZSHARE"
    result["source_adapter"]="M72_CANONICAL_CSV_GATE_NOT_RQDATA_AUTH"
    result["adjustment_status"]="NO_ADJUSTMENT_PARAMETER_REPORTED_BY_SDK_NOT_VENDOR_CERTIFIED"
    result["adjustment"]="UNVERIFIED_NOT_RQDATA_REQUEST"
    result["skip_suspended_rqdata"]=None
    return {"status":"ZZSHARE_PUBLIC_SINGLE_DAY_CANDIDATE_ADMITTED_NOT_AUTHOR_AUTHENTICATED",
            "provider":"ZZSHARE","candidate_date":day,"admission":result,
            "market_experiments":"NOT_RUN"}

def preflight(doc=None):
    doc=doc or json.loads(SPEC.read_text(encoding="utf-8"))
    require(doc.get("id")=="CHANLUN-M73-GITHUB-2007-1M-PUBLIC-ARCHIVE-ONE-DAY",
            "contract identifier")
    require(doc.get("candidate_dates")==list(CANDIDATES),
            "cannot change target hypothesis")
    require(doc.get("hf_dataset")==HF_DATASET and
            doc.get("zzshare_url")==ZZ_HOST+ZZ_ROUTE,
            "pinned public source identities")
    require(doc["source_status"]["2007_1m_acquired"] is False,
            "cannot fake market-data receipt")
    require(doc["default_no_network"] is True
            and doc["raw_rows_to_stdout"] is False
            and doc["write_market_data_to_git"] is False,
            "privacy and no-network invariants")
    return {"status":"M73_PUBLIC_ARCHIVE_GATE_READY_NOT_QUERIED",
            "primary_source":"HF_PUBLIC_ARCHIVE_2000_2024_1MIN",
            "secondary_source":"ZZSHARE_PUBLIC_SINGLE_DAY_1MIN",
            "data_2007_observed":False,"provider_network_queries":0,
            "F01":"OPEN","E1_E4":"NOT_RUN"}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode",choices=("preflight","hf-once","zzshare-once"),
                   default="preflight")
    p.add_argument("--candidate-date",choices=CANDIDATES,default="2007-05-18")
    p.add_argument("--timestamp-convention",choices=("bar_start","bar_end"))
    a=p.parse_args(argv)
    if a.mode=="preflight":
        print(json.dumps(preflight(),ensure_ascii=False,indent=2));return 0
    require(a.timestamp_convention is not None,
            "explicit convention required before public provider request")
    try:
        if a.mode=="hf-once":
            answer=hf_once(a.candidate_date,a.timestamp_convention)
        else:
            answer=zzshare_once(a.candidate_date,a.timestamp_convention)
    except Exception as err:
        answer={"status":"PUBLIC_SOURCE_REQUEST_OR_ADMISSION_FAILED_UNVERIFIED",
                "provider":"HF_PUBLIC_ARCHIVE" if a.mode=="hf-once" else "ZZSHARE",
                "candidate_date":a.candidate_date,
                "exception_class":type(err).__name__,
                "http_status":getattr(err,"code",None) if type(getattr(err,"code",None)) is int else None,
                "error_detail_redacted":True,
                "source_2007_unavailable_proven":False,
                "F01":"OPEN","E1_E4":"NOT_RUN"}
        print(json.dumps(answer,ensure_ascii=False,indent=2))
        return 3
    print(json.dumps(answer,ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
