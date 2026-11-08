"""Regression gates for the bounded original-text search of lessons 35/38/99."""
import importlib.util
import unittest
from pathlib import Path

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

    def test_source_only_and_sha_gates_present(self):
        code = SOURCE.read_text(encoding="utf-8")
        for word in ('get_text("text", sort=True)', 'digest_file(path)', 'pins[key] != sha',
                     "DISCOVERY_UNPINNED", "author_or_editor_historical_identity_verified"):
            self.assertIn(word, code)
        for forbidden in ("get_pixmap", "get_textpage_ocr", "pytesseract", "market_dataframe"):
            self.assertNotIn(forbidden, code)


if __name__ == "__main__":
    unittest.main()
