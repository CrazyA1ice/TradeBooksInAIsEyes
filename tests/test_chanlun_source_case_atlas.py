"""Read-only audit of the Chanlun reader atlas against canonical *existing* source evidence.

This does not fetch PDF pages, inspect chart pixels, or test live markets.
It checks provenance and the honesty of editorial/visual limitations.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/09_原书关键案例与定理证据对照.md"
EVIDENCE = ROOT / "knowledge/evidence"
SOURCE_REPORTS = ROOT / "reports/source_inventory"


class SourceCaseAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = ATLAS.read_text(encoding="utf-8")
        cls.case_sections = {}
        bits = re.split(r"(?=^## SRC-(?:009|024|035|053|059|062|071|100|108)｜)", cls.text, flags=re.M)
        for bit in bits:
            match = re.match(r"## SRC-([0-9]{3})｜", bit)
            if match:
                cls.case_sections[match.group(1)] = bit

    def test_all_nine_cases_are_unique_and_have_source_paths(self):
        lessons = {"009":9, "024":24, "035":35, "053":53, "059":59,
                   "062":62, "071":71, "100":100, "108":108}
        self.assertEqual(set(self.case_sections), set(lessons))
        self.assertEqual(len(re.findall(r"^## SRC-", self.text, flags=re.M)), len(lessons))
        for cid, lesson in lessons.items():
            with self.subTest(case=cid):
                section = self.case_sections[cid]
                source = EVIDENCE / f"chanlun_lesson{lesson:03}.json"
                evidence = json.loads(source.read_text(encoding="utf-8"))
                self.assertTrue(evidence["source"]["pdf_pages"])
                self.assertIn(f"knowledge/evidence/chanlun_lesson{lesson:03}.json", section)
                self.assertRegex(section, r"卷[一二三四五]")
                self.assertRegex(section, r"p[.]?[0-9]")
                self.assertIn("AI", section)
                self.assertRegex(section, r"【待核")
                self.assertRegex(section, r"VISUAL_LIMITED|PROVENANCE_LIMITED|UNVERIFIED|LIMITED")
                self.assertIn(f'<a id="src-{cid}"></a>', self.text)
                self.assertIn(f"[SRC-{cid}](#src-{cid})", self.text)

    def test_orig_009_probability_is_claimed_in_source_text(self):
        source = json.loads((EVIDENCE/"chanlun_lesson009.json").read_text(encoding="utf-8"))
        claims = "\n".join(x.get("summary", "") for x in source["claims"] if x.get("kind")=="SOURCE")
        for part in ("30%", "40%", "3.6%"):
            self.assertIn(part, claims)
            self.assertIn(part, self.case_sections["009"])
        self.assertIn("条件", self.case_sections["009"])

    def test_orig_059_prices_exist_in_source_text_not_verified_figures(self):
        source = json.loads((EVIDENCE/"chanlun_lesson059.json").read_text(encoding="utf-8"))
        claims = " ".join(x.get("summary", "") for x in source["claims"] if x.get("kind")=="SOURCE")
        for price in ("3994.57", "3994.21"):
            self.assertIn(price, claims)
            self.assertIn(price, self.case_sections["059"])
        self.assertFalse(source["quality"]["figure_prices_verified"])
        self.assertIn("原图", self.case_sections["059"])

    def test_source_053_has_independent_2009_addition(self):
        report = (SOURCE_REPORTS/"chanlun_lessons051_055_source_layers.md").read_text(encoding="utf-8")
        self.assertIn("2009-01-05 12:00:58", report)
        self.assertIn("p.162", report)
        self.assertIn("2007-05-23", self.case_sections["053"])
        self.assertIn("2009-01-05", self.case_sections["053"])
        self.assertIn("PROVENANCE_LIMITED", self.case_sections["053"])

    def test_062_077_081_are_not_silently_mixed(self):
        section = self.case_sections["062"]
        for n in (62,77,81):
            self.assertIn(f"knowledge/evidence/chanlun_lesson{n:03}.json", section)
        source81 = json.loads((EVIDENCE/"chanlun_lesson081.json").read_text(encoding="utf-8"))
        self.assertTrue(any("9月18日" in x.get("summary","") for x in source81["claims"] if x.get("kind")=="SOURCE"))
        self.assertIn("UNKNOWN_SOURCE_DATE", section)

    def test_100_editorial_disagreement_is_not_declared_proven(self):
        report = (SOURCE_REPORTS/"chanlun_lessons096_100_source_visual_review.md").read_text(encoding="utf-8")
        self.assertIn("娇注", report)
        section = self.case_sections["100"]
        for term in ("娇注", "没有", "不能", "编者", "UNVERIFIED"):
            self.assertIn(term, section)
        self.assertIn("作者原", section)

    def test_108_distinct_bottom_definitions_and_visual_gap(self):
        source = json.loads((EVIDENCE/"chanlun_lesson108.json").read_text(encoding="utf-8"))
        claims = " ".join(x.get("summary","") for x in source["claims"] if x.get("kind")=="SOURCE")
        for term in ("2284", "2952", "三买", "三卖"):
            self.assertIn(term, claims)
            self.assertIn(term, self.case_sections["108"])
        self.assertFalse(source["quality"]["fine_chart_numeric_verified"])
        section=self.case_sections["108"]
        for word in ("分型", "走势类型", "未", "2008-08-29", "VISUAL_LIMITED"):
            self.assertIn(word, section)

    def test_atlas_cannot_be_misrepresented_as_new_image_review_or_backtest(self):
        self.assertGreaterEqual(self.text.count("```mermaid"), 7)
        self.assertIn("没有重新逐页打开五卷PDF图片", self.text)
        self.assertIn("NOT_RUN", self.text)
        self.assertIn("AI教学重画", self.text)
        self.assertIn("PDF物理页", self.text)
        self.assertNotIn("所有原图已逐项核验", self.text)


if __name__=="__main__":
    unittest.main()
