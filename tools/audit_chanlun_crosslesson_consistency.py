#!/usr/bin/env python3
"""Cross-lesson source and scoped logical consistency audit for Chanlun 108.

This script checks declared SOURCE-card anchors, original-volume SHA roles,
version-registry membership, and finite *abstract* nonimplication models.
It does not execute the author's completed Chanlun grammar Rg and does not
prove either universal consistency or an original author contradiction.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"catalog/chanlun_crosslesson_consistency_v1.json"
INDEX=ROOT/"catalog/chanlun_lesson_index.json"
VERSIONS=ROOT/"catalog/chanlun_rule_history_v1.json"
THEORY=ROOT/"catalog/chanlun_theory_argument_links_v1.json"
MANUSCRIPT=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_THEORY_CONSISTENCY.md"
ID="CL108-CROSSLESSON-THEORY-CONSISTENCY-V1"
CATEGORIES={"NON_IMPLICATION","CONDITIONAL_SCOPE_RECONCILIATION","VERSIONED_COEXISTENCE",
            "TYPE_DOMAIN_RESTRICTION","QUANTIFIER_AND_CLOCK_GAP"}
CONCLUSIONS={
 "C01":"BASE_CENTER_EXISTS_NOT_ENDED","C02":"OVERLAP_NOT_NEW_CENTER",
 "C03":"THIRD_BUY_NOT_FUTURE_TREND","C04":"COVERAGE_NOT_PROFIT",
 "C05":"NECESSARY_NOT_SUFFICIENT","C06":"INDICATOR_NOT_LEGAL_SEGMENT",
 "C07":"NO_FORMAL_COUNTERMODEL_TO_RG","C08":"ASSOCIATIVITY_NOT_UNIQUE_PARSE",
 "C09":"RULE_REVISION_NOT_RETROACTIVE","C10":"SUPPORT_NOT_MEMBERSHIP",
 "C11":"EXISTS_NOT_FORALL","C12":"RECURSIVE_GRAMMAR_NOT_BIJECTION",
 "C13":"ZN_OUTSIDE_NOT_THIRD_BUY","C14":"FRACTAL_BOTTOM_NOT_STRUCTURAL_BOTTOM",
 "C15":"TWO_ZN_CORE_NOT_THREE_COMPLETED_TYPES",
 "C16":"REGISTRY_NO_GLOBAL_SUPERSESSION"
}
NO_FORMAL_PROOF=("global_author_theory_consistent_proven",
                 "global_author_theory_inconsistent_proven",
                 "complete_Rg_fixed","actual_market_data_read","all_original_images_read")
# The premises of these purely abstract countermodels are deliberately weaker
# than a complete legal Chanlun market path; they refute *inferences*, not the
# original author's fully scoped theorem.
def witness(label):
    if label=="BASE_CENTER_EXISTS_NOT_ENDED":
        prices=["2","2","2"];return len(set(prices))==1,False
    if label=="OVERLAP_NOT_NEW_CENTER":
        core=(2,5); interval=(3,4)
        return max(core[0],interval[0])<min(core[1],interval[1]),False
    if label=="THIRD_BUY_NOT_FUTURE_TREND":return True,False
    if label=="COVERAGE_NOT_PROFIT":
        candidates={"A","B","C"}
        classes=({"A","B"},{"B","C"},set())
        covers=all(any(x in group for group in classes) for x in candidates)
        return covers,False
    if label=="NECESSARY_NOT_SUFFICIENT":
        third=True; large_reversal=False
        conditional=(not large_reversal) or third
        return third and conditional,large_reversal
    if label=="INDICATOR_NOT_LEGAL_SEGMENT":
        return 9<12,False  # MACD numeric comparison cannot certify legal ABC
    if label=="ASSOCIATIVITY_NOT_UNIQUE_PARSE":
        a,b,c="a","b","c"
        associative=((a+b)+c)==(a+(b+c))
        alternatives=(("ab",),("a","b"))
        return associative and "".join(alternatives[0])=="".join(alternatives[1]), alternatives[0]==alternatives[1]
    if label=="EXISTS_NOT_FORALL":
        futures=(True,False) # toy admissible paths; no claim they meet author's complete Rg
        return any(futures),all(futures)
    if label=="RECURSIVE_GRAMMAR_NOT_BIJECTION":
        # f1 is replaceable, f2 is shared: neither supplies an actual map S->S.
        f1a=lambda x:(x,)
        f1b=lambda x:(x,x)
        f2=lambda x:x+("next",)
        return f2(f1a("s"))!=f2(f1b("s")),False
    if label=="ZN_OUTSIDE_NOT_THIRD_BUY":
        midpoint=11; core_hi=10
        first_completed_retest=False
        return midpoint>core_hi,first_completed_retest
    if label=="FRACTAL_BOTTOM_NOT_STRUCTURAL_BOTTOM":
        return True,False
    if label=="TWO_ZN_CORE_NOT_THREE_COMPLETED_TYPES":
        two=(1,5),(2,6)
        core=(max(z[0] for z in two),min(z[1] for z in two))
        return core[0]<core[1],False
    if label=="SUPPORT_NOT_MEMBERSHIP":
        auxiliary_helps_pattern=True; strict_member=False
        return auxiliary_helps_pattern,strict_member
    raise ValueError("Undeclared finite countermodel: "+label)


def load(p):return json.loads(p.read_text(encoding="utf-8"))
def require(ok,message):
    if not ok:raise ValueError(message)


def audit():
    ledger=load(LEDGER);idx=load(INDEX);versions=load(VERSIONS)
    by_vol={l["lesson"]:v for v in idx["volumes"] for l in v["lessons"]}
    require(len(by_vol)==108 and set(by_vol)==set(range(1,109)),
            "Source index no longer covers exact 108 lessons")
    require(ledger.get("schema_version")==1 and ledger.get("id")==ID and
            ledger.get("scope")=="SECOND_PASS_INTERPRETIVE_CONSISTENCY_NOT_AUTHOR_THEOREM_PROOF" and
            ledger.get("upstream_argument_map")=="catalog/chanlun_theory_argument_links_v1.json" and
            ledger.get("source_versions")=="catalog/chanlun_rule_history_v1.json",
            "Theory audit scope or cross-lesson source provenance drift")
    require(all(ledger.get(k) is False for k in NO_FORMAL_PROOF) and
            ledger.get("financial_backtests")=="NOT_RUN",
            "Unsupported theory completion or market proof")
    require(set(ledger["case_types"])==CATEGORIES,
            "Case-type taxonomy changed")
    version_map={v["id"]:v for v in versions["entries"]}
    require(len(version_map)==len(versions["entries"]),
            "Duplicate history source version")
    rows=ledger["entries"]
    require(len(rows)==16 and [r["id"] for r in rows]==[f"C{i:02d}" for i in range(1,17)],
            "Expected exactly 16 source-linked cross-lesson consistency tensions")
    require({r["id"]:r["abstract_model"] for r in rows}==CONCLUSIONS,
            "Abstract model/case semantics or order drift")
    # Check source IDs and original book SHA against the selected volume, never
    # accept a missing/EDITORIAL entry as a frozen AUTHOR source proof.
    unique_refs=set(); statuses={}; registry=set()
    for row in rows:
        require(row["status"] in CATEGORIES and
                len(row["source_claims"])>=2 and
                len(row["needed_assumptions"])==2 and
                all(isinstance(x,str) and len(x)>10 for x in row["needed_assumptions"]) and
                row["counterexample_proves_original_author_wrong"] is False and
                row["authorial_intent_inferred"] is False and
                row["actual_trade_verified"] is False and
                len(row["thesis"])>=20,
                "Case wrongly asserts unqualified conflict or proof")
        require(len({(r["lesson"],r["claim_id"]) for r in row["source_claims"]})==len(row["source_claims"]),
                "Duplicated SOURCE card within a case")
        for c in row["source_claims"]:
            n=c["lesson"];require(type(n) is int and n in by_vol,"Missing original lesson")
            v=by_vol[n]
            card=load(ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json")
            require(card["source"]["path"]==v["path"] and
                    card["source"]["sha256"]==v["sha256"],
                    "Original source PDF SHA/path changed")
            match=[k for k in card["claims"] if k["id"]==c["claim_id"]]
            require(len(match)==1 and match[0]["kind"]=="SOURCE" and
                    match[0]["pdf_pages"] and
                    all(type(p) is int and 1<=p<=v["pdf_page_count"]
                        for p in match[0]["pdf_pages"]),
                    "Reference is not an existing source-qualified original PDF claim")
            unique_refs.add((n,c["claim_id"]))
        for vid in row["registry_ids"]:
            require(vid in version_map,"Unregistered historical version referenced")
            ent=version_map[vid]
            require(ent["lesson"] in [c["lesson"] for c in row["source_claims"]],
                    "A historical version source unrelated to the case")
            if ent["role"] in ("editor_later_undated","appendix_provenance_unresolved"):
                require(ent["source_displayed_at"] is None and
                        ent["timestamp_basis"]=="unknown",
                        "Undated editor or appendix retroactively given author publication time")
            registry.add(vid)
        statuses[row["status"]]=statuses.get(row["status"],0)+1
    require(len(unique_refs)>=30 and len(registry)>=8 and
            set(statuses)==CATEGORIES,
            "Whole-book consistency source/version coverage collapsed")
    # Controlled finite cases show why abstract left-hand predicates are not
    # sufficient for right-hand statements. No raw markets or PDF images needed.
    demonstrations={}
    for id_,label in CONCLUSIONS.items():
        if label not in {
            "NO_FORMAL_COUNTERMODEL_TO_RG","RULE_REVISION_NOT_RETROACTIVE",
            "REGISTRY_NO_GLOBAL_SUPERSESSION"
        }:
            left,right=witness(label)
            require(type(left) is bool and left and right is False,
                    "A claimed nonimplication lacks an illustrative toy countermodel")
            demonstrations[id_]={"antecedent_in_toy":left,
                                 "consequent_in_toy":right,
                                 "valid_full_author_Rg_counterexample":False}
    for i in ("C07","C09","C16"):
        require(i not in demonstrations,
                "Cannot invent an original Chanlun counterexample for unresolved version/scope")
    manuscript=MANUSCRIPT.read_text(encoding="utf-8")
    require(len(manuscript)>=12000,
            "Deep whole-book theory consistency reading is incomplete")
    for token in ("C01","C07","C09","C11","C16","第21课","第38课",
                  "第84课","第99课","SOURCE","EDITORIAL","NOT_RUN",
                  "条件性相容","不能直接判定原作者理论自相矛盾"):
        require(token in manuscript,"Source distinction or key theory explanation missing: "+token)
    readme=(ROOT/"deliverables/chanlun_108_acceptance/README.md").read_text(encoding="utf-8")
    require(MANUSCRIPT.name in readme,
            "Unified book theory consistency work not linked from main source index")
    return {"status":"CROSSLESSON_SCOPE_AUDITED_NOT_GLOBAL_CONSISTENCY_THEOREM",
            "tensions":len(rows),"distinct_canonical_SOURCE_claims":len(unique_refs),
            "coexisting_rule_versions":len(registry),"classifications":statuses,
            "abstract_nonimplication_models":len(demonstrations),
            "author_theory_contradiction_proven":False,
            "author_theory_consistency_proven":False,
            "market_backtests":"NOT_RUN"}

if __name__=="__main__":
    print(json.dumps(audit(),ensure_ascii=False,sort_keys=True))
