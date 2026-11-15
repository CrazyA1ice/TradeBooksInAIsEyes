#!/usr/bin/env python3
"""M74: reproduce the L54 600151.SH 2007-05-18 minute chart, without claiming g/d completion.

Default preflight is offline. Opt-in network reads exactly one pinned public
annual CSV into memory; optional SVG stays inside the project's ignored work/ directory.
The SVG shows 1m candles, close MA5/10, volume MA5/10, and a session-seeded
MACD *illustration*, not historical software MACD equivalence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from decimal import Decimal
from pathlib import Path
from urllib import parse, request
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools import probe_chanlun_l54_public_archive_m73 as m73
from tools import probe_chanlun_l54_external_minute_m72 as m72

DATASET = "OpenFinMind/stock_dataset"
DAY = "2007-05-18"
STOCK = "600151.SH"
FILE = "A股分钟/2000-2024/2007/1分钟/sh600151.csv"
FILE_BYTES = 2897499
FILE_SHA256 = "84ae998ee80cbd13adc80759c1de6e465d57f6fe8d3e48015a02e0dd29ddc439"
BASE = "https://huggingface.co"
FILE_URL = BASE + "/datasets/" + DATASET + "/resolve/main/" + parse.quote(FILE, safe="/")
REFERENCE = {
    "day_high": "18.59", "day_low": "17.61",
    "day_high_times": ["13:07"], "last_time": "15:00",
    "last_close": "18.03", "last_low": "18.03",
    "last_volume": "1917", "volume_ma5": "1565.2",
    "volume_ma10": "1498.4", "close_ma5": "18.05",
    "close_ma10": "18.052", "afternoon_1321_high": "18.45",
    "afternoon_1321_low": "18.03",
}
MARKERS = [("g", i) for i in range(1, 8)] + [("d", i) for i in range(1, 8)]


def need(ok, why):
    if not ok:
        raise ValueError("M74_REJECTED: " + why)


def trusted_hf_download_url(url):
    """Allow official Hugging Face HTTPS CDN hosts, not unrelated redirects.

    Hugging Face's published download allowlist uses the hf.co and
    huggingface.co suffixes, including nested CDN and EU Xet hosts.
    Byte length and the pinned LFS SHA256 remain mandatory *after* download.
    """
    parsed = parse.urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    try:
        port = parsed.port
    except ValueError:
        return False
    allowed_host = (host in ("hf.co", "huggingface.co") or
                    host.endswith(".hf.co") or host.endswith(".huggingface.co"))
    return (parsed.scheme == "https" and port in (None, 443) and
            parsed.username is None and parsed.password is None and allowed_host)


def fetch_pinned(opener=None):
    """Only the verified 2007 single-stock annual file; no listing or token."""
    opener = opener or request.urlopen
    req = request.Request(FILE_URL, headers={"User-Agent": "Mozilla/5.0"})
    with opener(req, timeout=60) as resp:
        final_url = resp.geturl()
        final = parse.urlparse(final_url)
        need(trusted_hf_download_url(final_url),
             "unexpected source redirect host=" + (final.hostname or "unknown")[:120])
        need(getattr(resp, "status", 200) == 200, "source HTTP status")
        data = resp.read(FILE_BYTES + 1)
    return data


def exact_source(raw):
    need(isinstance(raw, bytes), "original source must be bytes")
    need(len(raw) == FILE_BYTES, "HF object size different from pinned metadata")
    need(hashlib.sha256(raw).hexdigest() == FILE_SHA256,
         "source does not match pinned HF LFS SHA256")
    return raw


def dec(row, key):
    return Decimal(str(row[key]))


def avg(values, n):
    need(len(values) >= n, "moving average requires enough earlier bars")
    return sum(values[-n:], Decimal("0")) / Decimal(n)


def fmt(n):
    return format(n, "f")


def summarize(rows, convention="bar_end"):
    """Pure OHLCV and fingerprint analysis; caller must separately verify raw bytes."""
    need(convention == "bar_end", "source minute convention explicitly bar_end")
    need(isinstance(rows, list) and len(rows) == 240, "target day must have exactly 240 rows")
    canonical = m72.encode_rows(rows, DAY)
    admission = m72.admit(canonical, "RQDATA", DAY, convention)
    need(admission["grid"]["grid_matches_under_declared_convention"],
         "full Shanghai 240 bar_end grid required")
    times = [r["time"].strftime("%H:%M") for r in rows]
    highs = [dec(r, "high") for r in rows]
    lows = [dec(r, "low") for r in rows]
    closes = [dec(r, "close") for r in rows]
    volumes = [dec(r, "volume") for r in rows]
    after = [r for r in rows if r["time"].strftime("%H:%M") >= "13:21"]
    high = max(highs)
    low = min(lows)
    actual = {
        "day_high": fmt(high),
        "day_low": fmt(low),
        "day_high_times": [times[i] for i, value in enumerate(highs) if value == high],
        "last_time": times[-1],
        "last_close": fmt(closes[-1]),
        "last_low": fmt(lows[-1]),
        "last_volume": fmt(volumes[-1]),
        "volume_ma5": fmt(avg(volumes, 5)),
        "volume_ma10": fmt(avg(volumes, 10)),
        "close_ma5": fmt(avg(closes, 5)),
        "close_ma10": fmt(avg(closes, 10)),
        "afternoon_1321_high": fmt(max(dec(r, "high") for r in after)),
        "afternoon_1321_low": fmt(min(dec(r, "low") for r in after)),
    }
    matches = {name: actual[name] == expected for name, expected in REFERENCE.items()}
    return {
        "status": "HISTORICAL_1M_FINGERPRINT_REPLAY_NOT_AUTHOR_GD_CERTIFIED",
        "instrument": STOCK, "candidate_date": DAY,
        "public_archive": DATASET, "file_path": FILE,
        "pinned_file_sha256": FILE_SHA256,
        "original_file_bytes_verified": False,
        "timestamp_convention_declared_not_vendor_attested": convention,
        "minute_rows": len(rows), "unique_minutes": len(set(times)),
        "grid_status": admission["grid"]["grid_status"],
        "grid_matches_under_declared_convention": True,
        "fingerprint": actual, "reference_exact_match": matches,
        "all_reference_fields_match": all(matches.values()),
        "reference_role": "USER_OBSERVED_AND_SECONDARY_FIGURE_CROSSCHECK_NOT_EXCHANGE_CERTIFICATE",
        "author_markers": {f"{prefix}{i}": {
            "market_minute": None, "price": None,
            "status": "NOT_LOCATED_BY_INDEPENDENT_FIGURE_TO_BAR_MAPPING",
        } for prefix, i in MARKERS},
        "author_alpha": {"center_first_formed_at_author_marker": "g5",
                         "g7_structure": "AUTHOR_THIRD_SELL"},
        "author_beta": {"center_first_formed_at_author_marker": "g6",
                        "g7_structure": "AUTHOR_CENTER_OSCILLATION_NOT_THIRD_SELL"},
        "adjustment": "UNVERIFIED",
        "chart_year_identity": "VERY_STRONG_CONSISTENCY_NOT_INDEPENDENTLY_AUTHENTICATED",
        "tick_order": "UNKNOWN_NOT_RECOVERABLE_FROM_1MIN_OHLCV",
        "macd_initialization": "SESSION_FIRST_CLOSE_ONLY_NOT_VENDOR_CROSS_DAY_MATCH",
        "historical_first_known": "NOT_CERTIFIED",
        "F01": "OPEN", "OB38": "OPEN", "OB99": "OPEN",
        "Phi20": "OPEN", "E1_E4": "NOT_RUN", "orders_sent": 0,
    }


def from_verified_source(raw):
    exact_source(raw)
    p = m73.csv_annual_day_rows(raw, DAY)
    result = summarize(p["rows"])
    result["original_file_bytes_verified"] = True
    result["annual_csv_rows"] = p["annual_rows"]
    return p["rows"], result


def moving(values, n):
    out = []
    for idx in range(len(values)):
        out.append(float(sum(values[idx + 1 - n:idx + 1], Decimal(0)) / n)
                   if idx + 1 >= n else None)
    return out


def macd_session(closes):
    """Chart aid only: EMA seeded at the first bar, no prior-day history."""
    ema12 = ema26 = float(closes[0])
    dea = 0.0
    result = []
    for value in closes:
        x = float(value)
        ema12 = ema12 + (2.0 / 13.0) * (x - ema12)
        ema26 = ema26 + (2.0 / 27.0) * (x - ema26)
        dif = ema12 - ema26
        dea = dea + (2.0 / 10.0) * (dif - dea)
        result.append((dif, dea, 2.0 * (dif - dea)))
    return result


def svg_figure(rows, report, window="afternoon"):
    """Stand-alone SVG; only market bars; do not forge coordinates for author g/d."""
    need(window in ("afternoon", "full"), "unknown time window")
    need(report["minute_rows"] == 240, "chart requires admitted full-day data")
    chosen = [(i, r) for i, r in enumerate(rows)
              if window == "full" or r["time"].strftime("%H:%M") >= "13:01"]
    need(chosen, "empty chart window")
    width, height = 1440, 940
    x0, x1 = 95, 1390
    p_top, p_bottom = 72, 532
    v_top, v_bottom = 584, 727
    m_top, m_bottom = 773, 872
    plot_h = p_bottom - p_top
    price_low = min(float(dec(r, "low")) for _, r in chosen)
    price_high = max(float(dec(r, "high")) for _, r in chosen)
    need(price_high > price_low, "chart range must be nonzero")
    price_pad = max((price_high-price_low) * .07, .02)
    price_low -= price_pad
    price_high += price_pad
    def x_at(j):
        return x0 + (x1-x0) * (j + .5) / len(chosen)
    def price_y(v):
        return p_bottom - (float(v)-price_low) / (price_high-price_low) * plot_h
    all_close = [dec(z, "close") for z in rows]
    all_volume = [dec(z, "volume") for z in rows]
    ma5, ma10 = moving(all_close, 5), moving(all_close, 10)
    vm5, vm10 = moving(all_volume, 5), moving(all_volume, 10)
    macd = macd_session(all_close)
    v_max = max([float(dec(r, "volume")) for _, r in chosen] +
                [vm10[i] or 0 for i, _ in chosen])
    v_max = max(v_max, 1)
    macd_abs = max(abs(v) for i, _ in chosen for v in macd[i])
    macd_abs = max(macd_abs, .001)
    def vol_y(v):
        return v_bottom - v / v_max * (v_bottom-v_top)
    def macd_y(v):
        return (m_top+m_bottom)/2 - v / macd_abs * (m_bottom-m_top)*.45
    el = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 940" role="img" aria-label="600151.SH 2007-05-18 historical one-minute candidate and indicators">',
        '<rect width="1440" height="940" fill="#ffffff"/>',
        '<text x="95" y="28" font-family="sans-serif" font-size="22" font-weight="bold" fill="#162a39">600151.SH / 2007-05-18 | 1m source replay</text>',
        '<text x="95" y="48" font-family="sans-serif" font-size="12" fill="#687988">OpenFinMind pinned SHA256; bar_end declared; g/d markers NOT independently located</text>',
    ]
    for top, bottom, name in [(p_top,p_bottom,"PRICE: OHLC + close MA5/MA10"),
                               (v_top,v_bottom,"VOLUME + MA5/MA10"),
                               (m_top,m_bottom,"MACD 12/26/9 (session-seeded demonstration)")]:
        el.append(f'<rect x="{x0}" y="{top}" width="{x1-x0}" height="{bottom-top}" fill="#fafbfd" stroke="#dce4e9"/>')
        el.append(f'<text x="{x0+8}" y="{top+18}" font-size="12" font-family="sans-serif" fill="#657584">{escape(name)}</text>')
    for frac in (0,.25,.5,.75,1):
        y=p_top+frac*plot_h
        val=price_high-frac*(price_high-price_low)
        el.append(f'<line x1="{x0}" x2="{x1}" y1="{y:.2f}" y2="{y:.2f}" stroke="#e6ecf0"/>')
        el.append(f'<text x="37" y="{y+4:.2f}" font-family="monospace" font-size="12" fill="#617380">{val:.2f}</text>')
    step=(x1-x0)/len(chosen)
    candle_w=max(1.5,min(7,step*.6))
    for j,(i,row) in enumerate(chosen):
        x=x_at(j); oo=float(dec(row,"open")); hh=float(dec(row,"high"))
        ll=float(dec(row,"low")); cc=float(dec(row,"close"))
        color="#bd4a45" if cc>=oo else "#267c74"
        el.append(f'<line x1="{x:.2f}" y1="{price_y(hh):.2f}" x2="{x:.2f}" y2="{price_y(ll):.2f}" stroke="{color}" stroke-width="1.1"/>')
        top=min(price_y(oo),price_y(cc)); body=max(1.1,abs(price_y(oo)-price_y(cc)))
        el.append(f'<rect x="{x-candle_w/2:.2f}" y="{top:.2f}" width="{candle_w:.2f}" height="{body:.2f}" fill="{color}"/>')
        vol=float(dec(row,"volume"))
        el.append(f'<rect x="{x-candle_w/2:.2f}" y="{vol_y(vol):.2f}" width="{candle_w:.2f}" height="{v_bottom-vol_y(vol):.2f}" fill="{color}" opacity=".70"/>')
        hist=macd[i][2]
        mid=(m_top+m_bottom)/2
        el.append(f'<rect x="{x-candle_w/2:.2f}" y="{min(mid,macd_y(hist)):.2f}" width="{candle_w:.2f}" height="{max(1,abs(macd_y(hist)-mid)):.2f}" fill="{color}" opacity=".70"/>')
    def line_for(values, y, color):
        pairs=[(x_at(j),y(values[i])) for j,(i,_) in enumerate(chosen)
               if values[i] is not None]
        if len(pairs)>1:
            points=" ".join(f"{x:.2f},{yy:.2f}" for x,yy in pairs)
            el.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="1.7"/>')
    line_for(ma5,price_y,"#b16a18")
    line_for(ma10,price_y,"#326eb7")
    line_for(vm5,vol_y,"#b16a18")
    line_for(vm10,vol_y,"#326eb7")
    line_for([a[0] for a in macd],macd_y,"#b16a18")
    line_for([a[1] for a in macd],macd_y,"#326eb7")
    mid=(m_top+m_bottom)/2
    el.append(f'<line x1="{x0}" x2="{x1}" y1="{mid}" y2="{mid}" stroke="#afb8c3" stroke-dasharray="4,3"/>')
    for j,(i,row) in enumerate(chosen):
        tm=row["time"].strftime("%H:%M")
        if tm in ("13:07","13:21","14:00","15:00","09:31","11:30"):
            x=x_at(j)
            el.append(f'<line x1="{x:.2f}" x2="{x:.2f}" y1="{p_top}" y2="{m_bottom}" stroke="#dae2e8" stroke-dasharray="3,5"/>')
            el.append(f'<text x="{x:.2f}" y="{m_bottom+18}" text-anchor="middle" font-family="monospace" font-size="12" fill="#38566b">{tm}</text>')
        if tm in ("13:07","15:00"):
            x=x_at(j)
            h=dec(row,"high"); l=dec(row,"low")
            val=h if tm=="13:07" else l
            y=price_y(val)
            shift=-12 if tm=="13:07" else 19
            anchor="end" if tm=="15:00" else "start"
            xx=x-8 if tm=="15:00" else x+8
            el.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="#34495e"/>')
            el.append(f'<text x="{xx:.2f}" y="{y+shift:.2f}" text-anchor="{anchor}" font-family="sans-serif" font-size="14" fill="#263646">{tm} / {fmt(val)}</text>')
    el.append('<text x="95" y="923" font-family="sans-serif" font-size="12" fill="#6f7d87">Source chart identity strongly supported by price+volume fingerprint, NOT exchange-certified. Author g/d assignments, adjustment and intraminute paths unverified.</text>')
    el.append('</svg>')
    return "\n".join(el) + "\n"


def canonical_project_root():
    """Linked review trees live *under* the canonical project's ignored work/."""
    if ROOT.parent.name == "review-worktrees" and ROOT.parent.parent.name == "work":
        return ROOT.parent.parent.parent.resolve()
    return ROOT.resolve()


