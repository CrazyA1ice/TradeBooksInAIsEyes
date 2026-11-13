"""v4.91: synthetic original-host / editorial-host misattribution and negative claims."""
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from tools.audit_chanlun_l70_comment_hosts_v491 import (
    CATALOG,audit,archived_host_entries,check_snapshot_dir,normalize_time
)

class Lesson70HostProvenanceV491(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=json.loads(CATALOG.read_text(encoding="utf-8"))

    def must_reject(self, mutate):
        x=deepcopy(self.spec)
        mutate(x)
        with self.assertRaises(ValueError):
            audit(x)

    def test_catalog(self):
        self.assertEqual(audit(self.spec)["verified_cross_article_receipts"],2)

    def test_before_lesson_publication_cannot_be_lesson_reply(self):
        self.assertLess(self.spec["actual_reply_hosts"][0]["author_at"],
                        self.spec["lesson70"]["published_at"])
        self.assertFalse(self.spec["actual_reply_hosts"][0]["may_belong_to_l70_original_comment_host"])

    def test_upstream_zero_not_original_sina_zero(self):
        self.assertEqual(self.spec["lesson70"]["baseline"]["uid_reply_count"],0)
        self.assertFalse(self.spec["false_claim_guards"]["lesson70_original_total_reply_count_proven_zero"])

    def test_l70_archive_without_real_host_reply_tags(self):
        self.assertEqual(archived_host_entries(
            '<style>.divReplyIsHostTrue .author{color:red}</style>'
            '<script>$(".divReplyIsHostTrue")</script><div id="divReply"></div>'),[])

    def test_false_html_class_name_not_accepted(self):
        sample='<div class="divReplyIsHostFalse"><fieldset><span class="author">缠中说禅</span><span class="pubtime">2007/8/16 15:50:48</span></fieldset></div>'
        self.assertEqual(archived_host_entries(sample),[])

    def test_author_identity_is_text_not_2007_authentication(self):
        self.must_reject(lambda x:x["false_claim_guards"].update(original_2007_sina_comment_bytes_authenticated=True))

    def test_cannot_infer_all_editorial_replies_wrong(self):
        self.must_reject(lambda x:x["false_claim_guards"].update(all_15_transcribed_author_blocks_proven_distinct_original_hosts=True))

    def test_cannot_infer_original_70_has_zero_comments(self):
        self.must_reject(lambda x:x["false_claim_guards"].update(lesson70_original_total_reply_count_proven_zero=True))

    def test_cannot_promote_kaixiang_exact_reply(self):
        self.must_reject(lambda x:x["false_claim_guards"].update(kaixiang_A087_identified_second_method=True))

    def test_cannot_claim_laohu(self):
        self.must_reject(lambda x:x["false_claim_guards"].update(laohu_full_document_obtained=True))

    def test_cannot_claim_market_backtest(self):
        self.must_reject(lambda x:x["false_claim_guards"].update(market_real_data_backtest_run=True))

    def test_wrong_edited_lesson_blob(self):
        self.must_reject(lambda x:x["lesson70"]["editor_compilation"].update(git_blob_sha="0"*40))

    def test_wrong_l70_true_host_reply_count(self):
        self.must_reject(lambda x:x["lesson70"]["archival_raw"].update(exact_host_reply_div_count=2))

    def test_aug13_parent_must_be_another_article(self):
        self.must_reject(lambda x:x["actual_reply_hosts"][0].update(parent_article_title="教你炒股票70：一个教科书式走势的示范分析"))

    def test_aug16_parent_must_be_another_article(self):
        self.must_reject(lambda x:x["actual_reply_hosts"][1].update(parent_article_title="教你炒股票70：一个教科书式走势的示范分析"))

    def test_aug13_bad_question_time(self):
        self.must_reject(lambda x:x["actual_reply_hosts"][0].update(question_at="2007-08-15 21:40:22"))

    def test_aug16_wrong_host_blob(self):
        self.must_reject(lambda x:x["actual_reply_hosts"][1]["raw"].update(git_blob_sha="a"*40))

    def test_cannot_merge_transplanted_as_original_l70(self):
        self.must_reject(lambda x:x["archive_counterexample"].update(do_not_merge_transplanted_replies_into_l70_same_host_count=False))

    def test_lesson0_conflicting_prior_metadata(self):
        self.must_reject(lambda x:x["lesson70"]["baseline"].update(uid_reply_count=15))

    def test_time_normalization(self):
        self.assertEqual(normalize_time("2007/8/13 21:56:16"),"2007-08-13 21:56:16")

    @staticmethod
    def raw(title,posted,reply=None,author="缠中说禅",questioner=None,q_at=None):
        q=""
        if reply:
            q=('<div class="divReplyIsHostTrue" style="margin:5px"><fieldset>'
               '<div><span class="author">'+author+'</span><span class="pubtime">'
               +reply.replace("-","/")+'</span></div><div>[匿名] '
               +(questioner or "新浪网友")+' '+(q_at or "2007-08-16 15:45:17")
               +' == 正确回复</div></fieldset></div>')
        return '<html><title>'+title+'</title><span class="pubtime">'+posted.replace("-","/")+'</span><style>.divReplyIsHostTrue .author{color:red}</style>'+q+'</html>'

    def write_fixture(self,d,wrong_l70=False,wrong_host=False):
        root=Path(d)
        lesson=self.spec["lesson70"]
        (root/"lesson70.html").write_text(self.raw(lesson["article_title"],lesson["published_at"],
                            reply="2007-08-16 15:50:48" if wrong_l70 else None),encoding="utf-8")
        for rid,filename in [("AUG13_215616","aug13"),("AUG16_155048","aug16")]:
            e=next(x for x in self.spec["actual_reply_hosts"] if x["id"]==rid)
            (root/(filename+".html")).write_text(
                self.raw(e["parent_article_title"] if not (wrong_host and filename=="aug16") else lesson["article_title"],
                         e["parent_published_at"],e["author_at"],questioner=e["questioner"],q_at=e["question_at"]),
                encoding="utf-8")
        (root/"editorial70.md").write_text("教你炒股票70\n2007-08-13 21:56:16\n2007-08-16 15:50:48",encoding="utf-8")

    def test_valid_synthetic_independent_host_proofs(self):
        with tempfile.TemporaryDirectory() as d:
            self.write_fixture(d)
            self.assertEqual(len(check_snapshot_dir(self.spec,d)["checked_cases"]),2)

    def test_reject_migrated_host_block_inserted_into_l70_raw(self):
        with tempfile.TemporaryDirectory() as d:
            self.write_fixture(d,wrong_l70=True)
            with self.assertRaises(ValueError):
                check_snapshot_dir(self.spec,d)

    def test_reject_wrong_original_article_host(self):
        with tempfile.TemporaryDirectory() as d:
            self.write_fixture(d,wrong_host=True)
            with self.assertRaises(ValueError):
                check_snapshot_dir(self.spec,d)

    def test_reject_missing_editorial_quote_without_inventing_migration(self):
        with tempfile.TemporaryDirectory() as d:
            self.write_fixture(d)
            Path(d,"editorial70.md").write_text("教你炒股票70\n",encoding="utf-8")
            with self.assertRaises(ValueError):
                check_snapshot_dir(self.spec,d)

    def test_reject_guest_as_author_under_original_host(self):
        with tempfile.TemporaryDirectory() as d:
            self.write_fixture(d)
            fn=Path(d,"aug16.html")
            fn.write_text(fn.read_text(encoding="utf-8").replace(
                '<span class="author">缠中说禅</span>','<span class="author">新浪网友</span>'),encoding="utf-8")
            with self.assertRaises(ValueError):
                check_snapshot_dir(self.spec,d)

    def test_reject_wrong_original_reply_questioner(self):
        with tempfile.TemporaryDirectory() as d:
            self.write_fixture(d)
            fn=Path(d,"aug13.html")
            fn.write_text(fn.read_text(encoding="utf-8").replace("深潜江湖","另一个人"),encoding="utf-8")
            with self.assertRaises(ValueError):
                check_snapshot_dir(self.spec,d)

if __name__=="__main__":
    unittest.main()
