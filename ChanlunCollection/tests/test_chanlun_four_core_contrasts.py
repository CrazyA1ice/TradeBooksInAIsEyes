"""Fail-closed tests for four core Chanlun cross-version contrast cards."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.audit_chanlun_four_core_contrasts import audit, ROOT, DATA

class FourCoreTests(unittest.TestCase):
    def test_real_sources(self):
        self.assertEqual(audit()["groups"],4)

    def test_bad_author_claim_id_and_editorial_omission(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            doc=json.loads((ROOT / DATA).read_text(encoding="utf-8"))
            for g in doc["groups"]:
                for item in g["source_claims"]:
                    n=item["lesson"]
                    p=f"knowledge/evidence/chanlun_lesson{n:03d}.json"
                    target=root/p
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes((ROOT/p).read_bytes())
            target=root/DATA
            target.parent.mkdir(parents=True,exist_ok=True)
            doc["groups"][0]["source_claims"][0]["id"]="FAKE-SOURCE-CLAIM"
            target.write_text(json.dumps(doc,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)
            doc=json.loads((ROOT/DATA).read_text(encoding="utf-8"))
            doc["groups"][1]["editorial_caution"]="完全没有历史来源与作者身份问题。"
            target.write_text(json.dumps(doc,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)

    def test_no_fake_empirical_upgrade(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            doc=json.loads((ROOT/DATA).read_text(encoding="utf-8"))
            doc["market_data"]="PROVEN"
            target=root/DATA
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(json.dumps(doc,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)

if __name__=="__main__":
    unittest.main()
