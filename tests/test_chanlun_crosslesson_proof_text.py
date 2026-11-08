"""Narrow text-only proof bridge discovery gates, no market backtests."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/inspect_chanlun_crosslesson_proof_text_readonly.py"
spec = importlib.util.spec_from_file_location("crosslesson_proof", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class CrossLessonProofTextTests(unittest.TestCase):
    def test_target_scope(self):
        self.assertEqual(m.VOLUME, 2)
        self.assertEqual(set(m.TARGETS), {256, 257, 305, 310, 320})

    def test_bounded_excerpts_not_full_transcript(self):
        raw = "Z" * 300 + "多义性" + "x" * 300 + "级别" + "x" * 300
        found = m.bounded_cues(raw, ("多义性", "级别"))
        self.assertEqual(len(found), 2)
        self.assertTrue(all(len(x["context"]) <= m.MAX_CONTEXT_CHARS for x in found))
        self.assertEqual(m.bounded_cues("none", ("不存在",)), [])

    def test_production_is_fail_closed_and_text_only(self):
        body = SCRIPT.read_text(encoding="utf-8")
        for word in ("locked_hashes()", "pins[str(page)] != sha", "DISCOVERY_UNPINNED",
                     'get_text("text", sort=True)', "source_role", "market_backtests"):
            self.assertIn(word, body.lower() if word == "source_role" else body)
        for prohibited in ("get_pixmap", "get_textpage_ocr", "pytesseract", "read_csv("):
            self.assertNotIn(prohibited, body)

if __name__ == "__main__":
    unittest.main()
