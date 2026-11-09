"""Narrow text-only proof bridge discovery gates, no market backtests."""
import importlib.util
import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

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

    def test_pinned_original_page_sha_and_editorial_cues(self):
        pins = m.locked_hashes()
        self.assertEqual(set(pins), set(map(str, m.TARGETS)))
        self.assertEqual(set(m.REQUIRED_NATIVE_ANCHORS), set(m.TARGETS))
        self.assertTrue(all(len(x) == 64 for x in pins.values()))
        self.assertIn("娇注", m.REQUIRED_NATIVE_ANCHORS[310])
        self.assertIn("（娇：", m.REQUIRED_NATIVE_ANCHORS[320])

    def test_lesson36_later_editorial_note_keeps_original_id(self):
        ev = json.loads((ROOT / "knowledge/evidence/chanlun_lesson036.json").read_text(encoding="utf-8"))
        note = next(x for x in ev["claims"] if x["id"] == "CL36-SOURCE-3")
        self.assertEqual(note["kind"], "EDITORIAL")
        source = note["attribution_evidence"]
        self.assertEqual(source["physical_pdf_page"], 310)
        self.assertEqual(source["marker_in_native_text"], "娇注")
        self.assertEqual(source["native_page_text_sha256"], m.locked_hashes()["310"])
        self.assertTrue(source["id_retained_for_backward_compatibility"])

    def test_research_report_and_local_links_remain_honest(self):
        guide = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE"
        report = guide / "18_多义性_结合律与固定级别唯一性的跨课证据桥.md"
        body = report.read_text(encoding="utf-8")
        for token in ("SOURCE_PDF_NATIVE_TEXT_VERIFIED", "PROVENANCE_LIMITED",
                      "ROLE_MISMATCH_RESOLVED", "OB38-UNIQUE", "OB38-ASOF",
                      "OB99-EXIST", "OB99-LOCATION", "PROOF_NOT_ESTABLISHED",
                      "TEXT_RULE_NOT_FOUND_IN_SCANNED_PAGES", "NOT_RUN",
                      "CL36-SOURCE-3", "未完成", "同级别"):
            self.assertIn(token, body)
        refs = re.findall(r"\]\(([^)]+)\)", body)
        local = 0
        for ref in refs:
            if ref.startswith(("http:", "https:", "#", "mailto:")):
                continue
            target = (report.parent / unquote(ref.split("#", 1)[0])).resolve()
            self.assertTrue(target == ROOT or ROOT in target.parents, str(target))
            self.assertTrue(target.exists(), str(target))
            local += 1
        self.assertGreaterEqual(local, 12)
        self.assertNotIn("get_pixmap", body)
        for entrypoint in (guide / "README.md", ROOT / "deliverables/chanlun_108_acceptance/README.md"):
            self.assertIn(report.name, entrypoint.read_text(encoding="utf-8"))

    def test_production_is_fail_closed_and_text_only(self):
        body = SCRIPT.read_text(encoding="utf-8")
        for word in ("locked_hashes()", "pins[str(page)] != sha", "DISCOVERY_UNPINNED",
                     'get_text("text", sort=True)', "source_role", "market_backtests"):
            self.assertIn(word, body.lower() if word == "source_role" else body)
        for prohibited in ("get_pixmap", "get_textpage_ocr", "pytesseract", "read_csv("):
            self.assertNotIn(prohibited, body)

if __name__ == "__main__":
    unittest.main()
