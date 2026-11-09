"""No exact cent-price assertions from enlarged low-resolution source charts."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "tools/audit_chanlun_native_figure_resolution.py"
spec = importlib.util.spec_from_file_location("chanlun_native_resolution_gate", FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SOURCE = mod.SOURCE_SHA256


def fixture():
    return {
        "target_set": "lineage",
        "fine_chart_prices_verified": False,
        "human_page_visual_verification_completed": False,
        "pages": [
            {"volume": 3, "pdf_physical_page": n, "source_sha256": SOURCE,
             "embedded_images": [{"width": w, "height": h, "xres": 96, "yres": 96}],
             "visual_audit_status": "RENDERED_NOT_INDEPENDENTLY_VISUALLY_VERIFIED"}
            for n, w, h in ((230, 601, 430), (233, 1020, 621))
        ],
    }


class NativeRasterCeilingTests(unittest.TestCase):
    def test_only_native_dimensions_are_certified(self):
        report = mod.audit(fixture())
        self.assertEqual(report["status"], "PASS_NATIVE_RASTER_PROVENANCE_ONLY")
        self.assertEqual([x["width"] for x in report["source_images"]], [601, 1020])
        self.assertEqual([x["height"] for x in report["source_images"]], [430, 621])
        self.assertEqual(report["difference_points"], 0.36)
        self.assertFalse(report["exact_price_pixel_endpoint_verified"])
        self.assertEqual(report["market_backtests_run"], 0)

    def test_requires_proper_original_pdf_source(self):
        data = fixture()
        data["pages"][0]["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Source fingerprint changed"):
            mod.audit(data)

    def test_rejects_pixel_dimension_substitutions(self):
        data = fixture()
        data["pages"][0]["embedded_images"][0]["width"] = 2862
        with self.assertRaisesRegex(ValueError, "Native image dimensions changed"):
            mod.audit(data)

    def test_rejects_unjustified_upgrade_to_verified(self):
        for field in ("fine_chart_prices_verified", "human_page_visual_verification_completed"):
            with self.subTest(field=field):
                data = fixture()
                data[field] = True
                with self.assertRaises(ValueError):
                    mod.audit(data)

    def test_requires_both_independent_figure_candidates(self):
        data = fixture()
        data["pages"].pop()
        with self.assertRaisesRegex(ValueError, "Missing one or both"):
            mod.audit(data)

    def test_source_reader_does_not_backfill_exact_pixel_claim(self):
        lesson = (ROOT / "analyses/books/chanlun/chapters/lesson_059.md").read_text(encoding="utf-8")
        guide = (ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/11_前课图例溯源与新笔版本时间线.md").read_text(encoding="utf-8")
        workflow = (ROOT / "docs/BOOK_RESEARCH_WORKFLOW.md").read_text(encoding="utf-8")
        for s in (lesson, guide, workflow):
            self.assertIn("601×430", s)
            self.assertIn("1020×621", s)
            self.assertIn("PRICE_TO_PIXEL_PENDING", s)
        self.assertIn("96 DPI", guide)
        self.assertIn("原生像素", workflow)
        self.assertIn("3994.57", lesson)
        self.assertIn("3994.21", guide)
        self.assertNotIn("已完全核定两个价位的原图像素端点", guide)


if __name__ == "__main__":
    unittest.main()
