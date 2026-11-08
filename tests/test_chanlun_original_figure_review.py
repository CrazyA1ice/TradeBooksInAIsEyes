"""Offline regression of carefully scoped original-PDF source figure observations.

The render workflow independently checks source hashes/pages and emits temporary
images; these tests prevent accidental overclaims and provenance backdating.
No OCR, no page pixels cached in repository, no market experiments.
"""
from __future__ import annotations
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/10_原书图像实页复核与后发资料辨析.md"
GAPS = ROOT / "deliverables/chanlun_108_acceptance/00_REVIEW/DETAIL_COVERAGE_GAPS.md"
PRESENTER = ROOT / "tools/render_chanlun_priority_original_pages.py"
INVENTORY = ROOT / "reports/source_inventory/chanlun_20261107_verified.json"
LESSONS = ROOT / "analyses/books/chanlun/chapters"

class OriginalFigureEvidenceRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atlas = ATLAS.read_text(encoding="utf-8")
        cls.gaps = GAPS.read_text(encoding="utf-8")
        cls.render = PRESENTER.read_text(encoding="utf-8")

    def test_source_sha_three_volumes_fixed(self):
        inv = json.loads(INVENTORY.read_text(encoding="utf-8"))["volumes"]
        self.assertEqual(len(inv), 5)
        for n in (1, 3, 5):
            with self.subTest(volume=n):
                x=next(x for x in inv if x["path"].endswith(f"卷{n}.pdf"))
                self.assertIn(x["sha256"], self.atlas)
                self.assertIn(f"volume{n}", self.render)

    def test_exact_target_page_count_and_reproducible_ci_artifact(self):
        # This is deliberately strict for this scoped milestone only.
        self.assertRegex(self.render, r"MAX_PAGES = 20")
        self.assertIn("162, 254, 255, 256, 257, 292, 293, 294, 295, 296, 297, 300, 301", self.render)
        self.assertIn("225, 395, 396, 397, 398, 400", self.render)
        self.assertIn("RENDERED_NOT_INDEPENDENTLY_VISUALLY_VERIFIED", self.render)
        self.assertIn('ROOT in out.parents', self.render)
        self.assertIn("retention", (ROOT / ".github/workflows/chanlun-priority-original-figure-render.yml").read_text())
        self.assertIn("20个指定物理页", self.atlas)

    def test_lesson009_chart_not_math_image(self):
        text=(LESSONS/"lesson_009.md").read_text(encoding="utf-8")
        self.assertIn("武钢JTB1(580001)", text)
        self.assertIn("并非数学公式图", text)
        self.assertNotIn("mathematical body on image page not yet visually verified", text)
        self.assertIn("p.30并非数学公式图", self.gaps)
        self.assertIn("日K线图", self.atlas)

    def test_lesson059_price_text_not_relabelled_as_chart(self):
        text=(LESSONS/"lesson_059.md").read_text(encoding="utf-8")
        for term in ("3994.57","3994.21","p.257无内嵌图","20—45","7—8—9"):
            self.assertIn(term,text)
            self.assertIn(term,self.atlas)
        self.assertIn("VISUAL_LIMITED",self.gaps)

    def test_lesson062_later_figure_stays_separate(self):
        text=(LESSONS/"lesson_062.md").read_text(encoding="utf-8")
        for term in ("张大山习作","FHSL 20080727","2007-06-30"):
            self.assertIn(term,text)
            self.assertIn(term,self.atlas)
        self.assertIn("PROVENANCE_LIMITED",self.gaps)

    def test_lesson108_anachronism_cannot_be_predated(self):
        text=(LESSONS/"lesson_108.md").read_text(encoding="utf-8")
        for term in ("2007年10月—2008年10月","2008-08-29","2284","2952","p.398"):
            self.assertIn(term,text)
            self.assertIn(term,self.atlas)
        self.assertRegex(self.atlas,r"后验|后附")
        self.assertIn("不能倒当作作者8月29日实时已知行情",text)
        self.assertIn("p.398图题明说",self.gaps)

    def test_unreviewed_images_are_not_misreported_as_finished(self):
        for phrase in ("FINE_CHART_NOT_EXHAUSTIVE","PROVENANCE_LIMITED","NOT_RUN",
                       "不是整章所有页面","没有核对五卷全部图表"):
            self.assertIn(phrase,self.atlas)
        self.assertNotIn("五卷所有图片已完全复核",self.atlas)
        self.assertNotIn("所有价位均已核实",self.atlas)
        self.assertIn("VISUAL_PARTIAL_REVIEWED",self.gaps)
        self.assertIn("PROVENANCE_PARTIAL_REVIEWED",self.gaps)

    def test_original_pdfs_are_not_recopied_into_acceptance(self):
        accept=ROOT/"deliverables/chanlun_108_acceptance"
        self.assertFalse(list(accept.rglob("*.pdf")))
        self.assertFalse(list(accept.rglob("*.jpg")))
        self.assertFalse(list(accept.rglob("*.png")))
        self.assertIn("临时",self.atlas)

if __name__=="__main__":
    unittest.main()
