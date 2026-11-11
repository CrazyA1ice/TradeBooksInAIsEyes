"""BookCollection universal registry, mirroring, proof status and stepwise workflow gates."""
import importlib.util
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
        self.assertEqual(meta["quote_status"],"MISSING_VERBATIM")
        self.assertEqual(meta["verbatim_quotes"],[])
        self.assertIn("不是本人发言",(mirror/"quotes.md").read_text(encoding="utf-8"))

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
