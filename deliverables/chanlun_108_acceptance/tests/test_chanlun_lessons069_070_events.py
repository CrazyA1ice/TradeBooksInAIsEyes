import runpy,unittest
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/audit_chanlun_lessons069_070_events.py"))
Log=m["EvidenceLog"];Center=m["CenterBranch"];ex=m["example"]
class Events(unittest.TestCase):
 def test_revision_keeps_earlier_event(self):
    x=ex()["immutable_history"];self.assertEqual(x[0]["action"],"OPEN");self.assertEqual(x[1]["action"],"REVISE")
 def test_revision_separates_states(self):
    x=ex()["current_states"];self.assertEqual(x["monthly-fractal-1"],"REVISED");self.assertEqual(x["monthly-fractal-2"],"CONFIRMED")
 def test_final_cannot_be_overwritten(self):
    l=Log();l.record(1,"x","OPEN");l.record(2,"x","CONFIRM")
    with self.assertRaises(ValueError):l.record(3,"x","REVISE",new_id="y")
 def test_no_time_rewind(self):
    l=Log();l.record(5,"x","OPEN")
    with self.assertRaises(ValueError):l.record(4,"x","CONFIRM")
 def test_cannot_revive_invalidated(self):
    l=Log();l.record(1,"x","OPEN");l.record(2,"x","INVALIDATE")
    with self.assertRaises(ValueError):l.record(3,"x","CONFIRM")
 def test_branch_pending_until_event(self):self.assertEqual(Center().state,"PENDING")
 def test_branch_actual_event(self):
    self.assertEqual(Center().observe("THIRD_SELL_CONFIRMED"),"THIRD_SELL_DOWN")
 def test_branch_cannot_double_confirm(self):
    b=Center();b.observe("THIRD_BUY_CONFIRMED")
    with self.assertRaises(ValueError):b.observe("THIRD_SELL_CONFIRMED")
 def test_failed_revision_is_atomic(self):
    l=Log();l.record(1,"x","OPEN")
    with self.assertRaises(ValueError):l.record(2,"x","REVISE")
    self.assertEqual(l.states["x"],"PENDING")
    self.assertEqual(len(l.events),1)
 def test_not_full_market_parser(self):self.assertFalse(ex()["complete_market_parser"])
if __name__=="__main__":unittest.main()
