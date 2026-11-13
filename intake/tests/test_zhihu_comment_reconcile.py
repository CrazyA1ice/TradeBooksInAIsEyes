"""Synthetic comment intake tests: no Zhihu network or authentic comment content."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import zhihu_comment_reconcile as mod


def fake_answers(n=3):
    out = ["# synthetic export", "", "- 用户主页: https://www.zhihu.com/people/tsk-47-98",
           "- 回答总数: " + str(n), "", "---", ""]
    for i in range(1, n + 1):
        out += [f"## 测试问题{i}", "",
                f"- 原文链接: https://www.zhihu.com/question/{i}/answer/{900000+i}",
                "- 发布时间: 2025-01-01 12:00", "- 赞同数: 0", "",
                f"虚构回答{i}", "", "---", ""]
    return "\n".join(out).encode("utf-8")


def comment(cid, aid=900001, question=1, **overrides):
    obj = {
        "comment_id": str(cid),
        "answer_url": f"https://www.zhihu.com/question/{question}/answer/{aid}",
        "parent_comment_id": None,
        "author_label": "synthetic author",
        "reported_author_role": "UNKNOWN",
        "published_at": "2025-01-02T12:00:00+08:00",
        "content": "这是合成测试评论，非真实用户文字",
    }
    obj.update(overrides)
    return obj


class CommentReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.md = self.root / "answers.md"
        self.idx = self.root / "answers-index.json"
        self.incoming = self.root / "comments.json"
        self.ledger = self.root / "ledger.json"
        self.md.write_bytes(fake_answers())
        self.idx.write_text(json.dumps({
            "schema_version": 1,
            "source_sha256": hashlib.sha256(self.md.read_bytes()).hexdigest(),
            "answer_count": 3,
            "answers": [{"id": f"A{i:03d}", "answer_id": str(900000+i),
                         "url": f"https://www.zhihu.com/question/{i}/answer/{900000+i}"}
                        for i in range(1, 4)],
        }), encoding="utf-8")
        self.write_comments([comment("10001")])

    def write_comments(self, rows, **overrides):
        obj = {
            "schema": mod.SCHEMA,
            "profile_url": "https://www.zhihu.com/people/tsk-47-98",
            "captured_at": "2025-01-03T12:00:00+08:00",
            "comments": rows,
        }
        obj.update(overrides)
        self.incoming.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")

    def run_review(self, ledger=None):
        return mod.review(self.md, self.idx, self.incoming, "tsk-47-98",
                          ledger_json=ledger)

    def ledger_from(self, report):
        self.ledger.write_text(json.dumps({
            "schema": mod.LEDGER_SCHEMA,
            "speaker_token": "tsk-47-98",
            "comments": [{**row, "stable_id": row.pop("proposed_id")}
                         for row in [dict(r) for r in report["new_comment_refs"]]],
        }, ensure_ascii=False), encoding="utf-8")
        return self.ledger

    def test_real_repository_answer_index_integrity_no_comments(self):
        root = Path(__file__).resolve().parents[2]
        source = root / "other_views" / "chanlun" / "speaker-unknown-001"
        md = source / "answers-2026-11-11.md"
        idx = source / "answers-index.json"
        if not md.is_file() or not idx.is_file():
            self.skipTest("full repository book source checkout unavailable")
        self.write_comments([])
        report = mod.review(md, idx, self.incoming, "tsk-47-98")
        self.assertEqual(report["comments_in_export"], 0)
        self.assertEqual(report["new_proposed"], 0)
        self.assertFalse(report["platform_comment_history_complete"])

    def test_basic_proposal_is_metadata_only(self):
        report = self.run_review()
        self.assertEqual(report["comments_in_export"], 1)
        self.assertEqual(report["new_proposed"], 1)
        self.assertEqual(report["new_comment_refs"][0]["proposed_id"], "C001")
        self.assertEqual(report["new_comment_refs"][0]["answer_ref"], "A001")
        self.assertNotIn("合成测试评论", json.dumps(report, ensure_ascii=False))
        self.assertFalse(report["authorship_independently_verified"])
        self.assertFalse(report["platform_comment_history_complete"])
        self.assertFalse(report["research_sources_modified"])
        self.assertEqual(report["priority_answer_coverage"][0]["status"],
                         "NOT_OBSERVED_IN_THIS_EXPORT")

    def test_parent_and_child_same_answer_can_be_proposed(self):
        self.write_comments([comment("10002", parent_comment_id="10001"), comment("10001")])
        r = self.run_review()
        self.assertEqual(r["new_proposed"], 2)
        self.assertFalse(r["blocked_for_context_review"])
        self.assertEqual({x["comment_id"] for x in r["new_comment_refs"]}, {"10001", "10002"})

    def test_missing_parent_is_blocked_not_invented(self):
        self.write_comments([comment("10002", parent_comment_id="99999")])
        r = self.run_review()
        self.assertEqual(r["new_proposed"], 0)
        self.assertEqual(r["blocked_for_context_review"][0]["review_reasons"],
                         ["PARENT_CONTEXT_NOT_IN_EXPORT_OR_LEDGER"])

    def test_unknown_answer_is_parked(self):
        self.write_comments([comment("10001", question=77, aid=977777)])
        r = self.run_review()
        self.assertEqual(r["new_proposed"], 0)
        self.assertIn("ANSWER_NOT_IN_BASE_INDEX",
                      r["blocked_for_context_review"][0]["review_reasons"])

    def test_missing_time_is_parked(self):
        self.write_comments([comment("10001", published_at=None)])
        r = self.run_review()
        self.assertIn("COMMENT_TIMESTAMP_MISSING",
                      r["blocked_for_context_review"][0]["review_reasons"])

    def test_correct_answer_id_wrong_question_rejected(self):
        self.write_comments([comment("10001", question=44)])
        with self.assertRaisesRegex(mod.CoverageError, "indexed_answer_url_mismatch"):
            self.run_review()

    def test_wrong_parent_answer_rejected(self):
        self.write_comments([comment("10001"),
                             comment("10002", question=2, aid=900002, parent_comment_id="10001")])
        with self.assertRaisesRegex(mod.CoverageError, "cross_answer_parent_relation"):
            self.run_review()

    def test_reply_cycle_rejected(self):
        self.write_comments([comment("10001", parent_comment_id="10002"),
                             comment("10002", parent_comment_id="10001")])
        with self.assertRaisesRegex(mod.CoverageError, "comment_reply_cycle"):
            self.run_review()

    def test_self_parent_rejected(self):
        self.write_comments([comment("10001", parent_comment_id="10001")])
        with self.assertRaisesRegex(mod.CoverageError, "self_parent_comment"):
            self.run_review()

    def test_duplicate_comment_id_rejected(self):
        self.write_comments([comment("10001"), comment("10001")])
        with self.assertRaisesRegex(mod.CoverageError, "duplicate_comment_id_in_export"):
            self.run_review()

    def test_invalid_role_rejected(self):
        self.write_comments([comment("10001", reported_author_role="PLATFORM_VERIFIED")])
        with self.assertRaisesRegex(mod.CoverageError, "invalid_reported_author_role"):
            self.run_review()

    def test_invalid_or_naive_time_rejected(self):
        for stamp in ("2025-01-02 12:00", "garbage", "2025-13-01T12:00+08:00"):
            with self.subTest(stamp=stamp):
                self.write_comments([comment("10001", published_at=stamp)])
                with self.assertRaises(mod.CoverageError):
                    self.run_review()

    def test_time_after_capture_rejected(self):
        self.write_comments([comment("10001", published_at="2025-01-04T12:00:00+08:00")])
        with self.assertRaisesRegex(mod.CoverageError, "comment_after_export_capture"):
            self.run_review()

    def test_wrong_speaker_rejected(self):
        self.write_comments([comment("10001")],
                            profile_url="https://www.zhihu.com/people/someone-else")
        with self.assertRaisesRegex(mod.CoverageError, "comment_export_profile_mismatch"):
            self.run_review()

    def test_answer_index_source_sha_mismatch_rejected(self):
        j = json.loads(self.idx.read_text(encoding="utf-8"))
        j["source_sha256"] = "0" * 64
        self.idx.write_text(json.dumps(j), encoding="utf-8")
        with self.assertRaisesRegex(mod.CoverageError, "answer_index_source_sha_mismatch"):
            self.run_review()

    def test_prior_ledger_preserves_ids_detects_changes_and_absences(self):
        r = self.run_review()
        ledger = self.ledger_from(r)
        self.write_comments([comment("10001"), comment("10002", question=2, aid=900002)])
        two = self.run_review(ledger)
        self.assertEqual(two["unchanged_existing_overlaps"], 1)
        self.assertEqual(two["new_comment_refs"][0]["proposed_id"], "C002")
        self.assertEqual(two["changed_existing_needing_review"], [])
        self.write_comments([comment("10001", content="amended synthetic text")])
        amended = self.run_review(ledger)
        self.assertEqual(amended["changed_existing_needing_review"][0]["stable_id"], "C001")
        self.assertEqual(amended["new_proposed"], 0)
        self.write_comments([])
        absent = self.run_review(ledger)
        self.assertEqual(absent["existing_not_in_this_export"][0]["stable_id"], "C001")

    def test_prior_ledger_comment_identity_cannot_move_answers(self):
        ledger = self.ledger_from(self.run_review())
        self.write_comments([comment("10001", question=2, aid=900002)])
        with self.assertRaisesRegex(mod.CoverageError, "comment_id_reassigned_to_other_answer"):
            self.run_review(ledger)

    def test_existing_parent_can_resolve_child(self):
        ledger = self.ledger_from(self.run_review())
        self.write_comments([comment("10002", parent_comment_id="10001")])
        r = self.run_review(ledger)
        self.assertEqual(r["new_proposed"], 1)
        self.assertEqual(r["new_comment_refs"][0]["proposed_id"], "C002")

    def test_priority_target_is_only_export_presence_not_verified_history(self):
        j = json.loads(self.idx.read_text(encoding="utf-8"))
        j["answers"][0]["id"] = "A094"
        self.idx.write_text(json.dumps(j), encoding="utf-8")
        r = self.run_review()
        self.assertEqual(r["priority_answer_coverage"][0]["records_in_this_export"], 1)
        self.assertEqual(r["priority_answer_coverage"][0]["status"],
                         "EXPORTED_UNVERIFIED_NOT_RESEARCH_APPROVED")

    def test_cli_writes_only_exclusive_private_receipt(self):
        path = self.root / "test.private.json"
        args = ["--answers-md", str(self.md), "--answers-index", str(self.idx),
                "--incoming-json", str(self.incoming), "--speaker-token", "tsk-47-98",
                "--output", str(path)]
        before = self.md.read_bytes()
        self.assertEqual(mod.main(args), 0)
        self.assertTrue(path.exists())
        self.assertEqual(before, self.md.read_bytes())
        self.assertEqual(mod.main(args), 2)
        self.assertEqual(mod.main(args[:-1] + [str(self.idx)]), 2)

    def test_unapproved_fabricated_comment_cannot_claim_authentication(self):
        self.write_comments([comment("10001", reported_author_role="ANSWER_AUTHOR")])
        r = self.run_review()
        self.assertEqual(r["new_comment_refs"][0]["reported_author_role"], "ANSWER_AUTHOR")
        self.assertEqual(r["new_comment_refs"][0]["provenance_status"],
                         "USER_EXPORT_NOT_PLATFORM_AUTHENTICATED")
        self.assertFalse(r["authorship_independently_verified"])


if __name__ == "__main__":
    unittest.main()
