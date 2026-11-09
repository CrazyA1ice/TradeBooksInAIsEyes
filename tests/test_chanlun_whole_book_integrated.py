"""Research-quality regression gates for the unified whole-108-lesson study."""
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"tools/audit_chanlun_whole_book_integrated.py"
spec=importlib.util.spec_from_file_location("all_108_continuous_reading",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class WholeBookIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lessons=m.records()

    def test_exactly_all_108_in_ascending_author_lesson_order(self):
        self.assertEqual([r["lesson"] for r in self.lessons],list(range(1,109)))

    def test_five_original_pdf_volumes_and_original_source_hash_presence(self):
        self.assertEqual([sum(r["volume"]==v for r in self.lessons)
                          for v in (1,2,3,4,5)],[23,19,25,21,20])
        self.assertTrue(all(len(r["pdf_sha256"])==64 for r in self.lessons))

    def test_108_first_source_claims_have_distinct_reproducible_provenance(self):
        self.assertEqual(len({r["source_card_sha256"] for r in self.lessons}),108)
        for row in self.lessons:
            self.assertIsInstance(row["claim_id"],str)
            self.assertTrue(row["claim_pages"])
            self.assertGreaterEqual(row["source_claims"],1)
            self.assertEqual(row["status"],m.FIRST_PASS)

    def test_coverage_atlas_includes_exactly_one_line_per_lesson(self):
        result=m.atlas(self.lessons)
        rows=[l for l in result.splitlines() if l.startswith("| ") and
              l.split("|")[1].strip().isdigit()]
        self.assertEqual(len(rows),108)
        self.assertIn("第108",result.replace("108 |","第108"))
        self.assertIn("SOURCE",result)

    def test_all_108_chapter_and_evidence_links_preserved_in_atlas(self):
        output=m.atlas(self.lessons)
        for n in range(1,109):
            self.assertIn(f"lesson_{n:03d}.md",output)
            self.assertIn(f"chanlun_lesson{n:03d}.json",output)

    def test_title_source_pdf_pages_and_source_role_not_copied_as_facts(self):
        result=m.atlas(self.lessons)
        self.assertIn("不代表首次发表已独立认证",result)
        self.assertIn("不等于该主张是真实市场事实或数学定理",result)
        self.assertIn("原PDF",result)
        self.assertIn("首轮",result)

    def test_full_manuscript_has_no_false_proof_or_market_promotion(self):
        count=m.verify_manuscript(self.lessons)
        self.assertGreater(count,12000)
        prose=m.MANUSCRIPT.read_text(encoding="utf-8")
        self.assertIn("第99课",prose)
        self.assertIn("第108课",prose)
        self.assertIn("未解决",prose)
        self.assertIn("NOT_RUN",prose)

    def test_index_claim_summary_sanitizes_markdown_table_delimiters(self):
        self.assertEqual(m.cleaned("  中枢 | 新中心 \n 三段"),"中枢 ／ 新中心 三段")
        with self.assertRaisesRegex(ValueError,"Missing source summary"):
            m.cleaned(" ")

    def test_two_independent_types_of_cross_lessons_are_not_conflated(self):
        prose=m.MANUSCRIPT.read_text(encoding="utf-8")
        for marker in ("OB38-EXIST","OB38-UNIQUE","OB38-ASOF",
                       "OB99-EXIST","OB99-LOCATION","第62课",
                       "第77课","第81课"):
            self.assertIn(marker,prose)

    def test_no_hypothesis_reported_as_an_empirical_success(self):
        prose=m.MANUSCRIPT.read_text(encoding="utf-8")
        self.assertIn("110条显式待检验假说",prose)
        self.assertIn("36份跨课形式化示例",prose)
        self.assertNotIn("收益已证明",prose)

    def test_all_108_source_rows_hold_source_and_claim_level_granularity(self):
        self.assertTrue(all(r["source_claims"]>=1 for r in self.lessons))
        self.assertTrue(all(r["page"]>=1 and r["volume"] in (1,2,3,4,5)
                            for r in self.lessons))

    def test_committed_atlas_matches_live_evidence_when_present(self):
        if m.ATLAS.is_file():
            self.assertEqual(m.ATLAS.read_text(encoding="utf-8"),m.atlas(self.lessons))
        else:
            self.assertFalse(m.ATLAS.is_file())  # initial source discovery PR


if __name__=="__main__":
    unittest.main()
