#!/usr/bin/env python3
"""Read-only Chanlun proof-readiness gate; never certifies a theorem.

Checks author-claim attribution, original PDF native-text page fingerprints,
version-registry coverage, and every unsatisfied logical proof slot. A copied
author assertion, compiler note, toy partition, or even a completed local test
is not a proof of all-path existence, uniqueness, or first-center location.
No PDF rendering, data files, OCR or market experiments.
"""
from __future__ import annotations
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "reports/source_inventory/chanlun_formal_proof_readiness_v1.json"
LEDGER = ROOT / "reports/source_inventory/chanlun_38_99_proof_obligation_ledger.json"
REGISTRY = ROOT / "catalog/chanlun_rule_history_v1.json"
INVENTORY = ROOT / "reports/source_inventory/chanlun_20261107_verified.json"
PIN_MODULE = ROOT / "tools/inspect_chanlun_original_proof_text_readonly.py"
GOALS = ("OB38-EXIST", "OB38-UNIQUE", "OB38-ASOF", "OB99-EXIST", "OB99-LOCATION")
REQUIRED_FROZEN_RULE_FAMILY = "same_level_decomposition_complete_spec"
BLOCKED = "BLOCKED_NOT_CERTIFIED"
ALLOWED_SCOPE = "COMPILATION_TEXT_ANCHOR_NOT_INDEPENDENT_FIRST_PUBLICATION"
ALLOWED_CLAIM_TYPE = "SOURCE"
ALLOWED_SLOT_STATUS = "OPEN"
ALLOWED_ASSERTION_STATUS = "AUTHOR_ASSERTION_NOT_FORMAL_DERIVATION"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def original_pins() -> dict[str, str]:
    spec = importlib.util.spec_from_file_location("chanlun_existing_verified_pdf_pins", PIN_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {f"{volume}:{page}": sha
            for (volume, page), sha in module.EXPECTED_TEXT_SHA256.items()}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify(packet: dict, ledger: dict, registry: dict, inventory: dict,
           pins: dict[str, str]) -> dict:
    require(packet.get("schema_version") == 1, "Unrecognized proof packet version")
    require(packet.get("claim_scope") == ALLOWED_SCOPE, "Historical source scope changed")
    require(packet.get("certifies_theorem") is False, "Self-certified theorem is forbidden")
    require(packet.get("real_market_data_accessed") is False, "Unexpected market data claim")
    require(packet.get("complete_parser_executed") is False, "Unexpected complete parser claim")
    require(packet.get("source_pdf_text_pin_origin") == str(PIN_MODULE.relative_to(ROOT)),
            "Proof anchor pin origin changed")
    source_volumes = {int(Path(v["path"]).stem.split("卷")[-1]): v
                      for v in inventory["volumes"]}
    ledger_by_id = {g["id"]: g for g in ledger["proof_obligations"]}
    require(set(ledger_by_id) == set(GOALS), "Proof obligation ledger changed")
    registry_entries = registry["entries"]
    require(len({x["id"] for x in registry_entries}) == len(registry_entries),
            "Ambiguous rule registry IDs")
    by_id = {x["id"]: x for x in registry_entries}
    full_rules = [x["id"] for x in registry_entries
                  if x["family"] == REQUIRED_FROZEN_RULE_FAMILY
                  and x["role"] in ("author_original", "author_separately_dated")]
    # If a complete-rule candidate is registered in the future, manually review
    # author-source evidence and upgrade this gate separately. Do not auto-certify.
    require(not full_rules, "New complete-rule candidate requires separate proof review")
    require(packet.get("complete_frozen_rule_ref") is None,
            "Cannot assert a registered complete rule that has not been reviewed")
    require(set(packet.get("registered_rule_family_snapshot", []))
            == {x["family"] for x in registry_entries},
            "Rule registry family coverage changed; refresh packet with review")
    rows = packet.get("goals")
    require(isinstance(rows, list) and len(rows) == len(GOALS),
            "Missing or extra proof goal")
    require([r["id"] for r in rows] == list(GOALS), "Proof goals changed or reordered")
    result = []
    for row in rows:
        key = row["id"]
        goal = ledger_by_id[key]
        require(goal["status"] == "NOT_ESTABLISHED", "Ledger theorem status altered")
        require(row.get("status") == BLOCKED, f"Unsupported proof certificate for {key}")
        require(row.get("assertion_status") == ALLOWED_ASSERTION_STATUS,
                f"Author claim promoted to derivation in {key}")
        require(row.get("complete_frozen_rule_ref") is None, "Unknown frozen rule reference")
        slot_map = row.get("proof_slots")
        require(isinstance(slot_map, list), "Missing formal proof slots")
        require([x["key"] for x in slot_map] == goal["still_required"],
                f"Proof obligations incomplete or shuffled: {key}")
        for slot in slot_map:
            require(slot.get("status") == ALLOWED_SLOT_STATUS and
                    slot.get("derivation_ref") is None,
                    f"Proof slot may not be self-declared satisfied: {key}:{slot['key']}")
        claim_anchors = row.get("author_claim_anchors")
        require(isinstance(claim_anchors, list) and claim_anchors,
                f"Missing author text anchors for {key}")
        observed = set()
        for anchor in claim_anchors:
            lesson = anchor["lesson"]
            claimed_page = anchor["page"]
            volume = anchor["volume"]
            claim_id = anchor["claim_id"]
            require(lesson in (38, 99) and volume == (2 if lesson == 38 else 5),
                    "Anchor crosses the wrong lesson/volume")
            entry = load_json(ROOT / f"knowledge/evidence/chanlun_lesson{lesson:03d}.json")
            claim = next((c for c in entry["claims"] if c["id"] == claim_id), None)
            require(claim is not None and claim["kind"] == ALLOWED_CLAIM_TYPE,
                    f"Missing author SOURCE; EDITORIAL/AI cannot prove theorem: {claim_id}")
            require(claimed_page in claim["pdf_pages"], f"Anchor page not in claim: {claim_id}")
            require(claimed_page in entry["source"]["pdf_pages"],
                    f"Anchor outside original lesson: {claim_id}")
            require(entry["source"]["sha256"] == source_volumes[volume]["sha256"],
                    "PDF source fingerprint mismatch")
            sha = pins.get(f"{volume}:{claimed_page}")
            require(sha is not None and re.fullmatch("[0-9a-f]{64}", sha),
                    "No previously verified native-text page hash")
            require(anchor.get("native_text_sha256") == sha,
                    f"Source page fingerprint mismatch: {claim_id}")
            require(anchor.get("role") == "author_claim_in_compiled_pdf",
                    "Unsupported independent first-publication attribution")
            require((lesson, claimed_page, claim_id) not in observed, "Duplicate claim anchor")
            observed.add((lesson, claimed_page, claim_id))
        require(set(f"{volume}:{page}" for _, page, _ in observed) <=
                set(goal["known_source_pages"]), "Claim anchors not in proof goal scope")
        result.append({
            "id": key, "proof_status": BLOCKED, "open_slot_count": len(slot_map),
            "author_claim_anchors_verified_against_frozen_native_text": len(observed),
            "complete_frozen_R_g_available": False,
        })
    return {
        "status": BLOCKED,
        "report_kind": "PROOF_READINESS_AUDIT_NOT_THEOREM_PROOF",
        "goal_count": len(result),
        "goals": result,
        "rule_registry_entry_count": len(by_id),
        "registered_complete_R_g": False,
        "confirmed_formal_theorems": 0,
        "uses_market_data": False,
        "original_PDF_image_inspection": False,
    }


def main() -> None:
    receipt = verify(load_json(PACKET), load_json(LEDGER), load_json(REGISTRY),
                     load_json(INVENTORY), original_pins())
    print(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
