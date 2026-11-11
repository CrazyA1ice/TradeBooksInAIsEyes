"""F01 finite-prefix first eligible third-point audit on synthetic declared-complete legs.

No ingestion or certification of real prices, trends, bars or author source bytes.
Not a full Chanlun parser; this checks only one old center and upward third-buy pairs.
"""
from __future__ import annotations
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "catalog/chanlun_first_eligible_retrace_author_replies_v442.json"
REPORT = ROOT / "deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_FIRST_ELIGIBLE_THIRD_RETRACE_ASOF_V442.md"

def require(ok, why):
    if not ok:
        raise ValueError("F01_FIRST_RETRACE_REJECTED: " + why)

def price(v):
    require(isinstance(v, str), "explicit decimal string")
    try:
        x = Decimal(v)
    except InvalidOperation:
        raise ValueError("F01_FIRST_RETRACE_REJECTED: malformed decimal") from None
    require(x.is_finite(), "finite decimal")
    return x

def integer(n):
    require(type(n) is int and n >= 0, "valid nonnegative ordinal")
    return n

def inspect_prefix(center, events, asof):
    """Unverified event history, not verification of independent completed movements."""
    asof = integer(asof)
    require(center["source_role"] == "UNVERIFIED_SYNTHETIC_CENTER"
            and center["independently_authenticated"] is False,
            "center never authenticates itself")
    lo, hi = price(center["zd"]), price(center["zg"])
    require(lo <= hi, "center bounds")
    pol = center["policy_id"]
    require(isinstance(pol, str) and len(pol) >= 8, "fixed policy identity")
    child = center["child_level"]
    require(isinstance(events, list), "event sequence")
    seen = set()
    last_endpoint = -1
    last_seen = -1
    for x in events:
        require(isinstance(x, dict) and
                x.get("source_role") == "UNVERIFIED_DECLARED_COMPLETED_LOWER_MOVEMENT",
                "cannot accept purported authenticated market type")
        require(isinstance(x.get("id"), str) and x["id"] not in seen,
                "unique event ids")
        seen.add(x["id"])
        require(x.get("leg") in ("DEPARTURE_UP", "RETRACE_DOWN"), "upward-case paired leg")
        require(x.get("child_level") == child and x.get("policy_id") == pol,
                "one unchanging type level and parsing policy")
        a, b = price(x.get("low")), price(x.get("high"))
        require(a <= b, "leg price range")
        end, known = integer(x.get("market_endpoint")), integer(x.get("first_known"))
        require(end > last_endpoint and known > last_seen and known >= end,
                "monotonic endpoints and first-observed proof clock")
        require(type(x.get("declared_finished")) is bool,
                "completion is only externally declared")
        last_endpoint, last_seen = end, known
    pending = None
    first_third_at = None
    uncertain_touch = False
    state = "CENTER_ACTIVE_NO_COMPLETED_EXIT"
    milestones = []
    for x in events:
        if x["first_known"] > asof:
            break
        if not x["declared_finished"]:
            return {"state":"PENDING_DECLARED_CHILD_COMPLETION",
                    "first_third_known_at": first_third_at,
                    "market_authenticated":False,"milestones":milestones}
        if x["leg"] == "DEPARTURE_UP":
            require(pending is None, "unmodeled extra departure before eligible retrace")
            require(price(x["high"]) > hi, "not an outward departure under this narrow model")
            pending = x
            state = "AWAITING_RETRACE_COMPLETION"
            continue
        require(pending is not None, "unmodeled retrace without departure")
        low = price(x["low"])
        if first_third_at is not None:
            if low > hi:
                state = "LATER_OUTSIDE_RETRACE_NOT_THIRD"
            else:
                state = "AFTER_THIRD_OLD_CENTER_EVENT_UNMODELLED"
        elif uncertain_touch:
            state = "BLOCKED_FIRSTNESS_AFTER_TOUCH"
        elif low < hi:
            state = "RETURNED_INSIDE_CENTER_OSCILLATION"
        elif low == hi:
            state = "BOUNDARY_TOUCH_SEMANTIC_FORK"
            uncertain_touch = True
        else:
            state = "NEW_THIRD_BUY_CONDITIONAL"
            first_third_at = x["first_known"]
        milestones.append({"departure_id":pending["id"],"retrace_id":x["id"],
                           "historical_retrace_endpoint":x["market_endpoint"],
                           "first_known_at":x["first_known"],
                           "state":state})
        pending = None
    return {"state":state,"first_third_known_at":first_third_at,
            "market_authenticated":False,"milestones":milestones}

