"""The independently observed source is not the F01 +1 terminal declaration."""
from __future__ import annotations
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location(
    "kx_exit_v457", ROOT/"tools/audit_kaixiang_exit_evidence_v457.py")
gate=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=gate
spec.loader.exec_module(gate)
CLAIMS=ROOT/"tests/fixtures/kaixiang_exit_evidence_v457.json"
SOURCE=ROOT/"tests/fixtures/kaixiang_raw_tape_v456.json"


class KaixiangExitProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.claims=json.loads(CLAIMS.read_text(encoding="utf-8"))
        cls.source=json.loads(SOURCE.read_text(encoding="utf-8"))

    def claim(self):
        return copy.deepcopy(self.claims)

    def sourcecopy(self):
        return copy.deepcopy(self.source)

    def test_all_prefixes_and_f01_dag_really_run(self):
        receipt=gate.audit_fixture(CLAIMS)
        self.assertEqual(receipt["pinned_raw_prices"],27)
        self.assertEqual(receipt["f01_graph_nodes"],43)
        self.assertEqual(receipt["observed_prefixes"],8)
        self.assertFalse(receipt["real_market_data"])
        self.assertEqual(receipt["independently_authenticated_exit_count"],0)

    def test_local_condition_is_observable_before_synthetic_exit_label(self):
        x=gate.examine_prefix(self.source,self.claims,9)
        self.assertEqual(x["local_nonadvance_condition_count"],1)
        self.assertEqual(x["synthetic_exit_label_count"],0)
        self.assertEqual(x["independently_completed_movement_count"],0)

    def test_synthetic_exit_label_can_never_promote_completion(self):
        x=gate.examine_prefix(self.source,self.claims,28)
        self.assertEqual(x["local_nonadvance_condition_count"],3)
        self.assertEqual(x["synthetic_exit_label_count"],3)
        self.assertEqual(x["source_backed_exit_event_count"],0)
        self.assertFalse(x["can_promote_to_verified_higher_center"])
        self.assertEqual(x["completion_status"],gate.UNKNOWN)

    def test_last_exit_tick_has_no_trade_in_27_price_source(self):
        x=gate.examine_prefix(self.source,self.claims,28)
        self.assertEqual(x["observed_raw_price_count"],27)
        self.assertEqual(x["label_provenance"][-1]["label_tick"],28)
        self.assertEqual(x["label_provenance"][-1]["raw_tape_at_tick"],
                         "NO_RAW_PRICE_EVENT_AT_CLAIM_TICK")

    def test_first_two_later_tape_trades_do_not_prove_previous_exit(self):
        x=gate.examine_prefix(self.source,self.claims,19)
        self.assertEqual([v["raw_tape_at_tick"] for v in x["label_provenance"]],
                         ["NEXT_MEMBER_RAW_PRICE_NOT_EXIT_EVENT"]*2)
        self.assertEqual(x["independently_completed_movement_count"],0)

    def test_future_price_changes_cannot_change_earlier_prefix_evidence(self):
        source=self.sourcecopy()
        early=gate.examine_prefix(source,self.claims,9)
        source["raw_prices"][20]="600"
        self.assertEqual(gate.examine_prefix(source,self.claims,9),early)

    def test_same_nine_raw_prices_allow_different_next_center_prices(self):
        v=gate.different_future_same_prefix(self.source)
        self.assertTrue(v["different_price_futures_possible"])
        self.assertTrue(v["original_prefix_condition_identical"])
        self.assertFalse(v["futures_are_legal_finished_chanlun_types_proven"])

    def test_forged_market_authenticated_flag_rejected(self):
        c=self.claim();c["exit_claims"][0]["independently_authenticated"]=True
        with self.assertRaisesRegex(ValueError,"masquerade"):
            gate.validate_claims(c,self.source)

    def test_forged_independent_market_event_id_rejected(self):
        c=self.claim();c["exit_claims"][1]["market_event_id"]="TICK-19-MARKET-EXIT"
        with self.assertRaisesRegex(ValueError,"masquerade"):
            gate.validate_claims(c,self.source)

    def test_arbitrary_exit_tick_not_accepted_as_original(self):
        c=self.claim();c["exit_claims"][2]["declared_first_known_tick"]=27
        with self.assertRaisesRegex(ValueError,"arbitrary"):
            gate.validate_claims(c,self.source)

    def test_exit_label_can_never_become_raw_trade_event_kind(self):
        c=self.claim();c["exit_claims"][0]["claim_kind"]="RAW_PRICE_COMPLETION"
        with self.assertRaisesRegex(ValueError,"masquerade"):
            gate.validate_claims(c,self.source)

    def test_invalid_member_reordering_rejected(self):
        c=self.claim();c["exit_claims"][0],c["exit_claims"][1]=(
            c["exit_claims"][1],c["exit_claims"][0])
        with self.assertRaisesRegex(ValueError,"label/member identity"):
            gate.validate_claims(c,self.source)

    def test_duplicate_ids_rejected(self):
        c=self.claim();c["exit_claims"][1]["id"]=c["exit_claims"][0]["id"]
        with self.assertRaisesRegex(ValueError,"duplicate"):
            gate.validate_claims(c,self.source)

    def test_injected_proof_data_fields_fail_closed(self):
        c=self.claim();c["exit_claims"][0]["source_trade_proves_completion"]=True
        with self.assertRaisesRegex(ValueError,"extra or missing"):
            gate.validate_claims(c,self.source)

    def test_wrong_source_digest_or_index_rejected(self):
        c=self.claim();c["source_tape_sha256"]="new-fake-digest"
        with self.assertRaisesRegex(ValueError,"source A-index"):
            gate.validate_claims(c,self.source)
        c=self.claim();c["source_answer_ids"]=["A001"]
        with self.assertRaisesRegex(ValueError,"source A-index"):
            gate.validate_claims(c,self.source)

    def test_wrong_synthetic_origin_rejected(self):
        c=self.claim();c["source_authentication"]="REAL_EXCHANGE"
        with self.assertRaisesRegex(ValueError,"market-authenticated"):
            gate.validate_claims(c,self.source)

    def test_no_source_prices_are_read_before_available_tick(self):
        x=gate.examine_prefix(self.source,self.claims,0)
        self.assertEqual(x["observed_raw_price_count"],0)
        self.assertEqual(x["local_nonadvance_condition_count"],0)
        self.assertEqual(x["synthetic_exit_label_count"],0)

    def test_invalid_asof_clock_rejected(self):
        for tick in (-1,True,3.1):
            with self.assertRaisesRegex(ValueError,"as-of"):
                gate.examine_prefix(self.source,self.claims,tick)


if __name__=="__main__":
    unittest.main()
