"""G0 intake independent, no actual copyrighted books used in unit tests."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "book_intake.py"
spec = importlib.util.spec_from_file_location("book_intake", SOURCE)
intake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intake)


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "books"
        self.root.mkdir()
        self.args = dict(book_id="a-second-book", title="第二本书", language="zh",
                         rights_status="UNKNOWN")

    def scan(self):
        return intake.inventory(self.root, **self.args)

    def test_pdf_metadata_only_never_content(self):
        original = b"%PDF-1.7\nnot a full parsed PDF\n"
        (self.root / "work.pdf").write_bytes(original)
        result = self.scan()
        self.assertEqual(result["source_count"], 1)
        self.assertEqual(result["status"], "NEEDS_REVIEW")
        self.assertEqual(result["source_files"][0]["container_check"],
                         "PDF_HEADER_ONLY_NOT_FULLY_PARSED")
        self.assertFalse(result["source_bytes_embedded"])
        self.assertNotIn("not a full parsed PDF", json.dumps(result))
        self.assertEqual((self.root / "work.pdf").read_bytes(), original)
        self.assertIsNone(result["source_files"][0]["physical_page_count"])

    def test_deterministic_metadata(self):
        (self.root / "note.md").write_text("资料", encoding="utf-8")
        self.assertEqual(self.scan(), self.scan())
        self.assertTrue(self.scan()["source_files"][0]["sha256"])

    def test_duplicates_are_recorded_but_not_deleted(self):
        (self.root / "a.txt").write_text("same")
        (self.root / "b.md").write_text("same")
        result = self.scan()
        self.assertEqual(result["source_files"][1]["duplicate_of"], "a.txt")
        self.assertIn("DUPLICATE_CONTENT_NEEDS_REVIEW", result["warnings"])
        self.assertTrue((self.root / "b.md").is_file())

    def test_wrong_pdf_signature_fails(self):
        (self.root / "fake.pdf").write_bytes(b"not a pdf")
        with self.assertRaisesRegex(intake.IntakeError, "signature"):
            self.scan()

    def test_invalid_text_encoding_fails(self):
        (self.root / "bad.txt").write_bytes(b"\xff")
        with self.assertRaisesRegex(intake.IntakeError, "UTF-8"):
            self.scan()

    def test_epub_metadata_is_not_contents(self):
        with zipfile.ZipFile(self.root / "book.epub", "w") as z:
            z.writestr("mimetype", "application/epub+zip")
            z.writestr("META-INF/container.xml", "<container />")
        self.assertEqual(self.scan()["source_files"][0]["format"], "epub")

    def test_fake_epub_rejected(self):
        with zipfile.ZipFile(self.root / "book.epub", "w") as z:
            z.writestr("file.txt", "x")
        with self.assertRaisesRegex(intake.IntakeError, "mimetype"):
            self.scan()

    def test_docx_container(self):
        with zipfile.ZipFile(self.root / "book.docx", "w") as z:
            z.writestr("[Content_Types].xml", "<Types />")
            z.writestr("word/document.xml", "<document />")
        self.assertEqual(self.scan()["source_files"][0]["format"], "docx")

    def test_invalid_slug_and_missing_source_fail(self):
        (self.root / "a.txt").write_text("ok")
        for invalid in ["../bad", "bad/slug", "Bad-Slug", ""]:
            with self.subTest(invalid=invalid), self.assertRaises(intake.IntakeError):
                intake.inventory(self.root, **(self.args | {"book_id": invalid}))
        (self.root / "a.txt").unlink()
        with self.assertRaisesRegex(intake.IntakeError, "No supported"):
            self.scan()

    def test_ignored_unsupported_files(self):
        (self.root / "book.txt").write_text("ok")
        (self.root / "cover.png").write_bytes(b"not an image")
        r = self.scan()
        self.assertEqual(r["ignored_files"], ["cover.png"])
        self.assertIn("UNSUPPORTED_INPUTS_NOT_PROCESSED", r["warnings"])

    def test_reject_symlink_without_following(self):
        target = Path(self.tmp.name) / "secret.txt"
        target.write_text("outside")
        try:
            (self.root / "link.txt").symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        with self.assertRaisesRegex(intake.IntakeError, "Symlinks"):
            self.scan()

    def test_reject_case_collision(self):
        (self.root / "A.txt").write_text("one")
        (self.root / "a.txt").write_text("two")
        if len(list(self.root.iterdir())) != 2:
            self.skipTest("case insensitive FS")
        with self.assertRaisesRegex(intake.IntakeError, "Case-colliding"):
            self.scan()

    def test_output_outside_input_only(self):
        (self.root / "book.md").write_text("sample")
        self.assertEqual(intake.main(["--input", str(self.root), "--book-id", "test-book",
                                     "--title", "Test", "--output", str(self.root / "receipt.json")]), 2)
        self.assertFalse((self.root / "receipt.json").exists())
        dest = Path(self.tmp.name) / "receipt.json"
        self.assertEqual(intake.main(["--input", str(self.root), "--book-id", "test-book",
                                     "--title", "Test", "--output", str(dest)]), 0)
        self.assertEqual(json.loads(dest.read_text())["book_id"], "test-book")


if __name__ == "__main__":
    unittest.main()
