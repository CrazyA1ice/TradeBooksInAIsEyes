"""Source-text-first regression tests for Chanlun argument dependency reading.

This is a documentary-logic check, *not* a proof of the author's theorems.
No image rendering, OCR, financial backtest, or code generator.
"""
import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/12_只读原文逻辑主线与证明缺口.md"
GUIDE = ATLAS.parent / "README.md"
LANDING = ROOT / "deliverables/chanlun_108_acceptance/README.md"
WORKFLOW = ROOT / "docs/BOOK_RESEARCH_WORKFLOW.md"
FIGURE_WORKFLOW = ROOT / ".github/workflows/chanlun-priority-original-figure-render.yml"
LESSONS = [15,17,20,21,24,27,33,35,53,62,65,67,71,77,81,99,100,102,108]


class SourceTextFirstLogicAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = ATLAS.read_text(encoding="utf-8")

    def test_eight_accurate_chain_sections_and_proof_obligations(self):
        sections = re.findall(r"^## 第[一二三四五六七八]链：", self.text, flags=re.M)
        self.assertEqual(len(sections), 8)
        for tag in ("【作者原文主张】", "【逻辑关系】", "【AI审查】"):
            self.assertGreaterEqual(self.text.count(tag), 8, tag)
        for concept in ("存在", "唯一", "实时", "完备", "安全", "后附", "NOT_RUN"):
            self.assertIn(concept, self.text)
        for issue in ("P0-A", "P0-B", "P0-C", "P1-D", "P1-E"):
            self.assertIn(issue, self.text)

    def test_every_critical_source_has_original_written_evidence(self):
        for lesson in LESSONS:
            with self.subTest(lesson=lesson):
                link = f"knowledge/evidence/chanlun_lesson{lesson:03}.json"
                self.assertIn(link, self.text)
                obj = json.loads((ROOT / link).read_text(encoding="utf-8"))
                self.assertTrue(obj["source"]["pdf_pages"])
                self.assertTrue(any(x.get("kind") == "SOURCE" for x in obj.get("claims", [])))

    def test_no_image_or_charts_or_new_trade_claims(self):
        self.assertNotIn("```mermaid", self.text)
        self.assertNotIn("<img", self.text)
        self.assertNotRegex(self.text, r"\]\([^)]*\.(?:png|jpe?g|webp)")
        self.assertIn("本轮改变研究方向：文字优先", self.text)
        self.assertIn("图", self.text)  # only described as deprioritized evidence
        self.assertIn("无行情检验、无交易回测", self.text)
        self.assertIn("没有", self.text)

    def test_local_references_resolve_and_no_duplicate_sources(self):
        links = re.findall(r"\]\(([^)]+)\)", self.text)
        checked = 0
        for ref in links:
            if ref.startswith(("https://", "http://", "#", "mailto:")):
                continue
            dest = (ATLAS.parent / unquote(ref.split("#",1)[0])).resolve()
            with self.subTest(ref=ref):
                self.assertTrue(dest.exists(), str(dest))
                self.assertTrue(ROOT == dest or ROOT in dest.parents)
            checked += 1
        self.assertGreaterEqual(checked, 20)
        accept = ATLAS.parent
        self.assertFalse(list(accept.glob("*.jpg")))
        self.assertFalse(list(accept.glob("*.png")))
        self.assertFalse(list(accept.glob("*.pdf")))

    def test_reading_route_and_workflow_prioritize_text(self):
        for file in (GUIDE, LANDING, WORKFLOW):
            with self.subTest(file=file.name):
                text = file.read_text(encoding="utf-8")
                self.assertIn(ATLAS.name, text)
                self.assertRegex(text, "文字|原文")
        work = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("TEXT_FIRST_LOGIC_AUDIT", work)
        self.assertIn("暂停", work)

    def test_original_figure_workflow_is_opt_in_only(self):
        flow = FIGURE_WORKFLOW.read_text(encoding="utf-8")
        header = flow.split("permissions:",1)[0]
        self.assertIn("workflow_dispatch:", header)
        self.assertNotIn("pull_request:", header)
        self.assertNotIn("push:", header)
        self.assertIn("opt-in only", header.lower())


if __name__ == "__main__":
    unittest.main()
