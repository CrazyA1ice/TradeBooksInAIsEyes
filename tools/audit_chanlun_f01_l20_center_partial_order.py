"""Audit local Lesson-20 paired-center inequalities, WITHOUT proving market centers.

'Core' [ZD,ZG] differs from 'Z-segment envelope' [DD,GG].
Author lesson 20 formulas are conditional on legal same-level centers.
This does NOT define lesson 35's globally complete "higher than" comparator,
certify the lowest single-center pan's end, or classify real transactions.
"""
from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "catalog/chanlun_f01_l20_center_partial_order_and_base_pan_v1.json"
OLD = ROOT / "catalog/chanlun_f01_completion_receipt_contract_v1.json"
REPORT = ROOT / "deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_F01_CENTER_ENVELOPE_ORDER_AND_BASE_PAN_DOMAIN_GAP.md"


def demand(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("L20_CENTER_PARTIAL_ORDER_FAIL: " + message)


def dval(value: object) -> Decimal:
    demand(isinstance(value, str), "all price inputs must be exact decimal strings")
    try:
        v = Decimal(value)
    except InvalidOperation:
        raise ValueError("L20_CENTER_PARTIAL_ORDER_FAIL: nondecimal input") from None
    demand(v.is_finite(), "nonfinite input")
    return v


def legal_envelope(x: dict) -> dict[str, Decimal]:
    demand(set(x) == {"DD", "ZD", "ZG", "GG"}, "must include exactly four defined extrema")
    values = {k: dval(x[k]) for k in ("DD", "ZD", "ZG", "GG")}
    demand(values["DD"] <= values["ZD"] <= values["ZG"] <= values["GG"],
           "four extrema must enclose a nonempty core zone")
    return values


def classify(earlier: dict, later: dict) -> str:
    """Only L20 local numeric theorem-II patterns; all OHLC semantics are external."""
    a, b = legal_envelope(earlier), legal_envelope(later)
    checks = [
        ("STRICT_UP_SEPARATED", b["DD"] > a["GG"]),
        ("STRICT_DOWN_SEPARATED", b["GG"] < a["DD"]),
        ("UPWARD_EXPANSION_PATTERN", b["ZD"] > a["ZG"] and b["DD"] <= a["GG"]),
        ("DOWNWARD_EXPANSION_PATTERN", b["ZG"] < a["ZD"] and b["GG"] >= a["DD"]),
    ]
    yes = [name for name, ok in checks if ok]
    demand(len(yes) <= 1, "author formula cases unexpectedly overlap")
    return yes[0] if yes else "UNDETERMINED_BY_THESE_FOUR_L20_FORMULAS"


def audit(spec: dict, old: dict, report: str, root: Path = ROOT) -> dict:
    demand(spec["id"] == "CHANLUN-F01-L20-CENTER-SEPARATION-AND-BASE-PAN-GAP-V433", "catalog identity")
    demand(spec["scope"] == "SOURCE_BOUNDED_LOCAL_ALGEBRA_AND_TYPE_GAP_NOT_FULL_TREND_PARSER", "scope")
    demand(old["id"] == "CHANLUN-F01-PROOF-CARRYING-COMPLETION-RECEIPT-V432", "prior receipt contract")
    cards = spec["source_cards"]
    demand(len(cards) == 9 and len({x["id"] for x in cards}) == 9, "source anchors")
    for card in cards:
        f = root / f"knowledge/evidence/chanlun_lesson{card['lesson']:03d}.json"
        demand(f.exists(), "evidence file missing")
        original = json.loads(f.read_text(encoding="utf-8"))
        matches = [x for x in original["claims"] if x["id"] == card["id"]]
        demand(len(matches) == 1 and matches[0]["kind"] == "SOURCE", "SOURCE claim not present")
        demand(set(card["physical_pages"]).issubset(set(matches[0]["pdf_pages"])), "PDF page mismatch")
    demand({x["id"] for x in cards}.issuperset({"CL020-S08","CL35-SO-9","CL35-SO-2","CL020-S03"}), "critical sources missing")
    assert_defs = spec["source_notation"]
    demand(assert_defs["necessary_enclosure"] == "DD <= ZD <= ZG <= GG", "core/envelope geometry")
    demand(assert_defs["cannot_authenticate_actual_legal_center_from_four_numbers"] is True,
           "four arbitrary extrema do not prove a legal center")
    demand(assert_defs["zone_touching_allowed_under_explicit_closed_interval_arithmetic"] is True,
           "closed price interval including point contact")
    formulas = spec["author_l20_conditional_formulas"]
    expected = {
        "L20-STRICT-UP": ("later.DD > earlier.GG", "STRICT_UP_SEPARATED"),
        "L20-STRICT-DOWN": ("later.GG < earlier.DD", "STRICT_DOWN_SEPARATED"),
        "L20-UP-EXPANSION": ("later.ZD > earlier.ZG AND later.DD <= earlier.GG", "UPWARD_EXPANSION_PATTERN"),
        "L20-DOWN-EXPANSION": ("later.ZG < earlier.ZD AND later.GG >= earlier.DD", "DOWNWARD_EXPANSION_PATTERN")
    }
    demand(len(formulas) == 4, "four comparison patterns")
    for f in formulas:
        demand(f["id"] in expected and (f["formula"], f["logical_output"]) == expected[f["id"]],
               "changed author inequality " + f["id"])
    examples = spec["worked_abstract_pairs"]
    demand(len(examples) == 7 and len({x["id"] for x in examples}) == 7, "seven non-market samples")
    for example in examples:
        demand(classify(example["earlier"], example["later"]) == example["expect"],
               "wrong numeric demonstration " + example["id"])
    by_id = {x["id"]: x for x in examples}
    first, second = by_id["EX-STRICT-UP"], by_id["EX-UP-EXPANSION"]
    demand(first["earlier"] == second["earlier"], "source first core identity")
    demand({k: first["later"][k] for k in ("ZD", "ZG")} == {k: second["later"][k] for k in ("ZD","ZG")},
           "same rear core has different L20 result; must keep illustrative witness")
    demand(first["later"]["DD"] != second["later"]["DD"], "outer extrema is relevant")
    demand(classify(first["earlier"], first["later"]) != classify(second["earlier"], second["later"]),
           "cannot classify from zone-core alone")
    constraints = {x["from"]: x for x in spec["interpretive_constraints"]}
    demand(constraints["L20-STRICT-UP"]["status"] == "NOT_GLOBALLY_PROVEN_EQUIVALENT",
           "strict L20 separation not globally equal to all L35 higher")
    demand(constraints["L20-THIRD-POINT"]["status"] == "TYPE_LEVEL_GAP",
           "absolute base has no smaller recursively finished level")
    demand(constraints["L35-THREE-EQUAL-TRADES"]["status"] == "NOT_AUTHORIZED",
           "one center not certified as completed pan")
    bottom = spec["bottom_case"]
    demand(bottom["absolute_minimum_trade_layer"] == 0
           and bottom["l20_third_point_uniformly_defined_at_absolute_base"] is False,
           "unresolved base case cannot disappear")
    demand(bottom["independent_single_center_pan_terminal_rule_found"] is False
           and bottom["not_author_theorem_disproof"] is True, "base pan not proved or disproved")
    old_status = old["proof_status"]
    demand(old_status["base_pan_completion"] == "OPEN" and old_status["f01"] == "OPEN",
           "prior no-proof state may not be overruled")
    status = spec["result_status"]
    demand(all(status[k] == "OPEN" for k in
               ("l35_higher_not_higher_global_comparator", "l35_lowest_single_center_pan_terminal",
                "l18_finished_child_membership", "F01", "OB38", "OB99")),
           "cannot close open proof obligations from local numeric comparisons")
    demand(status["historical_market_data"] == "NOT_ACCESSED"
           and status["market_backtest"] == "NOT_RUN", "no empirical validation")
    for token in ("第20课", "第35课", "GG", "DD", "ZD", "ZG", "最低", "OPEN", "NOT_RUN", "严格"):
        demand(token in report, "reader research report missing " + token)
    return {"audit":"PASS_LOCAL_FORMULAS_ONLY", "worked_abstract_pairs":len(examples),
            "L20_cases":len(formulas), "global_l35_comparator":"OPEN",
            "single_base_pan_terminal":"OPEN", "market_validation":"NOT_RUN"}


def main() -> None:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    old = json.loads(OLD.read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    print(json.dumps(audit(spec, old, report), ensure_ascii=False))


if __name__ == "__main__":
    main()
