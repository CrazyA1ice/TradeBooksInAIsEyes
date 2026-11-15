"""M66 author dated commentary: actual host, two clocks, existing F01 no-go."""
import json
import unittest
from pathlib import Path
from tools.audit_chanlun_july11_segment_confirmation_m66 import audit, classify

ROOT=Path(__file__).resolve().parents[1]
class M66July11ReplyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads((ROOT/"catalog/chanlun_july11_segment_confirmation_m66.json").read_text(encoding="utf-8"))
        cls.rep={x["id"]:x for x in cls.doc["replies"]}
        cls.cases={x["id"]:x for x in cls.doc["toy_cases"]}

    def test_actual_host_not_lesson64(self):
        h=self.doc["author_host"]
        self.assertEqual(h["url"],"https://chzhshch.blog/stocks/3850points/")
        self.assertEqual(h["host_article_published_at"],"2007-07-11T15:41:38")
        self.assertEqual(h["lesson64_original_date"],"2007-07-02T21:37:44")
        self.assertIn("NOT_LESSON64",h["role"])

    def test_exact_eight_dated_replies(self):
        self.assertEqual(len(self.rep),8)
        self.assertEqual(self.rep["J11_155925"]["question_author"],"在路上")
        self.assertEqual(self.rep["J11_155925"]["question_at"],"2007-07-11T15:51:23")
        self.assertEqual(self.rep["J11_155925"]["reply_at"],"2007-07-11T15:59:25")
        self.assertEqual(self.rep["J11_160823"]["reply_at"],"2007-07-11T16:08:23")
        self.assertEqual(self.rep["J11_163627"]["question_author"],"多来米")

    def test_source_grade_not_authenticated(self):
        self.assertTrue(all(not x["original_sina_comment_bytes_authenticated"] for x in self.rep.values()))
        self.assertFalse(self.doc["evidence_frontier"]["independent_original_sina_authenticated"])

    def test_reply_precedes_publication_is_forbidden(self):
        rows=self.doc["replies"]
        article=self.doc["author_host"]["host_article_published_at"]
        for x in rows:
            self.assertLess(article,x["reply_at"])
            self.assertLess(x["question_at"],x["reply_at"])
            self.assertEqual(x["host_url"],self.doc["author_host"]["url"])

    def test_toy_temporal_progression(self):
        for key,expected in [
          ("before_pivot","PENDING_EVENT_NOT_IN_PREFIX"),
          ("at_pivot_before_preview","HISTORICAL_ENDPOINT_NOT_YET_CONFIRMATION"),
          ("early_preview_not_confirmed","PREVIEW_ONLY_SEGMENT_UNCONFIRMED"),
          ("one_seq_before_break","PREVIEW_ONLY_SEGMENT_UNCONFIRMED"),
          ("asof_at_break_receipt","HYPOTHETICAL_SEGMENT_CONFIRMED_MOVEMENT_OPEN"),
          ("asof_after_break","HYPOTHETICAL_SEGMENT_CONFIRMED_MOVEMENT_OPEN")]:
            self.assertEqual(classify(self.cases[key]["input"]),expected)

    def test_all_18_toy_cases(self):
        self.assertEqual(len(self.cases),18)
        for k,x in self.cases.items():
            with self.subTest(k=k):self.assertEqual(classify(x["input"]),x["expected"])

    def test_forged_market_and_finished_movement_are_rejected(self):
        for k in ("root_exit_forged","higher_movement_finished_forged",
                  "market_certification_forged","orders_forged","macd_only_promoted",
                  "higher_role_forged"):
            self.assertTrue(classify(self.cases[k]["input"]).startswith("REJECT"))

    def test_root_and_prior_m65_gates_rerun(self):
        result=audit()
        self.assertEqual(result["status"],"M66_ARCHIVED_REPLY_SOURCE_AND_ASOF_BOUNDARY_PASS")
        self.assertEqual(result["f01_prior_negative_cases_retained"],6)
        self.assertFalse(result["m65_market_third_sell_certified"])
        self.assertEqual(result["root_pan_exit"],"OPEN")
        self.assertEqual(result["market"],"NOT_RUN")
        self.assertEqual(result["orders"],0)

    def test_no_author_98_percent_pseudostatistics(self):
        self.assertIn("AUTHOR_98_PERCENT_CLAIM_NOT_VERIFIED_PROBABILITY_SAMPLE",self.doc["disjoint_assertions"])
        self.assertEqual(self.rep["J11_160823"]["concept"],"MACD_NOT_CERTIFICATE")

    def test_no_kx_private_second_formula(self):
        s=self.doc["evidence_frontier"]
        for k in ("F01","OB38","OB99","Phi20"):self.assertEqual(s[k],"OPEN")
        self.assertEqual(s["A087_second_center_formula"],"UNKNOWN")
        self.assertEqual(s["market_experiments"],"NOT_RUN")

if __name__=="__main__":
    unittest.main()
