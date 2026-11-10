"""Audit source-grounded type conversion contracts, not a Chanlun segment parser.

A permitted source abstraction cannot be silently turned into a later strict
segment, a finished child movement type, or a trade-time certificate.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "catalog/chanlun_l54_f1_f2_typed_bridge_v1.json"
REPORT = ROOT / "deliverables/chanlun_108_acceptance/00_REVIEW/LESSON54_F1_F2_COMPONENT_ADMISSION_AND_UNPROVEN_BRIDGES.md"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("L54_F1_F2_AUDIT_FAILED: " + message)


def reachable(start: str, edges: list[dict]) -> set[str]:
    """Reachability across declared *conditional* author/source links only."""
    reached = {start}
    while True:
        next_set = reached | {e["to"] for e in edges if e["from"] in reached}
        if next_set == reached:
            return reached
        reached = next_set


def validate(record: dict, report: str, root: Path = ROOT) -> None:
    require(record["study_id"] == "CHANLUN-L54-F1-F2-COMPONENT-TYPE-BRIDGE-V430", "study ID")
    require(record["asof_market_data"] == "NOT_RUN" and record["empirical_backtest"] == "NOT_RUN", "no fabricated market test")
    require(record["old_frontiers"] == "F01_OB38_OPEN", "proof frontier status")
    require(record["scope"] == "AUTHOR_TEXT_AND_SOURCE_CARD_INTERFACES_NO_RAW_MARKET_REPLAY", "study scope")
    objects = record["objects"]
    nodes = {v["id"] for v in objects}
    require(len(nodes) == len(objects) == 11, "11 unique typed nodes")
    ids = set()
    for card in record["canonical_source_cards"]:
        require(card["role"] == "SOURCE", "no editorial claim masquerades as source")
        path = root / "knowledge" / "evidence" / ("chanlun_lesson%03d.json" % card["lesson"])
        require(path.is_file(), "source file exists " + str(path))
        evidence = json.loads(path.read_text(encoding="utf-8"))
        source = next((e for e in evidence["claims"] if e["id"] == card["id"]), None)
        require(source is not None and source["kind"] == "SOURCE", "source claim identity " + card["id"])
        require(set(card["physical_pages"]).issubset(set(source["pdf_pages"])), "physical page mismatch " + card["id"])
        require(card["id"] not in ids, "duplicate source ID")
        ids.add(card["id"])
    require(len(ids) >= 18, "required source coverage")

    allowed = record["licensed_links"]
    gaps = record["unlicensed_bridges"]
    require(len(allowed) == 6 and len(gaps) == 8, "expected licensed and blocked link counts")
    require(len({x["id"] for x in allowed + gaps}) == 14, "distinct edge IDs")
    for edge in allowed:
        require(edge["from"] in nodes and edge["to"] in nodes, "licensed edge references registered node")
        require(edge["source_ids"] and set(edge["source_ids"]).issubset(ids), "licensed edge lacks valid author source")
        require(edge["status"] != "UNCONDITIONAL_EQUIVALENCE", "unsupported equivalence assertion")
    for edge in gaps:
        require(edge["from"] in nodes and edge["to"] in nodes, "unlicensed edge references registered node")
        require(edge["state"] == "OPEN" and edge["is_author_quoted_theorem"] is False, "cannot turn a gap into author proof")
        require(edge["required_witness"] and edge["missing"], "missing the actual proof obligation")
    require({x["id"] for x in gaps} == {"G01","G02","G03","G04","G05","G06","G07","G08"}, "eight explicit open conversion edges")

    # The three most damaging unlicensed type promotions must never sneak
    # into the list of validated conditional links.
    blocked_pairs = {(g["from"], g["to"]) for g in gaps}
    licensed_pairs = {(e["from"], e["to"]) for e in allowed}
    require(not (blocked_pairs & licensed_pairs), "unlicensed conversion promoted into licensed edge")
    require(("L54_VIEW_LINE","L67_FORMAL_SEGMENT") in blocked_pairs, "abstract line vs formal segment gap")
    require(("L67_FORMAL_SEGMENT","L18_FINISHED_CHILD_TYPE") in blocked_pairs, "segment termination vs finished trend gap")
    require(("L83_BASE_CENTER","L18_FINISHED_CHILD_TYPE") in blocked_pairs, "minimal center vs finished movement gap")

    # This reachability check is deliberately *conditional*: source facts have
    # their own premises, and topology does NOT certify premise fulfillment.
    require("L18_PARENT_CENTER" in reachable("L18_FINISHED_CHILD_TYPE", allowed), "conditional definition path exists")
    require("L18_PARENT_CENTER" not in reachable("L54_VIEW_LINE", allowed), "54 assumptions cannot generate certified parent automatically")
    require("L18_FINISHED_CHILD_TYPE" not in reachable("L67_FORMAL_SEGMENT", allowed), "no segment-to-movement completion rule")
    require("L18_PARENT_CENTER" not in reachable("L83_INIT_SEGMENT", allowed), "f1 segments do not auto-certify f2 parents")

    ps = {x["id"]: x for x in record["policy_facts"]}
    require(set(ps) == {"P01","P02","P03"}, "source policy axes")
    require(ps["P01"]["source_id"] == "CL38-SOURCE-2" and ps["P01"]["role"] == "AUTHOR_SOURCE", "38 per-level policy")
    require(ps["P03"]["source_id"] == "CL84-SOURCE-3", "84 initializer flexibility")
    require(all(x is True for x in record["methodological_guardrails"].values()), "must keep all no-overclaim guards")
    for required in ("第18课", "第38课", "第53课", "第54课", "第67", "第83课", "第84课", "f1", "f2", "G01", "G02", "OPEN", "NOT_RUN"):
        require(required in report, "report coverage " + required)


def main() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    validate(record, report)
    print(json.dumps({
        "audit":"PASS",
        "typed_objects": len(record["objects"]),
        "conditional_links": len(record["licensed_links"]),
        "open_bridges": len(record["unlicensed_bridges"]),
        "L54_abstract_to_L18_parent": "NO_LICENSED_PATH",
        "L18_completed_children_to_parent": "CONDITIONAL_BY_DEFINITION",
        "f1_f2_equivalence": "NOT_PROVEN",
        "same_frozen_rule_uniqueness": "OPEN",
        "market_test": "NOT_RUN",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
