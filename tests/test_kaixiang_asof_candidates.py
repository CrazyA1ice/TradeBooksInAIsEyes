"""No-lookahead obligations for Kaixiang's quote-linked, synthetic branch gate."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "kaixiang_symbolic_asof", ROOT/"tools/audit_kaixiang_asof_candidates.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)
DATA = ROOT/"tests/fixtures/kaixiang_asof_symbolic_v452.json"


class KaixiangAsOfContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.j = json.loads(DATA.read_text(encoding="utf-8"))
        cls.old = json.loads((
            ROOT/"other_views/chanlun/speaker-unknown-001/decision_audit_v451.json"
        ).read_text(encoding="utf-8"))

    def get_case(self, number):
        return self.j["cases"][number-1]

    def test_exact_eight_prior_cases_and_source_identity(self):
        self.assertEqual(self.j["origin"], gate.ORIGIN)
        self.assertEqual(len(self.j["cases"]), 8)
        self.assertEqual(
            [x["id"] for x in self.j["cases"]],
            [x["id"] for x in self.old["cases"]])
        for a, b in zip(self.j["cases"], self.old["cases"]):
            self.assertEqual(a["source_answer_ids"], b["source_answer_ids"])

    def test_all_prefixes_and_no_market(self):
        row = gate.audit_fixture(DATA)
        self.assertEqual(row["cases"], 8)
        self.assertGreaterEqual(row["prefix_checks"], 15)
        self.assertEqual(row["real_trading_orders"], 0)
        self.assertFalse(row["market_data"])

    def test_future_evidence_cannot_backdate_a_prediction(self):
        case = self.get_case(1)
        early = gate.assess(case, 2)
        self.assertEqual(len(early["remaining_hypotheses"]), 3)
        self.assertEqual(early["observed_event_ids"], [])
        later = gate.assess(case, 5)
        self.assertEqual(later["remaining_hypotheses"], ["decline"])
        self.assertEqual(later["sole_survivor"], "decline")
        self.assertFalse(later["sole_survivor_confirmed_final"])
        self.assertFalse(later["candidate_universe_exhaustiveness_proven"])

    def test_local_condition_is_not_final_confirmation(self):
        state = gate.assess(self.get_case(2), 2)
        self.assertEqual(state["candidate_states"]["up_continues"],
                         "LOCAL_CONDITION_ONLY")
        self.assertIsNone(state["sole_survivor"])
        self.assertFalse(state["chanlun_structure_certified"])

    def test_late_data_known_after_observation_is_ignored(self):
        earlier = gate.assess(self.get_case(5), 3)
        later = gate.assess(self.get_case(5), 5)
        self.assertFalse(earlier["risk_exit_asserted"])
        self.assertTrue(later["risk_exit_asserted"])
        self.assertEqual(earlier["observed_event_ids"], [])

    def test_future_extension_does_not_change_frozen_history(self):
        c = json.loads(json.dumps(self.get_case(1)))
        before = gate.assess(c, 1)
        c["events"].append({
            "id": "e_future", "kind": "CANDIDATE_INVALIDATED",
            "occurred_tick": 100, "known_tick": 101,
            "candidate": "pan", "scope": c["scope"], "evidence": gate.EVIDENCE})
        self.assertEqual(gate.assess(c, 1), before)

    def test_cross_level_or_rule_is_never_relabelled(self):
        c = json.loads(json.dumps(self.get_case(3)))
        c["events"][0]["scope"] = "g_30min|policy_R_demo|segment_C"
        with self.assertRaisesRegex(ValueError, "cross-level"):
            gate.assess(c, 2)

    def test_different_segment_same_label_cannot_be_reused(self):
        c = json.loads(json.dumps(self.get_case(1)))
        c["events"][0]["scope"] = "g_5min|policy_R_demo|another_segment"
        with self.assertRaisesRegex(ValueError, "cross-level"):
            gate.assess(c, 5)

    def test_information_cannot_precede_event_time(self):
        c = json.loads(json.dumps(self.get_case(1)))
        c["events"][0]["known_tick"] = 1
        with self.assertRaisesRegex(ValueError, "before occurrence"):
            gate.assess(c, 5)

    def test_account_risk_independent_of_structure_and_not_a_fill(self):
        c = self.get_case(4)
        p = gate.assess(c, 3)
        q = gate.assess(c, 4)
        self.assertEqual(p["action"], gate.NO_TRADE)
        self.assertEqual(q["action"], gate.RISK)
        self.assertEqual(p["candidate_states"], q["candidate_states"])
        self.assertFalse(q["order_submitted"])
        self.assertFalse(q["fill_confirmed"])

    def test_risk_events_cannot_masquerade_as_technical_facts(self):
        c = json.loads(json.dumps(self.get_case(4)))
        c["events"][1]["scope"] = c["scope"]
        with self.assertRaisesRegex(ValueError, "account-risk"):
            gate.assess(c, 4)

    def test_resurrection_of_invalidated_same_hypothesis_is_rejected(self):
        c = json.loads(json.dumps(self.get_case(1)))
        c["events"].append({
            "id": "after_invalidation", "kind": "LOCAL_CONDITION",
            "occurred_tick": 6, "known_tick": 6,
            "candidate": "third_buy_extension",
            "scope": c["scope"], "evidence": gate.EVIDENCE})
        with self.assertRaisesRegex(ValueError, "resurrected"):
            gate.assess(c, 7)

    def test_no_comment_reconstructed_from_empty_events(self):
        c = self.get_case(8)
        x = gate.assess(c, 999)
        self.assertEqual(len(x["remaining_hypotheses"]), 2)
        self.assertEqual(x["observed_event_ids"], [])
        self.assertFalse(x["sole_survivor_confirmed_final"])

    def test_source_claim_cannot_turn_into_trade_instruction(self):
        c = self.get_case(7)
        x = gate.assess(c, 500)
        self.assertEqual(x["action"], gate.NO_TRADE)
        self.assertFalse(x["market_data_used"])


if __name__ == "__main__":
    unittest.main()
