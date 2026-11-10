"""Check provenance and *conditional* exits from 2007 author-reply archives.

This program neither fetches market data nor proves the author's global theorem.
It keeps archived comments separate from lesson prose and requires complete
lower-level movement witnesses BEFORE granting a third-type point exit.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog/chanlun_author_completion_event_witnesses_v1.json"
OLDER = ROOT / "catalog/chanlun_l54_f1_f2_typed_bridge_v1.json"
REPORT = ROOT / "deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_AUTHOR_REPLY_COMPLETION_EXIT_EVENTS_AND_NONCIRCULAR_PROOFS.md"


def check(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("COMPLETION_EXIT_AUDIT_FAIL: " + reason)


def validate(data: dict, old: dict, report: str, root: Path = ROOT) -> None:
    check(data["id"] == "CHANLUN-COMPLETION-EXIT-WITNESSES-V431", "dataset version")
    check(data["scope"] == "AUTHOR_SOURCE_TEXT_PLUS_ARCHIVED_AUTHOR_REPLIES__NOT_FULL_RULE_VALIDATION", "not market proof")
    replies = {x["id"]: x for x in data["findings"]}
    check(len(replies) == len(data["findings"]) == 4, "four dated attributed replies")
    check(all(x["archive_kind"] in ("REPOSTED_AUTHOR_REPLY", "REPOSTED_COMMENT_FROM_SAME_DAY_MARKET_ARTICLE") for x in replies.values()), "comments not chapter body")
    check(all(x["original_sina_comment_directly_authenticated"] is False for x in replies.values()), "no direct authenticated Sina comments")
    check(replies["AUTH-2007-08-21-162001"]["archive_timestamp"] == "16:20:01", "pan/trend exit reply time")
    check(replies["AUTH-2007-08-21-162001"]["historical_effective_date"] == "2007-08-21", "reply day")
    check(replies["AUTH-2007-08-21-162728"]["archive_timestamp"] == "16:27:28", "pen-vs-segment reply time")
    check(replies["AUTH-2007-08-21-170226"]["archive_timestamp"] == "17:02:26", "no mutual implication reply time")
    check(replies["AUTH-2007-05-09-C2"]["archive_timestamp"] == "16:56:39", "May9 archive time")
    check(replies["AUTH-2007-05-09-C2"]["another_archive_timestamp"] == "16:54:18", "secondary time variation retained")

    a = data["attribution_correction"]
    check(a["same_day_lesson72_published"] == "2007-08-21 22:37:20", "lesson 72 later publication")
    check(a["comment_162001_prior_to_lesson72_post"] is True, "chronology")
    check(a["comment_part_of_canonical_lesson72_body"] is False, "do not attribute earlier comment to lesson 72 body")
    check(a["comment_original_sina_authenticated"] is False, "no original authenticated post comment")

    source_ids = set()
    for link in data["original_lesson_prose"]:
        f = root / f"knowledge/evidence/chanlun_lesson{link['lesson']:03d}.json"
        check(f.is_file(), f"missing evidence file {f}")
        j = json.loads(f.read_text(encoding="utf-8"))
        source = {x["id"]: x for x in j["claims"] if x["kind"] == "SOURCE"}
        for claim_id in link["claim_ids"]:
            check(claim_id in source, "misattributed SOURCE " + claim_id)
            source_ids.add(claim_id)
    check(len(source_ids) >= 12, "minimum source coverage")

    events = {x["id"]: x for x in data["typed_events"]}
    check(set(events) == {"EV-SEGMENT-END", "EV-CENTER-MINIMUM", "EV-PAN-EXIT-THIRD", "EV-TREND-EXIT-BACK"}, "event universe")
    seg = events["EV-SEGMENT-END"]
    center = events["EV-CENTER-MINIMUM"]
    pan = events["EV-PAN-EXIT-THIRD"]
    trend = events["EV-TREND-EXIT-BACK"]
    check(seg["finished_child_movement_implied"] is False, "segment break cannot certify movement type")
    check(set(center["required_conditions"]) == {"THREE_CONSECUTIVE_COMPLETED_LOWER_MOVEMENT_TYPES", "PRICE_RANGE_INTERSECTION"}, "minimum center needs completed children")
    check(center["finished_parent_movement_implied"] is False, "minimum center not a completed parent")
    check(set(pan["required_conditions"]) == {"VALID_PARENT_CENTER", "FULL_LOWER_TYPE_DEPARTURE", "FIRST_FULL_LOWER_TYPE_RETRACE", "THIRD_POINT_NON_RETURN_BOUNDARY"}, "pan exit needs full complete departure and retrace, not partial")
    check(pan["third_point_cannot_certify_its_own_retrace_without_independent_child_completion"] is True, "block circular proof")
    check(set(trend["required_conditions"]) == {"VALID_TREND_AT_LEVEL", "LAST_CENTER_ID", "AUTHORED_TREND_DIVERGENCE_AT_LEVEL", "ACTUAL_PULLBACK_TO_LAST_CENTER_WITH_DEFINED_BOUNDARY"}, "trend exit needs actual post divergence pullback")
    check(trend["claimed_higher_center_effect_author_assertion_not_independent_proof"] is True, "higher center claim is unproven by script")
    for event in events.values():
        check(event["confirmation_time_from_market_bars_known"] is False, "cannot pretend to know event timestamp")
    check(pan["position_of_historical_turn_vs_first_confirmation_unproven"] is True, "pan time distinction")
    check(trend["position_of_historical_turn_vs_first_confirmation_unproven"] is True, "trend time distinction")

    gaps = {x["gap"] for x in data["known_missing_proofs"]}
    check(gaps == {"CE01","CE02","CE03","CE04","CE05","CE06"}, "six unresolved obligations")
    check(all(x["state"] == "OPEN" for x in data["known_missing_proofs"]), "cannot certify complete proof")
    check(old["followup_completion_exit_study"] == "catalog/chanlun_author_completion_event_witnesses_v1.json", "v4.30 study linked")
    for id in ("G02","G03"):
        g = next(x for x in old["unlicensed_bridges"] if x["id"] == id)
        check(g["state"] == "OPEN" and "followup_author_reply_evidence" in g, "source conclusion refines but does not close " + id)
    check(data["proof_status"] == "F01_OB38_OB99_OPEN", "no proof overclaim")
    check(data["market_asof"] == "NOT_ESTABLISHED", "no market timestamp")
    check(data["raw_ohlc_and_subminute_available"] is False, "no invented OHLC")
    check(data["empirical_status"] == "NOT_RUN", "no backtest")
    for phrase in ("第18", "第20", "第67", "第71", "第72", "16:20:01", "第三类", "回拉", "未完成", "OPEN", "NOT_RUN"):
        check(phrase in report, "missing source or boundary description in report: " + phrase)


def main() -> None:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    old = json.loads(OLDER.read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    validate(data, old, report)
    print(json.dumps({
        "result": "PASS",
        "archived_author_replies": 4,
        "lesson_prose_anchors": len(data["original_lesson_prose"]),
        "distinct_typed_events": 4,
        "unresolved_completion_proofs": 6,
        "lesson72_quote_misassignment": "REJECTED",
        "market_asof_certification": "NOT_ESTABLISHED",
        "full_chanlun_proof": "OPEN",
        "market_backtest": "NOT_RUN"
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
