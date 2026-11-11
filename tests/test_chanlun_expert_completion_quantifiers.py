"""Local logic models and negative provenance gates; not trading validation."""
import unittest,json
from copy import deepcopy
from tools.audit_chanlun_expert_completion_quantifiers import SPEC,REPORT,audit,example_completed,toy_policy

class TestQuantifiers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(SPEC.read_text(encoding="utf-8"))
        cls.report=REPORT.read_text(encoding="utf-8")
    def deny(self,mutate):
        x=deepcopy(self.data);mutate(x)
        with self.assertRaises(ValueError):audit(x,self.report)
    def test_sources(self):
        self.assertEqual(audit(self.data,self.report)["sources"],7)
    def test_any_finite_bound_can_be_exceeded(self):
        for n in (1,10,100,1000):
            self.assertEqual(len(example_completed(n)),n+1)
            self.assertTrue(example_completed(n).endswith("E"))
    def test_shared_prefix_distinct_end_times(self):
        self.assertEqual(example_completed(3)[:3],example_completed(6)[:3])
        self.assertNotEqual(len(example_completed(3)),len(example_completed(6)))
    def test_unique_each_policy_nonidentical(self):
        self.assertNotEqual(toy_policy("ABC","R1"),toy_policy("ABC","R2"))
    def test_original_expert_not_forged(self):
        self.deny(lambda x:x["provenance"].update(expert_verbatim_recovered=True))
    def test_expert_link_not_forged(self):
        self.deny(lambda x:x["provenance"].update(expert_original_post_recovered=True))
    def test_infinite_literal_not_assumed(self):
        self.deny(lambda x:x["claims"][2].update(strength="AUTHOR_PROVED_INFINITE_NEVER_ENDS"))
    def test_fixed_rule_theorem_not_misclaimed(self):
        self.deny(lambda x:x["claims"][3].update(strength="FORMALLY_PROVED"))
    def test_market_not_run(self):
        self.deny(lambda x:x["provenance"].update(market_backtest_performed=True))
    def test_wrong_source_rejected(self):
        self.deny(lambda x:x["anchors"][0].update(id="INVENTED"))
    def test_wrong_page_rejected(self):
        self.deny(lambda x:x["anchors"][1].update(pages=[999]))
    def test_open_ob38_not_erased(self):
        self.deny(lambda x:x["limits"].remove("OB38_OPEN"))
if __name__=="__main__":unittest.main()
