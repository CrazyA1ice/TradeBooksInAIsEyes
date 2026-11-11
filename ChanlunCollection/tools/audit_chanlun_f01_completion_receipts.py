"""F01: Source-pinned completion receipt contract and UNTRUSTED graph audit.

Checks necessary graph, price-overlap, temporal and policy conditions. Never
authenticates caller-provided raw trades, source hashes or author's empirical
claims. A structurally accepted receipt is NOT an actual completed movement.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "catalog/chanlun_f01_completion_receipt_contract_v1.json"
PREVIOUS = ROOT / "catalog/chanlun_author_completion_event_witnesses_v1.json"
REPORT = ROOT / "deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_F01_PROOF_CARRYING_COMPLETION_RECEIPTS_AND_BOTTOM_CASE.md"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("F01_RECEIPT_REJECTED: " + message)


def money(x: object) -> Decimal:
    require(isinstance(x, str), "price must be an explicit decimal string")
    try:
        value = Decimal(x)
    except InvalidOperation:
        raise ValueError("F01_RECEIPT_REJECTED: invalid decimal price") from None
    require(value.is_finite(), "non-finite price")
    return value


def integer(x: object) -> int:
    require(type(x) is int and x >= 0, "require nonnegative integer observation ordinal")
    return x


def validate_contract(spec: dict, old: dict, report: str, root: Path = ROOT) -> None:
    require(spec["id"] == "CHANLUN-F01-PROOF-CARRYING-COMPLETION-RECEIPT-V432", "catalog ID")
    require(spec["scope"] == "STRUCTURAL_ADMISSIBILITY_AUDIT_NOT_AUTHOR_COMPLETE_RECONSTRUCTION", "scope")
    require(old["id"] == "CHANLUN-COMPLETION-EXIT-WITNESSES-V431", "prior study")
    require(spec["author_reply_dataset"] == "catalog/chanlun_author_completion_event_witnesses_v1.json", "archived author replies")
    require(len(spec["sources"]) == 9, "nine original author lesson claim anchors")
    for card in spec["sources"]:
        file = root / f"knowledge/evidence/chanlun_lesson{card['lesson']:03d}.json"
        require(file.exists(), "missing author source evidence file")
        lesson = json.loads(file.read_text(encoding="utf-8"))
        match = next((x for x in lesson["claims"] if x["id"] == card["id"]), None)
        require(match is not None and match["kind"] == "SOURCE", "claimed author source does not exist")
        require(set(card["physical_pages"]).issubset(set(match["pdf_pages"])), "PDF physical page mismatch")

    by_id = {x["id"]: x for x in spec["formal_local_distinctions"]}
    require(set(by_id) == {"B01", "B02", "B03", "B04", "B05", "B06"}, "six local conclusions")
    require(by_id["B02"]["status"] == "AUTHOR_TEXT_CONDITIONAL_WITH_UNRESOLVED_COMPARATOR", "lowest trend N-th center comparison not certified")
    require(by_id["B05"]["status"] == "UNLICENSED_BRIDGE", "segment end cannot promote to movement finish")
    status = spec["proof_status"]
    require(status["base_pan_completion"] == "OPEN", "lowest pan terminal unresolved")
    require(status["base_trend_nonadvance"] == "AUTHOR_CONDITION_COMPARATOR_NOT_FORMALIZED", "base comparator unresolved")
    require(status["f01"] == "OPEN" and status["unique_frozen_parse"] == "OPEN_OB38", "global proof not complete")
    require(status["market_backtest"] == "NOT_RUN", "market run not claimed")
    require(all(v is True for v in spec["hard_limits"].values()), "hard research limits")
    require(spec["raw_claim_bundle_contract"]["terminal_claim"] == "only STRUCTURAL_CHECKED_NOT_MARKET_AUTHENTICATED is ever returned", "no false market verdict")
    for key in ("第18", "第20", "第35", "N>2", "F01", "OPEN", "NOT_RUN", "首个", "背驰"):
        require(key in report, "reader report missing " + key)


def check_graph(bundle: dict) -> dict:
    """Review abstract receipts. Caller-supplied timestamps and raw facts are untrusted."""
    require(bundle.get("schema_version") == 1, "bundle schema")
    require(bundle.get("mode") == "ABSTRACT_RECEIPTS_UNVERIFIED", "never accept certified market mode")
    policy = bundle.get("policy_id")
    require(isinstance(policy, str) and len(policy) >= 8, "frozen policy ID required")
    nodes = bundle.get("nodes")
    require(isinstance(nodes, list) and nodes, "nonempty list of receipts")
    require(all(isinstance(n, dict) for n in nodes), "nodes must be objects")
    require(all(isinstance(n.get("id"), str) and n["id"] for n in nodes), "stable IDs")
    ids = [n["id"] for n in nodes]
    require(len(ids) == len(set(ids)), "duplicate receipt ID")
    lookup = {n["id"]: n for n in nodes}
    kinds = {"RAW_TRADE", "F1_CENTER", "F1_TREND_NONADVANCE", "FINISHED_MOVEMENT",
             "F2_CENTER", "THIRD_POINT", "PAN_EXIT", "SEGMENT_END"}
    for n in nodes:
        require(n.get("kind") in kinds, "unsupported or unimplemented evidence kind")
        require(n.get("policy_id") == policy, "mixing analysis policy/initializer versions")
        level = integer(n.get("level"))
        known = integer(n.get("first_known_seq"))
        past = integer(n.get("historical_endpoint_seq"))
        require(past <= known, "cannot know historical endpoint before observation")
        deps = n.get("deps")
        require(isinstance(deps, list), "missing dependency list")
        require(all(isinstance(i, str) for i in deps), "dependency ID type")
        require(len(deps) == len(set(deps)), "duplicate dependencies")
        require(all(x in lookup and x != n["id"] for x in deps), "unknown/self-referential evidence")
        for d in deps:
            require(integer(lookup[d]["first_known_seq"]) <= known, "first-known timestamp is before dependency")
            require(lookup[d]["policy_id"] == policy, "dependency from incompatible policy")
    # DAG matters even when every recorded first-known time is equal.
    visited = set()
    active = set()

    def visit(k: str) -> None:
        require(k not in active, "circular completion evidence")
        if k in visited:
            return
        active.add(k)
        for dep in lookup[k]["deps"]:
            visit(dep)
        active.remove(k)
        visited.add(k)

    for k in ids:
        visit(k)

    def shape(n: dict, expected: tuple[str, ...], offsets: tuple[int, ...]) -> list[dict]:
        deps = n["deps"]
        require(len(deps) == len(expected), "wrong proof-input count for " + n["kind"])
        source = [lookup[k] for k in deps]
        require(tuple(x["kind"] for x in source) == expected, "wrong evidence types for " + n["kind"])
        require(all(x["level"] == n["level"] + off for x, off in zip(source, offsets)), "wrong lower/parent level")
        return source

    for n in nodes:
        kind = n["kind"]
        if kind == "RAW_TRADE":
            require(n["level"] == 0 and not n["deps"], "raw trade must be root at level 0")
            require(n.get("root_verified") is False, "raw source not authenticated by this tool")
            require(isinstance(n.get("stream_digest"), str) and len(n["stream_digest"]) >= 16, "caller source identity required")
            require(isinstance(n.get("stream_id"), str) and n["stream_id"], "missing stream")
            integer(n.get("ordinal"))
            money(n.get("price"))
        elif kind == "F1_CENTER":
            require(n["level"] == 0, "minimum center at initialization level")
            t = shape(n, ("RAW_TRADE", "RAW_TRADE", "RAW_TRADE"), (0, 0, 0))
            require(len({x["stream_digest"] for x in t}) == 1 and len({x["stream_id"] for x in t}) == 1, "same raw tape")
            indexes = [x["ordinal"] for x in t]
            require(indexes == list(range(indexes[0], indexes[0] + 3)), "three CONSECUTIVE trades")
            prices = [money(x["price"]) for x in t]
            require(prices[0] == prices[1] == prices[2], "same-price primitive base")
            require(money(n.get("low")) == money(n.get("high")) == prices[0], "single-price base center")
            integer(n.get("center_ordinal"))
            require(n["historical_endpoint_seq"] >= max(x["historical_endpoint_seq"] for x in t), "base center cannot be earlier than third trade")
        elif kind == "F1_TREND_NONADVANCE":
            require(n["level"] == 0, "base trend exit must be initializer level")
            first, second = shape(n, ("F1_CENTER", "F1_CENTER"), (0, 0))
            require(first["center_ordinal"] >= 2 and second["center_ordinal"] == first["center_ordinal"] + 1, "Nth center must be beyond second")
            require(n.get("direction") in ("UP", "DOWN"), "base trend direction")
            expected = "NOT_HIGHER" if n["direction"] == "UP" else "NOT_LOWER"
            require(n.get("author_comparator_claim") == expected, "directional nonadvance expression")
            require(n.get("comparison_independently_verified") is False, "source does not specify exact computable center comparator")
        elif kind == "FINISHED_MOVEMENT":
            require(n["level"] >= 0, "finished movement level")
            require(len(n["deps"]) == 1, "completed movement must carry its own exit event")
            exit_event = lookup[n["deps"][0]]
            require(exit_event["level"] == n["level"], "exit must belong to same level")
            allowed = ("F1_TREND_NONADVANCE",) if n["level"] == 0 else ("PAN_EXIT",)
            require(exit_event["kind"] in allowed, "no unfinished/segment-based or unsupported finish promotion")
            integer(n.get("movement_ordinal"))
            require(money(n.get("low")) <= money(n.get("high")), "finished movement price interval")
            require(n.get("market_finish_authenticated") is False, "structure only: no independent finish witness")
        elif kind == "F2_CENTER":
            require(n["level"] >= 1, "recursion center above initializer")
            children = shape(n, ("FINISHED_MOVEMENT",)*3, (-1,-1,-1))
            indices = [x["movement_ordinal"] for x in children]
            require(indices == list(range(indices[0], indices[0] + 3)), "child movements consecutive")
            lower = max(money(x["low"]) for x in children)
            upper = min(money(x["high"]) for x in children)
            require(lower <= upper, "three child intervals do not overlap")
            require(money(n.get("zone_low")) == lower and money(n.get("zone_high")) == upper, "parent center intersection incorrect")
        elif kind == "THIRD_POINT":
            require(n["level"] >= 1, "third point is higher than primitive initializer")
            center, departure, retrace = shape(n, ("F2_CENTER", "FINISHED_MOVEMENT", "FINISHED_MOVEMENT"), (0,-1,-1))
            require(retrace["movement_ordinal"] == departure["movement_ordinal"] + 1, "first retrace adjacency missing")
            require(n.get("first_retrace_claim_independently_proven") is False, "no global first-retrace proof from a local graph")
            zlow, zhigh = money(center["zone_low"]), money(center["zone_high"])
            if n.get("side") == "BUY":
                require(money(departure["high"]) > zhigh, "buy departure must leave above center")
                require(money(retrace["low"]) >= zhigh, "buy first retrace low must not BREAK upper bound; equality permitted")
            elif n.get("side") == "SELL":
                require(money(departure["low"]) < zlow, "sell departure must leave below center")
                require(money(retrace["high"]) <= zlow, "sell first retrace high must not BREAK lower bound; equality permitted")
            else:
                require(False, "third point requires BUY or SELL")
        elif kind == "PAN_EXIT":
            require(n["level"] >= 1, "no automatic lowest-pan terminal predicate")
            center, third = shape(n, ("F2_CENTER", "THIRD_POINT"), (0,0))
            require(third["deps"][0] == center["id"], "pan exit must depend on SAME center third point")
            require(n.get("historical_exit_authenticated") is False, "only structurally conditional pan exit")
        elif kind == "SEGMENT_END":
            require(not n["deps"] and n.get("segment_rule_authenticated") is False, "segment end is non-root, cannot replace movement exit")
            require(n.get("source_note") is not None, "segment source reference needed")
    return {
        "audit": "PASS_STRUCTURE_ONLY",
        "receipt_count": len(nodes),
        "policy": policy,
        "market_status": "NOT_AUTHENTICATED",
        "author_complete_rule_status": "OPEN",
        "claim": "STRUCTURAL_CHECKED_NOT_MARKET_AUTHENTICATED",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, help="optional UNTRUSTED abstract receipts JSON")
    args = parser.parse_args()
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    validate_contract(spec, previous, report)
    if args.bundle is None:
        print(json.dumps({"contract": "PASS", "market": "NOT_RUN", "f01": "OPEN", "real_receipts_certified": 0}, ensure_ascii=False))
    else:
        bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
        print(json.dumps(check_graph(bundle), ensure_ascii=False))


if __name__ == "__main__":
    main()
