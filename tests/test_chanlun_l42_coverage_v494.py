"""v4.94: audited lesson42 delta: host markup != UID reply != readable theory."""
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from tools.audit_chanlun_l42_coverage_v494 import (
    CATALOG, EXTRA, H02, RAW_BLOB, audit,
    archive_author_host_blocks, check_raw_html, git_blob_sha, normalize_time
)


class L42SourceSpecificCoverageV494(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))

    def rejected(self, mutation):
        copy = deepcopy(self.catalog)
        mutation(copy)
        with self.assertRaises(ValueError):
            audit(copy)

    def test_complete_frozen_crosswalk_30_vs_29(self):
        result = audit(self.catalog)
        self.assertEqual(result["host_marked"], 30)
        self.assertEqual(result["strict_UID"], 29)
        self.assertEqual(result["raw_only"], ["2007-04-07 14:52:10"])

    def test_exact_29_times_in_common(self):
        c = self.catalog["count_reconciliation"]
        self.assertEqual(
            set(c["raw_host_reply_time_list"]) - set(c["strict_uid_reply_time_list"]),
            {"2007-04-07 14:52:10"})
        self.assertEqual(
            set(c["strict_uid_reply_time_list"]) - set(c["raw_host_reply_time_list"]), set())

    def test_question_marks_are_not_a_new_center_axiom(self):
        receipt=self.catalog["raw_only_receipt"]
        self.assertEqual(receipt["literal_body"], "??????????")
        self.assertFalse(receipt["counts_as_readable_center_definition"])

    def test_no_inference_of_10_extra_full_site_replies(self):
        self.rejected(lambda x: x["count_reconciliation"].update(
            sitewide_delta_963_minus_953_not_comparable_as_missing_reply_count=False))

    def test_cannot_claim_the_other_nine_site_extra_replies_are_missing(self):
        self.rejected(lambda x: x["count_reconciliation"].update(
            cannot_infer_nine_other_missing_replies_from_sitewide_totals=False))

    def test_cannot_claim_ecszc_source_bytes_downloaded(self):
        self.rejected(lambda x: x["sites"][2].update(independent_source_bytes_acquired=True))

    def test_cannot_claim_source_independence(self):
        self.rejected(lambda x: x["evidence_caveats"].update(
            no_independence_of_public_mirrors_established=False))

    def test_cannot_claim_historical_sina_original_bytes(self):
        self.rejected(lambda x: x["sites"][1].update(
            original_sina_server_bytes_authenticated=True))

    def test_cannot_claim_laohu_pdf(self):
        self.rejected(lambda x: x["evidence_caveats"].update(
            no_laohu_edition_pdf_docx_acquired=False))

    def test_cannot_promote_garbled_marker_to_readable_formula(self):
        self.rejected(lambda x: x["raw_only_receipt"].update(
            counts_as_readable_center_definition=True))

    def test_cannot_deny_raw_marker_for_question_marks(self):
        self.rejected(lambda x: x["raw_only_receipt"].update(
            counts_as_archived_host_marked_reply=False))

    def test_cannot_guess_reason_for_question_mark_text(self):
        self.rejected(lambda x: x["raw_only_receipt"].update(
            reason_for_question_marks_not_known=False))

    def test_relevant_author_reply_was_already_in_old_baseline(self):
        r=self.catalog["relevant_original_author_reply"]
        self.assertEqual(r["date"], "2007-04-04 16:31:43")
        self.assertFalse(r["newly_discovered_reply"])

    def test_relevant_reply_does_not_define_second_center_axiom(self):
        self.rejected(lambda x: x["relevant_original_author_reply"].update(
            proves_two_independent_center_axioms=True))

    def test_relevant_reply_cannot_directly_identify_a087(self):
        self.rejected(lambda x: x["relevant_original_author_reply"].update(
            identifies_A087_second_center_definition=True))

    def test_parent_article_title_cannot_be_l70(self):
        self.rejected(lambda x: x["relevant_original_author_reply"].update(
            parent_article_title="教你炒股票70：一个教科书式走势的示范分析"))

    def test_raw_fixed_blob_identity(self):
        self.rejected(lambda x: x["sites"][1].update(blob_sha="a"*40))

    def test_stockserv_fixed_blob_identity(self):
        self.rejected(lambda x: x["sites"][0].update(blob_sha="a"*40))

    def test_external_963_is_reported_not_a_new_local_count(self):
        self.assertEqual(self.catalog["sites"][2]["reported_sitewide_count"], 963)
        self.assertTrue(self.catalog["evidence_caveats"]["no_full_site_963_record_by_record_download_or_verification"])

    def test_all_8_external_table_counts_fixed(self):
        self.assertEqual(len(self.catalog["site_index_top_lesson_counts"]), 8)
        self.rejected(lambda x: x["site_index_top_lesson_counts"][6].update(
            site_reported=29))

    def test_time_list_cannot_gain_new_missed_reply(self):
        self.rejected(lambda x: x["count_reconciliation"]["raw_host_reply_time_list"].append(
            "2007-04-08 08:11:11"))

    def test_time_list_cannot_falsify_single_raw_only_reply(self):
        self.rejected(lambda x: x["count_reconciliation"].update(
            raw_only_time_list=["2007-04-04 16:31:43"]))

    def test_no_dilution_of_A087_open_state(self):
        self.rejected(lambda x: x["state"].update(A087="CONFIRMED"))

    def test_css_or_js_cannot_count_as_real_host_markup(self):
        sample = '<style>.divReplyIsHostTrue .author{color:red}</style><script>"divReplyIsHostTrue"</script>'
        self.assertEqual(archive_author_host_blocks(sample), [])

    def test_false_host_marker_cannot_count(self):
        sample = '<div class="divReplyIsHostFalse"><fieldset><div><span class="author">缠中说禅</span><span class="pubtime">2007/4/7 14:52:10</span></div><div>??????????</div></fieldset></div>'
        self.assertEqual(archive_author_host_blocks(sample), [])

    def test_git_blob_standard_object_hash(self):
        import hashlib
        self.assertEqual(git_blob_sha(b"hello"),hashlib.sha1(b"blob 5\0hello").hexdigest())

    def test_timestamp_normalizer_formats_unpadded_month(self):
        self.assertEqual(normalize_time("2007/4/7 14:52:10"), "2007-04-07 14:52:10")

    @classmethod
    def sample_archive(cls, spec):
        rows=spec["count_reconciliation"]["raw_host_reply_time_list"]
        beginning=(
            '<html><head><title>教你炒股票42：有些人是不适合参与市场的</title></head>'
            '<body><style>.divReplyIsHostTrue .author{color:red}</style>'
            '<span class="pubtime">2007/4/4 15:31:30</span>')
        for at in rows:
            body = ('asdf 2007-04-04 15:55:25 不用一层一层'
                    ' == 趋势看背驰，盘整看第三类买卖点' if at==H02
                    else '??????????' if at==EXTRA else '别的问答')
            beginning+=(
                '<div class="divReplyIsHostTrue"><fieldset>'
                '<div><span class="author">缠中说禅</span>'
                '<span class="pubtime">' + at.replace('-04-', '/4/').replace("2007-04-07","2007/4/7") + '</span></div>'
                '<div>' + body + '</div></fieldset></div>')
        return beginning+'</body></html>'

    def sample_file(self, directory):
        path=Path(directory)/"lesson42.html"
        path.write_text(self.sample_archive(self.catalog),encoding="utf-8")
        return path

    def test_synthetic_complete_host_archive_passes_without_git_validation(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.sample_file(d)
            result=check_raw_html(self.catalog,p)
            self.assertEqual(result["raw_only_garbled"], EXTRA)
            self.assertFalse(result["exact_raw_git_blob"])

    def test_synthetic_source_must_not_pass_exact_git_sha_gate(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.sample_file(d)
            with self.assertRaises(ValueError):
                check_raw_html(self.catalog,p,verify_blob=True)

    def test_reject_wrong_original_article_title(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.sample_file(d)
            p.write_text(p.read_text().replace("教你炒股票42","教你炒股票41"),encoding="utf-8")
            with self.assertRaises(ValueError):
                check_raw_html(self.catalog,p)

    def test_reject_tampered_unreadable_source_content(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.sample_file(d)
            p.write_text(p.read_text().replace("??????????","确有新的第二套中枢公理"),encoding="utf-8")
            with self.assertRaises(ValueError):
                check_raw_html(self.catalog,p)

    def test_reject_missing_garbled_host_block(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.sample_file(d)
            p.write_text(p.read_text().replace("2007/4/7 14:52:10","2007/4/7 14:52:20"),encoding="utf-8")
            with self.assertRaises(ValueError):
                check_raw_html(self.catalog,p)

    def test_reject_guest_pretending_to_be_author(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.sample_file(d)
            p.write_text(p.read_text().replace(
                '<span class="author">缠中说禅</span>',
                '<span class="author">随便的旁观者</span>',1),encoding="utf-8")
            with self.assertRaises(ValueError):
                check_raw_html(self.catalog,p)

    def test_reject_unsupported_h02_reply_claim(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.sample_file(d)
            p.write_text(p.read_text().replace(
                '趋势看背驰，盘整看第三类买卖点','又一个中心的全新公理'),encoding="utf-8")
            with self.assertRaises(ValueError):
                check_raw_html(self.catalog,p)

    def test_missing_authorship_header_is_not_a_valid_recovered_marker(self):
        with self.assertRaises(ValueError):
            archive_author_host_blocks(
                '<div class="divReplyIsHostTrue"><fieldset>'
                '<div><span class="pubtime">2007/4/7 14:52:10</span></div>'
                '<div>??????????</div></fieldset></div>')


if __name__=="__main__":
    unittest.main()
