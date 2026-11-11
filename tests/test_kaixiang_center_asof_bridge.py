"""Typed synthetic three-member witness must not upgrade Kaixiang candidate claims."""
from __future__ import annotations
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "kaixiang_center_bridge_v453", ROOT/"tools/audit_kaixiang_center_asof_bridge.py")
bridge = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = bridge
spec.loader.exec_module(bridge)
FIXTURE = ROOT/"tests/fixtures/kaixiang_center_asof_bridge_v453.json"


class KaixiangCenterBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fx = json.loads(FIXTURE.read_text(encoding="utf-8"))
        c = json.loads((ROOT/"tests/fixtures/kaixiang_asof_symbolic_v452.json").read_text(encoding="utf-8"))
        cls.cases = {x["id"]: x for x in c["cases"]}
        cls.bridge_cases = {x["source_case_id"]: x for x in cls.fx["bridge_cases"]}

    def assess(self, id, tick):
        return bridge.assess(self.cases[id], self.bridge_cases[id], tick)

    def test_all_fixture_prefixes_checked(self):
        receipt = bridge.audit_fixture(FIXTURE)
        self.assertEqual(receipt["bridge_cases"], 5)
        self.assertEqual(receipt["prefix_checks"], 12)
        self.assertFalse(receipt["market_data"])
        self.assertEqual(receipt["orders_sent"], 0)

    def test_late_third_member_cannot_backfill_price_interval(self):
        early = self.assess("KX-CASE-01", 2)
        later = self.assess("KX-CASE-01", 3)
        self.assertEqual(early["three_member_check"], bridge.PENDING_KNOWLEDGE)
        self.assertIsNone(early["intersection_if_all_visible"])
        self.assertEqual(early["visible_member_ids"], ["u","v"])
        self.assertEqual(later["intersection_if_all_visible"], [9,12])
        self.assertEqual(later["positive_overlap_first_knowable_tick"], 3)

    def test_overlap_never_resurrects_an_invalidated_third_buy(self):
        r = self.assess("KX-CASE-01", 3)
        self.assertEqual(r["three_member_check"], bridge.OVERLAP)
        self.assertEqual(r["candidate_states_unchanged"]["third_buy_extension"], "INVALIDATED")
        self.assertFalse(r["third_buy_or_center_extension_proven"])
        self.assertFalse(r["center_sufficient_for_complete_chanlun_center"])

    def test_no_common_positive_interval_is_not_an_invalidated_trend(self):
        r = self.assess("KX-CASE-02", 3)
        self.assertEqual(r["three_member_check"], bridge.NO_OVERLAP)
        self.assertIsNone(r["intersection_if_all_visible"])
        self.assertEqual(len(r["candidate_remaining_unchanged"]), 2)

    def test_completion_event_and_first_known_time_are_distinct(self):
        r = self.assess("KX-CASE-03", 4)
        self.assertEqual(r["three_member_check"], bridge.PENDING_KNOWLEDGE)
        self.assertEqual(self.assess("KX-CASE-03", 5)["intersection_if_all_visible"], [22,26])

    def test_risk_signal_is_not_structure_change_or_trade(self):
        a, b = self.assess("KX-CASE-04", 3), self.assess("KX-CASE-04", 4)
        self.assertEqual(a["candidate_states_unchanged"], b["candidate_states_unchanged"])
        self.assertFalse(a["candidate_risk_exit_unchanged"])
        self.assertTrue(b["candidate_risk_exit_unchanged"])
        self.assertEqual(a["three_member_check"], b["three_member_check"])
        self.assertFalse(b["trade_or_fill_asserted"])

    def test_two_members_stay_pending_even_at_late_future_tick(self):
        self.assertEqual(self.assess("KX-CASE-07", 999)["three_member_check"], bridge.PENDING_MEMBER)

    def test_no_mutation_of_original_candidate_events(self):
        import copy
        case = copy.deepcopy(self.cases["KX-CASE-01"])
        center = copy.deepcopy(self.bridge_cases["KX-CASE-01"])
        original = (copy.deepcopy(case),copy.deepcopy(center))
        bridge.assess(case,center,3)
        self.assertEqual((case,center), original)

    def test_future_member_value_never_appears_in_earlier_output(self):
        import copy
        base = copy.deepcopy(self.bridge_cases["KX-CASE-01"])
        first = bridge.assess(self.cases["KX-CASE-01"],base,2)
        base["members"][2]["low"]=10
        base["members"][2]["high"]=100
        second = bridge.assess(self.cases["KX-CASE-01"],base,2)
        self.assertEqual(first,second)

    def test_cross_level_scope_rejected(self):
        import copy
        b=copy.deepcopy(self.bridge_cases["KX-CASE-01"])
        b["target_level"]="g_30min"
        with self.assertRaisesRegex(ValueError,"scope"):
            bridge.assess(self.cases["KX-CASE-01"],b,3)

    def test_cross_policy_or_member_source_rejected(self):
        import copy
        b=copy.deepcopy(self.bridge_cases["KX-CASE-01"])
        b["members"][1]["member_level"]="g_5min"
        with self.assertRaisesRegex(ValueError,"lower level"):
            bridge.assess(self.cases["KX-CASE-01"],b,3)
        b=copy.deepcopy(self.bridge_cases["KX-CASE-01"])
        b["policy"]="another_R"
        with self.assertRaisesRegex(ValueError,"scope"):
            bridge.assess(self.cases["KX-CASE-01"],b,3)

    def test_same_member_reuse_or_nonconsecutive_order_rejected(self):
        import copy
        b=copy.deepcopy(self.bridge_cases["KX-CASE-01"])
        b["members"][1]["key"]="u"
        with self.assertRaisesRegex(ValueError,"unique member"):
            bridge.assess(self.cases["KX-CASE-01"],b,3)
        b=copy.deepcopy(self.bridge_cases["KX-CASE-01"])
        b["members"][2]["ordinal"]=4
        with self.assertRaisesRegex(ValueError,"consecutive"):
            bridge.assess(self.cases["KX-CASE-01"],b,3)

    def test_nonfinite_prices_and_negative_intervals_rejected(self):
        import copy
        for value in (float("nan"), float("inf"), -float("inf"), True):
            b=copy.deepcopy(self.bridge_cases["KX-CASE-01"])
            b["members"][0]["high"]=value
            with self.assertRaisesRegex(ValueError,"finite"):
                bridge.assess(self.cases["KX-CASE-01"],b,3)
        b=copy.deepcopy(self.bridge_cases["KX-CASE-01"])
        b["members"][0]["low"]=b["members"][0]["high"]
        with self.assertRaisesRegex(ValueError,"positive member"):
            bridge.assess(self.cases["KX-CASE-01"],b,3)

    def test_claimed_known_before_completion_rejected(self):
        import copy
        b=copy.deepcopy(self.bridge_cases["KX-CASE-03"])
        b["members"][2]["first_known_tick"]=3
        with self.assertRaisesRegex(ValueError,"no earlier"):
            bridge.assess(self.cases["KX-CASE-03"],b,5)

    def test_only_asserted_completed_lower_level_members_accepted(self):
        import copy
        b=copy.deepcopy(self.bridge_cases["KX-CASE-01"])
        b["members"][0]["member_status"]="IN_PROGRESS"
        with self.assertRaisesRegex(ValueError,"asserted completed"):
            bridge.assess(self.cases["KX-CASE-01"],b,3)
        b=copy.deepcopy(self.bridge_cases["KX-CASE-01"])
        b["members"][0]["member_status"]="PROVEN_BY_CHANLUN"
        with self.assertRaisesRegex(ValueError,"asserted completed"):
            bridge.assess(self.cases["KX-CASE-01"],b,3)


if __name__ == "__main__":
    unittest.main()
