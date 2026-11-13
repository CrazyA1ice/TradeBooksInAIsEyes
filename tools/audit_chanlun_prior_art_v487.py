"""Cross-version provenance audit for the 2007-07-20 original Sina source."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "catalog/chanlun_source_novelty_v487.json"

def audit(data, root=ROOT):
    def check(condition, why):
        if not condition:
            raise ValueError("PRIOR_ART_V487: " + why)
    check(data.get("schema_version")==1 and data.get("version")=="4.87.0", "schema")
    check(data.get("claim_id")=="CHANLUN-20070720-PRIOR-ART", "id")
    check(data.get("prior_catalog")=="catalog/chanlun_20070720_dual_a0_original_post_v441.json", "old catalog path")
    old=json.loads((root/data["prior_catalog"]).read_text(encoding="utf-8"))
    posts={p["id"]:p for p in old["primary_posts"]}
    check(old["version"]==data["first_registered_in"]=="4.41.0", "prior version")
    check(posts["JUL20"]["url"]==data["canonical_url"]=="https://blog.sina.com.cn/s/blog_486e105c01000bs4.html", "URL")
    check(posts["JUL20"]["date"]==data["published_at"]=="2007-07-20 08:26:20" and posts["JUL20"]["role"]=="AUTHOR_MAIN_POST", "date/role")
    t=old["type_contract"]
    check(t["strict_a0_source"]=="INDIVIDUAL_TRANSACTION_EXECUTIONS" and t["practical_a0_source"]=="FRACTAL_PEN_SEGMENT_CONSTRUCTION", "historical dual a0")
    check(t["universal_equal_center_outputs_from_same_recurrence"] is False and t["a_segment_finish_proves_movement_finish"] is False, "old caveats")
    check(data.get("reused_for_new_hypothesis_analysis_in")=="4.86.0" and data.get("new_analytic_contribution")=="A087_B1a_B2_B3_H7_REINTERPRETATION", "new contribution")
    for key in ("first_discovered_in_v486","original_historical_html_bytes_verified","kaixiang_exact_reply_identified","market_experiment_run"):
        check(data.get(key) is False, "unsupported promotion: "+key)
    check(set(data.get("open_gates",[]))=={"F01","OB38","OB99","A087_EXACT_REPLY","A016_THIRD_LAYER","E1_E4_MARKET_NOT_RUN"}, "open gates")
    for key, terms in {
        "prior_report":("v4.41","08:26:20","a0"),
        "reused_report":("v4.87","v4.41","B1a"),
        "correction_report":("v4.41","v4.86","B1a","B2","B3","OPEN"),
    }.items():
        path=data.get(key,"")
        check(path and not path.startswith("/") and ".." not in path.split("/"), "path traversal")
        body=(root/path).read_text(encoding="utf-8")
        check(all(t in body for t in terms), "report continuity: "+key)
    return {"status":"PRIOR_ART_REUSE_VERIFIED", "previous_registration":"4.41.0", "reinterpretation":"4.86.0","workflow":"4.87.0","reply":"OPEN","market":"NOT_RUN"}

if __name__=="__main__":
    print(json.dumps(audit(json.loads(SPEC.read_text(encoding="utf-8"))),sort_keys=True))
