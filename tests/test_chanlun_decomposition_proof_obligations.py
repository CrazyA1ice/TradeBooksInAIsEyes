"""Read-only invariants of the Chanlun decomposition textual proof-obligation guide.

This validates source trails and epistemic distinctions, NOT mathematical truth
of the author's claims. No PDF visual inspection or market experiment.
"""
import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/13_走势分解定理的逐命题逻辑审查.md"
LESSONS = [17, 33, 35, 36, 38, 39, 99, 102]


class ChanlunDecompositionProofObligations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = DOC.read_text(encoding="utf-8")

    def test_all_eight_original_lessons_are_linked_to_canonical_source(self):
        for n in LESSONS:
            with self.subTest(n=n):
                slug = f"chanlun_lesson{n:03}.json"
                self.assertIn(slug, self.text)
                evidence = json.loads((ROOT/"knowledge/evidence"/slug).read_text(encoding="utf-8"))
                claims = evidence.get("claims", [])
                self.assertTrue(any(c.get("kind") == "SOURCE" for c in claims))
                self.assertTrue(evidence.get("source", {}).get("pdf_pages"))
        for n in [35, 38, 99, 102]:
            self.assertIn(f"lesson_{n:03}.md", self.text)

    def test_theorem_one_vs_two_vs_unique_are_not_conflated(self):
        for label in ["P35-1", "P35-2", "P35-A", "P38", "P99/102"]:
            self.assertIn(label, self.text)
        for idea in ["三种走势类型", "至少三个", "不能直接推出唯一", "第38课", "盘整＋盘整"]:
            self.assertIn(idea, self.text)
        self.assertIn("OB-EXIST", self.text)
        self.assertIn("OB-CANONICAL", self.text)
        self.assertIn("OB-ASOF", self.text)
        self.assertIn("OB-HIGHER", self.text)

    def test_38_bridge_has_real_writing_evidence(self):
        source=json.loads((ROOT/"knowledge/evidence/chanlun_lesson038.json").read_text(encoding="utf-8"))
        summaries=" ".join(c["summary"] for c in source["claims"] if c["kind"]=="SOURCE")
        self.assertIn("唯一性", summaries)
        self.assertIn("盘整+盘整", summaries)
        self.assertIn("固定同级别", self.text)
        self.assertIn("作者声称", self.text)
        self.assertIn("∀x∈D_R", self.text)

    def test_compiled_charts_are_not_used_as_proof_and_no_backtests(self):
        for token in ["TEXT_ONLY_ARGUMENT_ANALYSIS", "AUTHOR_CLAIM",
                      "AI_FORMALIZATION", "OPEN_PROOF_OBLIGATION", "NOT_RUN"]:
            self.assertIn(token, self.text)
        self.assertNotIn("```mermaid", self.text)
        self.assertNotIn("<img", self.text)
        self.assertNotRegex(self.text, r"\]\([^)]*\.(?:png|jpe?g|webp)")
        for expr in ["本篇只讨论作者的文字逻辑", "不是原作者原公式", "仍不", "不能单独证明"]:
            self.assertIn(expr, self.text)
        self.assertNotIn("已对所有行情唯一性进行了形式证明", self.text)

    def test_all_local_file_links_exist(self):
        refs = re.findall(r"\]\(([^)]+)\)", self.text)
        count=0
        for ref in refs:
            if ref.startswith(("http://", "https://", "#", "mailto:")):
                continue
            p=(DOC.parent/unquote(ref.split("#",1)[0])).resolve()
            with self.subTest(ref=ref):
                self.assertTrue(ROOT == p or ROOT in p.parents)
                self.assertTrue(p.exists(), str(p))
            count+=1
        self.assertGreaterEqual(count, 22)

    def test_navigation_is_primary_and_previous_logic_is_updated(self):
        for relative in ["deliverables/chanlun_108_acceptance/README.md",
                         "deliverables/chanlun_108_acceptance/04_AI_GUIDE/README.md",
                         "deliverables/chanlun_108_acceptance/04_AI_GUIDE/12_只读原文逻辑主线与证明缺口.md"]:
            with self.subTest(relative=relative):
                text=(ROOT/relative).read_text(encoding="utf-8")
                self.assertIn(DOC.name, text)


if __name__ == "__main__":
    unittest.main()
