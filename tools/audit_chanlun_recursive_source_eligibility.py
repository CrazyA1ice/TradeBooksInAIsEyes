#!/usr/bin/env python3
"""Chanlun lesson17/35/38 necessary-source-rule bridge; pure offline logic.

Source anchors are checked by existing original PDF native-text SHA locks.
Numbers are exact Decimal synthetic interval declarations. They are NOT proof
of genuine completed lower-type membership, tick history, a complete Chanlun
parser, or lesson38/99 theorems. No images, OCR, market data or trading.
"""
from __future__ import annotations
import importlib.util
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_FILE = ROOT / "catalog/chanlun_recursive_eligibility_bridge_v1.json"
FIXTURES_FILE = ROOT / "tests/fixtures/chanlun_recursive_eligibility_cases_v1.json"
PIN_ORIGIN = ROOT / "tools/inspect_chanlun_original_proof_text_readonly.py"
INVENTORY = ROOT / "reports/source_inventory/chanlun_20261107_verified.json"
CONTRACT_ID = "CHANLUN-RECURSIVE-ELIGIBILITY-ONLY-V1"
PINNED_LINKS = (
    ("L17-THREE-CONTINUOUS", 17, 1, 197, "CL017-S02", "HIGHER_CENTER_REQUIRES_3_CONSECUTIVE_LOWER_TYPES_WITH_OVERLAP"),
    ("L35-LOWEST-BASE", 35, 2, 291, "CL35-SO-2", "LOWEST_LEVEL_BASE_THREE_SAME_PRICE_TRADES"),
    ("L35-RECURSIVE-STEP", 35, 2, 291, "CL35-SO-3", "HIGHER_CENTER_RECURSIVE_3_LOWER_TYPES_WITH_OVERLAP"),
    ("L35-ASSOCIATIVITY", 35, 2, 292, "CL35-SO-4", "CONNECTION_ASSOCIATIVE_NOT_UNIQUE_BOUNDARIES"),
    ("L38-FIXED-G", 38, 2, 338, "CL38-SOURCE-1", "SELECTED_LEVEL_IS_FIXED"),
    ("L38-ASYMMETRIC", 38, 2, 339, "CL38-SOURCE-2", "SELECTED_AND_LOWER_LEVEL_CONNECTION_POLICIES_DIFFER"),
)
EXPECTED_PREMISES = (
    "three_completed_consecutive_eligible_subtypes",
    "one_frozen_rule_version_across_all_subtypes",
    "subtype_intervals_come_from_verified_source",
    "child_to_parent_level_mapping_is_author_consistent",
    "unique_cut_boundary_and_extension_precedence",
    "point_touch_vs_positive_width_author_semantics",
)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok, why):
    if not ok:
        raise ValueError(why)


