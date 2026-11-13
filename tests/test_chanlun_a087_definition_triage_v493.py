"""v4.93: offline A087 source/interpretation and formal interval counterexample guards."""
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from tools.audit_chanlun_a087_definition_triage_v493 import (
    CATALOG, audit, check_original_a087_export, check_optional_sources,
    example_from_endpoints, git_blob_sha, overlap, validate_math_case,
)


class A087DefinitionDisambiguationV493(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CATALOG.read_text(encoding="utf-8"))

    def reject(self, edit):
        snapshot = deepcopy(self.data)
        edit(snapshot)
        with self.assertRaises(ValueError):
            audit(snapshot)

    def test_normal_audit_does_not_proclaim_a087_solved(self):
        r = audit(self.data)
        self.assertEqual(r["A087"], "OPEN")
        self.assertEqual(r["hypotheses"], 4)

    def test_user_export_is_genuine_repo_blob_not_live_platform_proof(self):
        r = check_original_a087_export(self.data)
        self.assertEqual(r["question_answer_refs"], 2)
        self.assertEqual(r["exact_author_reply_citation_count"], 0)

    def test_cannot_invent_second_method_quote_in_a087(self):
        self.reject(lambda c: c["limits"].update(
            a087_quote_self_assigned_specific_historical_reply=True))

    def test_cannot_upgrade_a087_identity_to_platform_verified(self):
        self.reject(lambda c: c["limits"].update(kaixiang_identity_platform_verified=True))

    def test_cannot_announce_b3_independent_center_axiom(self):
        self.reject(lambda c: c["limits"].update(independent_B3_second_center_axiom_confirmed=True))

    def test_cannot_claim_laohu_file_obtained(self):
        self.reject(lambda c: c["limits"].update(laohu_edition_document_acquired=True))

    def test_cannot_claim_laohu_vs_other_version_research_run(self):
        self.reject(lambda c: c["limits"].update(laohu_vs_other_editions_comparison_run=True))

    def test_cannot_claim_market_results(self):
        self.reject(lambda c: c["limits"].update(real_market_E1_E4_experiments_run=True))

    def test_cannot_authenticate_2007_sina_server(self):
        self.reject(lambda c: c["limits"].update(original_2007_sina_reply_bytes_verified=True))

    def test_cannot_forge_original_zhihu_export_sha(self):
        self.reject(lambda c: c["expert_statement"].update(export_git_blob="0"*40))

    def test_cannot_forge_original_a087_permalink(self):
        self.reject(lambda c: c["expert_statement"].update(
            a087_url="https://www.zhihu.com/question/1/answer/2"))

    def test_cannot_claim_kaixiang_other_answer_backs_laohu_completeness(self):
        self.reject(lambda c: c["expert_statement"].update(
            other_answer_claim="INDEPENDENTLY_VERIFIED_FULL_LAOHU_EDITION"))

    def test_cannot_make_external_writer_kaixiang(self):
        self.reject(lambda c: c["external_interpretation"].update(
            identity_relation_to_kaixiang="SAME_PERSON"))

    def test_cannot_treat_2019_as_original_author_reply(self):
        self.reject(lambda c: c["external_interpretation"].update(
            third_party_2019_interpretation_is_author_reply=True) if False else
            c["limits"].update(third_party_2019_interpretation_is_author_reply=True))

    def test_external_cannot_be_promoted_to_verified_a087_source(self):
        self.reject(lambda c: c["external_interpretation"].update(
            cannot_use_as_A087_reply_identification=False))

    def test_pinned_lesson20_blob_identity(self):
        self.reject(lambda c: c["author_primary_text_mirrors"][0].update(
            git_blob_sha="a"*40))

    def test_pinned_lesson35_not_mislabeled_as_63(self):
        self.reject(lambda c: c["author_primary_text_mirrors"][1].update(lesson=63))

    def test_pinned_lesson63_marker_cannot_disappear(self):
        self.reject(lambda c: c["author_primary_text_mirrors"][2].update(
            required_markers=["中枢"]))

    def test_h01_cannot_be_claimed_second_axiom(self):
        self.reject(lambda c: c["candidate_triage"][0].update(
            status="AUTHOR_HAS_TWO_INDEPENDENT_CENTER_AXOMS_PROVEN"))

    def test_h02_is_context_not_a087_id(self):
        self.reject(lambda c: c["candidate_triage"][1].update(not_A087_verified=False))

    def test_h03_wrong_middle_theorem_cannot_be_canonical(self):
        self.reject(lambda c: c["candidate_triage"][2].update(
            status="PROVEN_CANONICAL_ORIGINAL_FORMULA"))

    def test_h04_remains_unknown_not_disproved(self):
        self.reject(lambda c: c["candidate_triage"][3].update(
            status="NOT_FOUND_THEREFORE_IMPOSSIBLE"))

    def test_correct_up_down_up_counterexample(self):
        ex = self.data["formal_formula"]["counterexample"]
        self.assertEqual(ex["endpoints"], [0, 10, 4, 8])
        self.assertTrue(validate_math_case(ex))
        self.assertEqual(overlap(ex["a"], ex["b"], ex["c"]), [4, 8])
        self.assertNotEqual(ex["middle_interval"], ex["triple_overlap"])

    def test_classical_middle_equals_center_is_only_special_case(self):
        ex = self.data["formal_formula"]["control_middle_equal_case"]
        self.assertFalse(validate_math_case(ex))
        self.assertEqual(overlap(ex["a"], ex["b"], ex["c"]), ex["b"])

    def test_reverse_direction_example_also_refutes_universal_claim(self):
        ex = self.data["formal_formula"]["mirror_counterexample"]
        self.assertTrue(validate_math_case(ex))
        self.assertEqual(overlap(ex["a"], ex["b"], ex["c"]), [2, 6])

    def test_cannot_rewrite_calculated_center_interval_as_middle(self):
        self.reject(lambda c: c["formal_formula"]["counterexample"].update(
            triple_overlap=[4, 10]))

    def test_cannot_misstate_endpoints_and_keep_old_ranges(self):
        self.reject(lambda c: c["formal_formula"]["counterexample"].update(
            endpoints=[0, 10, 4, 12]))

    def test_cannot_remove_middle_equal_control(self):
        self.reject(lambda c: c["formal_formula"].update(
            control_middle_equal_case={"endpoints":[0, 10, 4, 8]}))

    def test_no_overlap_for_disjoint_intervals(self):
        self.assertIsNone(overlap([0, 1], [2, 3], [4, 5]))

    def test_boundary_touches_are_not_arbitrarily_discarded(self):
        self.assertEqual(overlap([0, 3], [3, 5]), [3, 3])

    def test_needs_alternating_nonflat_segments(self):
        with self.assertRaises(ValueError):
            example_from_endpoints([0, 5, 6, 8])

    def test_pivot_consistency_for_many_numeric_alternating_walks(self):
        checked = 0
        for a in range(0, 6):
            for b in range(0, 6):
                for c in range(0, 6):
                    for d in range(0, 6):
                        if not ((a < b > c < d) or (a > b < c > d)):
                            continue
                        w = example_from_endpoints([a, b, c, d])
                        self.assertEqual(overlap(w["a"], w["b"], w["c"]),
                                         overlap(w["a"], w["c"]))
                        checked += 1
        self.assertGreater(checked, 20)

    def test_git_blob_has_exact_git_object_prefix(self):
        import hashlib
        self.assertEqual(git_blob_sha(b"hello"),
                         hashlib.sha1(b"blob 5\0hello").hexdigest())

    def test_optional_local_upstream_snapshot_bytes_are_checked(self):
        with tempfile.TemporaryDirectory() as d:
            fake = deepcopy(self.data)
            for item in fake["author_primary_text_mirrors"]:
                p = Path(d) / item["path"]
                p.parent.mkdir(parents=True, exist_ok=True)
                text = " ".join(item["required_markers"])
                p.write_text(text, encoding="utf-8")
                item["git_blob_sha"] = git_blob_sha(p.read_bytes())
            x = check_optional_sources(fake, d)
            self.assertEqual(x["lessons"], [20, 35, 63, 72])
            filename = Path(d)/fake["author_primary_text_mirrors"][0]["path"]
            filename.write_bytes(filename.read_bytes() + b"changed")
            with self.assertRaises(ValueError):
                check_optional_sources(fake, d)

    def test_optional_upstream_source_missing_is_not_treated_as_empty(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                check_optional_sources(self.data, d)

    def test_missing_historical_original_cannot_automatically_close_A087(self):
        self.reject(lambda c: c["frontier"].update(A087="CONFIRMED"))

    def test_cannot_obscure_prior_v438_origin(self):
        self.reject(lambda c: c["prior_evidence"].update(
            older_hypotheses_not_reidentified_as_new=False))


if __name__ == "__main__":
    unittest.main()
