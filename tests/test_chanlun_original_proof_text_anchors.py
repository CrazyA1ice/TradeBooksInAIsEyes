"""Check that a text-only Chanlun theorem reading remains provenance-correct.

The separate pinned-PyMuPDF CI job verifies original native PDF page hashes.
These tests cover source audit configuration and reader-facing claim boundaries.
They do not prove the author's mathematics or access chart images.
"""
import importlib.util
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/inspect_chanlun_original_proof_text_readonly.py"
DOC = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/14_原PDF原句核对_定理与同级别唯一性.md"
CI = ROOT / ".github/workflows/chanlun-original-theorem-text-check.yml"

spec = importlib.util.spec_from_file_location("chanlun_native_proof_text", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class OriginalProofTextReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = DOC.read_text(encoding="utf-8")

    def test_exact_page_fingerprints_for_three_canonical_volumes(self):
        keys = {(v, p) for v, pages in audit.TARGETS.items() for p in pages}
        self.assertEqual(len(keys), 11)
        self.assertEqual(keys, set(audit.EXPECTED_TEXT_SHA256))
        for key in keys:
            with self.subTest(page=key):
                self.assertRegex(audit.EXPECTED_TEXT_SHA256[key], r"^[0-9a-f]{64}$")
        self.assertEqual(set(audit.TARGETS), {1, 2, 5})
        self.assertEqual(set(audit.REQUIRED_TEXT_ANCHORS) - keys, set())
        self.assertIn((2, 292), audit.REQUIRED_TEXT_ANCHORS)
        self.assertIn((2, 339), audit.REQUIRED_TEXT_ANCHORS)
        self.assertIn((5, 202), audit.REQUIRED_TEXT_ANCHORS)

    def test_two_theorem_labels_are_both_original_and_order_is_recorded(self):
        checks = audit.REQUIRED_TEXT_ANCHORS[(2, 292)]
        for token in ("走势分解定理一", "走势分解定理二", "结合律"):
            self.assertIn(token, checks)
        for token in ("定理一", "定理二", "三段", "盘整", "下跌", "上涨"):
            self.assertIn(token, self.text)
        self.assertIn("主语是", self.text)

    def test_chosen_level_vs_lower_level_and_two_base_cases(self):
        for token in ("最低不可分解级别", "三笔同价", "单位K线",
                      "选定级别", "低于g的级别", "盘整＋盘整", "不定义中枢延伸"):
            self.assertIn(token, self.text)
        self.assertIn("同级别的划分", self.text)
        self.assertIn("娇注", self.text)

    def test_following_higher_center_claim_is_not_declared_proven(self):
        for token in ("第99课", "30分钟", "必然", "全域", "没有", "NOT_RUN"):
            self.assertIn(token, self.text)
        self.assertIn("不能由重括号直接推出", self.text)
        self.assertIn("严格", self.text)
        self.assertNotIn("已经完成唯一性严格证明", self.text)

    def test_text_only_ci_no_automatic_chart_processing(self):
        s = SCRIPT.read_text(encoding="utf-8")
        workflow = CI.read_text(encoding="utf-8")
        self.assertIn("pymupdf", s)
        self.assertNotIn("get_pixmap", s)
        self.assertNotIn("pytesseract", s.lower())
        self.assertNotIn("get_textpage_ocr", s)
        self.assertNotIn("render_chanlun_priority_original_pages", workflow)
        self.assertIn('PyMuPDF==1.26.7', workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("pull_request:", workflow)

    def test_original_pdf_links_resolve_without_copying_text(self):
        links = re.findall(r"\]\(([^)]+)\)", self.text)
        count = 0
        for ref in links:
            if ref.startswith(("http:", "https:", "#")):
                continue
            p = (DOC.parent / unquote(ref.split("#", 1)[0])).resolve()
            with self.subTest(ref=ref):
                self.assertTrue(p.exists(), str(p))
                self.assertTrue(p == ROOT or ROOT in p.parents)
            count += 1
        self.assertGreaterEqual(count, 16)
        for fragment in ("TEXT_FIRST_NO_IMAGE", "EDITORIAL_ROLE_SEPARATED",
                         "SOURCE_PDF_NATIVE_TEXT_VERIFIED", "AI_PROOF_OBLIGATIONS_OPEN"):
            self.assertIn(fragment, self.text)
        self.assertNotIn("```mermaid", self.text)
        self.assertNotIn("<img", self.text)

    def test_reader_navigation_and_previous_report_correction(self):
        for relative in ("deliverables/chanlun_108_acceptance/README.md",
                         "deliverables/chanlun_108_acceptance/04_AI_GUIDE/README.md",
                         "deliverables/chanlun_108_acceptance/04_AI_GUIDE/12_只读原文逻辑主线与证明缺口.md",
                         "deliverables/chanlun_108_acceptance/04_AI_GUIDE/13_走势分解定理的逐命题逻辑审查.md"):
            content = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(relative=relative):
                self.assertIn(DOC.name, content)


if __name__ == "__main__":
    unittest.main()
