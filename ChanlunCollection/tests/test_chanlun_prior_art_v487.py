import json
import unittest
from copy import deepcopy
from tools.audit_chanlun_prior_art_v487 import SPEC,audit

class PriorArtV487(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(SPEC.read_text(encoding="utf-8"))
    def rejects(self,change):
        bad=deepcopy(self.data)
        change(bad)
        with self.assertRaises(ValueError):
            audit(bad)
    def test_baseline(self):
        self.assertEqual(audit(self.data)["previous_registration"],"4.41.0")
    def test_source_was_not_first_found_in_v486(self):
        self.rejects(lambda x:x.update(first_discovered_in_v486=True))
    def test_cannot_change_prior_version(self):
        self.rejects(lambda x:x.update(first_registered_in="4.86.0"))
    def test_cannot_change_prior_url(self):
        self.rejects(lambda x:x.update(canonical_url="https://example.org"))
    def test_cannot_claim_original_html_bytes(self):
        self.rejects(lambda x:x.update(original_historical_html_bytes_verified=True))
    def test_cannot_claim_expert_reply(self):
        self.rejects(lambda x:x.update(kaixiang_exact_reply_identified=True))
    def test_cannot_claim_market_test(self):
        self.rejects(lambda x:x.update(market_experiment_run=True))
    def test_cannot_hide_f01(self):
        self.rejects(lambda x:x["open_gates"].remove("F01"))
    def test_cannot_replace_interpretive_increment(self):
        self.rejects(lambda x:x.update(new_analytic_contribution="NEW_SOURCE_DISCOVERY"))
    def test_cannot_falsify_timestamp(self):
        self.rejects(lambda x:x.update(published_at="2007-07-20"))
if __name__=="__main__":
    unittest.main()
