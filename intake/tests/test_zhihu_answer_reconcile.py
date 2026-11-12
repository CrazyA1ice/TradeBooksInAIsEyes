"""Offline synthetic Zhihu export coverage tests; no actual account content."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / "zhihu_answer_reconcile.py"
spec = importlib.util.spec_from_file_location("zhihu_answer_reconcile", SOURCE)
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)


def make_export(count, *, speaker="tsk-47-98", start=1, marker="REDACTED"):
    sections = [
        "# 知乎用户「虚构人物」的全部回答", "",
        "- 用户主页: https://www.zhihu.com/people/" + speaker,
        "- 导出时间: 2026-11-12 12:00",
        "- 回答总数: " + str(count),
        "", "---", "",
    ]
    for ident in range(start, start + count):
        sections.extend([
            "## 虚构测试问题 " + str(ident), "",
            "- 原文链接: https://www.zhihu.com/question/" + str(ident) +
            "/answer/" + str(ident + 900000),
            "- 发布时间: 2025-01-01 12:00",
            "- 赞同数: 0", "",
            "纯虚构正文 " + marker + " #" + str(ident), "",
            "---", "",
        ])
    return "\n".join(sections).encode("utf-8")


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.base = self.root / "answers-100.md"
        self.incoming = self.root / "full-200plus.md"
        self.index = self.root / "answers-index.json"
        self.base.write_bytes(make_export(100))
        self.incoming.write_bytes(make_export(215))
        refs = []
        for i in range(1, 101):
            refs.append({
                "id": "A" + str(i).zfill(3),
                "answer_id": str(i + 900000),
                "url": "https://www.zhihu.com/question/" + str(i) +
                       "/answer/" + str(i + 900000)
            })
        self.idx = {
            "schema_version": 1,
            "source_sha256": hashlib.sha256(self.base.read_bytes()).hexdigest(),
            "answer_count": 100,
            "answers": refs
        }
        self.write_index()

    def write_index(self):
        self.index.write_text(json.dumps(self.idx), encoding="utf-8")

    def run_reconcile(self, minimum=1):
        return rec.reconcile(self.base, self.index, self.incoming,
                             "tsk-47-98", min_candidate=minimum)

    def test_215_answer_full_export_has_no_100_cap(self):
        x = self.run_reconcile(200)
        self.assertEqual(x["base"]["parsed_answers"], 100)
        self.assertEqual(x["incoming"]["parsed_answers"], 215)
        self.assertEqual(x["kept_stable_answer_references"], 100)
        self.assertEqual(x["new_proposed"], 115)
        self.assertEqual(x["proposed_total_after_append"], 215)
        self.assertEqual(x["new_answer_refs"][0]["proposed_id"], "A101")
        self.assertEqual(x["new_answer_refs"][-1]["proposed_id"], "A215")
        self.assertEqual(x["unchanged_overlaps"], 100)
        self.assertEqual(x["status"], "APPEND_PROPOSAL_NOT_IMPORTED")
        self.assertFalse(x["full_zhihu_account_coverage_verified"])
        self.assertFalse(x["speaker_identity_independently_verified"])

    def test_no_new_items_does_not_fake_200(self):
        self.incoming.write_bytes(self.base.read_bytes())
        x = self.run_reconcile(100)
        self.assertEqual(x["new_proposed"], 0)
        self.assertEqual(x["status"], "SAME_COVERAGE_NO_NEW_ANSWERS")

    def test_user_specified_200_minimum_rejects_100_file(self):
        self.incoming.write_bytes(self.base.read_bytes())
        with self.assertRaisesRegex(rec.CoverageError, "candidate_below_explicit_minimum"):
            self.run_reconcile(200)

    def test_false_export_header_230_vs_100_is_rejected(self):
        self.incoming.write_bytes(make_export(100).replace(
            b"- \xe5\x9b\x9e\xe7\xad\x94\xe6\x80\xbb\xe6\x95\xb0: 100",
            b"- \xe5\x9b\x9e\xe7\xad\x94\xe6\x80\xbb\xe6\x95\xb0: 230"))
        with self.assertRaisesRegex(rec.CoverageError, "declared_and_parsed_counts_differ"):
            self.run_reconcile()

    def test_keep_new_partial_export_without_deleting_prior_ids(self):
        self.incoming.write_bytes(make_export(130, start=101))
        x = self.run_reconcile(100)
        self.assertEqual(x["prior_answers_not_in_this_export"], 100)
        self.assertEqual(x["new_proposed"], 130)
        self.assertEqual(x["new_answer_refs"][0]["proposed_id"], "A101")
        self.assertEqual(x["status"], "REVIEW_CHANGES_OR_PARTIAL_EXPORT")

    def test_changed_existing_body_never_overwrites(self):
        self.incoming.write_bytes(make_export(105, marker="DIFFERENT"))
        before = self.base.read_bytes()
        x = self.run_reconcile()
        self.assertEqual(x["changed_prior_answers_needing_review"], 100)
        self.assertEqual(x["new_proposed"], 5)
        self.assertEqual(self.base.read_bytes(), before)
        self.assertEqual(x["status"], "REVIEW_CHANGES_OR_PARTIAL_EXPORT")

    def test_duplicate_answer_id_in_export_rejected(self):
        data = make_export(2).decode("utf-8")
        data = data.replace("/answer/900002", "/answer/900001")
        self.incoming.write_text(data, encoding="utf-8")
        with self.assertRaisesRegex(rec.CoverageError, "duplicate_answer_id_in_export"):
            self.run_reconcile()

    def test_different_speaker_rejected(self):
        self.incoming.write_bytes(make_export(2, speaker="somebody-else"))
        with self.assertRaisesRegex(rec.CoverageError, "zhihu_speaker_mismatch"):
            self.run_reconcile()

    def test_bad_metadata_rejected_not_silently_ignored(self):
        data = make_export(2).decode("utf-8")
        data = data.replace("https://www.zhihu.com/question/1/answer/900001",
                            "https://malicious.invalid/question/1/answer/900001")
        self.incoming.write_text(data, encoding="utf-8")
        with self.assertRaisesRegex(rec.CoverageError, "invalid_answer_url_or_metadata"):
            self.run_reconcile()

    def test_false_markdown_subheading_does_not_become_new_answer(self):
        data = make_export(2).decode("utf-8")
        data = data.replace("纯虚构正文 REDACTED #1",
                            "纯虚构正文 REDACTED #1\n\n## 正文内部的小标题\n\n解释并不含来源元数据")
        self.incoming.write_text(data, encoding="utf-8")
        parsed = rec.parse_export(self.incoming, "tsk-47-98")
        self.assertEqual(parsed["declared_count"], 2)
        self.assertEqual(parsed["parsed_count"], 2)

    def test_invalid_index_source_hash_blocked(self):
        self.idx["source_sha256"] = "0" * 64
        self.write_index()
        with self.assertRaisesRegex(rec.CoverageError, "base_export_sha_not_indexed"):
            self.run_reconcile()

    def test_invalid_index_coverage_blocked(self):
        self.idx["answers"].pop()
        self.write_index()
        with self.assertRaisesRegex(rec.CoverageError, "base_index_count_drift"):
            self.run_reconcile()

    def test_duplicate_stable_ids_blocked(self):
        self.idx["answers"][1]["id"] = "A001"
        self.write_index()
        with self.assertRaisesRegex(rec.CoverageError, "duplicate_stable_answer_number"):
            self.run_reconcile()

    def test_answer_id_question_reassignment_blocked(self):
        data = make_export(101).decode("utf-8")
        data = data.replace("/question/1/answer/900001",
                            "/question/7001/answer/900001")
        self.incoming.write_text(data, encoding="utf-8")
        with self.assertRaisesRegex(rec.CoverageError, "same_answer_id_different_question"):
            self.run_reconcile()

    def test_crlf_and_bom_export_supported_without_loss(self):
        data = make_export(3).replace(b"\n", b"\r\n")
        self.incoming.write_bytes(b"\xef\xbb\xbf" + data)
        x = rec.parse_export(self.incoming, "tsk-47-98")
        self.assertEqual(x["parsed_count"], 3)

    def test_original_answer_bodies_are_not_in_metadata_report(self):
        self.incoming.write_bytes(make_export(102, marker="SENSITIVE_SYNTHETIC_TEST_BODY"))
        report = json.dumps(self.run_reconcile(), ensure_ascii=False)
        self.assertNotIn("SENSITIVE_SYNTHETIC_TEST_BODY", report)
        self.assertNotIn("纯虚构正文", report)
        self.assertTrue(self.run_reconcile()["no_source_body_in_report"])

    def test_explicit_private_output_and_no_overwrite(self):
        self.incoming.write_bytes(make_export(102))
        private = self.root / "review.private.json"
        args = ["--base-md", str(self.base), "--base-index", str(self.index),
                "--incoming-md", str(self.incoming), "--speaker-token", "tsk-47-98",
                "--min-incoming-answers", "100", "--output", str(private)]
        self.assertEqual(rec.main(args), 0)
        self.assertEqual(json.loads(private.read_text(encoding="utf-8"))["new_proposed"], 2)
        with mock.patch("sys.stderr"):
            self.assertEqual(rec.main(args), 2)
        self.assertEqual(json.loads(private.read_text(encoding="utf-8"))["new_proposed"], 2)

    def test_no_output_argument_means_no_private_file_writes(self):
        self.incoming.write_bytes(make_export(102))
        before = sorted(p.name for p in self.root.iterdir())
        with mock.patch("builtins.print"):
            self.assertEqual(rec.main([
                "--base-md", str(self.base), "--base-index", str(self.index),
                "--incoming-md", str(self.incoming),
                "--speaker-token", "tsk-47-98"]), 0)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), before)

    def test_symlink_candidate_is_rejected(self):
        link = self.root / "link.md"
        try:
            link.symlink_to(self.incoming)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(rec.CoverageError, "source_must_be_regular_file"):
            rec.parse_export(link, "tsk-47-98")


if __name__ == "__main__":
    unittest.main()
