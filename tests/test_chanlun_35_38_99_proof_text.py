"""Regression gates for the bounded original-text search of lessons 35/38/99."""
import importlib.util
import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/inspect_chanlun_35_38_99_proof_text_readonly.py"
spec = importlib.util.spec_from_file_location("chanlun_proof_native", SOURCE)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class ProofSourceAuditTests(unittest.TestCase):
    def test_exact_target_page_set_and_bounds(self):
        self.assertEqual(set(tool.TARGETS), {2, 5})
        self.assertEqual(set(tool.TARGETS[2]), {294, 295, 340, 341})
        self.assertEqual(set(tool.TARGETS[5]), {204, 205, 206, 207})
        self.assertEqual(sum(map(len, tool.TARGETS.values())), 8)

    def test_limit_excerpts_and_absent_cues(self):
        text = "A" * 100 + "分解" + "B" * 300 + "中枢" + "C" * 300
        items = tool.cues(text, ("分解", "中枢"))
        self.assertEqual(len(items), 2)
        self.assertTrue(all(len(x["context"]) <= tool.MAX_EXCERPT_CHARS for x in items))
        self.assertEqual(tool.cues(text, ("不存在",)), [])

    def test_all_eight_sha_pins_and_exact_document_boundaries(self):
        values = tool.pin_map()
        expected = {f"{v}:{page}" for v, pages in tool.TARGETS.items() for page in pages}
        self.assertEqual(set(values), expected)
        self.assertEqual(set(tool.PAGE_SCOPES), expected)
        self.assertEqual(set(tool.REQUIRED_BOUNDARY_TEXT) - expected, set())
        self.assertTrue(all(len(h) == 64 for h in values.values()))
        self.assertIn("解盘及互动问答", tool.REQUIRED_BOUNDARY_TEXT["2:341"])
        self.assertIn("2008-02-20", tool.REQUIRED_BOUNDARY_TEXT["5:206"])
        self.assertEqual({k for k, v in tool.PAGE_SCOPES.items()
                          if v == "LOW_NATIVE_TEXT_IMAGE_UNREVIEWED"},
                         {"2:294", "2:295", "2:340"})

    def test_five_proof_obligations_all_remain_open_and_sources_are_checked(self):
        path = ROOT / "reports/source_inventory/chanlun_38_99_proof_obligation_ledger.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        expected = {"OB38-EXIST", "OB38-UNIQUE", "OB38-ASOF",
                    "OB99-EXIST", "OB99-LOCATION"}
        obligations = data["proof_obligations"]
        self.assertEqual({x["id"] for x in obligations}, expected)
        self.assertTrue(all(x["status"] == "NOT_ESTABLISHED" for x in obligations))
        pinned = tool.pin_map()
        self.assertEqual({x["page"] for x in data["scan_page_safety"]}, set(pinned))
        for row in data["scan_page_safety"]:
            self.assertEqual(row["classification"], tool.PAGE_SCOPES[row["page"]])
            if row["page"].startswith("2:") and row["native_text_chars"] == 44:
                self.assertEqual(row["must_not_infer"], "no_unseen_definition")
        self.assertIn("LOW_NATIVE_TEXT_NOT_EVIDENCE_OF_ABSENCE", data["flags"])
        self.assertEqual(data["primary_author_article_boundaries"]["lesson_99_later_article"],
                         "vol5_p206_begins_separately_dated_2008_02_20_piece")

    def test_article_local_links_and_nonproof_claims(self):
        path = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/19_第35_38_99课原文边界与证明可达性审查.md"
        body = path.read_text(encoding="utf-8")
        for token in ("SOURCE_PDF_NATIVE_TEXT_VERIFIED", "PROVENANCE_LIMITED", "NOT_RUN",
                      "TEXT_FIRST_NO_IMAGE", "OB38-UNIQUE", "OB38-ASOF", "OB99-EXIST",
                      "OB99-LOCATION", "PROOF_NOT_ESTABLISHED",
                      "LOW_NATIVE_TEXT_IMAGE_UNREVIEWED", "TEXT_RULE_NOT_FOUND_IN_SCANNED_PAGES",
                      "2008-02-20", "44字符", "解盘及互动问答"):
            self.assertIn(token, body)
        links = re.findall(r"\]\(([^)]+)\)", body)
        count = 0
        for ref in links:
            if ref.startswith(("http:", "https:", "#", "mailto:")):
                continue
            target = (path.parent / unquote(ref.split("#", 1)[0])).resolve()
            self.assertTrue(target == ROOT or ROOT in target.parents, str(target))
            self.assertTrue(target.exists(), str(target))
            count += 1
        self.assertGreaterEqual(count, 12)
        for index in ("deliverables/chanlun_108_acceptance/04_AI_GUIDE/README.md",
                      "deliverables/chanlun_108_acceptance/README.md"):
            self.assertIn(path.name, (ROOT / index).read_text(encoding="utf-8"))

    def test_source_only_and_sha_gates_present(self):
        code = SOURCE.read_text(encoding="utf-8")
        for word in ('get_text("text", sort=True)', 'digest_file(path)', 'pins[key] != sha',
                     "DISCOVERY_UNPINNED", "author_or_editor_historical_identity_verified"):
            self.assertIn(word, code)
        for forbidden in ("get_pixmap", "get_textpage_ocr", "pytesseract", "market_dataframe"):
            self.assertNotIn(forbidden, code)


if __name__ == "__main__":
    unittest.main()
