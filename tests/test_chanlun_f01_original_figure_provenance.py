"""Regression guards for 18 genuinely rendered original-PDF page inspections."""
import copy
import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("f01_visual",ROOT/"tools/audit_chanlun_f01_original_figure_provenance.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class FigureProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.doc=mod.load(mod.REG)

    def test_all_18_pages_visually_reviewed_and_original_pdf_shas_source_linked(self):
        source,pages=mod.verify_header(self.doc)
        self.assertEqual(len(pages),18)
        self.assertEqual(len({x["original_pdf_sha256"] for x in pages.values()}),2)
        self.assertEqual(sum(x["pdf_native_image_objects"]>0 for x in pages.values()),10)

    def test_uncorrected_lesson71_last_diagram_must_point_to_lesson81(self):
        _,pages=mod.verify_header(self.doc)
        self.assertEqual(pages[(4,73)]["source_tag"],"CORRECTED_LAST_DIAGRAM_WARNING")
        self.assertEqual(pages[(4,232)]["source_tag"],"AUTHOR_L81_RETROSPECTIVE_CORRECTION")
        self.assertIn("lesson81",pages[(4,73)]["visible_finding"])

    def test_lesson67_september19_learning_screenshot_not_backdated_to_august1(self):
        _,pages=mod.verify_header(self.doc)
        self.assertEqual(pages[(3,390)]["source_tag"],"EDITORIAL_OBJECTION_AND_LATER_EXAMPLE")
        self.assertIn("2007-09-19",pages[(3,390)]["visible_finding"])
        self.assertTrue(pages[(3,390)]["thumbnail_visually_reviewed"])

    def test_lesson78_B_prior_confirmed_break_is_necessary_for_that_example(self):
        _,pages=mod.verify_header(self.doc)
        self.assertIn("confirmed B",pages[(4,177)]["visible_finding"])
        self.assertFalse(self.doc["completed_lower_trend_author_certified"])

    def test_no_editorial_source_role_or_fine_price_verification_forged(self):
        x=copy.deepcopy(self.doc)
        x["source_author_first_publication_authenticated"]=True
        with self.assertRaisesRegex(ValueError,"falsely promoted"):
            mod.verify_header(x)
        x=copy.deepcopy(self.doc)
        x["pages"][0]["fine_grained_price_and_member_labels_independently_verified"]=True
        with self.assertRaisesRegex(ValueError,"visual page"):
            mod.verify_header(x)

    def test_original_missing_page_or_obligation_fails_closed(self):
        x=copy.deepcopy(self.doc)
        x["pages"]=x["pages"][:-1]
        with self.assertRaisesRegex(ValueError,"coverage"):
            mod.verify_header(x)
        x=copy.deepcopy(self.doc)
        x["semantic_bridges_remaining_open"].pop()
        with self.assertRaisesRegex(ValueError,"coverage"):
            mod.verify_header(x)

    def test_figures_are_not_trading_or_universal_theorem_proof(self):
        self.assertFalse(self.doc["OB38_or_99_proven"])
        self.assertFalse(self.doc["real_market_data_accessed"])
        self.assertEqual(self.doc["backtesting"],"NOT_RUN")
        self.assertEqual(mod.verify_header(self.doc)[1][(4,241)]["source_tag"],
                         "SEPARATE_LATER_DATED_PEN_REVISION")

if __name__=="__main__":
    unittest.main()
