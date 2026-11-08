"""Read-only regression: keep Chanlun parsing, trading, and future claims separate."""
import itertools
import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE"
DOC = GUIDE / "16_分段_动作_未来中枢三种命题的证据作用域.md"

class SourceScope(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = DOC.read_text(encoding="utf-8")

    def test_canonical_sources_and_editor_identity(self):
        for num in (38,39,98,99,100):
            e = json.loads((ROOT / f"knowledge/evidence/chanlun_lesson{num:03d}.json").read_text(encoding="utf-8"))
            self.assertTrue(e["source"]["pdf_pages"])
            self.assertTrue(any(c["kind"] == "SOURCE" for c in e["claims"]))
            self.assertIn(f"chanlun_lesson{num:03d}.json", self.body)
            if num == 39:
                self.assertTrue(any(c["id"] == "CL39-SOURCE-3" and c["kind"] == "SOURCE" and "编者" in c.get("summary", "") for c in e["claims"]))
                self.assertIn("ROLE_MISMATCH_PENDING", self.body)
                self.assertIn("CL39-SOURCE-3", self.body)
            if num in (99,100):
                self.assertTrue(any(c["kind"] == "EDITORIAL" for c in e["claims"]))
        for word in ("作者", "编者", "娇注", "未重新抽取", "不是作者首发当时知道的事实"):
            self.assertIn(word, self.body)

    def test_separate_obligations(self):
        for marker in ("S：分段解析", "D：决策函数", "F：未来结构",
                       "OB38-EXIST","OB38-UNIQUE","OB38-ASOF","OB99-EXIST",
                       "OB99-LOCATION","OB39-DECISION-SCOPE","OB100-EDITORIAL-SCOPE",
                       "SOURCE_UNSPECIFIED","PROOF_NOT_ESTABLISHED"):
            self.assertIn(marker, self.body)
        self.assertIn("不能推得S38存在两个合法分段", self.body)
        self.assertIn("不是高级别必然性证明", self.body)

    def test_shared_prefix_does_not_reveal_future(self):
        prefix = ("C","U")
        yes = prefix + ("U","E")
        not_yet = prefix + tuple(itertools.repeat("U",32))
        self.assertEqual(yes[:2],not_yet[:2])
        self.assertIn("E", yes[2:])
        self.assertNotIn("E", not_yet[2:])
        self.assertIn("不能据此断言其**永远不会出现E**", self.body)
        self.assertIn("非市场实例", self.body)

    def test_all_local_links_and_reading_entrypoints(self):
        count = 0
        for link in re.findall(r"\]\(([^)]+)\)", self.body):
            if link.startswith(("http:","https:","#","mailto:")):
                continue
            p = (DOC.parent / unquote(link.split("#",1)[0])).resolve()
            self.assertTrue(p == ROOT or ROOT in p.parents, str(p))
            self.assertTrue(p.exists(), str(p))
            count += 1
        self.assertGreaterEqual(count, 14)
        for p in (GUIDE / "README.md", GUIDE / "15_同级别唯一性与高级别必然性的证明审查.md",
                  ROOT / "deliverables/chanlun_108_acceptance/README.md"):
            self.assertIn(DOC.name, p.read_text(encoding="utf-8"))

    def test_no_market_validation_or_visual_upgrade(self):
        for token in ("NOT_RUN","TEXT_FIRST_NO_IMAGE","SCOPE_CONFUSION_GUARDED","TEXT_RULE_NOT_FOUND_IN_SCANNED_PAGES"):
            self.assertIn(token, self.body)
        self.assertNotRegex(self.body,r"\]\([^)]*\.(png|jpe?g|webp)")

if __name__ == "__main__":
    unittest.main()
