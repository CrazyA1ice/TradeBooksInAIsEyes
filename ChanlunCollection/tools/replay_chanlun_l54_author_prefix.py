"""Replay *author-narrative* evidence stages, NOT a Chanlun OHLC or trading parser.

No external packages, real-market feed, indicator calculations or inferred fills.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "catalog/chanlun_l54_prefix_stage_evidence_v1.json"
LESSON_EVIDENCE = ROOT / "knowledge/evidence/chanlun_lesson054.json"
PRIOR_VISUAL = ROOT / "catalog/chanlun_l54_cross_archive_figure_and_decision_v1.json"


def require(condition: bool, what: str) -> None:
    if not condition:
        raise ValueError("L54_PREFIX_AUDIT_FAILED: " + what)


def load_record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def validate(record: dict, evidence: dict, visual: dict) -> None:
    order = record["stage_order"]
    require(len(order) == len(set(order)) and order[0] == "g0" and order[-1] == "AFTER_G7", "stage list")
    require(set(record["parsing_policies"]) == {"ALPHA", "BETA"}, "policy names")
    require(record["canonical_repository_pdf"] == evidence["source"]["path"], "canonical source path")
    by_claim = {e["id"]: e for e in evidence["claims"]}
    require(all(k in by_claim and by_claim[k]["kind"] == "SOURCE" for k in record["source_claim_ids"]), "source claim identity")
    require(visual["author_same_chart_two_parses"]["alpha"]["g7_structure_label"] == "THIRD_SELL", "alpha upstream source")
    require(visual["author_same_chart_two_parses"]["beta"]["g7_structure_label"] == "CENTER_OSCILLATION_NOT_THIRD_SELL", "beta upstream source")
    require(visual["author_same_chart_two_parses"]["author_says_g7_overall_conclusion_agrees"] is True, "qualitative upstream source")

    require(record["stage_order_is_author_narrative_not_raw_tick_timestamps"] is True, "not timestamp proof")
    require(record["canonical_pdf_this_step_visual_verification"] is False, "canonical PDF not inspected")
    require(record["market_asof_certification"] == "NOT_ESTABLISHED", "no market as-of proof")
    require(record["empirical_trading_tests"] == "NOT_RUN", "market tests not run")
    require(record["proof_f01_ob38_ob99"] == "OPEN", "formal proof open")
    require(all(v is True for v in record["immutable_constraints"].values()), "all guards must be enabled")
    require(len(record["source_notation_anomalies"]) == 1, "notation issue provenance")
    anomaly = record["source_notation_anomalies"][0]
    require(anomaly["printed_left"] == "g0g3" and anomaly["printed_last_right_component"] == "g2d3", "exact notation")
    require(anomaly["left_endpoint"] == "g3" and anomaly["right_endpoint"] == "d3", "endpoint distinction")
    require(anomaly["allowed_correction_claim"] is None and anomaly["status"].startswith("APPARENT_"), "do not silently correct")

    events = record["events"]
    ids = [e["id"] for e in events]
    require(len(ids) == len(set(ids)) and len(events) == 13, "unique, expected evidence events")
    allowed_kinds = {"AUTHOR_PROSE", "VISUAL_SECONDARY_ARCHIVE"}
    for e in events:
        require(e["stage"] in order, "unknown stage: " + e["id"])
        require(e["policy"] in ("BOTH", "ALPHA", "BETA"), "unknown policy")
        require(e["kind"] in allowed_kinds, "source role invalid")
        require(bool(e["text_locator"]), "missing text locator")
        require(e["stage"] == "AFTER_G7" if e["kind"] == "VISUAL_SECONDARY_ARCHIVE" else e["stage"] != "AFTER_G7", "event provenance time type")

    require(_event(events, "FIVE_MIN_CENTER_FIRST_FORMED", "ALPHA")["stage"] == "g5", "alpha center gate")
    require(_event(events, "FIVE_MIN_CENTER_FIRST_FORMED", "BETA")["stage"] == "g6", "beta center gate")
    require(_event(events, "FIVE_MIN_CENTER_FIRST_FORMED", "ALPHA")["value"]["interval"] == "[d2,g5]", "alpha center interval")
    require(_event(events, "FIVE_MIN_CENTER_FIRST_FORMED", "BETA")["value"]["interval"] == "[d3,g5]", "beta center interval")
    require(_event(events, "G7_STRUCTURAL_CLASS", "ALPHA")["value"] == "THIRD_SELL", "alpha g7")
    require(_event(events, "G7_STRUCTURAL_CLASS", "BETA")["value"] == "CENTER_OSCILLATION_NOT_THIRD_SELL", "beta g7")
    require(_event(events, "G7_STRUCTURAL_CLASS", "ALPHA")["stage"] == "g7", "alpha g7 stage")
    require(_event(events, "G7_STRUCTURAL_CLASS", "BETA")["stage"] == "g7", "beta g7 stage")
    require(_event(events, "AUTHOR_QUALITATIVE_CONCLUSION", "BOTH")["stage"] == "g7", "conclusion first available from author's commentary")
    require(_event(events, "CHART_RIGHTMOST_PRICE_LABEL", "BOTH")["stage"] == "AFTER_G7", "post g7 price is FUTURE at g7")
    require(_event(events, "CHART_RIGHTMOST_PRICE_LABEL", "BOTH")["value"] == "18.03", "post g7 source price")
    require(_event(events, "FUTURE_DECLINE_AFTER_G7_VISIBLE", "BOTH")["stage"] == "AFTER_G7", "future path must not appear at g7")


def _event(events: list[dict], predicate: str, policy: str) -> dict:
    matches = [e for e in events if e["predicate"] == predicate and e["policy"] == policy]
    require(len(matches) == 1, "expected exactly one evidence claim: " + predicate + "/" + policy)
    return matches[0]


def replay(record: dict, stage: str, policy: str) -> dict:
    order = record["stage_order"]
    require(stage in order, "requested stage not in author narrative")
    require(policy in record["parsing_policies"], "requested policy")
    index = order.index(stage)
    visible = [
        e for e in record["events"]
        if order.index(e["stage"]) <= index and e["policy"] in ("BOTH", policy)
    ]
    observed = {e["predicate"]: e for e in visible}
    center = observed.get("FIVE_MIN_CENTER_FIRST_FORMED")
    g7 = observed.get("G7_STRUCTURAL_CLASS")
    qualitative = observed.get("AUTHOR_QUALITATIVE_CONCLUSION")
    future = observed.get("CHART_RIGHTMOST_PRICE_LABEL")
    return {
        "author_stage": stage,
        "parse_policy": policy,
        "evidence_ids": [e["id"] for e in visible],
        "center_assertion": center["value"] if center else None,
        "g7_structural_assertion": g7["value"] if g7 else None,
        "author_qualitative_g7_conclusion": qualitative["value"] if qualitative else None,
        "chart_rightmost_price_label": future["value"] if future else None,
        "market_first_knowable_timestamp": None,
        "raw_ohlc_replay": "NOT_RUN",
        "order_or_pnl": None,
        "proof_status": "AUTHOR_TEXT_STAGE_ONLY",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--show", choices=("all", "g5", "g6", "g7", "AFTER_G7"), default="all")
    args = parser.parse_args()
    record = load_record()
    validate(
        record,
        json.loads(LESSON_EVIDENCE.read_text(encoding="utf-8")),
        json.loads(PRIOR_VISUAL.read_text(encoding="utf-8")),
    )
    selected = record["stage_order"] if args.show == "all" else [args.show]
    snapshots = [replay(record, stage, policy) for stage in selected for policy in record["parsing_policies"]]
    print(json.dumps({"audit": "PASS", "snapshots": snapshots, "empirical_trading": "NOT_RUN"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
