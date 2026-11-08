import runpy,unittest
from pathlib import Path
f=runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools/verify_chanlun_lessons106_108.py"))
def data():return f["load"]()
def validate(x):return f["validate"](*x)
class Source(unittest.TestCase):
 def test_all_three_lessons(self):self.assertEqual(validate(data())["claims"],21)
 def test_wrong_pdf_sha_rejected(self):
  x=data();x[-1][5]="incorrect"
  with self.assertRaises(AssertionError):validate(x)
 def test_108_out_of_range_rejected(self):
  x=data();x[2][2]["claims"][0]["pdf_pages"]=[200]
  with self.assertRaises(AssertionError):validate(x)
 def test_date_authorship_rejected(self):
  x=data();x[2][0]["source"]["original_date"]="2008-08-08"
  with self.assertRaises(AssertionError):validate(x)
 def test_no_forged_visual_review(self):
  x=data();x[1]["visual"]["actually_visually_reviewed_pages"]=[395]
  with self.assertRaises(AssertionError):validate(x)
 def test_no_forged_numeric_verification(self):
  x=data();x[2][2]["quality"]["fine_chart_numeric_verified"]=True
  with self.assertRaises(AssertionError):validate(x)
 def test_no_hypothesis_promoted(self):
  x=data();next(c for c in x[2][1]["claims"] if c["kind"]=="HYPOTHESIS")["test_status"]="proven"
  with self.assertRaises(AssertionError):validate(x)
 def test_later_dates_not_author(self):
  x=data();x[1]["source_role_flags"]=[v for v in x[1]["source_role_flags"] if v["kind"]!="DIFFERENT_DATED_POST"]
  with self.assertRaises(AssertionError):validate(x)
 def test_broken_graph_edge_rejected(self):
  x=data();x[5]["edges"][0]["to"]="UNLISTED"
  with self.assertRaises(AssertionError):validate(x)
 def test_no_backtest_overclaim(self):
  x=data();x[2][0]["real_market_backtest"]="completed"
  with self.assertRaises(AssertionError):validate(x)
 def test_all_seven_lenses(self):
  x=data();x[3][2]=x[3][2].replace("第七重","第八重")
  with self.assertRaises(AssertionError):validate(x)
if __name__=="__main__":unittest.main()