def audit_spec(spec, report, root=ROOT):
    require(spec["id"] == "CHANLUN-FIRST-ELIGIBLE-RETRACE-PREFIX-F01-V442"
            and spec["version"] == "4.42.0", "contract identity")
    flags = spec["scope_flags"]
    require(flags["primary_lesson38_main_post_visible"] is True
            and all(value is False for k, value in flags.items()
                    if k != "primary_lesson38_main_post_visible"),
            "archive or market source falsely upgraded")
    sources = spec["sources"]
    require(len(sources) == 5 and
            [x["date"] for x in sources] ==
            ["2007-03-21 15:23:21","2007-03-21 15:44:04",
             "2007-03-21 16:19:02","2007-03-21 16:29:42",
             "2007-08-21 16:20:01"],
            "timestamped source sequence")
    require(sources[0]["role"] == "DIRECT_AUTHOR_SINA_MAIN_POST" and
            sources[0]["url"] == "https://blog.sina.com.cn/s/blog_486e105c010009be.html"
            and all(x["role"]=="ARCHIVED_AUTHOR_ATTRIBUTED_COMMENT_NOT_ORIGINAL_SINA_BYTES"
                    for x in sources[1:]), "do not promote replies to original posts")
    anchors = spec["course_anchors"]
    require(len(anchors) == 11 and
            len({(x["lesson"],x["id"]) for x in anchors}) == 11,
            "distinct existing original course source cards")
    for a in anchors:
        p = root / ("knowledge/evidence/chanlun_lesson%03d.json" % a["lesson"])
        card = json.loads(p.read_text(encoding="utf-8"))
        c = [x for x in card["claims"]
             if x["kind"]=="SOURCE" and x["id"]==a["id"]]
        require(len(c) == 1 and set(a["pages"]).issubset(c[0]["pdf_pages"]),
                "SOURCE page claim mismatch " + a["id"])
    op = spec["operator_scope"]
    require(op["domain"] == "ONE_SYNTHETIC_CENTER_UPWARD_THIRD_BUY_ONLY"
            and op["source_class"] == "UNVERIFIED_ABSTRACT_DECLARED_COMPLETED_LOWER_TYPES"
            and op["lower_retrace_low_must_not_break_ZG"] == "low >= zg"
            and op["inside_center_return_condition"] == "low < zg"
            and op["touch_status"] == "BOUNDARY_TOUCH_SEMANTIC_FORK"
            and op["no_repeat_for_same_center"] is True
            and op["first_time_no_backdating"] is True
            and op["external_declared_completion_not_authenticated"] is True
            and op["no_complete_finished_child_generator"] is True,
            "not a firstness and proof policy guarantee")
    cases = spec["synthetic_scenarios"]
    require(len(cases) == 9 and len({x["id"] for x in cases})==len(cases),
            "must retain all nine comparison prefixes")
    for c in cases:
        output = inspect_prefix(spec["sample_center"], c["events"], c["asof"])
        require(output["state"] == c["expected"] and output["market_authenticated"] is False,
                "prefix expected outcome " + c["id"])
        if output["first_third_known_at"] is not None:
            require(output["first_third_known_at"]<=c["asof"],
                    "no early future third point")
    by = {x["id"]:x for x in cases}
    early = inspect_prefix(spec["sample_center"],by["PREMATURE_AT_HISTORICAL_EXTREMUM"]["events"],10)
    at12 = inspect_prefix(spec["sample_center"],by["FAIL_THEN_FIRST_THIRD"]["events"],12)
    require(early["first_third_known_at"] is None
            and at12["first_third_known_at"] == 12,
            "independent completion first known at t12")
    require(spec["proof_frontier"] == {
        "F01":"OPEN","OB38":"OPEN","OB99":"OPEN",
        "base_pan_finish":"OPEN","market":"NOT_RUN"},
        "proof remains open")
    require(spec["status"]=="FIRST_ELIGIBLE_RETRACE_EVENT_HISTORY_CONDITIONAL_ONLY_NO_AUTHOR_CERTIFIED_MARKET_THIRD",
            "never market-authenticated third")
    for token in ("2007-03-21 16:14:10","2007-03-21 16:23:48","16:19:02","16:29:42",
                  "low==ZG","t12","第20课","第一次","F01","NOT_RUN"):
        require(token in report,"missing reader explanation "+token)
    return {"status":"CONDITIONAL_FIRST_ELIGIBLE_RETRACE_HISTORY_GUARDED",
            "original_lesson_anchors":11,"dated_author_attributed_entries":len(sources),
            "synthetic_scenarios":len(cases),
            "asof_third_first_known":12,"proof_frontier":"F01/OB38/OB99 OPEN"}
if __name__=="__main__":
    print(json.dumps(audit_spec(json.loads(SPEC.read_text(encoding="utf-8")),
                                REPORT.read_text(encoding="utf-8")),ensure_ascii=False))
