"""Audit expert-attributed passage against dated author lesson evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/"catalog/chanlun_expert_history_two_methods_v1.json"
REPORT=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_HISTORICAL_LEVEL_SHIFT_AND_TWO_METHODS_V437.md"
def audit(s,r):
 def req(v,msg):
  if not v:raise ValueError("EXPERT_HISTORY_AUDIT_FAILED: "+msg)
 req(s["id"]=="CHANLUN-EXPERT-HISTORY-TWO-METHODS-V437","identity")
 p=s["provenance"]
 req(p["user_supplied_new_expert_attributed_passage"] and not p["expert_original_public_post_verified"] and p["prior_six_claims_remain_paraphrases"],"expert attribution")
 req(not p["original_sina_comment_bytes_verified"] and not p["laohu_version_verified"] and not p["market_backtest_run"] and not p["full_new_108_lesson_verbatim_reread"],"unverified provenance")
 a={x["id"]:x for x in s["expert_assertions"]}
 req(set(a)=={"H%02d"%i for i in range(1,10)} and len(s["expert_assertions"])==9,"nine propositions")
 req(a["H01"]["finding"]=="FALSE_AS_ABSOLUTE_BECAUSE_L17_AND_L33","pre35 false absolute")
 req(a["H02"]["finding"]=="VALID_L15_L16_FALSE_FOR_L17","pre18 exception")
 req(a["H05"]["finding"]=="TRUE_FOR_CHART_WINDOW_NOT_INSIDE_SINGLE_STRICT_5MIN_TYPE","chart vs structure")
 req(a["H06"]["finding"]=="UNRESOLVED_WHICH_OF_MULTIPLE_DISTINCT_PAIRS","two methods uncertain")
 req(a["H07"]["finding"]=="NOT_VERIFIED_AS_AUTHOR_UNIVERSAL_RANKING","unverified method ranking")
 req(a["H08"]["finding"]=="UNVERIFIED_EDITION_NOT_IDENTIFIED","laohu identification")
 for a in s["source_anchors"]:
  p=ROOT/("knowledge/evidence/chanlun_lesson%03d.json"%a["lesson"])
  matches=[c for c in json.loads(p.read_text(encoding="utf-8"))["claims"] if c["id"]==a["id"] and c["kind"]=="SOURCE"]
  req(len(matches)==1 and set(a["pages"]).issubset(matches[0]["pdf_pages"]),"anchor/page")
 req(len(s["source_anchors"])==22,"source count")
 req(len(s["two_way_distinctions"])==4 and all(not x["is_two_independent_center_axioms"] for x in s["two_way_distinctions"]),"four distinct senses")
 req(len(s["author_comments_archive"])==3 and all("NOT_SINA_ORIGINAL" in x["kind"] for x in s["author_comments_archive"]),"comment source status")
 req(s["read_scope"]["existing_chapter_research"]==108 and not s["read_scope"]["new_full_verbatim_108_recheck"],"reading coverage")
 req(set(s["open"])>={"F01_OPEN","OB38_OPEN","OB99_OPEN","LAOHU_VERSION_NOT_IDENTIFIED","SECOND_METHOD_IDENTIFICATION_OPEN","MARKET_NOT_RUN"},"open blockers")
 for v in ("第17课","第33课","第35课","第38课","第72课","2007-03-08","老虎版","NOT_RUN"):
  req(v in r,"report omitted "+v)
 return {"status":"SOURCE_SCOPED_INTERPRETIVE_AUDIT_PASS","claims":9,"source_anchors":22,"comment_archives":3,"pairs":4}
if __name__=="__main__":
 print(json.dumps(audit(json.loads(SPEC.read_text(encoding="utf-8")),REPORT.read_text(encoding="utf-8")),ensure_ascii=False))
