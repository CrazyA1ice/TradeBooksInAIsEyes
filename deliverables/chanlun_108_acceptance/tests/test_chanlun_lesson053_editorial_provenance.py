import json,runpy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
check=runpy.run_path(str(ROOT/"tools/audit_chanlun_lesson053_editorial_provenance.py"))["check"]
def source():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    v=idx["volumes"][2]
    return ROOT/v["path"],v["sha256"]
class EditorialOrigin(unittest.TestCase):
 def test_later_comment_starts_before_star_divider(self):
    x=check(*source());self.assertEqual(x["later_text_starts_pdf_page"],162);self.assertEqual(x["star_divider_pdf_page"],165)
 def test_original_date_and_later_date_distinct(self):
    x=check(*source());self.assertTrue(x["original_author_date"].startswith("2007"));self.assertTrue(x["later_discussion_date"].startswith("2009"))
 def test_sha_tamper_fails(self):
    p,_=source()
    with self.assertRaises(ValueError):check(p,"wrong")
 def test_wrong_later_date_fails(self):
    p,h=source()
    with self.assertRaises(AssertionError):check(p,h,later_date="2007-05-23 08:47:18")
 def test_not_a_figure_review(self):self.assertFalse(check(*source())["figure_contents_verified"])
if __name__=="__main__":unittest.main()
