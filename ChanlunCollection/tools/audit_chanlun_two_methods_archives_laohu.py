"""Audit author reply provenance, two pure views, author-preferred hybrid, Laohu filename."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/"catalog/chanlun_two_methods_archives_laohu_v438.json"
REPORT=ROOT/"deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_AUTHOR_REPLY_TWO_METHODS_AND_LAOHU_V438.md"
def audit(s,r,root=ROOT):
 def req(x,why):
  if not x:raise ValueError("TWO_METHODS_ARCHIVES_REJECTED: "+why)
 req(s.get("id")=="CHANLUN_TWO_METHODS_REPLY_TRIANGULATION_AND_LAOHU_FILENAME_V438" and s.get("version")=="4.38.0","identity")
 p=s["provenance"]
 req(not p["original_expert_post_recovered"] and p["user_supplied_expert_passage_present"] and
     not p["original_sina_reply_bytes_authenticated"] and not p["laohu_edition_file_bytes_obtained"] and
     not p["market_data_or_backtest_performed"],"source/experiment status")
 req(len(s["original_lessons"])==8,"source anchors")
 for a in s["original_lessons"]:
  f=root/("knowledge/evidence/chanlun_lesson%03d.json"%a["lesson"])
  card=json.loads(f.read_text(encoding="utf-8"))
  matches=[c for c in card["claims"] if c["id"]==a["id"] and c["kind"]=="SOURCE"]
  req(len(matches)==1 and set(a["pages"]).issubset(set(matches[0]["pdf_pages"])),"author original SOURCE and page")
 ids={x["id"] for x in s["author_replies_archive"]}
 req(ids=={"R1","R2","R3","R4"},"four archive reply objects")
 req(len(s["author_replies_archive"])==4 and
     all(x["source_status"]=="ARCHIVED_AUTHOR_ATTRIBUTED_NOT_SINA_ORIGINAL" and
     x["locator"]=="https://chzhshch.blog/stocks/confucius55/" for x in s["author_replies_archive"]),
     "archived comments cannot become sina original")
 cross=s["third_party_crosscheck"]
 req(cross["repo"]=="stockServ/chzhshch-108-plus" and
     cross["role"]=="THIRD_PARTY_REPOST_NOT_AUTHOR_ORIGINAL" and
     cross["independent_provenance_lineage_proved"] is False and
     cross["anonymous_commenters_can_include_impersonations"] is True,"third-party role")
 req(len(cross["files"])==3 and all(len(x["git_blob_sha"])==40 for x in cross["files"]),"cross-check blob inventory")
 laohu=s["laohu_edition"]
 req(laohu["attested_title"]=="108课老虎整理版" and
     laohu["identity_status"]=="FILENAME_ATTESTED_IN_TWO_CATALOGUES_CONTENT_NOT_VERIFIED" and
     not laohu["document_bytes_available"] and not laohu["comment_completeness_compared"] and
     not laohu["editorial_interpolation_compared"] and laohu["do_not_import_unlicensed_pdf"],
     "Laohu is a filename attestation only")
 v={x["id"]:x for x in s["three_distinct_judgments"]}
 req(set(v)=={"M1","M2","M3"},"different methods separated")
 req(v["M1"]["ranking"]=="NO_STRICT_WINNER_DEMONSTRATED","cannot falsely rank pure views")
 req(v["M2"]["ranking"]=="AUTHOR_EXPLICITLY_PREFERS_HYBRID_OVER_PURELY_SINGLE_VIEW","actual stronger source")
 req(v["M3"]["ranking"]=="AUTHOR_CALLS_APPROXIMATION_CONVENIENT_NOT_GLOBAL_WINNER","shortcut vs theory")
 req({"ORIGINAL_AUTHOR_SINA_COMMENT_BYTES","EXPERT_IDENTITY_AND_ORIGINAL_POST",
      "LAOHU_PDF_AND_DOCX_BYTES","EXPERT_WHICH_SECOND_METHOD_UNDETERMINED",
      "F01_OPEN","OB38_OPEN","OB99_OPEN","NOT_RUN_MARKET"}.issubset(set(s["unresolved"])),"open blockers")
 for phrase in ("16:10:43","16:38:56","2958","2858","第38课","混合","老虎版","NOT_RUN"):
  req(phrase in r,"reader-facing evidence "+phrase)
 return {"status":"ARCHIVE_SOURCE_TRIANGULATION_SCOPED_NOT_ORIGINAL_AUTHENTICATION",
         "author_lesson_anchors":8,"archived_author_attributed_replies":4,
         "third_party_git_blob_pins":3,"laohu_file_name_verified_in_catalogues":True,
         "original_sina_comment_verified":False}
if __name__=="__main__":
 print(json.dumps(audit(json.loads(SPEC.read_text(encoding="utf-8")),
 REPORT.read_text(encoding="utf-8")),ensure_ascii=False))
