"""Second-pass cross-lesson source and interpretation-proof boundary tests."""
import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"tools/audit_chanlun_theory_second_pass.py"
spec=importlib.util.spec_from_file_location("whole_book_deep_theory",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class WholeBookDeepTheoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=m.load(m.LEDGER)
        cls.essay=m.ESSAY.read_text(encoding="utf-8")

    def test_second_pass_has_16_reproducible_theory_arguments(self):
        receipt=m.verify()
        self.assertEqual(receipt["arguments"],16)
        self.assertGreaterEqual(receipt["distinct_source_claims"],45)
        self.assertEqual(receipt["original_volumes"],5)
        self.assertEqual(receipt["real_market_experiment"],"NOT_RUN")

    def test_every_argument_is_source_anchored_with_open_premises(self):
        for row in self.ledger["arguments"]:
            with self.subTest(id=row["id"]):
                self.assertGreaterEqual(len(row["source_claims"]),2)
                self.assertGreaterEqual(len(row["open_premises"]),2)
                self.assertFalse(row["formal_proof_completed"])
                self.assertEqual(row["market_empirical_test"],"NOT_RUN")

    def test_statement_set_contains_conditional_nonimplication_and_open_proof(self):
        categories={x["reasoning_role"] for x in self.ledger["arguments"]}
        self.assertEqual(categories,m.PERMITTED)
        for id_ in ("D04","D06","D08","D10","D14"):
            row=next(x for x in self.ledger["arguments"] if x["id"]==id_)
            self.assertEqual(row["reasoning_role"],"NON_IMPLICATION")

    def test_buypoint_coverage_not_profit_safety_and_second_third_can_overlap(self):
        self.assertIn("三类买卖点",self.essay)
        self.assertIn("B2∩B3",self.essay)
        self.assertIn("不要求集合两两不相交",self.essay)
        self.assertIn("分类覆盖定理",self.essay)
        self.assertIn("安全收益定理",self.essay)

    def test_divergence_is_not_macd_retroactive_segment_proof(self):
        for x in ("MACD","A_C(t)","乘二","ESTIMATED_DIVERGENCE",
                  "CONFIRMED_AFTER_C_END","不是充分条件"):
            self.assertIn(x,self.essay)

    def test_recursion_associativity_is_not_uniqueness_proof(self):
        for x in ("结合律","[ab]","[a][b]","OB38-UNIQUE","OB38-ASOF",
                  "最多只有一个有效解析","固定同级别"):
            self.assertIn(x,self.essay)

    def test_versioned_pen_segment_and_theory_self_isomorphism_separated(self):
        for x in ("f1(a0)=a1","f2(an)=an+1","双射",
                  "辅助元素","严格特征序列","第81课"):
            self.assertIn(x,self.essay)

    def test_real_asof_and_future_quantifiers_not_confused(self):
        self.assertIn("∀ future",self.essay)
        self.assertIn("∃ future",self.essay)
        self.assertIn("UNKNOWN/PENDING/INSUFFICIENT_DATA",self.essay)
        self.assertIn("2008年10月",self.essay)
        self.assertIn("2008年8月29日",self.essay)

    def test_original_pdfs_and_actual_trades_not_falsely_authenticated(self):
        for key in m.OPEN_LIMITS:
            self.assertIs(self.ledger[key],False)
        self.assertFalse(any(x["formal_proof_completed"]
                             for x in self.ledger["arguments"]))
        self.assertIn("NOT_RUN",self.essay)

    def test_source_card_claims_exist_with_page_origin(self):
        refs=set()
        for item in self.ledger["arguments"]:
            for claim in item["source_claims"]:
                n=claim["lesson"]
                data=m.load(ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json")
                entry=next(c for c in data["claims"] if c["id"]==claim["claim_id"])
                self.assertEqual(entry["kind"],"SOURCE")
                self.assertTrue(entry["pdf_pages"])
                refs.add((n,claim["claim_id"]))
        self.assertGreaterEqual(len(refs),45)

    def test_no_presumption_that_first_pass_source_label_is_independently_authenticated(self):
        self.assertIn("不能自动给它归原发作者",self.essay)
        self.assertIn("不是冒充作者当年的原文定理",self.essay)
        self.assertIn("部分页面",self.essay)

    def test_18_native_original_pages_are_exactly_pinned_across_five_pdf_volumes(self):
        pins=m.load(ROOT/"reports/source_inventory/chanlun_theory_second_pass_native_text_sha256.json")
        self.assertEqual(pins["method"],"pymupdf_1.26.7_get_text_sort_true")
        self.assertEqual(pins["original_pages_count"],18)
        self.assertEqual(len(pins["original_pages_native_text_sha256"]),18)
        self.assertEqual(set(pins["original_pdf_sha256"]),{"1","2","3","4","5"})
        self.assertTrue(all(len(v)==64 for v in pins["original_pages_native_text_sha256"].values()))
        self.assertFalse(pins["original_pdf_images_inspected"])
        self.assertFalse(pins["real_market_data_read"])

    def test_full_book_main_index_links_second_pass(self):
        index=(ROOT/"deliverables/chanlun_108_acceptance/README.md").read_text(encoding="utf-8")
        self.assertIn(m.ESSAY.name,index)
        primary=m.SYNTHESIS.read_text(encoding="utf-8")
        self.assertIn(m.ESSAY.name,primary)


if __name__=="__main__":
    unittest.main()