def original_pins():
    spec = importlib.util.spec_from_file_location("chanlun_original_pdf_page_pins", PIN_ORIGIN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.EXPECTED_TEXT_SHA256


def validate_contract(contract, inventory, pins, evidence_by_lesson):
    require(contract.get("schema_version") == 1 and contract.get("contract_id") == CONTRACT_ID,
            "Unexpected recursive source rule contract")
    require(contract.get("scope") == "CONDITIONAL_NECESSARY_SOURCE_RULES_NOT_COMPLETE_PARSE",
            "Conditional-only source scope removed")
    require(contract.get("original_publication_independently_checked") is False and
            contract.get("interval_model") == "AI_CLOSED_INTERVAL_SET_INTERSECTION_ONLY",
            "Compiled-PDF or interval-model scope changed")
    for name in ("complete_rule_R_g_available", "conditional_center_is_certified",
                 "lesson38_uniqueness_proven", "lesson99_eventual_center_proven"):
        require(contract.get(name) is False, "Proof status may not self-upgrade: " + name)
    require(contract.get("empirical_market_backtest") == "NOT_RUN", "Unexpected market claim")
    books = {str(item["volume"]): item["sha256"] for item in inventory["volumes"]}
    require(set(contract.get("author_verified_original_pdf_sha256", {})) == {"1", "2"},
            "Book source scope differs")
    for vol in ("1", "2"):
        require(contract["author_verified_original_pdf_sha256"][vol] == books[vol],
                "Original PDF volume fingerprint mismatch")
    rows = contract.get("original_author_claims")
    require(isinstance(rows, list) and len(rows) == len(PINNED_LINKS),
            "Original author rule coverage missing")
    for row, (key, lesson, vol, page, claim_id, concept) in zip(rows, PINNED_LINKS):
        require((row.get("id"), row.get("lesson"), row.get("volume"), row.get("page"),
                 row.get("claim_id"), row.get("concept"), row.get("source_role")) ==
                (key, lesson, vol, page, claim_id, concept, "SOURCE_IN_COMPILED_PDF"),
                f"Wrong scope or original-claim identity: {key}")
        require(row.get("native_text_sha256") == pins[(vol, page)],
                "Source native-PDF page fingerprint mismatch: " + key)
        ev = evidence_by_lesson[lesson]
        matches = [e for e in ev["claims"] if e["id"] == claim_id]
        require(len(matches) == 1 and matches[0]["kind"] == "SOURCE"
                and page in matches[0]["pdf_pages"]
                and page in ev["source"]["pdf_pages"], "Source role/physical page conflict: " + key)
        require(ev["source"]["sha256"] == books[str(vol)],
                "Canonical PDF mismatch with authored evidence: " + key)
    required = contract.get("premise_slots")
    require(isinstance(required, list) and
            [x.get("id") for x in required] == list(EXPECTED_PREMISES) and
            all(x.get("status") == "EXTERNAL_NOT_VERIFIED" and set(x) == {"id", "status"}
                for x in required), "Unreviewed source/legal premise was removed or self-certified")


FIXTURE_KEYS = {"kind", "input_id", "sequence", "sublevel",
                "rule_version", "complete", "intervals"}


def price(value):
    require(type(value) is str and value.strip() and
            all(c in "-+.0123456789" for c in value), "Only exact synthetic decimal strings accepted")
    try:
        d = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("Invalid exact decimal") from exc
    require(d.is_finite(), "Non-finite price")
    return d


def interval_result(row):
    require(isinstance(row, dict) and set(row) == FIXTURE_KEYS, "Unexpected source/market or claim fields")
    require(row["kind"] == "SYNTHETIC_INTERVALS" and
            isinstance(row["input_id"], str) and bool(row["input_id"]),
            "Only explicit synthetic input allowed")
    ids = row["sequence"]
    require(isinstance(ids, list) and len(ids) == 3 and
            all(type(x) is int and 0 <= x <= 1000 for x in ids),
            "Three finite, ordered symbolic IDs required")
    lv = row["sublevel"]
    versions = row["rule_version"]
    completed = row["complete"]
    intervals = row["intervals"]
    require(all(isinstance(x, list) and len(x) == 3 for x in (lv, versions, completed, intervals)),
            "Three matching subtype declarations required")
    require(all(isinstance(x, str) and x.strip() for x in lv + versions),
            "Level and rule version must be explicit")
    require(all(type(x) is bool for x in completed), "Completion flags must be booleans")
    bounds = []
    for item in intervals:
        require(isinstance(item, list) and len(item) == 2, "Each subtype needs low/high")
        low, high = map(price, item)
        require(low <= high, "Malformed price interval")
        bounds.append((low, high))
    # These are necessary data/scope gates on declarations, NOT proof they are real subtypes.
    if ids != list(range(ids[0], ids[0] + 3)):
        return "NOT_THREE_CONSECUTIVE_SUBTYPES"
    if len(set(lv)) != 1:
        return "CROSS_LEVEL_NOT_SAME_SUBTYPE"
    if len(set(versions)) != 1:
        return "RULE_VERSION_MISMATCH"
    if not all(completed):
        return "PENDING_UNFINISHED_SUBTYPE"
    left = max(low for low, _ in bounds)
    right = min(high for _, high in bounds)
    if left > right:
        return "NO_THREE_WAY_OVERLAP"
    if left == right:
        return "GEOMETRY_POINT_TOUCH_ONLY_UNRESOLVED_SOURCE_EQUALITY"
    return "GEOMETRY_OVERLAP_POSITIVE_WIDTH_ONLY"


def lowest_equal_three(prices):
    require(isinstance(prices, list) and len(prices) == 3,
            "Exactly three synthetic trade price strings")
    nums = [price(x) for x in prices]
    if nums[0] == nums[1] == nums[2]:
        return "SYMBOLIC_THREE_IDENTICAL_TRADE_PRICES_ONLY"
    return "SYMBOLIC_BASE_CONDITION_NOT_MET"


def check_examples(examples, contract):
    require(examples.get("schema_version") == 1 and
            examples.get("contract_id") == contract["contract_id"] and
            examples.get("contract_id") == CONTRACT_ID and
            examples.get("fixtures") is not None, "Wrong fixture contract")
    rows = examples["fixtures"]
    require(len(rows) == 8 and len({r["id"] for r in rows}) == len(rows), "Eight fixtures required")
    seen = {}
    for item in rows:
        result = interval_result(item["case"])
        require(result == item["expected"], "Wrong conditional-geometry verdict: " + item["id"])
        seen[result] = seen.get(result, 0) + 1
    base = examples["base_trade_cases"]
    require(len(base) == 2 and len({x["id"] for x in base}) == 2,
            "Two base case examples required")
    for row in base:
        require(lowest_equal_three(row["prices"]) == row["expected"], "Base case mismatch")
    require(sum(seen.values()) == 8, "Incomplete geometry cases")
    return {
        "status": "SOURCE_PINNED_CONDITIONAL_RECURSIVE_GEOMETRY_ONLY",
        "original_author_claim_anchors": len(PINNED_LINKS),
        "open_independent_premises": len(EXPECTED_PREMISES),
        "symbolic_geometry_cases": len(rows),
        "symbolic_base_cases": len(base),
        "verdicts": seen,
        "actual_lower_type_legality_certified": False,
        "actual_higher_center_certified": False,
        "theorem38_proven": False,
        "theorem99_proven": False,
        "real_market_data_accessed": False,
        "pdf_images_accessed": False,
    }


def main():
    c = read(CONTRACT_FILE)
    evidence = {lesson: read(ROOT / f"knowledge/evidence/chanlun_lesson{lesson:03d}.json")
                for lesson in (17, 35, 38)}
    validate_contract(c, read(INVENTORY), original_pins(), evidence)
    print(json.dumps(check_examples(read(FIXTURES_FILE), c), ensure_ascii=False))


if __name__ == "__main__":
    main()
