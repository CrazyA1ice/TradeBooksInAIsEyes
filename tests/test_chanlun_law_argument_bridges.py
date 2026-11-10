"""Regression tests for law-card cross-argument bridge integrity."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.audit_chanlun_law_argument_bridges import audit, BRIDGES, CARDS

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    for p in [BRIDGES, CARDS]:
        dst = root / p
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes((ROOT / p).read_bytes())
    cards = json.loads((root / CARDS).read_text(encoding="utf-8"))["cards"]
    files = {p for c in cards for p in c["source_cards"]}
    for p in files:
        dst = root / p
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes((ROOT / p).read_bytes())
    return tmp, root


class BridgeAuditTests(unittest.TestCase):
    def test_repo(self):
        report = audit(ROOT)
        self.assertEqual(report["bridges"], 13)
        self.assertEqual(report["reachable_cards"], 12)

    def test_reject_unsupported_implication_label(self):
        tmp, root = fixture()
        with tmp:
            doc = json.loads((root / BRIDGES).read_text(encoding="utf-8"))
            doc["edges"][0]["identity"] = "AUTHOR_PROVEN_THEOREM"
            (root / BRIDGES).write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)

    def test_reject_invented_source_and_wrong_pages(self):
        tmp, root = fixture()
        with tmp:
            doc = json.loads((root / BRIDGES).read_text(encoding="utf-8"))
            old = doc["edges"][0]["evidence"][0]["claim_id"]
            doc["edges"][0]["evidence"][0]["claim_id"] = "FABRICATED"
            (root / BRIDGES).write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)
            doc["edges"][0]["evidence"][0]["claim_id"] = old
            doc["edges"][0]["evidence"][0]["physical_pages"] = [99999]
            (root / BRIDGES).write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)

    def test_reject_missing_non_implication_and_invented_edge(self):
        tmp, root = fixture()
        with tmp:
            doc = json.loads((root / BRIDGES).read_text(encoding="utf-8"))
            doc["edges"][0]["not_implied"] = ""
            (root / BRIDGES).write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)
            doc["edges"][0]["not_implied"] = "从先验偏好不能自动推出可靠的划分结论。"
            doc["edges"][0]["to"] = "CL-LAW-999"
            (root / BRIDGES).write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)


if __name__ == "__main__":
    unittest.main()
