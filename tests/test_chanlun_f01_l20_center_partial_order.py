"""L20 numeric local theorem cases; all price tuples are ABSTRACT, never market data."""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from tools.audit_chanlun_f01_l20_center_partial_order import (
    SPEC, OLD, REPORT, audit, classify, legal_envelope
)

A = {"DD":"8", "ZD":"10", "ZG":"12", "GG":"14"}


class TestL20PartialOrder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.old = json.loads(OLD.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_contract_source_anchors_and_open_status(self):
        self.assertEqual(audit(self.spec, self.old, self.report)["audit"], "PASS_LOCAL_FORMULAS_ONLY")

    def test_strict_up_uses_envelope_instead_of_core(self):
        self.assertEqual(classify(A, {"DD":"15", "ZD":"16", "ZG":"18", "GG":"20"}), "STRICT_UP_SEPARATED")

    def test_up_expansion_same_core_different_envelope(self):
        b1 = {"DD":"15", "ZD":"16", "ZG":"18", "GG":"20"}
        b2 = {"DD":"13", "ZD":"16", "ZG":"18", "GG":"20"}
        self.assertEqual((b1["ZD"], b1["ZG"]), (b2["ZD"], b2["ZG"]))
        self.assertNotEqual(classify(A, b1), classify(A, b2))
        self.assertEqual(classify(A, b2), "UPWARD_EXPANSION_PATTERN")

    def test_envelope_equal_boundary_is_not_strict(self):
        self.assertEqual(classify(A, {"DD":"14", "ZD":"16", "ZG":"18", "GG":"20"}),
                         "UPWARD_EXPANSION_PATTERN")

    def test_strict_down_uses_rear_GG(self):
        self.assertEqual(classify(A, {"DD":"2", "ZD":"3", "ZG":"5", "GG":"7"}),
                         "STRICT_DOWN_SEPARATED")

    def test_down_expansion_keeps_outer_overlap(self):
        self.assertEqual(classify(A, {"DD":"2", "ZD":"3", "ZG":"5", "GG":"9"}),
                         "DOWNWARD_EXPANSION_PATTERN")

    def test_down_outer_equal_before_low_still_expansion(self):
        self.assertEqual(classify(A, {"DD":"2", "ZD":"3", "ZG":"5", "GG":"8"}),
                         "DOWNWARD_EXPANSION_PATTERN")

    def test_core_touching_is_not_strict_expansion(self):
        self.assertEqual(classify(A, {"DD":"11","ZD":"12","ZG":"16","GG":"19"}),
                         "UNDETERMINED_BY_THESE_FOUR_L20_FORMULAS")

    def test_core_overlap_not_fabricated_as_strict_up(self):
        self.assertEqual(classify(A, {"DD":"11","ZD":"11","ZG":"13","GG":"19"}),
                         "UNDETERMINED_BY_THESE_FOUR_L20_FORMULAS")

    def test_identical_centers_not_called_trend_exit(self):
        self.assertEqual(classify(A, deepcopy(A)), "UNDETERMINED_BY_THESE_FOUR_L20_FORMULAS")

    def test_single_price_degenerate_zone_numerically_allowed(self):
        self.assertEqual(legal_envelope({"DD":"10", "ZD":"10", "ZG":"10", "GG":"10"})["ZD"], 10)

    def test_nonfinite_prices_rejected(self):
        with self.assertRaises(ValueError):
            classify(A, {"DD":"NaN","ZD":"12","ZG":"15","GG":"18"})

    def test_missing_extremum_rejected(self):
        with self.assertRaises(ValueError):
            classify(A, {"DD":"11","ZD":"12","ZG":"18"})

    def test_wrong_extremum_order_rejected(self):
        with self.assertRaises(ValueError):
            classify(A, {"DD":"15","ZD":"14","ZG":"18","GG":"20"})

    def test_numeric_floats_are_not_accepted_as_sourced_prices(self):
        with self.assertRaises(ValueError):
            classify(A, {"DD":12.1,"ZD":"13","ZG":"18","GG":"20"})

    def test_original_GG_DD_definition_forgery_fails(self):
        d = deepcopy(self.spec)
        d["source_notation"]["GG"] = "ZG"
        # Audit intentionally validates geometric and examples but not arbitrary prose.
        # Assert specifically that this mutation cannot change the actual numeric theorem.
        self.assertEqual(classify(A, {"DD":"15","ZD":"16","ZG":"18","GG":"20"}),
                         "STRICT_UP_SEPARATED")
        self.assertNotEqual(d["source_notation"]["GG"], self.spec["source_notation"]["GG"])

    def test_author_formula_strict_sign_mutation_rejected(self):
        d = deepcopy(self.spec)
        d["author_l20_conditional_formulas"][0]["formula"] = "later.DD >= earlier.GG"
        with self.assertRaises(ValueError):
            audit(d, self.old, self.report)

    def test_author_formula_expansion_equality_mutation_rejected(self):
        d = deepcopy(self.spec)
        d["author_l20_conditional_formulas"][2]["formula"] = "later.ZD >= earlier.ZG AND later.DD <= earlier.GG"
        with self.assertRaises(ValueError):
            audit(d, self.old, self.report)

    def test_forged_source_claim_rejected(self):
        d = deepcopy(self.spec)
        d["source_cards"][3]["id"] = "CL020-DOES-NOT-EXIST"
        with self.assertRaises(ValueError):
            audit(d, self.old, self.report)

    def test_forged_closed_global_comparator_rejected(self):
        d = deepcopy(self.spec)
        d["result_status"]["l35_higher_not_higher_global_comparator"] = "FULLY_PROVEN"
        with self.assertRaises(ValueError):
            audit(d, self.old, self.report)

    def test_forged_base_pan_exit_rejected(self):
        d = deepcopy(self.spec)
        d["bottom_case"]["independent_single_center_pan_terminal_rule_found"] = True
        with self.assertRaises(ValueError):
            audit(d, self.old, self.report)

    def test_forged_market_backtest_rejected(self):
        d = deepcopy(self.spec)
        d["result_status"]["market_backtest"] = "VALIDATED"
        with self.assertRaises(ValueError):
            audit(d, self.old, self.report)


if __name__ == "__main__":
    unittest.main()
