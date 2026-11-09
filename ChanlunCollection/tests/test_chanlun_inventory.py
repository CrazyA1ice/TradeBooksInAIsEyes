import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import fitz

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "tools" / "inspect_chanlun_sources.py"

class ChanlunInventoryTests(unittest.TestCase):
    def test_lesson_header(self):
        import runpy
        pat = runpy.run_path(str(SCRIPT))["LESSON_HEADER"]
        ok = pat.match("教你炒股票24：MACD 对背弛的辅助判断")
        self.assertIsNotNone(ok)
        self.assertEqual(int(ok.group(1)), 24)
        self.assertIsNone(pat.match("1. 网友评论：这不是章节标题"))

    def test_five_volume_readonly_inventory(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            tools = root / "tools"
            tools.mkdir()
            (tools / "inspect_chanlun_sources.py").write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
            source = root / "ChineseBooks" / "缠论"
            source.mkdir(parents=True)
            before = {}
            for n in range(1, 6):
                doc = fitz.open()
                page = doc.new_page()
                page.insert_text((72, 80), "A synthetic sample " + ("hello " * 35))
                src = source / f"缠论_卷{n}.pdf"
                doc.save(src)
                doc.close()
                before[n] = hashlib.sha256(src.read_bytes()).hexdigest()
            output = root / "result.json"
            result = subprocess.run([sys.executable, str(tools / "inspect_chanlun_sources.py"),
                                     "--out", str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(len(report["volumes"]), 5)
            self.assertTrue(all(v["page_count"] == 1 for v in report["volumes"]))
            self.assertTrue(all(v["native_text_pages_100plus_chars"] == 1 for v in report["volumes"]))
            self.assertEqual(result.stdout.count("INVENTORY {"), 5)
            self.assertEqual(result.stdout.count("LESSONS {"), 5)
            for n in range(1, 6):
                self.assertEqual(before[n], hashlib.sha256((source / f"缠论_卷{n}.pdf").read_bytes()).hexdigest())

if __name__ == "__main__":
    unittest.main()
