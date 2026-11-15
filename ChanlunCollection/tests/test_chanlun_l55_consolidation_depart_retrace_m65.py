"""Source-anchored M65 third-point legal composition gate, no market feed."""
import json
import unittest
from pathlib import Path
from tools.audit_chanlun_l55_consolidation_depart_retrace_m65 import audit

ROOT=Path(__file__).resolve().parents[1]
class M65CompositionRetraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads((ROOT/"catalog/chanlun_l55_consolidation_depart_retrace_m65.json").read_text(encoding="utf-8"))
        cls.m64=json.loads((ROOT/"catalog/chanlun_l55_reply_chain_m64.json").read_text(encoding="utf-8"))

    def test_new_author_reply_precise_host_and_clock(self):
        q=self.doc["author_reply"]
        self.assertEqual((q["question_by"],q["question_at"],q["reply_at"]),
                         ("大盘","2007-05-28T16:15:20","2007-05-28T16:28:12"))
        self.assertEqual(q["article"],"教你炒股票55")
        self.assertEqual(q["url"],"https://chzhshch.blog/stocks/055/")
        self.assertFalse(q["sina_original_bytes_verified"])
        self.assertEqual(q["conclusion_strength"],
                         "AUTHOR_GENERIC_CONDITIONAL_REPLY_TO_TWO_PART_QUESTION_NOT_CASE_BY_CASE_CERTIFICATION")

    def test_not_accidentally_duplicate_m64_seven_original_replies(self):
        ids={x["id"] for x in self.m64["sources"]}
        self.assertEqual(len(ids),7)
        self.assertNotIn("L55_162812",ids)
        self.assertIn("L55_155528",ids)
        self.assertIn("L55_162510",ids)

    def test_prior_and_other_article_identity(self):
        cross={x["id"]:x for x in self.doc["corroborating_sources"]}
        self.assertEqual(cross["L55_155528"]["reply_at"],"2007-05-28T15:55:28")
        self.assertEqual(cross["L55_162510"]["reply_at"],"2007-05-28T16:25:10")
        self.assertEqual(cross["L38_162942"]["article"],"教你炒股票38")
        self.assertEqual(cross["L38_162942"]["reply_at"],"2007-03-21T16:29:42")
        self.assertEqual(cross["L20_AUTHOR_MAIN"]["published_at"],"2007-01-05T15:23:22")

    def test_responds_to_two_questions_not_a_fully_certified_market_case(self):
        q=self.doc["author_reply"]
        self.assertIn("SECOND_DAILY_CENTER",q["question_part_1"])
        self.assertIn("THIRD_SELL",q["question_part_2"])
        self.assertIn("CONDITIONAL",q["conclusion_strength"])

    def test_scope_separates_777_and_600151_and_the_two_Bs(self):
        x=self.doc["distinct_case_roles"]
        self.assertIn("600151",x["l54_chart"])
        self.assertIn("000777_OR_600777",x["l55_777"])
        self.assertEqual(self.doc["grade"],"SOURCE_TEXT_CONDITIONAL_NOT_REAL_MARKET")

    def test_registered_synthetic_statuses(self):
        self.assertEqual(len(self.doc["toy_cases"]),17)
        for c in self.doc["toy_cases"]:
            with self.subTest(case=c["id"]):
                self.assertEqual(audit(c["input"]),c["expected"])

    def test_no_synthetic_case_may_be_trading_certified(self):
        for c in self.doc["toy_cases"]:
            self.assertFalse(c["expected"]=="MARKET_THIRD_SELL_CONFIRMED")
            self.assertFalse(c["expected"]=="EXECUTED_ORDER_FILLED")
            self.assertFalse(c["input"]["origin"]=="SINA_ORIGINAL_VALIDATED")

    def test_unresolved_price_boundary_and_finished_members(self):
        self.assertEqual(self.doc["boundary_touch"],"UNRESOLVED_L20_L38")
        self.assertIn("separate_lower_movement_completion_receipts",self.doc["live_context_required"])
        self.assertIn("source_available_at_and_market_first_known_at",self.doc["live_context_required"])

    def test_author_second_center_formula_not_invented(self):
        p=self.doc["repo_status"]
        self.assertEqual(p["A087_second_center_formula"],"UNKNOWN")
        self.assertEqual(p["A016_third_layer"],"UNKNOWN")
        for k in ("F01","OB38","OB99","phi20"):
            self.assertEqual(p[k],"OPEN")

    def test_market_status_explicitly_not_run(self):
        p=self.doc["repo_status"]
        self.assertEqual(p["real_market"],"NOT_RUN")
        self.assertIs(p["market_data_acquired"],False)
        self.assertEqual(p["trade_count"],0)
        self.assertEqual(p["orders_sent"],0)

    def test_source_gate_forbids_invalid_promotions(self):
        f=self.doc["forbidden"]
        self.assertIn("CONSOLIDATION_CHILD_TYPE_EQUALS_COMPLETED_CHILD",f)
        self.assertIn("RETURN_INSIDE_CENTER_COUNTS_AS_OUTSIDE_THIRD_POINT",f)
        self.assertIn("L20_BOUNDARY_TOUCH_IS_SETTLED_BY_L55_REPLY",f)

if __name__=="__main__":
    unittest.main()
