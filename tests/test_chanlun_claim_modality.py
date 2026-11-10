"""Regression tests: do not turn necessity, heuristics or strong source claims into proof."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.audit_chanlun_claim_modality import audit, ROOT, DATA, CARDS

def make_fixture():
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    doc = json.loads((ROOT / DATA).read_text(encoding="utf-8"))
    for p in (DATA, CARDS):
        dest = root / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((ROOT / p).read_bytes())
    for n in {x["lesson"] for c in doc["classes"] for x in c["source_claims"]}:
        p = f"knowledge/evidence/chanlun_lesson{n:03d}.json"
        dest = root / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((ROOT / p).read_bytes())
    return tmp, root, doc

class ModalityTests(unittest.TestCase):
    def test_live_claims(self):
        r = audit(ROOT)
        self.assertEqual(r["classifications"],16)
        self.assertEqual(r["modalities"],7)

    def test_reject_invented_source_id(self):
        tmp, root, doc = make_fixture()
        with tmp:
            doc["classes"][0]["source_claims"][0]["id"] = "FAKE-SOURCE"
            (root / DATA).write_text(json.dumps(doc,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)

    def test_reject_strengthened_necessary_to_sufficient(self):
        tmp, root, doc = make_fixture()
        with tmp:
            c = next(c for c in doc["classes"] if c["modality"] == "NECESSARY_ONLY")
            c["modality"] = "PROVEN_SUFFICIENT"
            (root / DATA).write_text(json.dumps(doc,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)

    def test_reject_editorial_role_loss(self):
        tmp, root, doc = make_fixture()
        with tmp:
            doc["editorial_exceptions"]=[]
            (root / DATA).write_text(json.dumps(doc,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)

    def test_reject_pretend_empirical_proof(self):
        tmp, root, doc = make_fixture()
        with tmp:
            doc["classes"][0]["empirical_status"]="PROVEN_PROFIT"
            (root / DATA).write_text(json.dumps(doc,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)

if __name__=="__main__":
    unittest.main()
