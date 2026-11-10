"""Unit tests for the conservative Chanlun author-law card graph validator."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.audit_chanlun_author_law_cards import audit

ROOT = Path(__file__).resolve().parents[1]
CATALOG = "catalog/chanlun_author_law_cards_v1.json"

class LawCardsTests(unittest.TestCase):
    def test_real_cards(self):
        self.assertEqual(audit(ROOT)["cards"], 12)

    def test_reject_missing_evidence_and_bad_edges(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            cards = json.loads((ROOT / CATALOG).read_text(encoding="utf-8"))
            for c in cards["cards"]:
                for path in c["source_cards"]:
                    target = root / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    n = int(path.rsplit("lesson", 1)[1][:3])
                    target.write_bytes((ROOT / path).read_bytes())
            f = root / CATALOG
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(audit(root)["cards"], 12)
            cards["cards"][0]["links_to"].append("CL-LAW-999")
            f.write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "Broken law link"):
                audit(root)

    def test_reject_invented_author_claim_and_wrong_page(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            cards = json.loads((ROOT / CATALOG).read_text(encoding="utf-8"))
            for c in cards["cards"]:
                for path in c["source_cards"]:
                    target = root / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((ROOT / path).read_bytes())
            f = root / CATALOG
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(audit(root)["cards"], 12)
            anchored = next(c for c in cards["cards"] if c.get("source_assertions"))
            assertion = anchored["source_assertions"][0]
            original = assertion["claim_id"]
            assertion["claim_id"] = "INVENTED-SOURCE-ID"
            f.write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)
            assertion["claim_id"] = original
            assertion["physical_pages"] = [99999]
            f.write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)

    def test_reject_missing_claim_anchors_and_argument_trace(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            cards = json.loads((ROOT / CATALOG).read_text(encoding="utf-8"))
            f = root / CATALOG
            f.parent.mkdir(parents=True, exist_ok=True)
            original = json.loads(json.dumps(cards, ensure_ascii=False))
            for path in cards["cards"][0]["source_cards"]:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / path).read_bytes())
            cards["cards"][0]["source_assertions"] = []
            f.write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "source assertions required"):
                audit(root)
            cards = original
            del cards["cards"][0]["argument_trace"]
            f.write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
            # Does not need to materialize evidence; validation of the first card
            # must fail at the trace once actual evidence is present.
            for path in cards["cards"][0]["source_cards"]:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / path).read_bytes())
            with self.assertRaisesRegex(AssertionError, "bounded argument trace"):
                audit(root)

    def test_reject_empirical_upgrade(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            cards = json.loads((ROOT / CATALOG).read_text(encoding="utf-8"))
            cards["cards"][0]["research_status"] = "PROVEN_PROFITABLE"
            f = root / CATALOG
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(root)

if __name__ == "__main__":
    unittest.main()
