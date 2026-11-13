"""Offline tests use handwritten synthetic HTML, never redistribute source pages."""
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from tools.audit_chanlun_archive_crosswalk_v489 import CATALOG,audit,check_local_snapshots,extract_host_reply

class ArchivedHtmlCrosswalkV489(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(CATALOG.read_text(encoding="utf-8"))
    def reject(self,mutation):
        x=deepcopy(self.data);mutation(x)
        with self.assertRaises(ValueError):audit(x)
    def test_catalog(self):
        self.assertEqual(audit(self.data)["pinned_snapshots"],9)
    def test_wrong_sina_host_article(self):
        self.reject(lambda x:x["case_replies"][1].update(primary_article_url=x["case_replies"][0]["primary_article_url"]))
    def test_wrong_sina_blog_id(self):
        self.reject(lambda x:x["case_replies"][2].update(sina_blog_id="486e105c010008la"))
    def test_raw_blob_sha_not_replaced_by_other_archive(self):
        self.reject(lambda x:x["mirrored_snapshots"][0].update(git_blob_sha=x["mirrored_snapshots"][1]["git_blob_sha"]))
    def test_cannot_turn_raw_into_2007_authenticated_bytes(self):
        self.reject(lambda x:x["case_replies"][0].update(exact_original_2007_comment_bytes=True))
    def test_no_authentication_by_div_marker(self):
        self.reject(lambda x:x["provenance_limit"].update(archived_replies_substantive_author_identity_authentication=True))
    def test_no_independent_lineage_assumption(self):
        self.reject(lambda x:x["provenance_limit"].update(archives_proven_independent_collection_lineage=True))
    def test_no_claim_of_laohu_comparison(self):
        self.reject(lambda x:x["provenance_limit"].update(laohu_full_pdf_docx_bytes_collected=True))
    def test_no_claim_kaixiang_identified_a_reply(self):
        self.reject(lambda x:x["provenance_limit"].update(kaixiang_identified_exact_reply=True))
    def test_no_new_axio_claim(self):
        self.reject(lambda x:x["provenance_limit"].update(two_different_independent_center_axioms_discovered=True))
    def test_no_market_backtest(self):
        self.reject(lambda x:x["provenance_limit"].update(market_backtest_performed=True))
    def test_no_missing_b3_gate(self):
        self.reject(lambda x:x["state"].update(B3="PROVEN_NEW_AXIOM"))
    def test_prior_march_source_must_be_credited(self):
        self.reject(lambda x:x["predecessor"].update(v438_march_reply_previously_known=False))
    def test_wrong_report_path(self):
        self.reject(lambda x:x.update(report="catalog/chanlun_archived_html_crosswalk_v489.json"))
    def test_wrong_reply_time(self):
        self.reject(lambda x:x["case_replies"][0].update(author_reply_at="2007-02-10 16:20:18"))
    @staticmethod
    def synthetic(case,marked=True,author="缠中说禅",when=None,answer=None):
        t=when or case["author_reply_at"]
        date=t[:10].replace("-","/")+t[10:]
        cls="divReplyIsHostTrue" if marked else "divReplyIsHostFalse"
        body="".join(case["author_answer_markers"]) if answer is None else answer
        return '<div class="'+cls+'" style="margin:10px"><fieldset><div><span class="author">'+author+'</span><span class="pubtime">'+date+'</span></div><div>[匿名] '+case["questioner"]+' '+case["question_at"]+' == '+body+'</div></fieldset></div>'
    def test_valid_three_local_synthetic(self):
        with tempfile.TemporaryDirectory() as d:
            for case,fn in zip(self.data["case_replies"],("feb09.html","feb12.html","mar08.html")):
                Path(d,fn).write_text(self.synthetic(case),encoding="utf-8")
            self.assertEqual(len(check_local_snapshots(self.data,d)),3)
    def test_guest_cannot_spoof_host(self):
        e=self.data["case_replies"][0]
        with self.assertRaises(ValueError):extract_host_reply(self.synthetic(e,marked=False),e["author_reply_at"],e["questioner"],e["question_at"],e["author_answer_markers"])
    def test_author_name_required(self):
        e=self.data["case_replies"][0]
        with self.assertRaises(ValueError):extract_host_reply(self.synthetic(e,author="匿名用户"),e["author_reply_at"],e["questioner"],e["question_at"],e["author_answer_markers"])
    def test_questioner_must_match_same_reply(self):
        e=self.data["case_replies"][0]
        with self.assertRaises(ValueError):extract_host_reply(self.synthetic(e),e["author_reply_at"],"温柔的股客",e["question_at"],e["author_answer_markers"])
    def test_answer_must_match_same_reply(self):
        e=self.data["case_replies"][0]
        with self.assertRaises(ValueError):extract_host_reply(self.synthetic(e,answer="原作者未发表过任何中枢"),e["author_reply_at"],e["questioner"],e["question_at"],e["author_answer_markers"])
    def test_author_reply_timestamp_required(self):
        e=self.data["case_replies"][0]
        with self.assertRaises(ValueError):extract_host_reply(self.synthetic(e,when="2007-02-09 16:22:29"),e["author_reply_at"],e["questioner"],e["question_at"],e["author_answer_markers"])
    def test_ambiguous_duplicate_host_block_rejected(self):
        e=self.data["case_replies"][0]
        with self.assertRaises(ValueError):extract_host_reply(self.synthetic(e)+self.synthetic(e),e["author_reply_at"],e["questioner"],e["question_at"],e["author_answer_markers"])

if __name__=="__main__":
    unittest.main()
