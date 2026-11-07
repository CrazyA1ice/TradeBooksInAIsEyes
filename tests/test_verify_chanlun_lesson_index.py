import copy
import runpy
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
verify = runpy.run_path(str(REPO / "tools" / "verify_chanlun_lesson_index.py"))["verify"]

class LessonMapVerificationTests(unittest.TestCase):
    def make_fixture(self):
        groups = [23, 19, 25, 21, 20]
        expected, observed, number = [], [], 1
        for i, count in enumerate(groups, 1):
            entries = []
            for j in range(count):
                entries.append({"lesson": number, "title": f"Synthetic {number}", "start_pdf_page": j+3})
                number += 1
            p = f"ChineseBooks/缠论/缠论_卷{i}.pdf"
            expected.append({"path": p, "pdf_page_count": 100, "sha256": f"synthetic_sha_{i}", "lessons": entries})
            observed.append({"path": p, "page_count": 100, "sha256": f"synthetic_sha_{i}", "lesson_starts": copy.deepcopy(entries)})
        return {"volume_count": 5, "lesson_count": 108, "volumes": expected}, {"volumes": observed}

    def test_all_108_unique_headers(self):
        ref, actual = self.make_fixture()
        verify(ref, actual)

    def test_reject_changed_page(self):
        ref, actual = self.make_fixture()
        actual["volumes"][0]["lesson_starts"][0]["start_pdf_page"] = 999
        with self.assertRaises(ValueError):
            verify(ref, actual)

    def test_reject_missing_lesson(self):
        ref, actual = self.make_fixture()
        actual["volumes"][-1]["lesson_starts"].pop()
        with self.assertRaises(ValueError):
            verify(ref, actual)
