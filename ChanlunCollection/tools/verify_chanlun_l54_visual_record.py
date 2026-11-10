"""Validate lesson 54 figure/source/decision provenance and limits; no image OCR or trading backtest."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "catalog" / "chanlun_l54_cross_archive_figure_and_decision_v1.json"
EVIDENCE = ROOT / "knowledge" / "evidence" / "chanlun_lesson054.json"
REPORT = ROOT / "deliverables" / "chanlun_108_acceptance" / "00_REVIEW" / "LESSON54_SOURCE_FIGURE_AND_STRUCTURAL_VS_DECISION_AGREEMENT.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError("L54_AUDIT_FAILED: " + message)


def validate_record(record: dict, evidence: dict, report: str) -> None:
    a = record["source_author"]
    image = record["external_crosscheck"]
    figure = record["figure_visual_observations"]
    parses = record["author_same_chart_two_parses"]
    replay = record["cross_version_replay"]

    require(record["lesson"] == 54 and evidence["lesson"] == 54, "lesson identity")
    require(a["canonical_repository_pdf"] == evidence["source"]["path"], "source path")
    require(a["canonical_repository_pdf_sha256"] == evidence["source"]["sha256"], "canonical PDF SHA")
    require(set(a["canonical_repository_pdf_physical_pages"]).issubset(set(evidence["source"]["pdf_pages"])), "PDF page range")
    by_id = {claim["id"]: claim for claim in evidence["claims"]}
    require(len(a["source_claim_ids"]) >= 4, "source claim coverage")
    for claim_id in a["source_claim_ids"]:
        require(claim_id in by_id and by_id[claim_id]["kind"] == "SOURCE", "SOURCE role: " + claim_id)
    editorial = a["later_editorial_claim_id"]
    require(editorial in by_id and by_id[editorial]["kind"] == "EDITORIAL", "editorial role")

    require(image["visual_observation_role"] == "VISUAL_SECONDARY_ARCHIVE", "visual archive role")
    require(image["text_observation_role"] == "AUTHOR_TEXT_IN_ARCHIVE_REPRINT", "text role")
    require(image["archived_compilation_screenshot_zero_index"] == 128, "external PDF screenshot index")
    require(image["archived_compilation_printed_page_for_chart"] == 125, "external printed page")
    require(image["pixel_identity_to_repository_pdf_not_verified"] is True, "do not assert image identity")
    require(a["canonical_pdf_independently_opened_this_step"] is False, "do not assert canonical rendering")
    require(figure["printed_chart_title"] == "航天机电(1分钟)", "chart title")
    require(figure["printed_calendar_fragment"] == "05月18日", "printed chart date")
    require(figure["calendar_year_visible_in_chart"] is False, "do not invent chart year")
    require(figure["rightmost_price_annotation_in_chart"] == "18.03", "visible final price label")
    require(figure["starts_analysis_at_price_from_author_prose"] == "18.50", "g0 is author prose, not the 18.59 chart high")
    require(figure["those_equalities_independently_pixel_verified"] is False, "equivalence unverified")
    require(figure["individual_ohlc_bar_values_recovered"] is False, "not raw bar data")
    require(figure["sub_minute_substructure_accessible"] is False, "not sub-minute data")
    require(figure["exact_1min_to_sub1min_segment_completion_independently_certified"] is False, "not author segment certification")

    aa, bb = parses["alpha"], parses["beta"]
    require(aa["high_level_center_first_formed_at_author_marker"] == "g5", "alpha center time")
    require(bb["high_level_center_first_formed_at_author_marker"] == "g6", "beta center time")
    require(aa["high_level_center_interval_author_symbolic"] == "[d2,g5]", "alpha interval")
    require(bb["high_level_center_interval_author_symbolic"] == "[d3,g5]", "beta interval")
    require(aa["g7_structure_label"] == "THIRD_SELL", "alpha g7 label")
    require(bb["g7_structure_label"] == "CENTER_OSCILLATION_NOT_THIRD_SELL", "beta g7 label")
    require(parses["structure_label_agreement"] is False, "structural classes differ")
    require(parses["center_boundary_agreement"] is False, "center ranges differ")
    require(parses["author_says_g7_overall_conclusion_agrees"] is True, "author qualitative conclusion")
    require(parses["same_exact_order_time_or_size_implied"] is False, "same conclusion does NOT imply same executable trades")
    require(parses["empirical_return_validation"] == "NOT_RUN", "no empirical test")

    require(replay["complete_replay_performed"] is False, "no full cross-era replay")
    require(replay["first_actionable_timestamp_independently_established"] is False, "no independently known as-of timestamp")
    require(record["real_market_experiments"] == "NOT_RUN", "real-market tests not run")
    require("OPEN" in record["proof_status"], "formal proof still open")
    for term in ("结构标签", "操作", "外部", "g7", "OPEN", "NOT_RUN"):
        require(term in report, "report missing " + term)


def main() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    validate_record(record, evidence, report)
    print("PASS L54 archive-figure provenance, divergent g7 structure, bounded conclusion, no unearned certification")


if __name__ == "__main__":
    main()
