"""Fail-closed configuration tests for SHA-pinned, text-only bridge page audit."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/inspect_chanlun_bridge_text_readonly.py"
spec = importlib.util.spec_from_file_location("bridge_text", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BridgeSourceTextAuditTests(unittest.TestCase):
    def test_target_pages_and_canonical_inventory(self):
        self.assertEqual(module.TARGETS.keys(), {2, 5})
        self.assertEqual(set(module.TARGETS[2]), {353, 354})
        self.assertEqual(set(module.TARGETS[5]), {192, 193, 194, 224, 225})
        source = json.loads(module.INVENTORY.read_text(encoding="utf-8"))
        volumes = {int(Path(v["path"]).stem.split("卷")[-1]): v for v in source["volumes"]}
        for vol in module.TARGETS:
            self.assertRegex(volumes[vol]["sha256"], "^[0-9a-f]{64}$")

    def test_context_is_strictly_bounded_and_deduplicated(self):
        raw = "abc " + ("PAD" * 100) + " 背驰 " + ("STUFF" * 80) + " 买卖 " * 8
        items = module.bounded_excerpts(raw, ("背驰", "买卖"))
        self.assertLessEqual(len(items), module.MAX_EXCERPTS_PER_PAGE)
        self.assertTrue(all(len(x["context"]) <= module.MAX_CONTEXT_CHARS for x in items))
        self.assertEqual(module.bounded_excerpts("no matches", ("盘整背驰",)), [])

    def test_production_requires_independent_pinfile_and_fixed_extraction(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("if pinned is not None and pinned[key] != page_sha", text)
        self.assertIn("if pinned is not None and set(pinned) != keys", text)
        self.assertIn('get_text("text", sort=True)', text)
        self.assertIn("DISCOVERY_UNPINNED", text)
        self.assertNotIn("get_pixmap", text)
        self.assertNotIn("get_textpage_ocr", text)
        self.assertNotIn("pytesseract", text)

if __name__ == "__main__":
    unittest.main()
