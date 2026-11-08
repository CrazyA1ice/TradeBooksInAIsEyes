#!/usr/bin/env python3
"""Read-only source-qualified computation of Chanlun 18/20 center inequalities.

Numeric outcomes are only mathematical implications of exact, synthetic Zn
interval declarations. They never establish legal Zn, actual center existence,
as-of completion, trading action, or original theorem38/99.
"""
from __future__ import annotations
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "catalog/chanlun_center_order_completion_partial_v1.json"
CASES = ROOT / "tests/fixtures/chanlun_center_order_completion_cases_v1.json"
PINS = ROOT / "reports/source_inventory/chanlun_center_order_completion_native_text_sha256.json"
INVENTORY = ROOT / "reports/source_inventory/chanlun_20261107_verified.json"
PDF_SHA = "0a402e19bbcabc24a5d031b047aeebcf96cdb7f777d2462cc7e5b28ed121b865"
ID = "CL18-20-CENTER-ORDER-COMPLETION-PARTIAL-V1"
PROOF_PAGES = {"234": "69121d9a964de1298165d08291f802d4263be12adaabdd8f5e5353b396aca86f",
               "235": "d4f06d4d8395748f7b38307ccdc83436fdf9480a729fad413c45f772ae7023d4",
               "236": "434c7daf3ccae1460d9f1aa2078ec57a05454e73c3f6cbd3705b66187dca9794",
               "245": "b699993c6d57238640eb94844f53d5391fcb1572659cae08fb2248139ca74ea3",
               "246": "441f33589318f29d539f01124a9be0ecf8fd98e372b2340cb2367a785a5397f9",
               "247": "413cbc347ea62f60139f49920b667084aeb5d8453645d5f99d9387aaa8ea8039"}
SOURCES = (("CL018-S01", 18, (234,), "FIRST_THREE_COMPLETED_CHILD_TYPES_CENTER_PREMISE"),
           ("CL018-S07", 18, (235,), "CAN_COMPLETE_VS_ACTUALLY_COMPLETED_DISTINCT"),
           ("CL020-S08", 20, (246,247), "GG_DD_ZG_ZD_AND_STRICT_COMPARISON_AND_EXPANSION"))
FORMULAS = {"GG": "max(g_n)", "DD": "min(d_n)", "ZG": "min(g_1,g_2)",
            "ZD": "max(d_1,d_2)", "up": "later.DD > earlier.GG",
            "down": "later.GG < earlier.DD",
            "expansion_left": "later.ZG < earlier.ZD AND later.GG >= earlier.DD",
            "expansion_right": "later.ZD > earlier.ZG AND later.DD <= earlier.GG"}
OPEN = ("legal_z_element_membership", "legal_three_consecutive_lower_types",
        "actual_center_and_center_relative_placement",
        "actual_center_and_parent_type_completion",
        "original_historical_asof_confirmation_and_version",
        "original_author_inequality_boundary_semantics_vs_closed_interval_model")
CENTER_KEYS = {"kind", "z_segments", "first_three_lower_completed",
               "first_three_lower_confirmed_at", "rule_version"}
CASE_KEYS = {"kind", "as_of", "earlier", "later"}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def need(v, message):
    if not v:
        raise ValueError(message)


