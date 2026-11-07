import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_056_058_timing.py"))
TL=m["SignalTimeline"];example=m["example"]
class Online(unittest.TestCase):
 def test_pending_not_confirmed(self):self.assertFalse(example()["events"][2]["confirmed"])
 def test_future_confirmation_not_backfilled(self):
    x=example()["events"];self.assertFalse(x[2]["confirmed"]);self.assertTrue(x[3]["confirmed"])
 def test_no_fake_closed_market_sale(self):
    with self.assertRaises(ValueError):TL().append(1,"SELL",market_open=False,filled=True)
 def test_no_fake_filled_sale(self):
    with self.assertRaises(ValueError):TL().append(1,"SELL",market_open=True,filled=False)
 def test_pending_cannot_be_confirmed(self):
    with self.assertRaises(ValueError):TL().append(1,"PENDING_DIVERGENCE",confirmed=True)
 def test_confirmation_explicit(self):
    with self.assertRaises(ValueError):TL().append(1,"CONFIRM_DIVERGENCE",confirmed=False)
 def test_no_time_rewind(self):
    s=TL();s.append(2,"OPEN_GAP")
    with self.assertRaises(ValueError):s.append(1,"PENDING_DIVERGENCE")
 def test_not_real_market_data(self):self.assertFalse(example()["real_orders_sent"])
if __name__=="__main__":unittest.main()
