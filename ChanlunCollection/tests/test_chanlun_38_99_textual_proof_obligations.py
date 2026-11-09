"""Textual reasoning gates for Chanlun lessons 38/99.

The toy countermodels establish *non-implication of isolated assumptions*.
They are not compliant Chanlun trajectories, validation of author theorems,
stock market data, backtests, or new trading rules.
"""
import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/15_同级别唯一性与高级别必然性的证明审查.md"
PROOF_ANCHOR = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/14_原PDF原句核对_定理与同级别唯一性.md"


def interval_intersection(*intervals):
    """Pure set arithmetic; no claim that these are real Chanlun movements."""
    lo = max(x[0] for x in intervals)
    hi = min(x[1] for x in intervals)
    return (lo, hi) if lo <= hi else None


class LogicalProofObligations38And99(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = DOC.read_text(encoding="utf-8")

    def test_source_ids_have_author_claims_and_fixed_pdf_pages(self):
        for n in (17, 33, 35, 38, 39, 98, 99, 100):
            with self.subTest(lesson=n):
                item = json.loads((ROOT / f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8"))
                self.assertTrue(item["source"]["pdf_pages"])
                self.assertTrue(any(x.get("kind") == "SOURCE" for x in item["claims"]))
                self.assertIn(f"chanlun_lesson{n:03d}.json", self.text)
        for phrase in ("卷二p.338—339", "卷五p.202—203", "首发署时", "作者声称"):
            self.assertIn(phrase, self.text)

    def test_38_asymmetric_rule_is_explicit_and_uniqueness_not_assumed(self):
        for token in ("选定级别g", "低于g的级别", "高于g的级别", "不定义", "不允许",
                      "盘整＋盘整", "OB38-EXIST", "OB38-UNIQUE", "OB38-ASOF", "|P_Rg(x)|=1"):
            self.assertIn(token, self.text)
        self.assertIn("不是", self.text)
        self.assertIn("没有展开逐个竞争切分排除的全域证明", self.text)

    def test_99_exist_location_and_asof_are_distinct(self):
        for token in ("OB99-EXIST", "OB99-LOCATION", "共同交集", "有限t′",
                      "一般性走势划分", "同级别划分", "时间", "后继"):
            self.assertIn(token, self.text)
        self.assertIn("不是第99课的有效反例", self.text)
        self.assertIn("更高级别中枢", self.text)

    def test_associativity_alone_does_not_make_segmentation_unique(self):
        atoms = ("a", "b", "c", "d")
        # Pure concatenation is associative, independently of grouping.
        self.assertEqual(((atoms[:1] + atoms[1:2]) + atoms[2:]),
                         (atoms[:1] + (atoms[1:2] + atoms[2:])))
        partition_1 = (atoms[:2], atoms[2:])
        partition_2 = (atoms[:1], atoms[1:])
        self.assertNotEqual(partition_1, partition_2)
        self.assertEqual(sum((tuple(x) for x in partition_1), ()), atoms)
        self.assertEqual(sum((tuple(x) for x in partition_2), ()), atoms)
        self.assertIn("不是", self.text)
        self.assertIn("“第38课有两个合法解”", self.text)
        self.assertIn("它**不是**", self.text)

    def test_pairwise_overlap_does_not_imply_triple_overlap(self):
        a, b, c = (1,4), (3,6), (5,8)
        self.assertEqual(interval_intersection(a,b), (3,4))
        self.assertEqual(interval_intersection(b,c), (5,6))
        self.assertIsNone(interval_intersection(a,b,c))
        self.assertEqual(interval_intersection((1,4),(2,5),(3,6)),(3,4))
        self.assertIn("这仍不是第99课的有效反例", self.text)

    def test_links_resolve_and_visual_experiments_absent(self):
        refs = re.findall(r"\]\(([^)]+)\)",self.text)
        checked = 0
        for ref in refs:
            if ref.startswith(("https://","http://","#","mailto:")):
                continue
            dst=(DOC.parent / unquote(ref.split("#",1)[0])).resolve()
            with self.subTest(ref=ref):
                self.assertTrue(dst.exists(), str(dst))
                self.assertTrue(dst == ROOT or ROOT in dst.parents)
            checked+=1
        self.assertGreaterEqual(checked,14)
        self.assertNotIn("```mermaid",self.text)
        self.assertNotRegex(self.text,r"\]\([^)]*\.(png|jpe?g|webp)")
        for token in ("TEXT_FIRST_NO_IMAGE","NOT_RUN","ORIGINAL_TEXT_GROUNDED",
                      "OB38_UNIQUENESS_PROOF_OPEN","OB99_HIGHER_CENTER_PROOF_OPEN"):
            self.assertIn(token,self.text)

    def test_entrypoints_and_prior_source_text_check_agree(self):
        for file in (PROOF_ANCHOR,
                     ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/README.md",
                     ROOT / "deliverables/chanlun_108_acceptance/README.md"):
            self.assertIn(DOC.name, file.read_text(encoding="utf-8"))
        for phrase in ("不对称", "同级别", "中阴", "不能"):
            self.assertIn(phrase,PROOF_ANCHOR.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
