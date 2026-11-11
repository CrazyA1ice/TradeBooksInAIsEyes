"""Source-pinned *non-equivalence* of two lowest-center initialization predicates.

L17: common price interval among at least 3 consecutive completed unit bars.
L35: 3 consecutive trade prints at exactly the same price.
Both are author-text local construction rules, NOT pan-completion certificates.
All audited traces are explicitly invented for logic, never market replay.
"""
from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "catalog/chanlun_f1_unitbar_trade_non_equivalence_v1.json"
REPORT = ROOT / "deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_F1_INITIALIZERS_NON_EQUIVALENCE_AND_BASE_PAN_CLOCK.md"
PREVIOUS = ROOT / "catalog/chanlun_f01_l20_center_partial_order_and_base_pan_v1.json"


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError("F1_INITIALIZER_AUDIT_REJECTED: " + why)


def decimal(x: object) -> Decimal:
    require(isinstance(x, str), "no floats or implicit unit of prices")
    try:
        v = Decimal(x)
    except InvalidOperation:
        raise ValueError("F1_INITIALIZER_AUDIT_REJECTED: price not a decimal string") from None
    require(v.is_finite(), "nonfinite price")
    return v


def evaluate_trace(prices: list, bar_ids: list) -> dict:
    """Return only 2 formation predicates for a fixed explicit bar partition."""
    require(isinstance(prices, list) and isinstance(bar_ids, list), "trace must be lists")
    require(len(prices) == len(bar_ids) and len(prices) >= 3, "matching trade events")
    pp = [decimal(x) for x in prices]
    require(all(type(b) is int and b >= 0 for b in bar_ids), "nonnegative integer bar IDs")
    require(bar_ids[0] == 0, "bar partition must begin with 0")
    require(all(bar_ids[i] <= bar_ids[i + 1] <= bar_ids[i] + 1
                for i in range(len(bar_ids) - 1)), "bars must be consecutive, contiguous in trade time")
    groups: list[list[Decimal]] = [[] for _ in range(bar_ids[-1] + 1)]
    for p, bar in zip(pp, bar_ids):
        groups[bar].append(p)
    require(all(groups), "every listed unit bar must have source trade events")
    p35 = any(pp[i] == pp[i + 1] == pp[i + 2] for i in range(len(pp) - 2))
    common = None
    p17 = False
    for i in range(len(groups) - 2):
        lo = max(min(g) for g in groups[i:i + 3])
        hi = min(max(g) for g in groups[i:i + 3])
        if lo <= hi:
            common = [str(lo), str(hi)]
            p17 = True
            break
    return {
        "f1_17_3_complete_bars_overlap": p17,
        "f1_35_3_consecutive_identical_trades": p35,
        "bar_overlap": common,
        "bar_count": len(groups),
        "trade_count": len(pp),
        "market_verified": False,
        "finished_lowest_pan_confirmed": False,
    }


