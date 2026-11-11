"""Check provenance and quantifier-scope separation (not an author theory proof)."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/"catalog/chanlun_expert_completion_quantifiers_v1.json"
REPORT=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_COMPLETION_QUANTIFIERS_V436.md"

def audit(spec, report):
    def check(ok, msg):
        if not ok: raise ValueError("QUANTIFIER_AUDIT_FAILED: "+msg)
    check(spec.get("id")=="CHANLUN-EXPERT-COMPLETION-QUANTIFIERS-V436","identity")
    p=spec["provenance"]
    check(not p["expert_verbatim_recovered"] and not p["expert_original_post_recovered"]
          and p["expert_issues_paraphrased"],"source attribution")
    check(p["author_source_not_theorem_proof"] and not p["market_backtest_performed"],"research limit")
    by_id={c["id"]:c for c in spec["claims"]}
    check(len(spec["claims"])==7 and set(by_id)=={"EV","UB","IN","FU","PI","ON","TR"},
          "seven distinct propositions")
    check(by_id["IN"]["strength"]=="HYPOTHETICAL_DOMAIN_NOT_AUTHENTICATED",
          "literal infinite history must not be asserted")
    check(by_id["FU"]["strength"]=="AUTHOR_ASSERTION_PROOF_OPEN","unique parser is open")
    check(by_id["TR"]["strength"]=="NOT_RUN","no backtest")
    check(spec["status"]=="LOGICAL_SCOPING_ONLY_NOT_A_FORMAL_AUTHOR_PROOF","proof limit")
    expected={(17,"CL017-S01"),(18,"CL018-S07"),(38,"CL38-SOURCE-1"),
              (38,"CL38-SOURCE-2"),(99,"CL99-SOURCE-1"),
              (102,"CL102-SOURCE-1"),(102,"CL102-SOURCE-3")}
    check(len(spec["anchors"])==7 and
          {(x["lesson"],x["id"]) for x in spec["anchors"]}==expected,"anchor inventory")
    for a in spec["anchors"]:
        path=ROOT/("knowledge/evidence/chanlun_lesson%03d.json"%a["lesson"])
        card=json.loads(path.read_text(encoding="utf-8"))
        found=[c for c in card["claims"] if c["id"]==a["id"] and c["kind"]=="SOURCE"]
        check(len(found)==1 and set(a["pages"]).issubset(found[0]["pdf_pages"]),
              "original author claim id or physical page")
    check({x["id"] for x in spec["toy_models"]}==
          {"FINITE_UNBOUNDED","INFINITE_PATH_IF_ADMITTED","DISTINCT_FIXED_POLICIES","COMMON_PREFIX"},
          "four logical countermodels")
    for keyword in ("EV与UB可以同时", "FU不能推出PI","不能推出ON","原帖",
                    "F01 / OB38 / OB99 = OPEN","NOT_RUN"):
        check(keyword in report,"required qualification: "+keyword)
    check(set(spec["limits"])>=
          {"EXPERT_ORIGINAL_UNAVAILABLE","INFINITE_SEMANTIC_DOMAIN_UNRESOLVED",
           "F01_OPEN","OB38_OPEN","OB99_OPEN","REAL_MARKET_NOT_RUN"},"open blockers")
    return {"status":"SCOPED_SEVEN_CLAIMS_SEVEN_SOURCE_ANCHORS_NOT_AUTHOR_PROOF",
            "claims":7,"sources":7,"toy_models":4}

def example_completed(n):
    if type(n) is not int or n<1: raise ValueError("positive integer required")
    return "A"*n+"E"

def toy_policy(sequence,policy):
    if sequence!="ABC" or policy not in ("R1","R2"): raise ValueError("toy domain")
    return ("A","BC") if policy=="R1" else ("AB","C")

if __name__=="__main__":
    print(json.dumps(audit(json.loads(SPEC.read_text(encoding="utf-8")),
                           REPORT.read_text(encoding="utf-8")),ensure_ascii=False))
