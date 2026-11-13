import json
import unittest
from copy import deepcopy
from tools.audit_chanlun_reply_identity_v488 import SPEC,audit

class EarlyReplyTriageV488(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=json.loads(SPEC.read_text(encoding="utf-8"))
    def reject(self,change):
        bad=deepcopy(self.spec);change(bad)
        with self.assertRaises(ValueError):
            audit(bad)
    def test_baseline(self):
        self.assertEqual(audit(self.spec)["replies"],2)
    def test_wrong_archive_date(self):
        self.reject(lambda x:x["archival_replies"][0].update(reply_at="2007-03-09 11:51:34"))
    def test_wrong_questioner(self):
        self.reject(lambda x:x["archival_replies"][0].update(questioner="凯翔"))
    def test_wrong_question_clock(self):
        self.reject(lambda x:x["archival_replies"][1].update(question_at="2007-02-12 16:30:00"))
    def test_confucius_reply_not_lesson29(self):
        self.reject(lambda x:x["archival_replies"][1].update(parent_context="LESSON29_COMMENT_ARCHIVE"))
    def test_dont_make_archived_reply_sina_original(self):
        self.reject(lambda x:x["archival_replies"][0].update(source_role="HISTORIC_SINA_ORIGINAL_AUTHENTICATED"))
    def test_cant_upgrade_citation_to_second_formula(self):
        self.reject(lambda x:x["archival_replies"][1].update(no_independent_center_formula=False))
    def test_separate_views_from_partition_policy(self):
        self.reject(lambda x:x["candidate_taxonomy"][1].update(changes="LEGAL_DECOMPOSITION_POLICY_R"))
    def test_sep_views_vs_decomposition_receipts(self):
        self.reject(lambda x:x["candidate_taxonomy"][2].update(reply_evidence=["MAR08_TWO_VIEWS"]))
    def test_preregistered_old_march_reply_not_new(self):
        self.reject(lambda x:x["prior_evidence"][0].update(date="2007-07-20"))
    def test_cannot_identify_kaixiang_statement(self):
        self.reject(lambda x:x["provenance_limit"].update(kaixiang_explicitly_identified_one_of_these_replies=True))
    def test_cannot_claim_2007_original_html(self):
        self.reject(lambda x:x["provenance_limit"].update(exact_historical_sina_comment_bytes_verified=True))
    def test_no_laohu_book(self):
        self.reject(lambda x:x["provenance_limit"].update(laohu_complete_edition_bytes_reviewed=True))
    def test_no_market_experiment(self):
        self.reject(lambda x:x["provenance_limit"].update(market_experiment_run=True))
    def test_no_automatic_completion(self):
        self.reject(lambda x:x["provenance_limit"].update(source_replies_certify_finished_movement=True))
    def test_open_a087_not_removed(self):
        self.reject(lambda x:x["gates"].remove("A087_REFERENT_OPEN"))
    def test_unknown_b3_cannot_have_fabricated_evidence(self):
        self.reject(lambda x:x["candidate_taxonomy"][3].update(reply_evidence=["FEB09_R29"]))
    def test_cannot_duplicate_lesson29_reply_in_r52(self):
        self.reject(lambda x:x["archival_replies"][1].update(archive_url="https://eczsc.com/replies?lesson=29"))

if __name__=="__main__":
    unittest.main()
