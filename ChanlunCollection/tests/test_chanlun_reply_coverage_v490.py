"""v4.90: archive metadata, UID screening, synthetic edition intake and negative gates."""
import json
import tempfile
import unittest
import zipfile
from copy import deepcopy
from pathlib import Path
from tools.audit_chanlun_reply_coverage_v490 import (
    CATALOG, audit, compare_edition_text, dated_strings, extract_edition_text,
    git_blob_sha, parse_uid_comments, reverify_source_dir, source_facts
)


class UidReplyBaselineV490(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))

    def reject(self, mutate):
        bad = deepcopy(self.catalog)
        mutate(bad)
        with self.assertRaises(ValueError):
            audit(bad)

    def test_baseline(self):
        receipt = audit(self.catalog)
        self.assertEqual(receipt["matching_author_uid_comments"], 953)
        self.assertEqual(receipt["lessons_with_matching_author_uid"], 58)

    def test_all_lesson_sources_present_even_when_no_replies_found(self):
        self.assertEqual(len(self.catalog["records"]), 108)
        self.assertEqual(sum(x["author_uid_confirmed_count"] == 0 for x in self.catalog["records"]), 50)

    def test_cannot_change_author_uid(self):
        self.reject(lambda x: x["parser"].update(exact_author_uid="0"))

    def test_cannot_claim_complete_original_replies(self):
        self.reject(lambda x: x["limits"].update(not_complete_original_author_replies=False))

    def test_cannot_claim_108_files_means_108_comment_coverage(self):
        self.reject(lambda x: x["limits"].update(all_108_lessons_covered_does_not_imply_reply_coverage=False))

    def test_cannot_claim_laohu_downloaded(self):
        self.reject(lambda x: x["limits"].update(laohu_file_bytes_obtained=True))

    def test_cannot_claim_laohu_compared(self):
        self.reject(lambda x: x["limits"].update(laohu_vs_baseline_compared=True))

    def test_cannot_claim_kaixiang_identified(self):
        self.reject(lambda x: x["limits"].update(kaixiang_A087_exact_reply_identified=True))

    def test_cannot_claim_real_market_backtest(self):
        self.reject(lambda x: x["limits"].update(market_backtest_run=True))

    def test_cannot_promote_nickname_to_original_sina_identity(self):
        self.reject(lambda x: x["limits"].update(nickname_and_uid_may_be_copied=False))

    def test_cannot_move_lesson29_reply_to_54(self):
        self.reject(lambda x: x["records"][28]["author_timestamps"].remove("2007-02-09 16:20:18"))

    def test_cannot_make_question_54_an_author_axiom(self):
        self.reject(lambda x: x["keyword_review"][1].update(role="AUTHOR_PROVED_SECOND_CENTER_AXIOM"))

    def test_cannot_change_computed_total(self):
        self.reject(lambda x: x["summary"].update(matching_name_and_uid_records=954))

    def test_cannot_swap_source_blob(self):
        self.reject(lambda x: x["records"][0].update(blob_sha=x["records"][1]["blob_sha"] + "x"))

    def test_source_doc_uid_parser_only_recognizes_exact_uid_and_name(self):
        example = (
            "UID:[1215172700] 昵称：缠中说禅 日期：(2007-02-09 16:20:18)\n"
            "提问 == 这是作者回复\n"
            "UID:[0] 昵称：缠中说禅 日期：(2007-02-09 16:22:29)\n"
            "这不能通过严格UID身份门\n"
            "UID:[1215172700] 昵称：其他人 日期：(2007-02-09 16:23:34)\n"
            "这也不算\n"
        )
        parsed = source_facts(example)
        self.assertEqual(parsed["comments_total"], 3)
        self.assertEqual(parsed["author_uid_confirmed_count"], 1)
        self.assertEqual(parsed["unverified_uid0_name_count"], 1)

    def test_question_keyword_is_only_candidate_not_author_proof(self):
        example = (
            "UID:[1215172700] 昵称：缠中说禅 日期：(2007-05-24 16:04:41)\n"
            "网友：按照第二种分解，中枢应该怎样？\n"
            "==\n这只是在回答条件。\n"
        )
        facts = source_facts(example)
        self.assertEqual(facts["keyword_candidate_timestamps"], ["2007-05-24 16:04:41"])
        self.assertTrue(self.catalog["limits"]["keyword_hits_not_author_own_quotation"])

    def test_strict_git_blob_sha_and_local_reverification(self):
        with tempfile.TemporaryDirectory() as d:
            text = "UID:[1215172700] 昵称：缠中说禅 日期：(2007-02-09 16:20:18)\n==\n回应\n"
            data = text.encode("utf-8")
            rel = "108/FAKE-029.md"
            p = Path(d)/rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
            row = {"lesson": 29, "path": rel, "blob_sha": git_blob_sha(data), **source_facts(text)}
            self.assertEqual(reverify_source_dir({"records": [row]}, d)["verified_files"], 1)
            p.write_bytes(data + b"tamper")
            with self.assertRaises(ValueError):
                reverify_source_dir({"records": [row]}, d)

    def test_date_only_is_not_certification(self):
        snippet = "某转载只写2007/2/9 16:20:18，并不证明是作者发言"
        result = compare_edition_text(self.catalog, snippet)
        self.assertEqual(result["uid_and_name_timestamp_markers_shared"], 0)
        self.assertEqual(result["priority"]["FEB09_R29"], "TIMESTAMP_TEXT_ONLY_LOW_CONFIDENCE")
        self.assertFalse(result["claims_original_sina_historical_identity_authenticated"])

    def test_uid_match_remains_textual_not_historical_authentication(self):
        snippet = "UID:[1215172700] 昵称：缠中说禅 日期：(2007-02-09 16:20:18)"
        result = compare_edition_text(self.catalog, snippet)
        self.assertEqual(result["uid_and_name_timestamp_markers_shared"], 1)
        self.assertEqual(result["priority"]["FEB09_R29"], "ARCHIVED_UID_AND_NAME_STRING_MATCH")
        self.assertFalse(result["claims_kaixiang_A087_identified"])

    def test_no_text_returns_unverifiable_not_missing(self):
        result = compare_edition_text(self.catalog, "")
        self.assertEqual(result["status"], "NO_READABLE_TEXT_UNVERIFIABLE_OCR_OR_FORMAT")
        self.assertFalse(result["claims_actual_edition_missing_replies"])

    def test_no_replies_in_edition_does_not_certify_absence(self):
        result = compare_edition_text(self.catalog, "前言：相关结构介绍。")
        self.assertEqual(result["uid_and_name_timestamp_markers_shared"], 0)
        self.assertEqual(result["baseline_timestamps_not_observed_in_text_count"], 953)
        self.assertFalse(result["claims_actual_edition_missing_replies"])

    def test_txt_file_and_docx_extraction_offline(self):
        with tempfile.TemporaryDirectory() as d:
            text = "缠中说禅 2007/2/9 16:20:18"
            src = Path(d)/"edition.txt"
            src.write_text(text, encoding="utf-8")
            self.assertEqual(extract_edition_text(src), text)
            docx = Path(d)/"edition.docx"
            xmlns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xml = ('<w:document xmlns:w="' + xmlns + '"><w:body><w:p><w:r><w:t>'
                   + text + '</w:t></w:r></w:p></w:body></w:document>')
            with zipfile.ZipFile(docx, "w") as z:
                z.writestr("word/document.xml", xml)
            self.assertIn(text, extract_edition_text(docx))

    def test_unsupported_file_type_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            file = Path(d)/"untrusted.exe"
            file.write_bytes(b"x")
            with self.assertRaises(ValueError):
                extract_edition_text(file)

    def test_date_parser_supports_slash_and_dash(self):
        self.assertEqual(dated_strings("2007/2/9 16:20:18 | 2007-02-09 16:20:18"),
                         {"2007-02-09 16:20:18"})

    def test_no_outer_quoted_reply_can_inflate_author_count(self):
        value = "UID:[0] 昵称：网友 日期：(2007-02-09 16:20:18)\n引述缠中说禅"
        self.assertEqual(source_facts(value)["author_uid_confirmed_count"], 0)


if __name__ == "__main__":
    unittest.main()