def private_work_root():
    return (canonical_project_root() / "work").resolve()


def safe_svg_destination(value):
    path = Path(value).expanduser().resolve()
    work = private_work_root()
    need(path.suffix.lower() == ".svg", "output must be .svg")
    need(work in path.parents, "generated files must stay inside project work/")
    need(path.parent.is_dir(), "output parent directory must already exist")
    need(not path.exists(), "refuse overwriting existing SVG")
    return path


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--mode", default="preflight", choices=("preflight", "openfinmind-once"))
    cli.add_argument("--window", default="afternoon", choices=("afternoon", "full"))
    cli.add_argument("--svg-output", default=None)
    a = cli.parse_args(argv)
    if a.mode == "preflight":
        need(a.svg_output is None, "preflight cannot generate chart")
        print(json.dumps({"status":"OFFLINE_M74_REPLAY_READY_NOT_QUERIED",
                          "provider":DATASET,"candidate_date":DAY,
                          "expected_sha256":FILE_SHA256,
                          "network_queries":0,"chart_saved":False,
                          "g_d_authenticated":False,"F01":"OPEN","E1_E4":"NOT_RUN"},
                         ensure_ascii=False))
        return 0
    destination = safe_svg_destination(a.svg_output) if a.svg_output else None
    rows, report = from_verified_source(fetch_pinned())
    if destination:
        destination.write_text(svg_figure(rows,report,a.window),encoding="utf-8",newline="\n")
        report["local_svg_written"] = str(destination)
        report["chart_window"] = a.window
    else:
        report["local_svg_written"] = None
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
