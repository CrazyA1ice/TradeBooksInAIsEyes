"""M67 F01: author-archived 2007-04-03 pan-end time/level scope, no trades."""
import json
import unittest
from pathlib import Path
from tools.audit_chanlun_confucius61_pan_end_root_cut_m67 import audit,classify

ROOT=Path(__file__).resolve().parents[1]
class M67PanEndScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract=json.loads((ROOT/"catalog/chanlun_confucius61_pan_end_root_cut_m67.json").read_text(encoding="utf-8"))
        cls.cases={c["id"]:c for c in cls.contract["synthetic_cases"]}

    def test_correct_original_host_not_lesson40(self):
        h=self.contract["source_host"]
        self.assertEqual(h["article"],"论语详解61")
        self.assertEqual(h["original_post_at"],"2007-04-03T15:27:02")
        self.assertFalse(h["original_2007_sina_bytes_authenticated"])

    def test_first_reply_155118_not_155451(self):
        a,b=self.contract["source_replies"]
        self.assertEqual(a["question_author"],"你的样子")
        self.assertEqual(a["question_at"],"2007-04-03T15:39:53")
        self.assertEqual(a["reply_at"],"2007-04-03T15:51:18")
        self.assertEqual(b["question_author"],"hehe2")
        self.assertEqual(b["question_at"],"2007-04-03T15:53:00")
        self.assertEqual(b["reply_at"],"2007-04-03T15:54:51")

    def test_23_synthetic_cases(self):
        self.assertEqual(len(self.cases),23)
        for key,c in self.cases.items():
            with self.subTest(key=key):
                self.assertEqual(classify(c["input"]),c["expected"])

    def test_level_g_end_does_not_exclude_higher_pan(self):
        a=self.cases["g1_center_end_local_pan_end"]
        b=self.cases["g1_pan_ends_higher_pan_remains"]
        self.assertEqual(classify(a["input"]),classify(b["input"]))
        self.assertTrue(b["input"]["higher_level_pan_present"])

    def test_strict_tick_root_stays_open(self):
        a=self.cases["g0_no_independent_root_exit"]
        b=self.cases["g0_third_point_without_gminus1"]
        self.assertEqual(classify(a["input"]),"PENDING_STRICT_ROOT_PAN_EXIT_RULE")
        self.assertEqual(classify(b["input"]),"REJECT_ROOT_THIRD_POINT_WITHOUT_CHILD_GRAMMAR")

    def test_author_pan_divergence_not_universal_pan_exit(self):
        c=self.cases["g1_pan_divergence_not_exit"]
        self.assertEqual(classify(c["input"]),"REJECT_PAN_DIVERGENCE_AS_SUFFICIENT")
        self.assertTrue(self.contract["scope"]["pan_divergence_only_not_universal_pan_exit"])

    def test_an_event_may_not_be_used_before_first_known(self):
        self.assertEqual(classify(self.cases["asof_before_first_known"]["input"]),"PENDING_ASOF_CONFIRMATION")
        self.assertEqual(classify(self.cases["future_center_label_not_ready"]["input"]),"PENDING_ASOF_CONFIRMATION")

    def test_global_conclusion_rejected(self):
        c=self.cases["g1_no_global_pan_claim"]
        self.assertEqual(classify(c["input"]),"REJECT_GLOBAL_NO_PAN_PROMOTION")

    def test_prior_f01_and_m66_really_executed(self):
        res=audit()
        self.assertEqual(res["prior_f01_negative_rejections"],6)
        self.assertEqual(res["root_pan_exit"],"OPEN")
        self.assertEqual(res["market"],"NOT_RUN")
        self.assertEqual(res["orders"],0)

    def test_no_new_algorithm_claimed(self):
        self.assertFalse(self.contract["missing_independent_witness"]["formal_global_impossibility_claim"])
        self.assertFalse(self.contract["missing_independent_witness"]["source_available"])
        self.assertEqual(self.contract["status"]["A087_second_center_formula"],"UNKNOWN")

if __name__=="__main__":
    unittest.main()
