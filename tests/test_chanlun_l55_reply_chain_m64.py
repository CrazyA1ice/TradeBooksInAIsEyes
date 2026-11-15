"""M64: dated author-reply provenance and typed non-promotion, not historical market proof."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "catalog/chanlun_l55_reply_chain_m64.json"
M54 = ROOT / "catalog/chanlun_l54_dual_policy_witness_m54.json"

class M64ArchivedReplyChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DATA.read_text(encoding="utf-8"))
        cls.m54 = json.loads(M54.read_text(encoding="utf-8"))
        cls.rows = {x["id"]: x for x in cls.doc["sources"]}

    def test_schema_and_provenance_grade(self):
        self.assertEqual(self.doc["schema_version"], 1)
        self.assertIn("NOT_SINA_ORIGINAL_BYTES", self.doc["role"])
        self.assertEqual(len(self.rows), 7)

    def test_source_host_articles_are_distinct(self):
        h = {x["article"]:x for x in self.doc["origin_hosts"]}
        self.assertEqual(set(h), {"论语详解55", "教你炒股票55"})
        self.assertEqual(h["论语详解55"]["published_at"], "2007-03-08T15:27:19")
        self.assertEqual(h["教你炒股票55"]["published_at"], "2007-05-28T08:12:41")
        self.assertTrue(all(x["original_sina_html_authenticated"] is False for x in h.values()))

    def test_each_question_precedes_reply_and_article_published(self):
        h = {x["article"]:x for x in self.doc["origin_hosts"]}
        for x in self.rows.values():
            self.assertEqual(x["role"], "ARCHIVED_AUTHOR_REPLY")
            self.assertLess(x["question_at"], x["reply_at"])
            self.assertLess(h[x["article"]]["published_at"], x["reply_at"])
            self.assertEqual(x["url"], h[x["article"]]["url"])

    def test_march_two_methods_not_second_definition(self):
        self.assertEqual(self.rows["C55_161043"]["reply_at"], "2007-03-08T16:10:43")
        self.assertEqual(self.rows["C55_163856"]["question_author"], "缠文观止")
        self.assertEqual(self.rows["C55_163856"]["reply_at"], "2007-03-08T16:38:56")
        self.assertEqual(self.doc["obligations"]["A087_second_formula"], "UNKNOWN")

    def test_l55_third_point_completion_reply(self):
        x = self.rows["L55_155528"]
        self.assertEqual(x["question_at"], "2007-05-28T15:48:54")
        self.assertEqual(x["reply_at"], "2007-05-28T15:55:28")
        gates = self.doc["third_point_gates"]
        self.assertEqual(gates["source_ids"], ["L55_155528", "L55_162510"])
        self.assertIn("COMPONENT_B_IS_COMPLETED_LOWER_LEVEL", gates["source_author_assertions"])
        self.assertIn("RETRACE_IS_COMPLETED_LOWER_LEVEL", gates["source_author_assertions"])
        self.assertIs(gates["inferred_complete_sufficiency"], False)
        self.assertIs(gates["market_certified"], False)

    def test_l55_d4_comparison_reuses_existing_m54_policies(self):
        c = self.doc["l54_case"]
        self.assertEqual(c["referenced_by"], "L55_160426")
        self.assertEqual(self.rows["L55_160426"]["question_author"], "雪狼")
        self.assertEqual(c["target"], "g3d4")
        self.assertEqual(c["baseline_by_policy"], {"R_A":"g2d3","R_B":"g1d2"})
        self.assertEqual({x["id"] for x in self.m54["policies"]}, {"R_A","R_B"})
        self.assertTrue(c["author_says_other_conditions_can_disagree"])
        self.assertIs(c["raw_macd_series_acquired"], False)

    def test_third_sell_rejection_is_different_security(self):
        self.assertEqual(self.rows["L55_162510"]["question_author"], "卖错了吗")
        self.assertEqual(self.rows["L55_162510"]["reply_at"], "2007-05-28T16:25:10")
        scope = self.doc["distinct_case_scope"]
        self.assertIn("000777_AND_600777", scope["third_sell_rejection"])
        self.assertIn("600151", scope["l54_d4"])
        self.assertIn("NOT_SOURCE_LINKED_TO_600151", scope["third_sell_rejection"])

    def test_execution_cost_and_horizon_are_distinct_replies(self):
        self.assertEqual(self.rows["L55_162940"]["reply_at"], "2007-05-28T16:29:40")
        self.assertEqual(self.rows["L55_163101"]["reply_at"], "2007-05-28T16:31:01")
        self.assertNotEqual(self.rows["L55_162940"]["question_author"], self.rows["L55_163101"]["question_author"])
        self.assertIn("OTHER_READER", self.doc["distinct_case_scope"]["fee_warning"])

    def test_study_rejects_market_proof_inflation(self):
        p = self.doc["obligations"]
        self.assertEqual(p["historical_price_data"], "NOT_ACQUIRED")
        self.assertEqual(p["independent_completion_receipts"], "MISSING")
        self.assertEqual(p["F01"], "OPEN")
        self.assertEqual(p["OB38"], "OPEN")
        self.assertEqual(p["OB99"], "OPEN")
        self.assertEqual(p["real_market_experiments"], "NOT_RUN")
        self.assertEqual(p["orders_sent"], 0)
        self.assertEqual(p["actual_pnl"], "NOT_RUN")

    def test_reply_time_does_not_equal_market_first_known(self):
        self.assertEqual(self.doc["obligations"]["first_known_from_market"], "UNKNOWN")
        self.assertFalse(self.doc["l54_case"]["original_chart_year_authenticated"])
        self.assertTrue(self.doc["l54_case"]["d4_not_same_event_as_g7"])

    def test_forbidden_promotions_explicit(self):
        x = self.doc["forbidden_promotions"]
        self.assertGreaterEqual(len(x), 6)
        self.assertIn("D4_MACD_WEAKER_IMPLIES_THIRD_SELL", x)
        self.assertIn("TWO_METHODS_EQUALS_A087_SECOND_CENTER_FORMULA", x)
        self.assertIn("DATED_ARCHIVED_COMMENT_EQUALS_SINA_ORIGINAL_AUTHENTICATED", x)

if __name__ == "__main__":
    unittest.main()
