import json,unittest
from copy import deepcopy
from tools.audit_chanlun_two_methods_archives_laohu import SPEC,REPORT,audit
class SourceProvenanceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=json.loads(SPEC.read_text(encoding="utf-8"));cls.report=REPORT.read_text(encoding="utf-8")
 def reject(self,fn):
  d=deepcopy(self.source);fn(d)
  with self.assertRaises(ValueError):audit(d,self.report)
 def test_baseline_anchored_eight_originals(self):
  self.assertEqual(audit(self.source,self.report)["author_lesson_anchors"],8)
 def test_author_comment_is_repost(self):
  self.reject(lambda d:d["author_replies_archive"][1].update(source_status="ORIGINAL_SINA_VERIFIED"))
 def test_no_original_sina_byte_authentication(self):
  self.reject(lambda d:d["provenance"].update(original_sina_reply_bytes_authenticated=True))
 def test_no_public_original_expert_post(self):
  self.reject(lambda d:d["provenance"].update(original_expert_post_recovered=True))
 def test_author_hybrid_not_second_pure_winner(self):
  self.reject(lambda d:d["three_distinct_judgments"][0].update(ranking="SECOND_ALWAYS_BEST"))
 def test_hybrid_source_not_swapped_for_second(self):
  self.reject(lambda d:d["three_distinct_judgments"][1].update(ranking="PURE_SECOND_ALWAYS_BEST"))
 def test_shortcut_not_always_identical(self):
  self.reject(lambda d:d["three_distinct_judgments"][2].update(ranking="STRICT_APPROX_EQUIVALENT"))
 def test_wrong_source_page(self):
  self.reject(lambda d:d["original_lessons"][0].update(pages=[999]))
 def test_wrong_source_id(self):
  self.reject(lambda d:d["original_lessons"][2].update(id="INVENTED"))
 def test_third_party_alias_not_author_verified(self):
  self.reject(lambda d:d["third_party_crosscheck"].update(anonymous_commenters_can_include_impersonations=False))
 def test_blob_identity_must_exist(self):
  self.reject(lambda d:d["third_party_crosscheck"]["files"][1].update(git_blob_sha="unknown"))
 def test_laohu_file_bytes_not_owned(self):
  self.reject(lambda d:d["laohu_edition"].update(document_bytes_available=True))
 def test_laohu_completeness_not_compared(self):
  self.reject(lambda d:d["laohu_edition"].update(comment_completeness_compared=True))
 def test_unlicensed_pdf_not_auto_imported(self):
  self.reject(lambda d:d["laohu_edition"].update(do_not_import_unlicensed_pdf=False))
 def test_market_not_run(self):
  self.reject(lambda d:d["provenance"].update(market_data_or_backtest_performed=True))
 def test_ob38_still_open(self):
  self.reject(lambda d:d["unresolved"].remove("OB38_OPEN"))
if __name__=="__main__":unittest.main()
