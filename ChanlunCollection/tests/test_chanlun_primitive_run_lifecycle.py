"""Fail closed on converting a raw same-price run into a completed Chanlun center."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "primitive_run_lifecycle", ROOT / "tools/audit_chanlun_primitive_run_lifecycle.py")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class RawRunEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool = m.original_primitive()
        cls.contract = m.load(m.CONTRACT)
        cls.original = m.load(m.SOURCE_CONTRACT)
        cls.recursion = m.load(m.RECURSION_CONTRACT)
        cls.fixtures = m.load(m.FIXTURES)

    def case(self, key):
        return copy.deepcopy(next(row["input"] for row in self.fixtures["cases"]
                                  if row["id"] == key))

    def check(self, contract=None, original=None, recursion=None):
        return m.verify_contract(self.contract if contract is None else contract,
                                 self.tool,
                                 self.original if original is None else original,
                                 self.recursion if recursion is None else recursion)

    def test_source_locks_three_primary_author_claims_and_open_six_conditions(self):
        self.check()
        self.assertEqual(len(self.contract["source_claims"]), 3)
        self.assertEqual(len(self.contract["required_upstream_to_downstream_evidence"]), 6)
        self.assertEqual(len(self.contract["state_rules"]), 5)
        self.assertFalse(self.contract["completion_semantics"]["raw_run_closed_is_center_completed"])

    def test_rejects_renaming_price_run_close_as_author_center_end(self):
        doc = copy.deepcopy(self.contract)
        doc["state_rules"][-1]["status"] = "AUTHORED_CHANLUN_CENTER_COMPLETED"
        with self.assertRaisesRegex(ValueError, "conflated"):
            self.check(contract=doc)
        doc = copy.deepcopy(self.contract)
        doc["completion_semantics"]["raw_run_closed_is_center_completed"] = True
        with self.assertRaisesRegex(ValueError, "completed center"):
            self.check(contract=doc)

    def test_rejects_proof_conditions_removed_or_recursion_auto_certified(self):
        doc = copy.deepcopy(self.contract)
        doc["required_upstream_to_downstream_evidence"].pop()
        with self.assertRaisesRegex(ValueError, "Missing independent"):
            self.check(contract=doc)
        recursive = copy.deepcopy(self.recursion)
        recursive["conditional_center_is_certified"] = True
        with self.assertRaisesRegex(ValueError, "completion proof"):
            self.check(recursion=recursive)

    def test_source_role_or_upstream_contract_mutation_fails(self):
        source = copy.deepcopy(self.original)
        source["actual_center_completed"] = True
        with self.assertRaisesRegex(ValueError, "completion proof"):
            self.check(original=source)
        doc = copy.deepcopy(self.contract)
        doc["source_claims"][1] = "CL018-EDITORIAL_FAKE"
        with self.assertRaisesRegex(ValueError, "Source claim lineage"):
            self.check(contract=doc)

    def test_all_eight_lifecycle_fixtures_match_existing_raw_witnesses(self):
        receipt = m.run_fixtures(self.fixtures, self.contract, self.tool)
        self.assertEqual(receipt["status"], m.FINAL_CERT)
        self.assertEqual(receipt["lifecycle_cases"], 8)
        self.assertEqual(receipt["actual_completed_centers"], 0)
        self.assertEqual(receipt["eligible_child_type_certificates"], 0)
        self.assertFalse(receipt["proof38_or_99"])

    def test_exact_third_trade_and_extension_preserve_first_time(self):
        first = m.audit(self.case("first_three_equal"), self.contract, self.tool)
        extended = m.audit(self.case("extend_equal_fourth"), self.contract, self.tool)
        self.assertEqual(first["raw_price_runs"][0]["third_trade_id"], 3)
        self.assertEqual(extended["raw_price_runs"][0]["third_trade_id"], 3)
        self.assertEqual(first["raw_price_runs"][0]["third_observed_at"],
                         extended["raw_price_runs"][0]["third_observed_at"])
        self.assertEqual(extended["raw_price_runs"][0]["trade_count"], 4)
        self.assertFalse(extended["raw_price_runs"][0]["raw_price_run_closed"])

    def test_first_price_change_closes_only_price_run_not_center(self):
        result = m.audit(self.case("first_price_break_closes_only_raw_run"),
                         self.contract, self.tool)
        old, new = result["raw_price_runs"]
        self.assertTrue(old["raw_price_run_closed"])
        self.assertEqual(old["closed_by_trade_id"], 4)
        self.assertEqual(old["closed_observed_at"], "2026-11-08T09:03:00+00:00")
        self.assertFalse(old["legal_center_completed"])
        self.assertFalse(new["raw_price_run_closed"])
        self.assertEqual(new["start_trade_id"], 4)
        self.assertFalse(result["may_enter_recursive_center_constructor"])

    def test_repeated_price_after_interruption_starts_new_run(self):
        r = m.audit(self.case("two_equal_runs_separated"), self.contract, self.tool)
        self.assertEqual([(x["start_trade_id"],x["third_trade_id"])
                          for x in r["raw_price_runs"]], [(1,3),(4,None),(5,7)])
        self.assertEqual([x["raw_price_run_closed"] for x in r["raw_price_runs"]],
                         [True,True,False])
        self.assertEqual(r["eligible_base_witness_count"], 2)

    def test_second_equal_trade_has_no_third_witness(self):
        r = m.audit(self.case("before_third"), self.contract, self.tool)
        self.assertEqual(r["event_provenance"][-1]["event_state"],
                         "RAW_EQUAL_PREFIX_BELOW_THIRD")
        self.assertIsNone(r["raw_price_runs"][0]["third_trade_id"])
        self.assertEqual(r["eligible_base_witness_count"], 0)

    def test_future_events_do_not_change_prefix_hash_or_lifecycle(self):
        x = m.audit(self.case("first_three_equal"), self.contract, self.tool)
        y = m.audit(self.case("future_change_not_asof_visible"), self.contract, self.tool)
        self.assertEqual(x, y)
        self.assertEqual(len(x["visible_prefix_sha256"]), 64)

    def test_mixed_version_blocks_derived_center_lifecycle(self):
        r = m.audit(self.case("observed_mixed_version_blocks"), self.contract, self.tool)
        self.assertEqual(r["status"], "RULE_VERSION_INCOMPATIBLE_NOT_EVALUATED")
        self.assertEqual(r["raw_price_runs"], [])
        self.assertEqual(r["event_provenance"], [])
        self.assertEqual(r["eligible_base_witness_count"], 0)

    def test_user_forged_real_center_or_out_of_order_events_rejected(self):
        bad = self.case("first_three_equal")
        bad["events"][-1]["legal_center_completed"] = True
        with self.assertRaisesRegex(ValueError, "certification"):
            m.audit(bad, self.contract, self.tool)
        bad = self.case("first_three_equal")
        bad["events"][1]["trade_id"] = 1
        with self.assertRaisesRegex(ValueError, "out-of-order"):
            m.audit(bad, self.contract, self.tool)

    def test_lifecycle_output_cannot_be_consumed_as_three_completed_child_types(self):
        r = m.audit(self.case("first_three_equal"), self.contract, self.tool)
        path = ROOT / "tools/audit_chanlun_recursive_source_eligibility.py"
        spec = importlib.util.spec_from_file_location("three_child_geometry", path)
        recursion_tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(recursion_tool)
        with self.assertRaisesRegex(ValueError, "Unexpected source/market or claim fields"):
            recursion_tool.interval_result(r)

    def test_decimal_trade_prices_are_canonically_normalized(self):
        previous = m.load(ROOT / "tests/fixtures/chanlun_lowest_trade_prefix_cases_v1.json")
        inp = next(row["input"] for row in previous["cases"]
                   if row["id"] == "exact_decimal_canonical_equal")
        receipt = m.audit(inp, self.contract, self.tool)
        self.assertEqual(receipt["raw_price_runs"][0]["price"], "2")
        self.assertEqual(receipt["raw_price_runs"][0]["third_trade_id"], 3)

    def test_article_and_indexes_describe_raw_closure_not_parent_completion(self):
        article = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/26_同价成交段的生命周期与中枢完成证据隔离.md"
        data = article.read_text(encoding="utf-8")
        for key in ("CL35-SO-2", "CL018-S07", "CL020-S01",
                    "PRICE_CHANGED_CLOSES_PREVIOUS_RAW_RUN_ONLY",
                    "visible_prefix_sha256", "价格段结束不等于中枢完成",
                    "未完成", "OB38-UNIQUE", "NOT_RUN"):
            self.assertIn(key, data)
        for index in (
            ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE/README.md",
            ROOT / "deliverables/chanlun_108_acceptance/README.md",
        ):
            self.assertIn(article.name,index.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
