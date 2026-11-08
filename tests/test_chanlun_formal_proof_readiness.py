"""Negative-proof fixtures: text citations are not complete mathematical certificates."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "tools/verify_chanlun_formal_proof_readiness.py"
spec = importlib.util.spec_from_file_location("proof_ready", PROGRAM)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class ChanlunProofReadiness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = tool.load_json(tool.PACKET)
        cls.ledger = tool.load_json(tool.LEDGER)
        cls.registry = tool.load_json(tool.REGISTRY)
        cls.inventory = tool.load_json(tool.INVENTORY)
        cls.pins = tool.original_pins()

    def gate(self, packet=None, ledger=None, registry=None, inventory=None, pins=None):
        return tool.verify(
            self.packet if packet is None else packet,
            self.ledger if ledger is None else ledger,
            self.registry if registry is None else registry,
            self.inventory if inventory is None else inventory,
            self.pins if pins is None else pins)

    def test_all_five_are_blocked_with_exact_missing_derivation_slots(self):
        output = self.gate()
        self.assertEqual(output["status"], "BLOCKED_NOT_CERTIFIED")
        self.assertFalse(output["registered_complete_R_g"])
        self.assertEqual(output["confirmed_formal_theorems"], 0)
        self.assertEqual(tuple(x["id"] for x in output["goals"]), tool.GOALS)
        self.assertEqual(sum(x["open_slot_count"] for x in output["goals"]), 17)
        self.assertTrue(all(x["proof_status"] == "BLOCKED_NOT_CERTIFIED" for x in output["goals"]))
        self.assertFalse(output["uses_market_data"])
        self.assertFalse(output["original_PDF_image_inspection"])

    def test_source_pdf_native_hash_corruption_fails(self):
        p = copy.deepcopy(self.packet)
        p["goals"][0]["author_claim_anchors"][0]["native_text_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            self.gate(packet=p)

    def test_editorial_is_never_author_proof(self):
        p = copy.deepcopy(self.packet)
        target = p["goals"][3]["author_claim_anchors"][0]
        target["claim_id"] = "CL99-EDITORIAL-5"
        with self.assertRaisesRegex(ValueError, "EDITORIAL/AI cannot prove"):
            self.gate(packet=p)

    def test_proof_slot_not_satisfied_by_self_declaration(self):
        for status in ("SATISFIED", "VERIFIED", "PROVEN"):
            with self.subTest(status=status):
                p = copy.deepcopy(self.packet)
                p["goals"][1]["proof_slots"][1]["status"] = status
                with self.assertRaisesRegex(ValueError, "may not be self-declared"):
                    self.gate(packet=p)

    def test_proof_slip_cannot_remove_equal_price_or_future_overlap(self):
        for goal, idx in [(1, 2), (3, 2), (4, 0)]:
            with self.subTest(goal=goal):
                p = copy.deepcopy(self.packet)
                p["goals"][goal]["proof_slots"].pop(idx)
                with self.assertRaisesRegex(ValueError, "incomplete or shuffled"):
                    self.gate(packet=p)

    def test_unknown_rule_version_cannot_make_theorem_certified(self):
        p = copy.deepcopy(self.packet)
        p["complete_frozen_rule_ref"] = "pen_081_later_dated_post"
        with self.assertRaisesRegex(ValueError, "Cannot assert a registered complete rule"):
            self.gate(packet=p)

    def test_new_registry_family_requires_fresh_review_not_auto_promotion(self):
        registry = copy.deepcopy(self.registry)
        registry["entries"].append({
            "id": "EXAMPLE_UNREVIEWED",
            "family": "same_level_decomposition_complete_spec",
            "role": "author_original",
            "lesson": 38,
        })
        with self.assertRaisesRegex(ValueError, "requires separate proof review"):
            self.gate(registry=registry)

    def test_wrong_source_page_and_claim_cannot_cross_38_to_99(self):
        p = copy.deepcopy(self.packet)
        p["goals"][0]["author_claim_anchors"][0]["page"] = 202
        with self.assertRaisesRegex(ValueError, "not in claim"):
            self.gate(packet=p)

    def test_report_and_readme_link_only_provisional_certificate(self):
        guide = ROOT / "deliverables/chanlun_108_acceptance/04_AI_GUIDE"
        page = guide / "20_同级别唯一性证明资格与来源证据闸门.md"
        text = page.read_text(encoding="utf-8")
        for word in ("OB38-EXIST", "OB38-UNIQUE", "OB38-ASOF",
                     "OB99-EXIST", "OB99-LOCATION",
                     "17", "BLOCKED_NOT_CERTIFIED", "TEXT_FIRST_NO_IMAGE",
                     "NOT_RUN", "第38课", "第99课", "不是缠论反例"):
            self.assertIn(word, text)
        for index in (guide / "README.md", ROOT / "deliverables/chanlun_108_acceptance/README.md"):
            self.assertIn(page.name, index.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