def validate(doc, pins, inventory, cards):
    need(doc.get("schema_version") == 1 and doc.get("id") == ID
         and doc.get("scope") == "AUTHOR_COMPILATION_NATIVE_PROSE_MATHEMATICAL_NECESSITY_ONLY",
         "Original-source contract identity or scope changed")
    need(doc.get("source_pdf_sha256") == PDF_SHA
         and doc.get("source_native_text_sha_file") ==
             "reports/source_inventory/chanlun_center_order_completion_native_text_sha256.json",
         "Original PDF provenance mismatch")
    volume = next(v for v in inventory["volumes"] if v["path"].endswith("缠论_卷1.pdf"))
    need(volume["sha256"] == PDF_SHA and pins["source_pdf_sha256"] == PDF_SHA
         and pins["reader"] == "pymupdf_1.26.7_get_text_sort_true"
         and pins["page_native_text_sha256"] == PROOF_PAGES,
         "Frozen PDF native-text fingerprints changed")
    claims = doc.get("source_claims")
    need(isinstance(claims, list) and len(claims) == len(SOURCES),
         "Missing source lessons or clause identity")
    for source, (claim_id, lesson, pages, purpose) in zip(claims, SOURCES):
        need((source.get("claim"), source.get("lesson"),
              tuple(source.get("physical_pages", ())), source.get("purpose")) ==
             (claim_id, lesson, pages, purpose), "Claim scope or author role changed")
        card = cards[lesson]
        matched = [c for c in card["claims"] if c["id"] == claim_id]
        need(len(matched) == 1 and matched[0]["kind"] == "SOURCE"
             and all(p in matched[0]["pdf_pages"] for p in pages)
             and card["source"]["sha256"] == PDF_SHA,
             "Claim source lacks corresponding authored PDF page")
        if claim_id in ("CL018-S07", "CL020-S08"):
            anchor = matched[0]["source_anchor"]
            need(anchor["canonical_pdf_sha256"] == PDF_SHA and
                 anchor["role"] ==
                    "AUTHOR_MAIN_TEXT_IN_COMPILATION_WITH_INLINE_LATER_EDITORIAL_NOTES"
                 and anchor["independent_first_publication_verified"] is False
                 and anchor["inline_editorial_markers_present"] is True
                 and anchor["full_image_review"] is False
                 and anchor["not_a_complete_legal_center_certification"] is True
                 and anchor["native_text_sha256_by_physical_page"] ==
                 {str(page): PROOF_PAGES[str(page)] for page in pages},
                 "Author/editor boundary or new claim page hashes altered")
    need(doc.get("author_comparison_formulas") == FORMULAS,
         "Original strict comparison and equality predicates changed")
    need(doc.get("author_completion_distinctions") ==
         {"center_requires": "three_consecutive_completed_lower_types",
          "consolidation_after_threshold": "may_finish_but_may_extend",
          "trend_after_two_centers": "may_finish_but_may_extend"},
         "Possible completion has been misreported as confirmed completion")
    need(doc.get("formula_input_qualifier") ==
         "z_elements_must_be_author_qualified_directional_subtypes_not_any_three_intervals"
         and doc.get("computed_indicator_semantics") ==
         "EXACT_DECIMAL_ON_SYNTHETIC_DECLARED_Z_ELEMENTS_ONLY",
         "Loss of original Zn membership source restrictions")
    need(doc.get("unverified_source_premises") == list(OPEN),
         "Unverified center legality or source semantics erased")
    for flag in ("complete_chanlun_parser", "actual_center_certified",
                 "actual_type_completed", "proof_38_or_99_established", "market_data_read"):
        need(doc.get(flag) is False, "Self-certified market center or theorem")


def decimal(s):
    need(type(s) is str and s.strip()
         and all(ch in "0123456789.-+" for ch in s), "Only exact synthetic decimal strings")
    try:
        v = Decimal(s)
    except InvalidOperation as err:
        raise ValueError("Bad decimal") from err
    need(v.is_finite(), "Non-finite value")
    return v


def time(s):
    need(type(s) is str, "Expected exact synthetic timestamp")
    try:
        v = datetime.fromisoformat(s)
    except ValueError as err:
        raise ValueError("Bad timestamp") from err
    need(v.tzinfo is not None and v.utcoffset() is not None, "Timezone-naive timestamp")
    return v


def parse_center(center):
    need(type(center) is dict and set(center) == CENTER_KEYS, "Unexpected legal certificate fields")
    need(center["kind"] == "SYNTHETIC_DECLARED_Z_NOT_AUTHOR_CERTIFIED",
         "Actual center membership cannot be self-certified")
    need(type(center["rule_version"]) is str and center["rule_version"].strip(),
         "No pinned hypothetical rule version")
    z = center["z_segments"]
    need(type(z) is list and 2 <= len(z) <= 12, "Zn symbolic sequence must contain first two members")
    bounds = []
    for item in z:
        need(type(item) is list and len(item) == 2, "Zn must contain decimal low/high")
        lo, hi = map(decimal, item)
        need(lo <= hi, "Invalid Zn interval")
        bounds.append((lo, hi))
    flags = center["first_three_lower_completed"]
    stamps = center["first_three_lower_confirmed_at"]
    need(type(flags) is list and len(flags) == 3 and all(type(k) is bool for k in flags),
         "Exactly three declared lower subtype completion booleans")
    need(type(stamps) is list and len(stamps) == 3, "Exactly three declared confirmation timestamps")
    time_values = [time(s) if s is not None else None for s in stamps]
    need(all(a is None or b is None or a < b for a,b in zip(time_values, time_values[1:])),
         "Declared lower confirmation clock must advance")
    need(all(k or t is None for k,t in zip(flags,time_values)),
         "Incomplete lower subtype cannot have completed-at timestamp")
    zg = min(bounds[0][1],bounds[1][1])
    zd = max(bounds[0][0],bounds[1][0])
    gg = max(hi for _,hi in bounds)
    dd = min(lo for lo,_ in bounds)
    return {"GG": gg,"DD":dd,"ZG":zg,"ZD":zd,"times":time_values,"flags":flags,
            "version":center["rule_version"]}


