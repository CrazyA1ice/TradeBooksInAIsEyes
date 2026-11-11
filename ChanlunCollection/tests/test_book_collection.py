"""BookCollection universal registry, mirroring, proof status and stepwise workflow gates."""
import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def imported(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
m=imported("book_collection","tools/book_collection.py")
gate=imported("collection_workflow_gate","tools/audit_book_collection_change.py")

class BookCollectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book=m.collection("chanlun")
        cls.snapshot=m.snapshot(cls.book)

    def test_registers_chanlun_and_has_per_book_folder(self):
        self.assertEqual(self.book["folder"],"ChanlunCollection")
        self.assertRegex(self.book["workflow_version"],r"^4\.[0-9]+\.[0-9]+$")
        book_flow=(ROOT/"ChanlunCollection/WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("v"+self.book["workflow_version"],book_flow)
        self.assertTrue(self.book["canonical_unchanged"])

    def test_all_five_original_pdf_volumes_present_in_manifest(self):
        self.assertEqual(self.snapshot["original_pdf_count"],5)
        self.assertEqual(self.snapshot["chapter_research_count"],108)
        self.assertEqual(self.snapshot["evidence_card_count"],108)

    def test_manifest_records_real_git_blob_and_source_bytes(self):
        for item in self.snapshot["entries"]:
            self.assertEqual(m.blob_sha(ROOT/item["source_path"]),item["git_blob_sha"])
            self.assertEqual((ROOT/item["source_path"]).stat().st_size,item["size_bytes"])
            self.assertEqual(item["mirror_path"],m.mirror_destination(self.book,item["source_path"]))
            if item["source_path"].startswith("other_views/chanlun/"):
                expected="ChanlunCollection/OtherVoices/"+item["source_path"].split("other_views/chanlun/",1)[1]
                self.assertEqual(item["mirror_path"],expected)

    def test_per_person_archive_contains_quotes_analysis_and_provenance(self):
        source=ROOT/"other_views/chanlun/speaker-unknown-001"
        mirror=ROOT/"ChanlunCollection/OtherVoices/speaker-unknown-001"
        for part in ["README.md","quotes.md","analysis.md","sources.json","updates.md"]:
            self.assertTrue((source/part).is_file())
            self.assertEqual((source/part).read_bytes(),(mirror/part).read_bytes())
        meta=json.loads((mirror/"sources.json").read_text(encoding="utf-8"))
        self.assertFalse(meta["speaker_verified"])
        self.assertEqual(meta["original_speaker_name"],"凯翔")
        self.assertEqual(meta["quote_status"],"VERBATIM_FROM_USER_SUPPLIED_EXPORT")
        self.assertEqual(len(meta["verbatim_quotes"]),100)
        self.assertIn("A089",(mirror/"quotes.md").read_text(encoding="utf-8"))
        self.assertIn("归属",(mirror/"quotes.md").read_text(encoding="utf-8"))

    def test_kaixiang_100_answer_export_and_no_independent_comments(self):
        d=ROOT/"ChanlunCollection/OtherVoices/speaker-unknown-001"
        data=(d/"answers-2026-11-11.md").read_bytes()
        self.assertEqual(len(data),130167)
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         "3fb9f3255cffe62a93f5473cfbf003f15d4c60ae8ee4d9f2e4e56083b935b7b9")
        t=data.decode("utf-8")
        self.assertEqual(t.count("\r\n## "),100)
        self.assertEqual(t.count("- 原文链接: https://www.zhihu.com/question/"),100)
        self.assertIn("中枢的定义方法是有两种的",t)
        self.assertIn("第三层意思:在正文中有几次点到了",t)
        j=json.loads((d/"answers-index.json").read_text(encoding="utf-8"))
        self.assertEqual(j["answer_count"],100)
        self.assertEqual(j["unique_answer_urls"],100)
        self.assertEqual(j["explicit_chanlun_mentions"],31)
        self.assertEqual(j["independent_comment_records"],0)
        self.assertEqual(len(set(x["answer_id"] for x in j["answers"])),100)
        self.assertEqual([x["id"] for x in j["answers"]],["A%03d"%i for i in range(1,101)])
        self.assertTrue(j["answers"][6]["contains_third_party_quoted_trader"])
        self.assertEqual(j["answers"][88]["id"],"A089")
        self.assertIn("NOT_PRESENT_IN_UPLOAD",(d/"comments.md").read_text(encoding="utf-8"))

    def test_kaixiang_asof_decision_audit_is_provenance_bound(self):
        base=ROOT/"other_views/chanlun/speaker-unknown-001"
        mirrored=ROOT/"ChanlunCollection/OtherVoices/speaker-unknown-001"
        name="decision_audit_v451.json"
        self.assertEqual((base/name).read_bytes(),(mirrored/name).read_bytes())
        audit=json.loads((base/name).read_text(encoding="utf-8"))
        index=json.loads((base/"answers-index.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["status"],"RESEARCHER_TEST_DESIGN_NOT_KAIXIANG_TRADING_ALGORITHM")
        self.assertEqual(audit["market_data"],"NOT_RUN")
        self.assertEqual(audit["source_sha256"],index["source_sha256"])
        self.assertEqual(len(audit["cases"]),8)
        self.assertEqual(len({x["id"] for x in audit["cases"]}),8)
        known={answer["id"] for answer in index["answers"]}
        for case in audit["cases"]:
            self.assertTrue(set(case["source_answer_ids"]) <= known)
            self.assertTrue(case["preconditions"])
            self.assertTrue(case["when_can_exclude"])
            self.assertTrue(case["must_not_claim"])
            self.assertTrue(case["researcher_judgment"])
        self.assertEqual(
            audit["independent_comment_evidence"],
            "MISSING_IN_UPLOADED_EXPORT_NOT_ZERO_ON_ZHIHU")

    def test_kaixiang_symbolic_gate_runs_on_same_eight_source_cases(self):
        fixture=ROOT/"tests/fixtures/kaixiang_asof_symbolic_v452.json"
        text=json.loads(fixture.read_text(encoding="utf-8"))
        previous=json.loads((ROOT/"other_views/chanlun/speaker-unknown-001/decision_audit_v451.json").read_text(encoding="utf-8"))
        self.assertEqual(text["origin"],"SYNTHETIC_SYMBOLS_NOT_MARKET")
        self.assertEqual(len(text["cases"]),len(previous["cases"]))
        self.assertEqual(
            [(x["id"],x["source_answer_ids"]) for x in text["cases"]],
            [(x["id"],x["source_answer_ids"]) for x in previous["cases"]])
        gate=imported("kaixiang_asof_candidates","tools/audit_kaixiang_asof_candidates.py")
        checked=gate.audit_fixture(fixture)
        self.assertEqual(checked["cases"],8)
        self.assertGreaterEqual(checked["prefix_checks"],15)
        self.assertFalse(checked["market_data"])
        last=gate.assess(text["cases"][0],5)
        self.assertEqual(last["sole_survivor"],"decline")
        self.assertFalse(last["sole_survivor_confirmed_final"])
        self.assertFalse(last["candidate_universe_exhaustiveness_proven"])
        self.assertFalse(last["order_submitted"])

    def test_kaixiang_three_member_asof_bridge_consumes_existing_source_gates(self):
        source=ROOT/"tests/fixtures/kaixiang_center_asof_bridge_v453.json"
        fixture=json.loads(source.read_text(encoding="utf-8"))
        self.assertEqual(fixture["origin"],"SYNTHETIC_SYMBOLS_NOT_MARKET")
        self.assertEqual(len(fixture["bridge_cases"]),5)
        gate=imported("kaixiang_three_member_bridge","tools/audit_kaixiang_center_asof_bridge.py")
        proof=gate.audit_fixture(source)
        self.assertEqual(proof["bridge_cases"],5)
        self.assertEqual(proof["prefix_checks"],12)
        self.assertFalse(proof["market_data"])
        self.assertFalse(proof["genuine_lower_level_completion_verified"])
        self.assertFalse(proof["third_buy_detected"])
        self.assertEqual(proof["orders_sent"],0)

    def test_kaixiang_f01_graph_bridge_has_structural_not_market_proof(self):
        data=ROOT/"tests/fixtures/kaixiang_f01_graph_bridge_v454.json"
        source=json.loads(data.read_text(encoding="utf-8"))
        self.assertEqual(source["source_answer_ids"],["A026","A084","A016"])
        bridge=imported("kaixiang_f01_graph","tools/audit_kaixiang_f01_graph_completion_bridge.py")
        receipt=bridge.audit_fixture(data)
        self.assertEqual(receipt["f01_receipts"],31)
        self.assertEqual(receipt["visible_members"],[0,1,2,3])
        self.assertFalse(receipt["lower_level_finished_movements_independently_proven"])
        self.assertFalse(receipt["f01_authenticates_market"])
        self.assertFalse(receipt["real_market_data"])
        self.assertEqual(receipt["orders"],0)

    def test_alias_paths_are_safe_and_no_registry_collision(self):
        self.assertEqual(
            m.mirror_destination(self.book,"other_views/chanlun/speaker-unknown-001/analysis.md"),
            "ChanlunCollection/OtherVoices/speaker-unknown-001/analysis.md")
        broken=dict(self.book)
        broken["mirror_path_overrides"]={"other_views/chanlun":"../unsafe"}
        with self.assertRaisesRegex(ValueError,"Unsafe or unregistered"):
            m.validate_mirror_overrides(broken)
        broken["mirror_path_overrides"]={"unregistered":"OtherVoices"}
        with self.assertRaisesRegex(ValueError,"Unsafe or unregistered"):
            m.validate_mirror_overrides(broken)

    def test_mirrored_paths_do_not_break_existing_relative_references(self):
        for rel in ["deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_LOGICAL_CONTINUITY.md",
                    "knowledge/evidence/chanlun_lesson108.json",
                    "ChineseBooks/缠论/缠论_卷5.pdf"]:
            self.assertTrue((ROOT/rel).is_file())
            self.assertTrue((ROOT/"ChanlunCollection"/rel).is_file())

    def test_every_original_has_identical_byte_for_byte_mirror(self):
        receipt=m.check(self.book)
        self.assertEqual(receipt["status"],"EXACT_PER_BOOK_COLLECTION_SOURCE_MIRROR_PASSED")
        self.assertEqual(receipt["chapters"],108)
        self.assertEqual(receipt["original_pdfs"],5)

    def test_book_workflow_log_and_qa_entry_exist(self):
        for p in m.MANAGED:
            self.assertTrue((ROOT/"ChanlunCollection"/p).is_file())
        text=(ROOT/"ChanlunCollection"/"QUESTION_GUIDE.md").read_text(encoding="utf-8")
        self.assertIn("PDF物理页",text)
        self.assertIn("未证",text)

    def test_no_market_or_author_proof_claims_in_book_registry(self):
        self.assertTrue(self.book["proof_status"].startswith("OPEN_"))
        self.assertEqual(self.book["real_market_experiments"],"NOT_RUN")
        self.assertEqual(self.snapshot["real_market_experiments"],"NOT_RUN")

    def test_new_research_step_requires_workflow_worklog_status_manifest(self):
        changes={"analyses/books/chanlun/chapters/lesson_035.md"}
        with self.assertRaisesRegex(ValueError,"Every book research step"):
            gate.validate(changes,{"schema_version":1,"collections":[self.book]})
        required={"docs/BOOK_RESEARCH_WORKFLOW.md","ChanlunCollection/WORKFLOW.md",
                  "ChanlunCollection/WORK_LOG.md","ChanlunCollection/RESEARCH_STATUS.md",
                  "ChanlunCollection/COLLECTION_MANIFEST.json"}
        receipt=gate.validate(changes|required,{"schema_version":1,"collections":[self.book]})
        self.assertEqual(receipt["books_affected"],["chanlun"])

    def test_mirror_only_changes_also_require_workflow_update(self):
        with self.assertRaisesRegex(ValueError,"Every book research step"):
            gate.validate({"ChanlunCollection/knowledge/evidence/chanlun_lesson035.json"},
                          {"schema_version":1,"collections":[self.book]})

    def test_unrelated_new_book_does_not_force_chanlun_revision(self):
        receipt=gate.validate({"SomeOtherBookCollection/README.md"},
                              {"schema_version":1,"collections":[self.book]})
        self.assertFalse(receipt["books_affected"])

    def test_no_directly_edited_mirror_which_does_not_match_manifest(self):
        e=self.snapshot["entries"][0]
        self.assertEqual((ROOT/e["source_path"]).read_bytes(),
                         (ROOT/e["mirror_path"]).read_bytes())

    def test_workflow_doc_version_is_updated(self):
        text=(ROOT/"docs/BOOK_RESEARCH_WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("v"+self.book["workflow_version"],text)
        self.assertIn("每做一步",text)
        self.assertIn("G7",text)
        self.assertIn("ChanlunCollection",text)

if __name__=="__main__":
    unittest.main()
