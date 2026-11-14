"""M53 conditional interval inclusion and anti-provenance-laundering gates."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/"tools/audit_chanlun_l35_rebracketing_m53.py"
spec=importlib.util.spec_from_file_location("m53",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
DATA=json.loads(m.CATALOG.read_text(encoding="utf-8"))
CASES={x["id"]:x for x in DATA["cases"]}

class M53SourceAnchoredRangeTests(unittest.TestCase):
    def test_all_frozen_examples(self):
        self.assertEqual(m.audit(DATA)["cases"],11)

    def test_nonempty_group_when_raw_empty(self):
        r=m.assess(CASES["created_touching_overlap"])
        self.assertIsNone(r["raw_intersection"])
        self.assertEqual(r["grouped_intersection"],[3.5,3.5])
        self.assertTrue(r["strictly_wider"])

    def test_wider_even_when_both_nonempty(self):
        r=m.assess(CASES["nonempty_strict_widening"])
        self.assertEqual(r["raw_intersection"],[3,4])
        self.assertEqual(r["grouped_intersection"],[1,6])

    def test_equal_case(self):
        r=m.assess(CASES["raw_overlap_equal"])
        self.assertEqual(r["raw_intersection"],r["grouped_intersection"])

    def test_both_empty_case(self):
        r=m.assess(CASES["neither_intersection"])
        self.assertIsNone(r["raw_intersection"])
        self.assertIsNone(r["grouped_intersection"])

    def test_point_touch_case(self):
        r=m.assess(CASES["point_touch_only"])
        self.assertEqual(r["grouped_intersection"],[2,2])

    def test_no_future_b_range_leaked(self):
        self.assertEqual(m.assess(CASES["future_b_hidden"]),{"status":"PENDING_FIRST_KNOWN_NO_FUTURE_LEAK"})

    def test_same_source_required(self):
        self.assertEqual(m.assess(CASES["source_mismatch"]),{"status":"SOURCE_ID_MISMATCH"})

    def test_fixed_policy_required(self):
        self.assertEqual(m.assess(CASES["policy_mismatch"]),{"status":"R_POLICY_MISMATCH"})

    def test_complete_membership_not_self_certified(self):
        self.assertEqual(m.assess(CASES["component_not_completed"]),{"status":"COMPONENT_COMPLETION_NOT_EVEN_DECLARED"})
        valid=m.assess(CASES["created_touching_overlap"])
        self.assertFalse(valid["author_level_movement_completed"])
        self.assertFalse(valid["L20_two_center_Phi_authenticated"])
        self.assertFalse(valid["higher_center_authenticated"])

    def test_order_qualifier(self):
        self.assertEqual(m.assess(CASES["ordinal_corrupted"]),{"status":"PART_ORDER_INVALID"})

    def test_duplicate_part_name(self):
        self.assertEqual(m.assess(CASES["duplicate_id"]),{"status":"PART_ID_INVALID_OR_DUPLICATE"})

    def test_subset_operator_direction(self):
        self.assertTrue(m.subset([3,4],[1,6]))
        self.assertFalse(m.subset([1,6],[3,4]))
        self.assertTrue(m.subset(None,[1,6]))
        self.assertFalse(m.subset([1,2],None))

    def test_guard_illegal_interval(self):
        c=copy.deepcopy(CASES["created_touching_overlap"])
        c["parts"][1]["low"]=99
        self.assertEqual(m.assess(c),{"status":"INVALID_CLOSED_INTERVAL"})

if __name__=="__main__":unittest.main()
