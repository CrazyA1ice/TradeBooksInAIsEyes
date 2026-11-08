#!/usr/bin/env python3
"""Partial authored-policy checker, NOT a Chanlun parser or a theorem proof.

Checks seven text-anchored clauses and only explicit abstract connection tags;
two apparently compatible cutpoint sequences are NOT evidence of two legal
Chanlun parses because complete eligibility/precedence rules remain missing.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_FILE = ROOT / "catalog/chanlun_lesson038_partial_rule_contract_v1.json"
FIXTURES_FILE = ROOT / "tests/fixtures/chanlun38_symbolic_policy_cases_v1.json"
ORIGINAL_PINS = ROOT / "tools/inspect_chanlun_original_proof_text_readonly.py"
EVIDENCE = ROOT / "knowledge/evidence/chanlun_lesson038.json"
INVENTORY = ROOT / "reports/source_inventory/chanlun_20261107_verified.json"
ID = "CL38-FIXED-G-PARTIAL-TEXT-SEMANTICS-V1"
PAGE_HASH = {"338": "369d79117897f949976704c21e81818f9e75899b0e925f637c581c32e1b21da7",
             "339": "1f48433d41259c6f82e4f5233dccd3728c823e9ab3723fe3ac77a06697689ce8"}
POLICIES = (
    ("fixed_level", "FIXED_G", 338, "CL38-SOURCE-1"),
    ("selected_extension", "UNDEFINED_NOT_IMPOSSIBLE", 339, "CL38-SOURCE-2"),
    ("selected_pan_pair", "PERMITTED", 339, "CL38-SOURCE-2"),
    ("lower_extension", "PERMITTED", 339, "CL38-SOURCE-2"),
    ("lower_pan_pair", "PROHIBITED", 339, "CL38-SOURCE-2"),
    ("higher_level", "NOT_CONSIDERED", 339, "CL38-SOURCE-2"),
    ("uniqueness", "AUTHOR_ASSERTS_NOT_INDEPENDENTLY_PROVED", 338, "CL38-SOURCE-1"),
)
MISSING = ("canonical_segment_type_rules", "competition_boundary_priority",
           "equal_price_tiebreak", "unfinished_tail_confirmation",
           "version_and_asof_clock")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(value, reason):
    if not value:
        raise ValueError(reason)


def locked_original_pins():
    module_spec = importlib.util.spec_from_file_location("original_chanlun_pdf_pins", ORIGINAL_PINS)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.EXPECTED_TEXT_SHA256


def verify_contract(doc, evidence, inventory, original_pins):
    require(doc.get("schema_version") == 1 and doc.get("id") == ID, "Contract identity mismatch")
    require(doc.get("scope") == "ORIGINAL_PDF_NATIVE_TEXT_FRAGMENT_NOT_COMPLETE_CHANLUN_GRAMMAR",
            "Partial-source scope removed")
    require(doc.get("completed_R_g") is False and doc.get("theorem_certified") is False
            and doc.get("market_data_used") is False
            and doc.get("original_first_publication_independently_verified") is False,
            "Invented completeness, original-publication or market claims")
    require(doc.get("page_text_sha256") == PAGE_HASH, "Page lock altered")
    require(tuple(doc.get("open_fields", ())) == MISSING, "Missing unresolved rule requirements")
    book = next(x for x in inventory["volumes"] if x["path"].endswith("缠论_卷2.pdf"))
    require(doc["pdf_sha256"] == book["sha256"] == evidence["source"]["sha256"],
            "PDF fingerprint mismatch")
    claims = {c["id"]: c for c in evidence["claims"]}
    actual = doc.get("clauses")
    require(isinstance(actual, list) and len(actual) == len(POLICIES),
            "Missing or extra policy clauses")
    for row, (id_, policy, page, claim_id) in zip(actual, POLICIES):
        require((row.get("id"), row.get("policy"), row.get("page"), row.get("claim_id"),
                 row.get("volume"), row.get("role"), row.get("native_text_sha256")) ==
                (id_, policy, page, claim_id, 2, "AUTHOR_IN_COMPILATION", PAGE_HASH[str(page)]),
                f"Original clause identity/value/source altered: {id_}")
        require(original_pins[(2, page)] == PAGE_HASH[str(page)],
                f"Previously verified native PDF text changed: {page}")
        claim = claims[claim_id]
        require(claim["kind"] == "SOURCE" and page in claim["pdf_pages"],
                f"Clause has invalid author role / page: {id_}")


FIELDS = frozenset(("kind", "n", "source", "rule", "level", "cuts",
                   "links", "extension", "complete"))


def assess(row):
    require(isinstance(row, dict) and set(row) == FIELDS, "Synthetic candidate schema mismatch")
    require(row["kind"] == "SYNTHETIC_SYMBOLS_NOT_MARKET", "Market data forbidden")
    require(type(row["n"]) is int and 2 <= row["n"] <= 32, "Abstract input size invalid")
    require(isinstance(row["source"], str) and row["source"].strip()
            and isinstance(row["rule"], str) and row["rule"].strip(),
            "Input identity or rule version missing")
    require(row["level"] in ("g", "lower_g"), "Level outside documented scope")
    require(type(row["extension"]) is bool and type(row["complete"]) is bool,
            "Evidence flags must be boolean")
    cuts = row["cuts"]
    require(isinstance(cuts, list) and len(cuts) >= 3 and
            all(type(x) is int for x in cuts) and cuts[0] == 0 and cuts[-1] == row["n"]
            and all(x < y for x, y in zip(cuts, cuts[1:])),
            "Candidate bounds do not partition the same abstract word")
    tags = row["links"]
    require(isinstance(tags, list) and len(tags) == len(cuts)-2
            and all(t in ("PAN_PLUS_PAN", "OTHER") for t in tags),
            "Connection labels must align with cutpoints")
    if row["level"] == "g" and row["extension"]:
        return "UNDEFINED_IN_SELECTED_DECOMPOSITION_NOT_MARKET_IMPOSSIBILITY"
    if row["level"] == "lower_g" and "PAN_PLUS_PAN" in tags:
        return "DECLARED_CONNECTION_RULE_CONFLICT"
    return "PARTIAL_POLICY_COMPATIBLE_NOT_LEGAL_PARSE_PROOF"


def compare(a, b, contract):
    require(contract["id"] == ID, "Wrong rule contract")
    va, vb = assess(a), assess(b)
    if any(a[k] != b[k] for k in ("source", "n", "rule", "level")) or a["rule"] != ID:
        return "NOT_SAME_FROZEN_RULE_DOMAIN"
    if "UNDEFINED_IN_SELECTED_DECOMPOSITION_NOT_MARKET_IMPOSSIBILITY" in (va, vb):
        return "UNDEFINED_POLICY_DOES_NOT_PROVE_IMPOSSIBILITY"
    if "DECLARED_CONNECTION_RULE_CONFLICT" in (va, vb):
        return "DECLARED_POLICY_CONFLICT_NOT_FULL_PARSE_VERDICT"
    if not (a["complete"] and b["complete"]):
        return "UNFINISHED_ASOF_PENDING"
    if a["cuts"] == b["cuts"]:
        return "SAME_CUTS_LOCAL_ONLY"
    return "COMPETING_CUTS_UNRESOLVED_NOT_CHANLUN_COUNTEREXAMPLE"


def verify_cases(cases, contract):
    require(cases.get("schema_version") == 1 and cases.get("contract_id") == ID
            and cases.get("synthetic_only") is True, "Fixture scope changed")
    rows = cases["cases"]
    require(isinstance(rows, list) and len(rows) == 7 and
            len({c["id"] for c in rows}) == len(rows), "Seven unique cases required")
    outcomes = {}
    for case in rows:
        verdict = compare(case["left"], case["right"], contract)
        require(verdict == case["expected"], f"Case {case['id']} returned {verdict}")
        outcomes[verdict] = outcomes.get(verdict, 0) + 1
    require(outcomes.get("COMPETING_CUTS_UNRESOLVED_NOT_CHANLUN_COUNTEREXAMPLE") == 1,
            "Unresolved competition case missing")
    return {"status": "PARTIAL_AUTHOR_RULE_FRAGMENT_VERIFIED_NOT_A_THEOREM",
            "original_policy_clauses_checked": len(POLICIES),
            "symbolic_scenarios": len(rows),
            "verdict_counts": outcomes, "complete_parser": False,
            "counterexample_to_complete_chanlun": False,
            "mathematical_uniqueness_proven": False, "market_data": False}


def main():
    contract = read(CONTRACT_FILE)
    verify_contract(contract, read(EVIDENCE), read(INVENTORY), locked_original_pins())
    print(json.dumps(verify_cases(read(FIXTURES_FILE), contract), ensure_ascii=False))


if __name__ == "__main__":
    main()
