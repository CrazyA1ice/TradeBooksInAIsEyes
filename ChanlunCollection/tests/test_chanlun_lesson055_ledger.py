import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lesson055_ledger.py"))
Ledger=m["Ledger"];ex=m["example"]
class LedgerTests(unittest.TestCase):
 def test_cash_share_updates(self):self.assertEqual(ex()["after_sell"]["shares"],10)
 def test_after_sale_value_can_fall(self):self.assertEqual(ex()["after_sell"]["wealth"]-ex()["after_stock_decline"]["wealth"],150)
 def test_buy_cannot_use_nonexistent_cash(self):
    with self.assertRaises(ValueError):Ledger(10).buy(5,10)
 def test_cannot_sell_unowned_shares(self):
    with self.assertRaises(ValueError):Ledger(100,1).sell(2,10)
 def test_cash_untouched_when_marking(self):
    x=Ledger(100,2);x.mark(12);self.assertEqual(x.cash,100)
 def test_mark_price_nonnegative(self):
    with self.assertRaises(ValueError):Ledger(100,2).mark(-1)
 def test_not_real_trade(self):self.assertFalse(ex()["market_orders_sent"])
if __name__=="__main__":unittest.main()
