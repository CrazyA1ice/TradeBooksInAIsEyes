"""F01: real author sources imply typed prerequisites, not universal completion."""
import copy
import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S=importlib.util.spec_from_file_location("f01",ROOT/"tools/audit_chanlun_f01_typed_completion_obligations.py")
m=importlib.util.module_from_spec(S);S.loader.exec_module(m)

def packet():
    return {"as_of":"2026-01-06T10:00:00+08:00","level":1,"rule_version":"SYNTHETIC_R1",
            "declaration_origin":"SYNTHETIC_EXTERNAL_COMPLETION_ASSERTIONS_NOT_SOURCE_PROOF",
            "children":[{"id":f"child{i}","seq":i,"low":low,"high":high,
                "level":0,"rule_version":"SYNTHETIC_R1",
                "declared_completed_at":"2026-01-06T09:59:00+08:00",
                "source_certification":"NOT_AUTHOR_AUTHENTICATED"}
                for i,(low,high) in enumerate([("1","5"),("2","6"),("3","4")],1)]}

class FinishedChildTypeTests(unittest.TestCase):
    def test_original_13_source_claims_really_resolve_and_preserve_unproven_roles(self):
        result=m.audit()
        self.assertEqual(result["author_source_claims"],13)
        self.assertEqual(result["distinct_observation_types"],9)
        self.assertFalse(result["universal_prefix_completion_proven"])
    def test_hypothetical_three_completed_children_can_calculate_only_abstract_overlap(self):
        x=m.conditional_three_child_intersection(packet())
        self.assertEqual(x["status"],"CONDITIONAL_THREE_DECLARED_CHILD_INTERVAL_OVERLAP_ONLY")
        self.assertEqual(x["declared_intersection"],["3","4"])
        self.assertFalse(x["actual_author_center_certified"])
        self.assertFalse(x["parent_completed"])
    def test_future_child_completion_not_available_in_past(self):
        p=packet();p["children"][2]["declared_completed_at"]="2026-01-06T10:15:00+08:00"
        x=m.conditional_three_child_intersection(p)
        self.assertEqual(x["status"],"PENDING_DECLARED_CHILD_COMPLETION")
        self.assertIsNone(x["declared_intersection"])
    def test_wrong_level_version_and_forged_author_certificate_rejected(self):
        for mutation in ("level","version","source"):
            p=packet()
            if mutation=="level":p["children"][2]["level"]=2
            if mutation=="version":p["children"][2]["rule_version"]="PEN_081"
            if mutation=="source":p["children"][2]["source_certification"]="AUTHOR_VERIFIED"
            with self.subTest(mutation=mutation),self.assertRaisesRegex(ValueError,"mismatched"):
                m.conditional_three_child_intersection(p)
    def test_necessary_segment_break_does_not_suffice_for_higher_trajectory(self):
        d=m.read(m.CONTRACT)
        disallowed={(x["from"],x["to"]) for x in d["nonimplications"]}
        self.assertIn(("PEN_BREAK_OBSERVED","SEGMENT_BROKEN"),disallowed)
        self.assertIn(("LEGAL_SEGMENT_BROKEN","FINISHED_LOWER_TREND"),disallowed)
        self.assertIn(("PARENT_CENTER_EXISTS","PARENT_TREND_FINISHED_NOW"),disallowed)
        self.assertIn(("FINAL_PARSE_UNIQUE_HYPOTHESIS","ONLINE_FIRST_CONFIRMATION_KNOWN"),disallowed)
if __name__=="__main__":unittest.main()