def evaluate(case, contract):
    need(contract["id"] == ID, "Wrong source scope for comparison")
    need(type(case) is dict and set(case) == CASE_KEYS, "Unexpected market or proof-certificate fields")
    need(case["kind"] == "SYNTHETIC_DIRECTIONAL_Z_NUMERIC_ONLY",
         "Real market and original PDF figure extraction forbidden")
    asof = time(case["as_of"])
    previous, later = parse_center(case["earlier"]), parse_center(case["later"])
    if previous["version"] != later["version"]:
        return "DIFFERENT_RULE_VERSION_NO_COMPARISON"
    if not all(previous["flags"]+later["flags"]):
        return "UNCOMPLETED_LOWER_TYPE_PENDING"
    if any(t is None or t > asof for center in (previous,later) for t in center["times"]):
        return "ASOF_LOWER_TYPE_NOT_YET_CONFIRMED"
    if any(center["ZG"] < center["ZD"] for center in (previous,later)):
        return "DECLARED_CENTER_CORE_EMPTY"
    if any(center["ZG"] == center["ZD"] for center in (previous,later)):
        return "POINT_TOUCH_CORE_AUTHOR_SEMANTICS_UNRESOLVED"
    if later["DD"] > previous["GG"]:
        return "AUTHOR_STRICT_UP_NUMERIC_CONDITION_ONLY"
    if later["GG"] < previous["DD"]:
        return "AUTHOR_STRICT_DOWN_NUMERIC_CONDITION_ONLY"
    if ((later["ZG"] < previous["ZD"] and later["GG"] >= previous["DD"]) or
        (later["ZD"] > previous["ZG"] and later["DD"] <= previous["GG"])):
        return "AUTHOR_EXPANSION_NUMERIC_CONDITION_ONLY"
    return "AUTHOR_NUMERIC_RELATION_UNRESOLVED"


def run_cases(doc, contract):
    need(doc.get("schema_version") == 1 and doc.get("contract_id") == ID
         and doc.get("synthetic_only") is True, "Bad source-qualified fixture set")
    cases = doc["cases"]
    need(isinstance(cases,list) and len(cases)==10
         and len({c["id"] for c in cases}) == len(cases),
         "Ten distinct numeric/scope cases required")
    counts={}
    for c in cases:
        actual = evaluate(c["input"],contract)
        need(actual == c["expected"], "Changed original numeric relation: "+c["id"]+" -> "+actual)
        counts[actual]=counts.get(actual,0)+1
    need(counts.get("AUTHOR_STRICT_UP_NUMERIC_CONDITION_ONLY")>=1
         and counts.get("AUTHOR_STRICT_DOWN_NUMERIC_CONDITION_ONLY")>=1
         and counts.get("AUTHOR_EXPANSION_NUMERIC_CONDITION_ONLY")>=1,
         "No original author strict/up/down/expansion coverage")
    return {"status":"AUTHOR_CENTER_FORMULAS_PINNED_CONDITIONAL_ONLY",
            "native_pdf_pages_pinned":len(PROOF_PAGES),"source_claims":len(SOURCES),
            "unverified_source_premises":len(OPEN),"symbolic_cases":len(cases),
            "case_status_counts":counts,"author_legal_center_certificates":0,
            "completed_actual_trends":0,"proof_38_or_99":False,
            "market_data_accessed":False,"pdf_images_accessed":False}


def main():
    contract=read(CONTRACT)
    validate(contract,read(PINS),read(INVENTORY),
             {n:read(ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json")
              for n in (18,20)})
    print(json.dumps(run_cases(read(CASES),contract),ensure_ascii=False))


if __name__=="__main__":
    main()
