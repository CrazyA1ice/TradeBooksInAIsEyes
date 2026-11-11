import json,unittest
from copy import deepcopy
from tools.audit_chanlun_expert_history_two_methods import SPEC,REPORT,audit
class TestHistory(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=json.loads(SPEC.read_text(encoding="utf-8"));cls.r=REPORT.read_text(encoding="utf-8")
 def denied(self,mut):
  obj=deepcopy(self.s);mut(obj)
  with self.assertRaises(ValueError):audit(obj,self.r)
 def test_baseline(self):self.assertEqual(audit(self.s,self.r)["source_anchors"],22)
 def test_original_expert_post(self):self.denied(lambda x:x["provenance"].update(expert_original_public_post_verified=True))
 def test_full_recheck_not_claimed(self):self.denied(lambda x:x["provenance"].update(full_new_108_lesson_verbatim_reread=True))
 def test_sina_not_verified(self):self.denied(lambda x:x["provenance"].update(original_sina_comment_bytes_verified=True))
 def test_laohu_unverified(self):self.denied(lambda x:x["provenance"].update(laohu_version_verified=True))
 def test_lesson17_exception(self):self.denied(lambda x:x["expert_assertions"][1].update(finding="BEFORE18_NO_CENTER"))
 def test_lesson33_before35(self):self.denied(lambda x:x["expert_assertions"][0].update(finding="PRE35_ONLY_CLOCK"))
 def test_chart_not_5min_object(self):self.denied(lambda x:x["expert_assertions"][4].update(finding="FIVE_MIN_TYPE_CONTAINS_DAILY_CENTER"))
 def test_second_pair_not_proven(self):self.denied(lambda x:x["expert_assertions"][5].update(finding="SECOND_PRACTICAL_METHOD_FULLY_IDENTIFIED"))
 def test_ranking_not_verified(self):self.denied(lambda x:x["expert_assertions"][6].update(finding="RANKING_PROVED"))
 def test_no_second_axiom(self):self.denied(lambda x:x["two_way_distinctions"][0].update(is_two_independent_center_axioms=True))
 def test_comment_provenance(self):self.denied(lambda x:x["author_comments_archive"][0].update(kind="ORIGINAL_SINA_BYTES"))
 def test_wrong_author_claim(self):self.denied(lambda x:x["source_anchors"][0].update(id="FORGED"))
 def test_wrong_page(self):self.denied(lambda x:x["source_anchors"][1].update(pages=[900]))
 def test_ob38_open(self):self.denied(lambda x:x["open"].remove("OB38_OPEN"))
 def test_no_market(self):self.denied(lambda x:x["provenance"].update(market_backtest_run=True))
if __name__=="__main__":unittest.main()
