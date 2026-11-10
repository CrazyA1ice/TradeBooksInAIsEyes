"""Audit L54 archived equation witnesses and *conditional* endpoint normalization.

This verifies endpoint strings only, not valid Chanlun segments/centers, trade signals,
historical author's correction, source independence, or a securities market feed.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "catalog/chanlun_l54_equation_variant_witnesses_v1.json"
PREVIOUS = ROOT / "catalog/chanlun_l54_prefix_stage_evidence_v1.json"
EVIDENCE = ROOT / "knowledge/evidence/chanlun_lesson054.json"
REPORT = ROOT / "deliverables/chanlun_108_acceptance/00_REVIEW/LESSON54_EQUATION_VARIANTS_AND_ONE_PRICE_CENTER_AUTHORITY.md"


def require(ok: bool, label: str) -> None:
    if not ok:
        raise ValueError("L54_VARIANT_AUDIT_FAIL: " + label)


def endpoints(path: str) -> tuple[str, str]:
    # This tool intentionally accepts simple g/d-labelled *abstract endpoints* only.
    # It is NOT a tokenizer or grammar for raw OHLC market data.
    import re

    match = re.fullmatch(r"(g[0-9]+|d[0-9]+)(g[0-9]+|d[0-9]+)", path)
    require(match is not None, "invalid endpoint token " + path)
    return match.group(1), match.group(2)


def is_contiguous(parts: list[str]) -> bool:
    return all(endpoints(a)[1] == endpoints(b)[0] for a, b in zip(parts, parts[1:]))


def endpoint_span(parts: list[str]) -> tuple[str, str]:
    require(parts and is_contiguous(parts), "parts must form a continuous path")
    return endpoints(parts[0])[0], endpoints(parts[-1])[1]


def validate(record: dict, previous: dict, lesson: dict, report: str) -> None:
    require(record["lesson"] == 54 and lesson["lesson"] == 54, "lesson identity")
    require(record["source_root_path"] == lesson["source"]["path"], "canonical path")
    require(record["source_root_sha256"] == lesson["source"]["sha256"], "canonical SHA")
    require(previous["source_notation_anomalies"][0]["printed_left"] == "g0g3", "prior author raw text locked")
    require(previous["source_notation_anomalies"][0]["allowed_correction_claim"] is None, "no author correction invented")
    require(record["original_sina_page_for_this_article_retrieved"] is False, "no primary original retrieved")
    require(record["source_family_independence_established"] is False, "cannot assert sources independent")
    require(record["research_status"].startswith("SECONDARY_TEXT_WITNESSES"), "source epistemic role")
    require(record["market_experiments"] == "NOT_RUN", "no market experiment")
    require("OPEN" in record["proof_status"], "formal obligations unresolved")

    w = record["witnesses"]
    require(len(w) == 6 and len(set(x["id"] for x in w)) == 6, "six witness records")
    by_id = {x["id"]: x for x in w}
    for name in ("W01-PDF-PRINT", "W02-ECZSC", "W03-CHANLUN108", "W04-CHANSHI"):
        require(by_id[name]["readable_left_endpoint"] == "g0g3", "preserved variant " + name)
        require(by_id[name]["readable_right_final_segment"] == "g2d3", "preserved RHS " + name)
    require(by_id["W05-FENGMR"]["readable_left_endpoint"] == "g0d3", "conditional normalized witness")
    require(by_id["W05-FENGMR"]["role"] == "SILENT_EDITORIAL_NORMALIZATION_NOT_PROVEN_AUTHOR_REVISION", "silent editorial normalization is not author")
    require(by_id["W06-TTYFP"]["readable_left_endpoint"] == "g0g3(d3?)", "annotated witness")
    require(by_id["W06-TTYFP"]["annotated_as_correction"] is True, "editor questioning")
    require(by_id["W06-TTYFP"]["role"] == "EDITOR_QUESTION_NOT_AUTHOR_CORRECTION", "not author correction")
    require(by_id["W01-PDF-PRINT"]["pdf_zero_based_page_index"] == 129, "PDF zero-based printed text page")

    p = record["path_semantics"]
    require(p["right_hand_segments"] == ["g0d1", "d1g1", "g1d2", "d2g2", "g2d3"], "underlying sequence")
    require(p["right_hand_chain_contiguous"] is True and is_contiguous(p["right_hand_segments"]), "RHS continuity")
    require(endpoint_span(p["right_hand_segments"]) == ("g0", "d3"), "LHS should end at d3")
    require(endpoints("g0g3") == ("g0", "g3"), "archival LHS token")
    require(endpoints(p["normalized_candidate_left"]) == ("g0", "d3"), "editorial normalization")
    require(p["displayed_original_endpoints_match"] is False, "mismatch stays visible")
    require(p["cannot_claim_unique_author_intended_repair"] is True, "multiple possible endpoint repairs")
    require(p["independent_theorem_disproof_not_established"] is True, "not a global refutation")
    fixes = {x["id"]: x for x in p["possible_repairs"]}
    require(set(fixes) == {"R1-LEFT-TO-D3", "R2-APPEND-D3G3"}, "alternative repairs must be preserved")
    require(fixes["R1-LEFT-TO-D3"]["stage_d3_compatible"] is True, "R1 stage")
    require(fixes["R2-APPEND-D3G3"]["stage_d3_compatible"] is False, "R2 uses post-d3 material")
    require(endpoint_span(p["right_hand_segments"] + ["d3g3"]) == ("g0", "g3"), "R2 alternative endpoint proof")
    require(all(x["author_issued_erratum_verified"] is False for x in fixes.values()), "no author's confirmed erratum")

    center = record["edge_touching_center"]
    require(center["premise"] == "d1=g2", "source equality premise")
    require(center["author_prose_degenerate_center_symbolic"] == "[d1,g2]", "one-price interval")
    require(center["center_overlap_price_count_under_author_text"] == "ONE_PRICE_POINT", "one-price boundary")
    require(center["original_sina_comment_directly_verified"] is False, "author original reply not directly inspected")
    require(center["source_role"] == "ARCHIVED_AUTHOR_REPLY_UNVERIFIED_ORIGINAL_SINA", "reply archive only")
    require(center["not_a_claim_of_market_profits"] is True, "not a trading result")

    fig = record["figure_identification"]
    require(fig["date_fragment_visible"] == "05月18日", "chart date fragment")
    require(fig["year_visible_on_chart"] is False, "cannot invent chart year")
    require(fig["stock_code_directly_verified_from_image"] is False, "cannot invent stock code read from image")
    require(fig["raw_minute_ohlc_found_and_authenticated"] is False, "no exact OHLC input")
    require(fig["earliest_actionable_timestamp_established"] is False, "no as-of certification")
    require(fig["external_pdf_figure_screenshot_zero_based_page_index"] == 128, "chart screenshot index")

    for term in ("g0g3", "g0d3", "g2d3", "R2", "单个", "2007", "OPEN", "NOT_RUN"):
        require(term in report, "reader report missing " + term)


def main() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    lesson = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    validate(record, previous, lesson, report)
    print(json.dumps({
        "audit": "PASS",
        "witnesses": 6,
        "path_span": list(endpoint_span(record["path_semantics"]["right_hand_segments"])),
        "editorial_candidate": "g0d3",
        "author_erratum": "UNVERIFIED",
        "primary_original": "NOT_RETRIEVED",
        "full_chanlun_proof": "OPEN",
        "market_experiment": "NOT_RUN",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
