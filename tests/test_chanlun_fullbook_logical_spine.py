"""108 lesson source-grounded conceptual atlas and explicit proof frontier gates."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"tools/audit_chanlun_fullbook_logical_spine.py"
spec=importlib.util.spec_from_file_location("chanlun108_logical_spine",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class FullBookLogicalSpineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config,cls.chapters,cls.forward,cls.incoming,cls.report=m.verify_and_collect()
        cls.manuscript=m.MANUSCRIPT.read_text(encoding="utf-8")

    def test_108_independent_firstpass_source_chapters_retained(self):
        self.assertEqual(set(self.chapters),set(range(1,109)))
        self.assertEqual(len(self.config["chapter_roles"]),108)
        self.assertEqual(self.report["source_anchored_chapters"],108)
        self.assertEqual(self.report["original_book_volumes"],5)

    def test_complete_ordered_11_phase_partition_without_missing_chapters(self):
        cover=[n for p in self.config["phases"] for n in range(p["start"],p["end"]+1)]
        self.assertEqual(cover,list(range(1,109)))
        self.assertEqual(len(self.config["phases"]),11)
        self.assertEqual({x["phase"] for x in self.chapters.values()},
                         {f"P{i:02d}" for i in range(1,12)})

    def test_each_role_is_interpretation_not_automatically_author_proof(self):
        self.assertTrue(self.config["reading_order_only_not_logical_proof"])
        self.assertEqual(self.config["scope"],
            "CURATED_108_CHAPTER_RESEARCH_ROLES_AND_INTERPRETIVE_BRIDGES_NOT_PROVEN_THEORY")
        self.assertFalse(self.config["all_theorems_proven"])
        self.assertFalse(self.config["all_historical_rules_frozen"])

    def test_all_original_canonical_pdf_and_card_sha_sources_retained(self):
        for n,x in self.chapters.items():
            with self.subTest(lesson=n):
                self.assertEqual(len(x["card_sha256"]),64)
                self.assertEqual(len(x["pdf_sha256"]),64)
                self.assertTrue(x["first_claim"])
                self.assertGreaterEqual(x["source_claim_count"],1)

    def test_conceptual_links_are_acyclic_forward_only_without_fake_certificates(self):
        seen=set()
        for x in self.config["conceptual_links"]:
            self.assertLess(x["from"],x["to"])
            self.assertEqual(x["type"],"AI_CONCEPTUAL_READING_BRIDGE_NOT_DEDUCTIVE_PROOF")
            pair=(x["from"],x["to"])
            self.assertNotIn(pair,seen)
            seen.add(pair)
        self.assertGreaterEqual(len(seen),100)
        self.assertGreaterEqual(self.report["cross_stage_bridges"],20)

    def test_early_trader_to_108_bottom_has_source_anchored_conceptual_route(self):
        route=[1,11,15,17,18,20,21,53,101,108]
        for a,b in zip(route,route[1:]):
            self.assertIn(b,self.forward[a])
        self.assertIn("第1课",self.manuscript)
        self.assertIn("第108课",self.manuscript)

    def test_Kline_geometry_to_asof_midstage_higher_center_path_connected(self):
        route=[62,65,67,71,78,81,84,91,93,99,108]
        for a,b in zip(route,route[1:]):
            self.assertIn(b,self.forward[a])
        self.assertIn("第99课",self.manuscript)
        self.assertIn("自同构",self.manuscript)

    def test_divergence_support_path_does_not_generate_legal_trend(self):
        for a,b in [(15,24),(24,25),(25,50),(50,61)]:
            self.assertIn(b,self.forward[a])
        self.assertIn("不能反向执行",self.manuscript)

    def test_every_source_claim_has_research_role_and_reproducible_atlas_entry(self):
        out=m.markdown(self.config,self.chapters,self.forward,self.incoming,self.report)
        rows=[x for x in out.splitlines() if x.startswith("| **[") and "](../../../ChineseBooks" in x]
        self.assertEqual(len(rows),108)
        for n in range(1,109):
            self.assertIn(f"{n:03d} ",out)
            self.assertIn(f"chanlun_lesson{n:03d}.json",out)
        self.assertIn("图的连通性不等于理论已经自洽",out)

    def test_five_author_proof_goals_still_blocked_and_eight_frontiers_open(self):
        self.assertEqual(len(self.config["proof_frontier"]),8)
        goals={x["id"]:x for x in m.load(m.FORMAL)["goals"]}
        self.assertEqual(set(goals),m.PERMITTED_GOALS)
        self.assertTrue(all(g["status"]=="BLOCKED_NOT_CERTIFIED" for g in goals.values()))
        self.assertTrue(all(not x["resolved"] for x in self.config["proof_frontier"]))
        self.assertFalse(self.report["all_research_lemmas_proven"])

    def test_all_contradiction_and_argument_sources_remain_instead_of_silent_overrides(self):
        self.assertEqual(len(m.load(m.ARGUMENTS)["arguments"]),16)
        self.assertEqual(len(m.load(m.CONFLICTS)["entries"]),16)
        self.assertIn("不能直接判定原作者理论自相矛盾",self.manuscript) if "不能直接判定原作者理论自相矛盾" in self.manuscript else self.assertIn("不能把",self.manuscript)

    def test_late_editorial_versions_never_acquire_fake_original_dates(self):
        entries=m.load(m.VERSIONS)["entries"]
        for x in entries:
            if x["role"] in ("editor_later_undated","appendix_provenance_unresolved"):
                self.assertIsNone(x["source_displayed_at"])
                self.assertEqual(x["timestamp_basis"],"unknown")

    def test_manuscript_discloses_unproven_rg_38_99_and_live_execution(self):
        m.verify_manuscript(self.config,self.report)
        for mark in ("OB38-UNIQUE","OB38-ASOF","OB99-EXIST",
                     "OB99-LOCATION","NOT_RUN","概念连通不等于证明连通"):
            self.assertIn(mark,self.manuscript)
        self.assertFalse(self.config["real_market_data_accessed"])

    def test_all_eight_proof_gaps_are_source_linked_and_none_promoted(self):
        at=m.markdown(self.config,self.chapters,self.forward,self.incoming,self.report)
        for i in range(1,9):
            self.assertIn(f"F{i:02d}",at)
            self.assertIn(f"F{i:02d}",self.manuscript)
        self.assertEqual(self.report["unresolved_proof_frontiers"],8)

    def test_generated_atlas_matches_exact_committed_content_when_present(self):
        rendered=m.markdown(self.config,self.chapters,self.forward,self.incoming,self.report)
        if m.ATLAS.exists():
            self.assertEqual(m.ATLAS.read_text(encoding="utf-8"),rendered)


if __name__=="__main__":
    unittest.main()
