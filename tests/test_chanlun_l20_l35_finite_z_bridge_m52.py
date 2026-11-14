"""Local M52 theorem gates, not market data or completed movements."""
import importlib.util
import json
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/"tools/audit_chanlun_l20_l35_finite_z_bridge_m52.py"
spec=importlib.util.spec_from_file_location("m52",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
D=json.loads(m.CATALOG.read_text(encoding="utf-8"))
C={x["id"]:x for x in D["cases"]}

class M52FiniteIntervalTests(unittest.TestCase):
    def test_catalog(self):
        self.assertEqual(m.audit(D)["cases"],7)
    def test_connected_envelope_overlap(self):
        r=m.check(C["qualified_overlap"])
        self.assertEqual(r["left_hull"],[9,14])
        self.assertEqual(r["right_hull"],[13,19])
        self.assertEqual(r["overlap"],[13,14])
        self.assertTrue(r["has_pair"])
    def test_never_certify_high_center(self):
        r=m.check(C["qualified_overlap"])
        self.assertFalse(r["higher_center_authenticated"])
        self.assertFalse(r["completed_higher_movements_authenticated"])
        self.assertFalse(r["market_data"])
    def test_invalid_extension_gate(self):
        r=m.check(C["invalid_extension"])
        self.assertEqual(r,{"status":"INVALID_EXTENSION_MEMBER"})
        a=C["invalid_extension"]["left"]["z"]
        b=C["invalid_extension"]["right"]["z"]
        self.assertEqual(m.overlap(m.hull(a),m.hull(b)),[14,18])
        self.assertFalse(any(m.overlap([x["lo"],x["hi"]],[y["lo"],y["hi"]]) is not None for x in a for y in b))
    def test_future_is_not_visible(self):
        self.assertEqual(m.check(C["future_hidden"]),{"status":"PENDING_ASOF"})
    def test_policy_mismatch(self):
        self.assertEqual(m.check(C["rule_mismatch"]),{"status":"RULE_MISMATCH"})
    def test_disjoint(self):
        r=m.check(C["disjoint"])
        self.assertIsNone(r["overlap"])
        self.assertFalse(r["has_pair"])
    def test_point_touch_closed(self):
        self.assertEqual(m.check(C["point_touch"])["overlap"],[13,13])
    def test_fake_seed_rejected(self):
        self.assertEqual(m.check(C["fake_core"]),{"status":"BAD_SEED_CORE"})
    def test_closed_interval_single_point(self):
        self.assertEqual(m.overlap([1,2],[2,3]),[2,2])
        self.assertIsNone(m.overlap([1,2],[3,4]))
if __name__=="__main__":unittest.main()
