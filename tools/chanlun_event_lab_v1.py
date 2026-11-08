#!/usr/bin/env python3
"""Synthetic / read-only prefix replay: containment -> three-bar fractals -> pen NECESSARY gates.

Not a full Chanlun pen/segment/center parser, historical trade simulator, signal
generator or proof that a displayed book date was publicly knowable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
PEN_FAMILY = {"pen_062_original": "old", "pen_077_exposition": "old",
              "pen_081_later_dated_post": "revised"}
RESEARCH_ONLY = "synthetic_or_experimental_necessary_conditions_not_a_full_parser_or_trade_signal"
CHINA_OFFSET = timezone(timedelta(hours=8))  # Only a conservative convention for date comparison.

def dt(value):
    if isinstance(value, datetime):
        result = value
    else:
        if not isinstance(value, str):
            raise ValueError("ISO-8601 timestamp string required")
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("Naive timestamps prohibited: explicit UTC offset required")
    return result.astimezone(timezone.utc)

def dec(value):
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError("Prices must be exact decimal strings, never float/bool")
    if not isinstance(value, (str, Decimal, int)):
        raise ValueError("Exact decimal string required")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Invalid decimal value") from exc
    if not result.is_finite():
        raise ValueError("NaN/infinite prices prohibited")
    return result

@dataclass(frozen=True)
class ClosedBar:
    key: str
    symbol: str
    timeframe: str
    seq: int
    start: datetime
    end: datetime
    known: datetime
    o: Decimal
    h: Decimal
    l: Decimal
    c: Decimal
    volume: Decimal
    is_closed: bool
    source_revision_sha256: str

    @classmethod
    def parse(cls, raw):
        required = ("key", "symbol", "timeframe", "seq", "start_at", "end_at", "known_at",
                    "open", "high", "low", "close", "volume", "is_closed", "source_revision_sha256")
        if any(k not in raw for k in required):
            raise ValueError("Bar missing required provenance or OHLC fields")
        if type(raw["seq"]) is not int or raw["seq"] < 0 or type(raw["is_closed"]) is not bool:
            raise ValueError("Sequence and closed flag must be explicitly typed")
        start, end, known = (dt(raw[x]) for x in ("start_at", "end_at", "known_at"))
        o,h,l,c,v = (dec(raw[x]) for x in ("open","high","low","close","volume"))
        if not (start < end and start <= known):
            raise ValueError("Invalid bar times")
        if raw["is_closed"] and known < end:
            raise ValueError("Closed bar cannot be knowable before end")
        if l > min(o,c) or h < max(o,c) or l > h or l <= 0 or v < 0:
            raise ValueError("Invalid OHLCV bounds")
        if not all(isinstance(raw[x], str) and raw[x].strip() for x in ("key","symbol","timeframe")):
            raise ValueError("Missing market key")
        source_sha = raw["source_revision_sha256"]
        if not isinstance(source_sha, str) or SHA_RE.fullmatch(source_sha) is None:
            raise ValueError("Source revision SHA256 required")
        return cls(raw["key"],raw["symbol"],raw["timeframe"],raw["seq"],start,end,known,o,h,l,c,v,
                   raw["is_closed"],source_sha)

@dataclass(frozen=True)
class Merged:
    low: Decimal
    high: Decimal
    keys: tuple[str, ...]
    seqs: tuple[int, ...]
    known_at: datetime

    @classmethod
    def from_bar(cls, b):
        return cls(b.l,b.h,(b.key,),(b.seq,),b.known)

@dataclass(frozen=True)
class Fractal:
    kind: str
    center: int
    extreme: Decimal
    available_at: datetime

def included(a,b):
    return (a.low <= b.low and a.high >= b.high) or (b.low <= a.low and b.high >= a.high)

def normalize(bars, direction):
    """Only fixed-direction adjacent containment. No inference of directional regime."""
    if direction not in ("UP","DOWN"):
        raise ValueError("Predeclared fixed UP or DOWN direction required")
    merged = []
    for b in bars:
        next_bar = Merged.from_bar(b)
        if merged and included(merged[-1], next_bar):
            prev = merged.pop()
            merged.append(Merged(
                max(prev.low,next_bar.low) if direction=="UP" else min(prev.low,next_bar.low),
                max(prev.high,next_bar.high) if direction=="UP" else min(prev.high,next_bar.high),
                prev.keys+next_bar.keys,prev.seqs+next_bar.seqs,
                max(prev.known_at,next_bar.known_at)))
        else:
            merged.append(next_bar)
    return tuple(merged)

def fractals(merged):
    """Three closed normalized bars; returned labels are prefix-local, may revise."""
    out=[]
    for i in range(1,len(merged)-1):
        a,m,c=merged[i-1:i+2]
        if m.high>a.high and m.high>c.high and m.low>a.low and m.low>c.low:
            out.append(Fractal("TOP",i,m.high,c.known_at))
        elif m.high<a.high and m.high<c.high and m.low<a.low and m.low<c.low:
            out.append(Fractal("BOTTOM",i,m.low,c.known_at))
    return tuple(out)

def pair_gates(fracs, merged, mode):
    """Conservative NECESSARY pen conditions, never complete unique pen extraction."""
    if mode not in ("old","revised"):
        raise ValueError("Explicit pen necessary-rule mode required")
    out=[]
    for left,right in zip(fracs,fracs[1:]):
        if left.kind==right.kind:
            outcome="TIE_PENDING" if left.extreme==right.extreme else "SAME_KIND_UNRESOLVED"
        else:
            lidx,ridx=left.center,right.center
            lkeys={key for x in merged[lidx-1:lidx+2] for key in x.keys}
            rkeys={key for x in merged[ridx-1:ridx+2] for key in x.keys}
            if lkeys & rkeys:
                outcome="REJECT_SHARED_KLINE"
            elif (left.extreme if left.kind=="TOP" else right.extreme) <= (
                  right.extreme if right.kind=="BOTTOM" else left.extreme):
                outcome="REJECT_PRICE_ORDER"
            elif mode=="old":
                outcome="LOCAL_ELIGIBLE_NECESSARY_ONLY" if ridx-lidx>=4 else "REJECT_NO_INDEPENDENT_MERGED_BAR"
            elif len(merged[lidx].seqs)!=1 or len(merged[ridx].seqs)!=1:
                outcome="UNKNOWN_RAW_EXTREMUM_PROVENANCE"
            else:
                a,b=merged[lidx].seqs[0],merged[ridx].seqs[0]
                outcome="LOCAL_ELIGIBLE_NECESSARY_ONLY" if b-a-1>=3 else "REJECT_INSUFFICIENT_RAW_MIDDLE"
        out.append({"left":left.center,"right":right.center,
                    "left_kind":left.kind,"right_kind":right.kind,"status":outcome,
                    "trade_signal":False})
    return out

def rule_gate(registry, pin, asof):
    if pin is None:
        return {"state":"NO_RULE_PIN","mode":None,"version_id":None}
    allowed={"version_id","attested_known_at","proof_ref","proof_kind"}
    if set(pin)!=allowed or pin["proof_kind"] not in ("synthetic_fixture","external_documented") or (
         not isinstance(pin["proof_ref"],str) or not pin["proof_ref"].strip()):
        raise ValueError("Rule pin requires explicit evidence and source-attested availability")
    ident=pin["version_id"]
    rows=[v for v in registry["entries"] if v["id"]==ident]
    if len(rows)!=1 or rows[0]["family"]!="pen":
        raise ValueError("Rule version not in immutable pen registry")
    row=rows[0]
    if ident not in PEN_FAMILY or row["source_displayed_at"] is None or row["role"] not in (
        "author_original","author_separately_dated"):
        return {"state":"BLOCKED_UNKNOWN_OR_EDITORIAL_PROVENANCE","mode":None,"version_id":ident}
    attested=dt(pin["attested_known_at"])
    # A displayed text timestamp is *only* a lower-bound sanity check. Separate
    # proof_ref is needed; neither this comparison nor external_documented proves it.
    displayed=datetime.fromisoformat(row["source_displayed_at"]).replace(tzinfo=CHINA_OFFSET)
    if attested < displayed.astimezone(timezone.utc):
        raise ValueError("Rule attestation predates displayed source timestamp")
    if attested > asof:
        return {"state":"PENDING_ATTESTED_AVAILABILITY","mode":None,"version_id":ident}
    return {"state":"RESEARCH_RULE_PINNED","mode":PEN_FAMILY[ident],"version_id":ident,
            "attested_known_at":attested.isoformat(),"proof_kind":pin["proof_kind"],
            "trade_ready":False}

def replay(raw_bars, *, market_asof, direction, rule_pin=None, registry=None):
    asof=dt(market_asof)
    if not isinstance(raw_bars,list) or not raw_bars:
        raise ValueError("Nonempty chronological market bar list required")
    if direction not in ("UP","DOWN"):
        raise ValueError("Direction must be frozen before replay")
    bars=[ClosedBar.parse(raw) for raw in raw_bars]
    seen=set()
    for i,b in enumerate(bars):
        if b.key in seen:
            raise ValueError("Duplicate source bar key")
        seen.add(b.key)
        if i:
            prev=bars[i-1]
            if (b.symbol,b.timeframe,b.source_revision_sha256)!=(prev.symbol,prev.timeframe,prev.source_revision_sha256):
                raise ValueError("Mixed symbol/timeframe/revision in one replay")
            if b.seq != prev.seq+1 or b.start < prev.end or b.known < prev.known:
                raise ValueError("Gap, overlap or non-monotone availability; fail closed")
    visible=[]
    for bar in bars:
        if not bar.is_closed or bar.end > asof or bar.known > asof:
            break  # Never bridge an unfinished/unavailable internal bar.
        visible.append(bar)
    merged=normalize(visible,direction)
    fracs=fractals(merged)
    reg=registry if registry is not None else json.loads((ROOT/"catalog/chanlun_rule_history_v1.json").read_text("utf8"))
    pinned=rule_gate(reg,rule_pin,asof)
    pens=pair_gates(fracs,merged,pinned["mode"]) if pinned["mode"] else []
    visible_digest=hashlib.sha256(json.dumps(
        [{"key":b.key,"open":str(b.o),"high":str(b.h),"low":str(b.l),
          "close":str(b.c),"volume":str(b.volume),"end":b.end.isoformat(),
          "known":b.known.isoformat()} for b in visible],sort_keys=True).encode()).hexdigest()
    return {"market_asof":asof.isoformat(),"symbol":bars[0].symbol,"timeframe":bars[0].timeframe,
            "source_revision_sha256":bars[0].source_revision_sha256,
            "visible_prefix_digest_sha256":visible_digest, "visible_closed_bars":len(visible),
            "direction_experiment":direction, "rule":pinned,
            "normalized_bars":[{"low":str(m.low),"high":str(m.high),"raw_keys":list(m.keys),
                                "known_at":m.known_at.isoformat()} for m in merged],
            "fractal_candidates":[{"kind":f.kind,"center_normalized_index":f.center,
                                   "extreme":str(f.extreme),"available_at":f.available_at.isoformat(),
                                   "status":"PREFIX_LOCAL_REVISABLE_NOT_STABLE_CONFIRMED_PEN"} for f in fracs],
            "pen_necessary_gates":pens,"complete_pen_parser":False,"complete_segment_parser":False,
            "complete_center_parser":False,"orders_sent":False,"real_market_data_used":False,
            "scope":RESEARCH_ONLY}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture",default="experiments/fixtures/chanlun_prefix_synthetic_v1.json")
    parser.add_argument("--asof",required=True,help="Offset-aware ISO timestamp")
    parser.add_argument("--direction",choices=("UP","DOWN"),required=True)
    parser.add_argument("--rule",choices=tuple(PEN_FAMILY))
    parser.add_argument("--attested-known-at",help="Explicit independent availability timestamp; required with --rule")
    parser.add_argument("--proof-ref",help="Source attestation reference; required with --rule")
    args=parser.parse_args()
    fixture=json.loads((ROOT/args.fixture).read_text("utf8"))
    if fixture.get("kind")!="synthetic_non_market_fixture":
        raise ValueError("Only explicitly synthetic fixtures supported in this phase")
    if bool(args.rule)!=(args.attested_known_at is not None and args.proof_ref is not None):
        raise ValueError("Provide --rule, --attested-known-at and --proof-ref together")
    pin=({"version_id":args.rule,"attested_known_at":args.attested_known_at,
          "proof_ref":args.proof_ref,"proof_kind":"synthetic_fixture"} if args.rule else None)
    print(json.dumps(replay(fixture["bars"],market_asof=args.asof,direction=args.direction,
                            rule_pin=pin),ensure_ascii=False,sort_keys=True,indent=2))
if __name__=="__main__":main()
