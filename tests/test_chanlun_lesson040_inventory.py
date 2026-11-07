import runpy,unittest
from pathlib import Path
ns=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson040_inventory.py"))
Inv=ns["Inventory"];demo=ns["demo"]
class AllocationAudit(unittest.TestCase):
 def test_atomic_shift_preserves_total(self):
  x=demo()["after_shift"];self.assertEqual(x["available_total_shares"],100);self.assertEqual(x["allocations"],{"5min":50,"30min":50})
 def test_sale_decreases_real_inventory(self):
  x=demo()["after_sell"];self.assertEqual(x["available_total_shares"],50)
 def test_overallocating_other_strategy_rejected(self):
  b=Inv({"5min":40,"30min":60})
  with self.assertRaises(ValueError):b.reserve_sale("5min",41)
 def test_shift_more_than_available_rejected(self):
  b=Inv({"5min":10,"30min":90})
  with self.assertRaises(ValueError):b.shift("5min","30min",11)
 def test_invalid_negative_rejected(self):
  with self.assertRaises(ValueError):Inv({"5min":-1})
 def test_duplicate_same_level_shift_no_change(self):
  b=Inv({"5min":10});b.shift("5min","5min",5);self.assertEqual(b.total,10)
 def test_synthetic_no_real_orders(self):self.assertFalse(demo()["real_orders_sent"])
if __name__=="__main__":unittest.main()
