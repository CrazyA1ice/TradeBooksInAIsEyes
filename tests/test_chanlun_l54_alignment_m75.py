"""M75: offline tests with invented PDF/SVG bytes only, no historical data."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import prepare_chanlun_l54_alignment_m75 as m


class AlignmentTests(unittest.TestCase):
    def fixture(self, folder):
        root=Path(folder)/"TradeBooksInAIsEyes"
        pdf=root/m.PDF_REL
        svg=root/m.SVG_REL
        pdf.parent.mkdir(parents=True,exist_ok=True)
        svg.parent.mkdir(parents=True,exist_ok=True)
        pdf.write_bytes(b"%PDF-1.4\nsynthetic-only")
        svg.write_text('<svg role="img">600151.SH / 2007-05-18 '
                       '13:07 / 18.59 15:00 / 18.03 OpenFinMind pinned SHA256'
                       '</svg>',encoding="utf-8")
        return m.files(root),hashlib.sha256(pdf.read_bytes()).hexdigest()

    def test_default_preflight_does_not_access_svg_pdf_or_network(self):
        with mock.patch.object(m,"verify_inputs",side_effect=AssertionError("checked files")):
            self.assertEqual(m.main(["--mode","preflight"]),0)

    def test_paths_remain_inside_canonical_project(self):
        with tempfile.TemporaryDirectory() as d:
            location,_=self.fixture(d)
            self.assertEqual(location["directory"],
                             location["project"]/m.ALIGN_REL)
            self.assertIn(location["project"]/"work",
                          location["svg"].parents)
            self.assertIn(location["project"]/"work",
                          location["directory"].parents)

    def test_pdf_mismatch_is_rejected_before_any_output(self):
        with tempfile.TemporaryDirectory() as d:
            location,_=self.fixture(d)
            with self.assertRaisesRegex(ValueError,"PDF SHA256"):
                m.verify_inputs(location)
            self.assertFalse(location["directory"].exists())

    def test_chart_missing_or_forged_does_not_create_alignment(self):
        with tempfile.TemporaryDirectory() as d:
            location,digest=self.fixture(d)
            location["svg"].unlink()
            with self.assertRaisesRegex(ValueError,"SVG missing"):
                m.verify_inputs(location,expected_pdf_sha=digest)
            location["svg"].write_text("<svg>fake</svg>",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"anchor missing"):
                m.verify_inputs(location,expected_pdf_sha=digest)

    def test_prepared_html_links_to_local_pdf_and_svg_and_preserves_unknowns(self):
        with tempfile.TemporaryDirectory() as d:
            location,digest=self.fixture(d)
            with mock.patch.object(m,"PDF_SHA",digest):
                report=m.prepare(location)
            self.assertEqual(report["marker_count"],14)
            self.assertEqual(report["assigned_markers"],0)
            self.assertEqual(report["network_queries"],0)
            self.assertEqual(report["E1_E4"],"NOT_RUN")
            html=Path(report["html"]).read_text(encoding="utf-8")
            self.assertIn(location["svg"].as_uri(),html)
            self.assertIn(location["pdf"].as_uri(),html)
            self.assertIn("#page=170",html)
            self.assertIn("g7",html)
            annotations=json.loads(Path(report["annotation_template"]).read_text(encoding="utf-8"))
            self.assertEqual(len(annotations["marks"]),14)
            self.assertIsNone(annotations["marks"]["g7"]["candidate_market_minute"])
            self.assertIsNone(annotations["marks"]["d1"]["candidate_price"])
            self.assertFalse(annotations["marks"]["g1"]["independent_author_point_certified"])
            self.assertFalse(annotations["price_adjustment_verified"])

    def test_existing_alignment_files_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            location,digest=self.fixture(d)
            with mock.patch.object(m,"PDF_SHA",digest):
                m.prepare(location)
                with self.assertRaisesRegex(ValueError,"must not be overwritten"):
                    m.prepare(location)

    def test_bad_document_destination_outside_work_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            location,digest=self.fixture(d)
            location["directory"]=Path(d)/"outside"
            with self.assertRaisesRegex(ValueError,"inside project work"):
                m.verify_inputs(location,expected_pdf_sha=digest)

    def test_known_anchors_are_not_auto_assigned_to_author_markers(self):
        fake={"pdf_sha256":"a"*64,"svg_sha256":"b"*64}
        doc=m.image_template(fake)
        self.assertEqual(doc["observed_anchors"][0]["time"],"13:07")
        self.assertEqual(doc["observed_anchors"][0]["author_marker_identity"],"NOT_ASSIGNED")
        self.assertIsNone(doc["marks"]["g1"]["candidate_price"])
        self.assertEqual(doc["F01"],"OPEN")


if __name__=="__main__":
    unittest.main()
