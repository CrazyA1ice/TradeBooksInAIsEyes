"""Offline safeguards for original Chanlun figure numbering and rule provenance.

Structural/content checks only: source high-DPI review was done separately in
GitHub Actions; passing these tests is not proof of pixel-level price mapping.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/11_前课图例溯源与新笔版本时间线.md"
GAPS = ROOT / "deliverables/chanlun_108_acceptance/00_REVIEW/DETAIL_COVERAGE_GAPS.md"
RENDER = ROOT / "tools/render_chanlun_priority_original_pages.py"
LESSONS = ROOT / "analyses/books/chanlun/chapters"
WORKFLOW = ROOT / ".github/workflows/chanlun-priority-original-figure-render.yml"


class FigureLineageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guide = GUIDE.read_text(encoding="utf-8")
        cls.gaps = GAPS.read_text(encoding="utf-8")
        cls.renderer = RENDER.read_text(encoding="utf-8")

    def test_20_page_second_set_is_separate_and_not_proof_of_pixel_read(self):
        script = self.renderer
        self.assertIn("TARGETS_LINEAGE", script)
        self.assertIn("3: [221, 224, 230, 233, 234, 236, 237, 239, 242, 247", script)
        self.assertIn("251, 252, 253, 294, 295, 296, 297, 298, 299]", script)
        self.assertIn("5: [399]", script)
        self.assertIn('choices=["priority", "lineage"]', script)
        self.assertIn('targets = TARGETS if args.target_set == "priority" else TARGETS_LINEAGE',script)
        w=WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("--target-set lineage",w)
        self.assertIn("retention-days: 7",w)
        self.assertIn("chanlun-source-figure-lineage-evidence",w)

    def test_original_58_two_numbered_figures_not_silently_identified(self):
        text=(LESSONS/"lesson_058.md").read_text(encoding="utf-8")
        for term in ("p.230","p.233","2007-06-06","2007-06-04","7、8、9","编号系统不能直接混用"):
            self.assertIn(term,text)
        for term in ("p.230","p.233","2007-06-06","CANDIDATES_LOCATED"):
            self.assertIn(term,self.guide)
        self.assertIn("FIGURE_CANDIDATES_LOCATED",self.gaps)

    def test_59_original_numbers_remain_text_and_mapping_pending(self):
        text=(LESSONS/"lesson_059.md").read_text(encoding="utf-8")
        for term in ("3994.57","3994.21","7中最后一个高点","8下来","PRICE_TO_PIXEL_PENDING"):
            self.assertIn(term,text)
            self.assertIn(term,self.guide)
        self.assertIn("前面一课的7-8-9", self.guide)
        self.assertIn("PRICE_TO_PIXEL_PENDING",self.gaps)
        self.assertNotIn("PRICE_TO_PIXEL_VERIFIED",text)
        self.assertNotIn("PRICE_TO_PIXEL_VERIFIED",self.guide)

    def test_lesson_62_rules_time_and_figure_identity_distinct(self):
        text=(LESSONS/"lesson_062.md").read_text(encoding="utf-8")
        for term in ("张大山习作","FHSL 20080727","2007-06-23 16:15:21","UNKNOWN_SOURCE_DATE","至少有3根K线"):
            self.assertIn(term,text)
            self.assertIn(term,self.guide)
        self.assertIn("TEXT_CONDITIONS_READ",self.gaps)
        self.assertIn("UNKNOWN_SOURCE_DATE",self.gaps)

    def test_108_two_independent_same_day_essays_and_later_charts(self):
        text=(LESSONS/"lesson_108.md").read_text(encoding="utf-8")
        for term in ("2008-08-29 09:15:01","2008-08-29 15:11:47","p.398"):
            self.assertIn(term,text)
            self.assertIn(term,self.guide)
        self.assertIn("2008年10月",self.guide)
        self.assertIn("AS_OF_CAUSALITY_BOUNDARY_CONFIRMED",self.gaps)

    def test_original_evidence_stays_unique_and_no_backtest(self):
        accept=ROOT/"deliverables/chanlun_108_acceptance"
        self.assertFalse(list(accept.rglob("*.pdf")))
        self.assertFalse(list(accept.rglob("*.jpg")))
        self.assertFalse(list(accept.rglob("*.png")))
        self.assertIn("NOT_RUN",self.guide)
        self.assertIn("不在仓库复制",self.guide)
        info=json.loads((ROOT/"reports/source_inventory/chanlun_20261107_verified.json").read_text(encoding="utf-8"))
        vol3=next(x for x in info["volumes"] if x["path"].endswith("卷3.pdf"))
        self.assertIn(vol3["sha256"],(LESSONS/"lesson_059.md").read_text(encoding="utf-8"))
        self.assertTrue(vol3["sha256"] and len(vol3["sha256"])==64)


if __name__=="__main__":
    unittest.main()
