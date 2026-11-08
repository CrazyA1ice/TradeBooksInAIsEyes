#!/usr/bin/env python3
"""Purely synthetic as-of audits for lessons 106–108, NOT a Chanlun parser or trading system."""
from __future__ import annotations
from math import isfinite

MA_WINDOWS = (5, 13, 21, 34, 55, 89, 144, 233)

def _finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and isfinite(x)

def ma_rebound_class(crossed, *, observed_clock, asof_clock, complete=True):
    """Operationalisation: longest consecutive prefix of MAs *ever* conquered in this rebound.
    'Conquered' must be computed externally using a prespecified price/MA cross rule,
    fixed rebound start, completed bars and as-of history. This does not infer crossings.
    """
    if observed_clock > asof_clock or not complete:
        return {"state": "PENDING", "class": None, "reason": "not_asof_complete"}
    for rank, window in enumerate(MA_WINDOWS, start=1):
        v = crossed.get(window, None)
        if v is None:
            return {"state": "UNKNOWN", "class": None, "reason": "unobserved_ma_"+str(window)}
        if type(v) is not bool:
            raise ValueError("Each MA crossing must be explicitly True, False or None")
        if not v:
            return {"state": "CLASSIFIED", "class": rank, "reason": "first_unconquered_ma_"+str(window)}
    return {"state": "CLASSIFIED", "class": 9, "reason": "all_eight_conquered"}

def sector_strength(rows, *, expected_members, asof_clock):
    """Fixed point-in-time member set, no missing/imputed classes, equally weighted mean."""
    if not expected_members or len(expected_members) != len(set(expected_members)):
        raise ValueError("Nonempty unique point-in-time constituent snapshot required")
    by_symbol = {}
    for row in rows:
        s = row["symbol"]
        if s in by_symbol:
            raise ValueError("Duplicate symbol")
        by_symbol[s] = row
    if set(by_symbol) != set(expected_members):
        return {"state": "UNKNOWN", "mean_class": None, "reason": "member_coverage_incomplete"}
    for row in by_symbol.values():
        if row["observed_clock"] > asof_clock or not row.get("complete", False):
            return {"state": "PENDING", "mean_class": None, "reason": "future_or_partial_member"}
        if row["observed_clock"] < asof_clock:
            return {"state": "UNKNOWN", "mean_class": None, "reason": "stale_member_clock"}
        if row["state"] != "CLASSIFIED" or type(row["class"]) is not int or not 1 <= row["class"] <= 9:
            return {"state": "UNKNOWN", "mean_class": None, "reason": "member_class_unknown"}
    return {"state": "CLASSIFIED", "mean_class": sum(x["class"] for x in by_symbol.values()) / len(by_symbol), "members": len(by_symbol)}

def lower_level_rebound(legs, *, asof_clock):
    """Check the necessary up/down/up overlap for a 30min-center *candidate* from completed 5min legs."""
    if len(legs) > 3:
        raise ValueError("This bounded audit accepts first three component legs only")
    directions = ("up", "down", "up")
    for i, leg in enumerate(legs):
        if leg["direction"] != directions[i]:
            return {"state": "INVALID_SEQUENCE", "center_candidate": False}
        if not leg.get("complete", False) or leg["end_clock"] > asof_clock:
            return {"state": "PENDING", "center_candidate": False, "completed_legs": i}
        if i and leg["end_clock"] <= legs[i-1]["end_clock"]:
            return {"state": "INVALID_SEQUENCE", "center_candidate": False}
        if not _finite(leg["low"]) or not _finite(leg["high"]) or leg["low"] > leg["high"]:
            raise ValueError("Invalid price interval")
    if len(legs) < 3:
        return {"state": "PENDING", "center_candidate": False, "completed_legs": len(legs)}
    lo = max(x["low"] for x in legs)
    hi = min(x["high"] for x in legs)
    return {"state": "CANDIDATE" if lo <= hi else "NO_THREE_LEG_OVERLAP",
            "center_candidate": lo <= hi, "overlap": [lo, hi] if lo <= hi else None,
            "third_high_exceeds_first_high": legs[2]["high"] > legs[0]["high"],
            "trade_signal": False}

def tplus_one_sellable(*, shares, acquired_day, sell_day):
    """Simplified A-share rule: no same-day resale of newly acquired shares."""
    if type(shares) is not int or shares < 0:
        raise ValueError("Nonnegative integral position required")
    return shares if sell_day > acquired_day else 0

def fractal_bottom(*, lower, upper, price, price_clock, asof_clock, upper_break_confirmed=False, confirmation_clock=None):
    """A level-specific fractal bottom; crossing upper alone is not confirmed holding."""
    if not all(_finite(x) for x in (lower, upper, price)) or not lower < upper:
        raise ValueError("Invalid bottom observation interval")
    if type(upper_break_confirmed) is not bool:
        raise ValueError("Confirmation must be explicit")
    if price_clock > asof_clock:
        return {"state": "PENDING", "reason": "future_price"}
    if price < lower:
        return {"state": "FAILED", "reason": "lower_edge_broken"}
    if price > upper and upper_break_confirmed:
        if confirmation_clock is None:
            return {"state": "UNKNOWN", "reason": "confirmation_has_no_timestamp"}
        if confirmation_clock > asof_clock:
            return {"state": "PENDING", "reason": "future_confirmation"}
        return {"state": "BREAKOUT_CONFIRMED", "reason": "independent_upper_confirmation"}
    return {"state": "FORMING", "reason": "upper_confirmation_not_complete"}

def structural_bottom(events, *, asof_clock):
    """Event-sourced separate bottom: first buy -> center -> independently completed third buy/sell."""
    state = "UNOBSERVED"
    last_clock = None
    for e in events:
        clock = e["clock"]
        if last_clock is not None and clock <= last_clock:
            return {"state": "INVALID_SEQUENCE"}
        last_clock = clock
        if clock > asof_clock or not e.get("complete", False):
            return {"state": "PENDING"}
        kind = e["kind"]
        if (state, kind) == ("UNOBSERVED", "FIRST_BUY"):
            state = "FIRST_BUY"
        elif (state, kind) == ("FIRST_BUY", "CENTER"):
            state = "CENTER_FORMING"
        elif (state, kind) == ("CENTER_FORMING", "THIRD_BUY"):
            return {"state": "BOTTOM_COMPLETED", "trade_signal": False}
        elif (state, kind) == ("CENTER_FORMING", "THIRD_SELL"):
            return {"state": "BOTTOM_FAILED", "trade_signal": False}
        else:
            return {"state": "INVALID_SEQUENCE"}
    return {"state": state, "trade_signal": False}

if __name__ == "__main__":
    assert ma_rebound_class({w: True for w in MA_WINDOWS}, observed_clock=3, asof_clock=3)["class"] == 9
    assert lower_level_rebound([], asof_clock=3)["state"] == "PENDING"
    assert fractal_bottom(lower=2284, upper=2952, price=2800, price_clock=3, asof_clock=3)["state"] == "FORMING"
    print("PASS lessons106–108 bounded synthetic online gates; no real-market data")