def audit(spec: dict, earlier: dict, report: str, root: Path = ROOT) -> dict:
    require(spec["study_id"] == "CHANLUN-F1-UNITBAR-TRADE-CONSTRUCTIVE-NON-EQUIVALENCE-V434", "study identity")
    require(spec["formal_answer"] == "NO_BOTH_DIRECTIONS_REFUTED_ON_SYNTHETIC_STREAMS", "two directions required")
    require(spec["scope"] == "EXPLICIT_SYNTHETIC_TRADE_EVENT_STREAMS_AND_FIXED_BAR_PARTITIONS_NOT_REAL_MARKET", "no market provenance")
    require(earlier["id"] == "CHANLUN-F01-L20-CENTER-SEPARATION-AND-BASE-PAN-GAP-V433", "prior source study")

    cards = spec["sources"]
    require(len(cards) == 7 and len({c["id"] for c in cards}) == 7, "seven distinct author card anchors")
    by_id = {x["id"]: x for x in cards}
    need = {
        "CL017-S03": (17, "2006-12-18", "lowest"),
        "CL018-S07": (18, "2006-12-26", "extension"),
        "CL35-SO-2": (35, "2007-03-09", "trade"),
        "CL38-SOURCE-2": (38, "2007-03-21", "pan+pan"),
        "CL72-SOURCE-3": (72, "2007-08-21", "segment"),
        "CL83-SOURCE-1": (83, "2007-09-26", "pen"),
        "CL84-SOURCE-3": (84, "2007-10-07", "f1")
    }
    require(set(by_id) == set(need), "source claims and dates are fixed")
    for key, (n, date, _) in need.items():
        c = by_id[key]
        require(c["lesson"] == n and c["original_date"] == date, "author timeline "+key)
        p = root / f"knowledge/evidence/chanlun_lesson{n:03d}.json"
        require(p.is_file(), "missing source evidence " + key)
        j = json.loads(p.read_text(encoding="utf-8"))
        match = next((x for x in j["claims"] if x["id"] == key), None)
        require(match is not None and match["kind"] == "SOURCE", "no SOURCE author claim for " + key)
        require(set(c["pdf_pages"]).issubset(set(match["pdf_pages"])), "PDF physical pages wrong "+key)

    types = spec["types"]
    require("three consecutive" in types["f1_17"] and "price interval" in types["f1_17"], "L17 three bars")
    require("three CONSECUTIVE" in types["f1_35"] and "identical" in types["f1_35"], "L35 equal prints")
    require("completed" in types["f2"], "upper recurrence requires completed movements")
    rules = spec["comparison_contract"]
    require(all(v is True for v in rules.values()), "source preservation and not-overclaim requirements")

    w = {x["id"]: x for x in spec["witnesses"]}
    require(set(w) == {"W17_YES_35_NO", "W35_YES_17_NO", "W_DEGENERATE_17_ONLY"}, "two directions plus degenerate case")
    for wid, item in w.items():
        require(item["author_quote_synthetic"] is False and item["market_actual"] is False, "no fictional market provenance")
        got = evaluate_trace(item["prices"], item["bar_ids"])
        require(got["f1_17_3_complete_bars_overlap"] is item["f1_17"], "L17 value " + wid)
        require(got["f1_35_3_consecutive_identical_trades"] is item["f1_35"], "L35 value " + wid)
        require(got["bar_overlap"] == item["bar_overlap"], "bar overlap is source-computed " + wid)
        require(got["finished_lowest_pan_confirmed"] is False, "no automatic pan completion")
    require(w["W17_YES_35_NO"]["f1_17"] and not w["W17_YES_35_NO"]["f1_35"],
            "not(L17 implies L35)")
    require(w["W35_YES_17_NO"]["f1_35"] and not w["W35_YES_17_NO"]["f1_17"],
            "not(L35 implies L17)")
    require(w["W_DEGENERATE_17_ONLY"]["bar_overlap"] == ["11", "11"], "one-price center intersection")

    axes = {x["id"]: x for x in spec["policy_axes"]}
    require(set(axes) == {"AX_F1", "AX_RG", "AX_F2"}, "do not combine initializer and parser")
    require("L17_THREE_LOWEST_BAR_OVERLAP" in axes["AX_F1"]["possibilities"], "bar init")
    require("L35_THREE_IDENTICAL_CONSECUTIVE_TRADES" in axes["AX_F1"]["possibilities"], "tick init")
    require("L38_FIXED_OPERATING_LEVEL_SAME_LEVEL_DECOMPOSITION" in axes["AX_RG"]["possibilities"], "separate fixed Rg")
    require(spec["bottom_pan_obligation"]["proof_status"] == "OPEN", "base pan remains unproven")
    require(all(v is True for k, v in spec["bottom_pan_obligation"].items() if k not in ("proof_status","base_complete_pan_certificate_found_in_sources")),
            "no unauthorized pan completion")
    require(spec["bottom_pan_obligation"]["base_complete_pan_certificate_found_in_sources"] is False,
            "no independent primitive pan termination certificate")
    status = spec["frontier_status"]
    require(all(status[x] == "OPEN" for x in ("f01","ob38","ob99","base_pan")), "unresolved author proof")
    require(status["market"] == "NOT_RUN", "no market run")
    require(status["f1_equivalence"] == "REFUTED_FOR_THESE_TWO_PREDICATES", "local quantifier scope")
    require(all(v is False for v in spec["limits"].values()), "all source/market/proof limits must stay honest")
    for needle in ("第17课","第35课","第38课","第84课","逐笔","相同","重叠","OPEN","NOT_RUN"):
        require(needle in report, "report lacks critical qualification "+needle)
    return {
        "audit": "PASS_CONSTRUCTIVE_LOCAL_NON_EQUIVALENCE_ONLY",
        "witnesses_checked": len(w),
        "two_implications": "BOTH_REFUTED_AS_PREDICATES",
        "pan_completion": "OPEN",
        "market_replay": "NOT_RUN",
        "parser_uniqueness": "NOT_DISPROVEN",
    }


def main() -> None:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    old = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    print(json.dumps(audit(spec, old, report), ensure_ascii=False))


if __name__ == "__main__":
    main()
