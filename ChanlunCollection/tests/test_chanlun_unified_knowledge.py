import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("unified", ROOT/"tools/audit_chanlun_unified_knowledge.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class UnifiedEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.inputs = audit.load_sources()
    def check(self):
        return audit.build_index(*self.inputs)
    def test_unified_index_is_current(self):
        result=self.check()
        audit.validate_snapshot(result)
        self.assertEqual(result["counts"], {"lessons":108,"graph_nodes":84,"graph_edges":145,
                                             "rule_attributions":16,"evidence_files":108})
    def test_all_graph_edge_targets_known(self):
        result=self.check()
        ids={x["id"] for x in result["nodes"]}
        self.assertTrue(all(e["from"] in ids and e["to"] in ids for e in result["edges"]))
    def test_108_legacy_evidence_coverage(self):
        index=self.check()
        self.assertEqual(index["lessons"][0]["lesson"],1)
        self.assertEqual(index["lessons"][-1]["lesson"],108)
        self.assertEqual(index["lessons"][0]["start_pdf_page"],3)
        self.assertEqual(index["lessons"][-1]["end_pdf_page"],441)
    def test_duplicate_concept_rejected(self):
        self.inputs[1][1]["nodes"].append(copy.deepcopy(self.inputs[1][0]["nodes"][0]))
        with self.assertRaisesRegex(audit.AuditError, "Duplicate node"):
            self.check()
    def test_dangling_cross_graph_edge_rejected(self):
        self.inputs[1][9]["edges"][0]["to"]="NO_SUCH_SOURCE"
        with self.assertRaisesRegex(audit.AuditError, "Dangling"):
            self.check()
    def test_fake_source_sha_rejected(self):
        self.inputs[1][9]["source_pdf_sha256_by_volume"]["5"]="0"*64
        with self.assertRaisesRegex(audit.AuditError, "SHA"):
            self.check()
    def test_evidence_sha_immutable(self):
        self.inputs[3][107]["source"]["sha256"]="bad"
        with self.assertRaisesRegex(audit.AuditError, "Evidence PDF SHA"):
            self.check()
    def test_evidence_physical_pages_not_outside_course(self):
        self.inputs[3][107]["source"]["pdf_pages"]=[1]
        with self.assertRaisesRegex(audit.AuditError, "page out of course"):
            self.check()
    def test_legacy_lesson_number_still_supported(self):
        self.assertNotIn("lesson", self.inputs[3][0])
        self.assertEqual(self.inputs[3][0]["source"]["lesson_number"],1)
        self.check()
    def test_unknown_editor_is_never_auto_backdated(self):
        entry=next(x for x in self.inputs[2]["entries"] if x["id"]=="segment_067_editor_objection")
        entry["source_displayed_at"]="2007-08-01T22:31:55"
        with self.assertRaisesRegex(audit.AuditError, "backdated"):
            self.check()
    def test_unresolved_appendix_never_auto_backdated(self):
        entry=next(x for x in self.inputs[2]["entries"] if x["id"]=="pen_062_appended_candidate")
        entry["source_displayed_at"]="2007-06-30T09:49:51"
        with self.assertRaisesRegex(audit.AuditError, "backdated"):
            self.check()
    def test_earlier_asof_does_not_include_later_pen_rule(self):
        reg=self.inputs[2]
        before=audit.eligible_dated_source_versions(reg,"pen","2007-09-17T23:00:00")
        after=audit.eligible_dated_source_versions(reg,"pen","2007-09-19T00:00:00")
        self.assertNotIn("pen_081_later_dated_post",before)
        self.assertIn("pen_081_later_dated_post",after)
        self.assertNotIn("pen_062_appended_candidate",after)
    def test_2008_author_editor_conflict_coexists(self):
        reg=self.inputs[2]
        a={x["id"]:x for x in reg["entries"]}
        self.assertNotEqual(a["branch_100_author"]["role"],a["branch_100_editor"]["role"])
        self.assertIsNone(a["branch_100_editor"]["source_displayed_at"])
        self.assertIn("branch_100_author",[x["target"] for x in a["branch_100_editor"]["links"]])
        self.check()
    def test_no_rule_link_to_fabricated_version(self):
        e=self.inputs[2]["entries"][2]
        e["links"].append({"target":"fictitious_new_rule","relation":"supersedes"})
        with self.assertRaisesRegex(audit.AuditError, "Bad rule version link"):
            self.check()
    def test_graph_reference_path_must_exist(self):
        self.inputs[1][9]["references"].append("fake_definition.json")
        with self.assertRaisesRegex(audit.AuditError, "dependency path missing"):
            self.check()
    def test_node_source_outside_actual_volume(self):
        self.inputs[1][9]["nodes"][0]["source"]["pdf_pages"]=[999]
        with self.assertRaisesRegex(audit.AuditError, "Invalid node source page"):
            self.check()

if __name__=="__main__":unittest.main()
