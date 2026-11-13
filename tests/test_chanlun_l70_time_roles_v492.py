"""v4.92: source-host vs quoted-question-time, 16 entries, synthetic HTML only."""
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from tools.audit_chanlun_l70_time_roles_v492 import (
    CATALOG, AUG13_AUTHOR_AT, AUG16_AUTHOR_ACTUAL_AT,
    MISTAKEN_EDITORIAL_AT, OLD_AUTHOR_AT,
    audit, actual_host_blocks, git_blob_sha, parse_editorial_labels,
    verify_snapshot_dir
)


class EditorialL70TimeRolesV492(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CATALOG.read_text(encoding="utf-8"))

    def reject(self, mutate):
        changed = deepcopy(self.data)
        mutate(changed)
        with self.assertRaises(ValueError):
            audit(changed)

    def test_all_16_time_roles(self):
        outcome = audit(self.data)
        self.assertEqual(outcome["editorial_blocks"], 16)
        self.assertEqual(outcome["direct_other_host_time_matches"], 15)

    def test_all_fifteen_august_replies_outside_l70(self):
        records = self.data["author_attributed_entries"]
        self.assertEqual(sum(x["original_post_id"] == "AUG16" for x in records), 15)
        self.assertEqual(sum(x["original_post_id"] == "L70" for x in records), 0)

    def test_july_time_is_a_question_not_author_reply(self):
        row = self.data["author_attributed_entries"][3]
        self.assertEqual(row["editorial_author_label_at"], MISTAKEN_EDITORIAL_AT)
        self.assertEqual(row["actual_author_reply_at"], AUG16_AUTHOR_ACTUAL_AT)
        self.assertFalse(row["time_label_is_author_reply"])

    def test_cannot_claim_editorial_question_is_author_timestamp(self):
        self.reject(lambda x: x["author_attributed_entries"][3].update(time_label_is_author_reply=True))

    def test_cannot_keep_july_question_as_august_answer(self):
        self.reject(lambda x: x["author_attributed_entries"][3].update(
            actual_author_reply_at=MISTAKEN_EDITORIAL_AT))

    def test_no_duplicate_author_dates_among_rebased_reply_blocks(self):
        rows = self.data["author_attributed_entries"]
        self.assertEqual(len({(x["original_post_id"], x["actual_author_reply_at"]) for x in rows}), 16)

    def test_cannot_change_original_july_author_answer(self):
        self.reject(lambda x: x["historical_question_time_disambiguation"].update(
            historical_original_author_reply_at=MISTAKEN_EDITORIAL_AT))

    def test_cannot_change_august_questioner(self):
        self.reject(lambda x: x["historical_question_time_disambiguation"].update(
            august_quote_questioner="新浪网友"))

    def test_cannot_make_nested_quote_from_l70(self):
        self.reject(lambda x: x["historical_question_time_disambiguation"].update(
            august_original_post="L70"))

    def test_edited_source_sha_locked(self):
        self.reject(lambda x: x["editorial_source"].update(git_blob_sha="0"*40))

    def test_july_source_sha_locked(self):
        self.reject(lambda x: x["original_post_archives"]["JUL31"].update(git_blob_sha="0"*40))

    def test_august_source_sha_locked(self):
        self.reject(lambda x: x["original_post_archives"]["AUG16"].update(git_blob_sha="0"*40))

    def test_lesson70_raw_zero_not_historical_zero_claim(self):
        self.assertEqual(self.data["original_post_archives"]["L70"]["archived_author_host_block_count"], 0)
        self.reject(lambda x: x["source_limits"].update(
            zero_l70_archive_host_blocks_not_proof_historical_zero=False))

    def test_cannot_assert_unobserved_independence_of_archives(self):
        self.reject(lambda x: x["source_limits"].update(
            copies_are_not_proven_independent_collection_chain=False))

    def test_cannot_assert_historical_original_sina_bytes(self):
        self.reject(lambda x: x["source_limits"].update(
            archived_html_is_not_verified_original_2007_sina_server_bytes=False))

    def test_cannot_assert_laohu_document(self):
        self.reject(lambda x: x["source_limits"].update(laohu_source_document_obtained=True))

    def test_cannot_assert_kaixiang_referent(self):
        self.reject(lambda x: x["source_limits"].update(
            kaixiang_A087_actual_second_center_definition_identified=True))

    def test_cannot_promote_feature_sequence_to_second_center_axiom(self):
        self.reject(lambda x: x["source_limits"].update(
            independent_B3_new_center_axiom_proven=True))

    def test_cannot_claim_market_experiment(self):
        self.reject(lambda x: x["source_limits"].update(market_E1_E4_experiments_run=True))

    def test_cannot_erase_prior_v491_discovery(self):
        self.reject(lambda x: x["prior_art"].update(
            v491_first_two_cross_host_examples_are_not_new_discoveries=False))

    def test_false_host_selector_from_css_not_counted(self):
        raw = '<style>.divReplyIsHostTrue .author {color:red}</style><script>"divReplyIsHostTrue"</script>'
        self.assertEqual(actual_host_blocks(raw), [])

    def test_unmarked_guest_not_counted(self):
        raw = '<div class="divReplyIsHostFalse"><fieldset><span class="author">缠中说禅</span><span class="pubtime">2007/8/16 15:58:06</span></fieldset></div>'
        self.assertEqual(actual_host_blocks(raw), [])

    def test_label_parser_distinguishes_inline_and_bold(self):
        s = ("教你炒股票70\n缠中说禅 " + AUG13_AUTHOR_AT + "\n"
             "**缠中说禅**：\n" + MISTAKEN_EDITORIAL_AT)
        self.assertEqual(parse_editorial_labels(s), [AUG13_AUTHOR_AT, MISTAKEN_EDITORIAL_AT])

    def test_git_blob_sha_uses_standard_blob_prefix(self):
        import hashlib
        raw = b"hello"
        self.assertEqual(git_blob_sha(raw), hashlib.sha1(b"blob 5\0hello").hexdigest())

    @staticmethod
    def make_html(title, published, dates, overrides=None):
        blocks=[]
        overrides=overrides or {}
        for date in dates:
            text=overrides.get(date, "网友提问 == 博主答复")
            blocks.append(
                '<div class="divReplyIsHostTrue"><fieldset>'
                '<span class="author">缠中说禅</span>'
                '<span class="pubtime">' + date.replace("-", "/") + '</span>'
                '<div>' + text + '</div></fieldset></div>')
        return '<html><head><title>' + title + '</title></head><body>' + (
            '<span class="pubtime">' + published.replace("-", "/") + '</span>'
            '<style>.divReplyIsHostTrue .author{color:red}</style>') + "\n".join(blocks) + '</body></html>'

    def build_fixtures(self, directory):
        originals=self.data["original_post_archives"]
        rows=self.data["author_attributed_entries"]
        aug16=[x["actual_author_reply_at"] for x in rows if x["original_post_id"]=="AUG16"]
        aug13=[AUG13_AUTHOR_AT]+[f"2007-08-13 23:00:{i:02d}" for i in range(1,6)]
        jul31=[OLD_AUTHOR_AT]+[f"2007-07-31 17:00:{i:02d}" for i in range(1,19)]
        aug16=aug16 + [f"2007-08-16 17:10:{i:02d}" for i in range(1,6)]
        cases={"L70":("lesson070.html",[],{}),
               "AUG13":("aug13.html",aug13,{}),
               "JUL31":("jul31.html",jul31,{
                  OLD_AUTHOR_AT:"[匿名] 新浪网友 " + MISTAKEN_EDITORIAL_AT + " == 旧回复"}),
               "AUG16":("aug16.html",aug16,{
                  AUG16_AUTHOR_ACTUAL_AT:"[匿名] 蓝羽 2007-08-16 15:48:44 引用：" + MISTAKEN_EDITORIAL_AT + " == 新回复"})}
        for case,(file,dates,overrides) in cases.items():
            meta=originals[case]
            Path(directory,file).write_text(
                self.make_html(meta["article_title"],meta["article_published_at"],dates,overrides),
                encoding="utf-8")
        editor="教你炒股票70\n" + "缠中说禅 " + AUG13_AUTHOR_AT + "\n"
        editor += "".join("**缠中说禅**：\n" + row["editorial_author_label_at"] + "\n"
                          for row in rows[1:])
        Path(directory,"editorial070.md").write_text(editor,encoding="utf-8")

    def test_synthetic_five_archives_pass_without_byte_verification(self):
        with tempfile.TemporaryDirectory() as d:
            self.build_fixtures(d)
            r=verify_snapshot_dir(self.data,d)
            self.assertEqual(r["blocks"],16)
            self.assertEqual(r["actual_author_host_distribution"]["AUG16"],15)
            self.assertFalse(r["verify_exact_git_bytes"])

    def test_synthetic_blobs_must_fail_exact_git_verification(self):
        with tempfile.TemporaryDirectory() as d:
            self.build_fixtures(d)
            with self.assertRaises(ValueError):
                verify_snapshot_dir(self.data,d,verify_blobs=True)

    def test_reject_false_jul31_author_reply_time(self):
        with tempfile.TemporaryDirectory() as d:
            self.build_fixtures(d)
            file=Path(d,"jul31.html")
            file.write_text(file.read_text(encoding="utf-8").replace(
                OLD_AUTHOR_AT.replace("-","/"),MISTAKEN_EDITORIAL_AT.replace("-","/")),
                encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_snapshot_dir(self.data,d)

    def test_reject_aug16_quoted_question_time_rewritten(self):
        with tempfile.TemporaryDirectory() as d:
            self.build_fixtures(d)
            file=Path(d,"aug16.html")
            file.write_text(file.read_text(encoding="utf-8").replace(
                "引用："+MISTAKEN_EDITORIAL_AT,"引用：2007-07-31 16:11:02"),
                encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_snapshot_dir(self.data,d)

    def test_reject_replaced_aug16_author_time_with_july_question(self):
        with tempfile.TemporaryDirectory() as d:
            self.build_fixtures(d)
            file=Path(d,"aug16.html")
            file.write_text(file.read_text(encoding="utf-8").replace(
                AUG16_AUTHOR_ACTUAL_AT.replace("-","/"),
                MISTAKEN_EDITORIAL_AT.replace("-","/")),
                encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_snapshot_dir(self.data,d)

    def test_reject_malformed_editorial_author_label_order(self):
        with tempfile.TemporaryDirectory() as d:
            self.build_fixtures(d)
            file=Path(d,"editorial070.md")
            file.write_text(file.read_text(encoding="utf-8").replace(
                "2007-08-16 15:51:35","2007-08-16 15:55:35"),
                encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_snapshot_dir(self.data,d)

    def test_reject_original_l70_fake_author_post(self):
        with tempfile.TemporaryDirectory() as d:
            self.build_fixtures(d)
            file=Path(d,"lesson070.html")
            file.write_text(file.read_text(encoding="utf-8").replace(
                "</body></html>",
                '<div class="divReplyIsHostTrue"><fieldset><span class="author">缠中说禅</span>'
                '<span class="pubtime">2007/8/15 23:41:35</span></fieldset></div></body></html>'),
                encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_snapshot_dir(self.data,d)

    def test_reject_august_user_not_lanyu(self):
        with tempfile.TemporaryDirectory() as d:
            self.build_fixtures(d)
            file=Path(d,"aug16.html")
            file.write_text(file.read_text(encoding="utf-8").replace("蓝羽","另一用户"),
                            encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_snapshot_dir(self.data,d)

if __name__=="__main__":
    unittest.main()
