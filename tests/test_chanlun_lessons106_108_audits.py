import runpy
import unittest
from pathlib import Path

f = runpy.run_path(str(Path(__file__).resolve().parents[1] / "tools/audit_chanlun_lessons106_108.py"))
MA = f["MA_WINDOWS"]
class Audit106(unittest.TestCase):
    def test_nine_classes(self):
        for i in range(1, 10):
            won = {w: (rank < i) for rank, w in enumerate(MA, 1)}
            self.assertEqual(f["ma_rebound_class"](won, observed_clock=3, asof_clock=3)["class"], i)
    def test_prefix_not_individual_any_ma(self):
        won = {w: True for w in MA}; won[13] = False
        self.assertEqual(f["ma_rebound_class"](won, observed_clock=2, asof_clock=2)["class"], 2)
    def test_missing_not_weakest(self):
        self.assertEqual(f["ma_rebound_class"]({5: True}, observed_clock=1, asof_clock=1)["state"], "UNKNOWN")
    def test_future_or_partial(self):
        m = {w: True for w in MA}
        self.assertEqual(f["ma_rebound_class"](m, observed_clock=4, asof_clock=3)["state"], "PENDING")
        self.assertEqual(f["ma_rebound_class"](m, observed_clock=3, asof_clock=3, complete=False)["state"], "PENDING")
    def test_invalid_cross_type(self):
        with self.assertRaises(ValueError):
            f["ma_rebound_class"]({5: 1}, observed_clock=3, asof_clock=3)
    def test_sector_snapshot(self):
        rows=[{"symbol":"A","class":7,"state":"CLASSIFIED","complete":True,"observed_clock":2},
              {"symbol":"B","class":5,"state":"CLASSIFIED","complete":True,"observed_clock":2}]
        self.assertEqual(f["sector_strength"](rows,expected_members=["A","B"],asof_clock=2)["mean_class"],6)
        self.assertEqual(f["sector_strength"](rows[:1],expected_members=["A","B"],asof_clock=2)["state"],"UNKNOWN")
        rows[1]["observed_clock"]=3
        self.assertEqual(f["sector_strength"](rows,expected_members=["A","B"],asof_clock=2)["state"],"PENDING")

class Audit107(unittest.TestCase):
    def legs(self):
        return [{"direction":"up","complete":True,"end_clock":1,"low":10,"high":15},
                {"direction":"down","complete":True,"end_clock":2,"low":11,"high":14},
                {"direction":"up","complete":True,"end_clock":3,"low":12,"high":13}]
    def test_first_up_down_up_lower_high(self):
        v=f["lower_level_rebound"](self.legs(),asof_clock=3)
        self.assertEqual(v["state"],"CANDIDATE")
        self.assertFalse(v["third_high_exceeds_first_high"])
        self.assertFalse(v["trade_signal"])
    def test_no_foreknowledge(self):
        self.assertEqual(f["lower_level_rebound"](self.legs(),asof_clock=2)["state"],"PENDING")
    def test_no_overlap(self):
        x=self.legs();x[2]["low"]=16;x[2]["high"]=18
        self.assertEqual(f["lower_level_rebound"](x,asof_clock=3)["state"],"NO_THREE_LEG_OVERLAP")
    def test_no_forged_middle(self):
        x=self.legs();x[1]["direction"]="up"
        self.assertEqual(f["lower_level_rebound"](x,asof_clock=3)["state"],"INVALID_SEQUENCE")
    def test_tplus1_independent(self):
        self.assertEqual(f["tplus_one_sellable"](shares=100,acquired_day=3,sell_day=3),0)
        self.assertEqual(f["tplus_one_sellable"](shares=100,acquired_day=3,sell_day=4),100)

class Audit108(unittest.TestCase):
    def test_price_edges_and_confirmation(self):
        g=f["fractal_bottom"]
        opts={"lower":2284,"upper":2952,"price_clock":10,"asof_clock":10}
        self.assertEqual(g(**opts,price=2283)["state"],"FAILED")
        self.assertEqual(g(**opts,price=2284)["state"],"FORMING")
        self.assertEqual(g(**opts,price=3100,upper_break_confirmed=False)["state"],"FORMING")
        self.assertEqual(g(**opts,price=3100,upper_break_confirmed=True)["state"],"BREAKOUT_CONFIRMED")
    def test_future_month_is_unknown(self):
        self.assertEqual(f["fractal_bottom"](lower=2284,upper=2952,price=3100,price_clock=11,asof_clock=10,upper_break_confirmed=True)["state"],"PENDING")
    def test_two_distinct_bottom_contracts(self):
        g=f["structural_bottom"]
        a=[{"kind":"FIRST_BUY","clock":1,"complete":True},
           {"kind":"CENTER","clock":2,"complete":True},
           {"kind":"THIRD_BUY","clock":3,"complete":True}]
        self.assertEqual(g(a,asof_clock=2)["state"],"PENDING")
        self.assertEqual(g(a,asof_clock=3)["state"],"BOTTOM_COMPLETED")
        a[2]["kind"]="THIRD_SELL"
        self.assertEqual(g(a,asof_clock=3)["state"],"BOTTOM_FAILED")
    def test_missing_center_or_rule(self):
        g=f["structural_bottom"]
        self.assertEqual(g([{"kind":"FIRST_BUY","clock":1,"complete":True},{"kind":"THIRD_BUY","clock":2,"complete":True}],asof_clock=2)["state"],"INVALID_SEQUENCE")
    def test_open_event(self):
        self.assertEqual(f["structural_bottom"]([{"kind":"FIRST_BUY","clock":1,"complete":False}],asof_clock=1)["state"],"PENDING")

if __name__ == "__main__": unittest.main()
