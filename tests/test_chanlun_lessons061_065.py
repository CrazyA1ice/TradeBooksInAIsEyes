import json,runpy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
validate=runpy.run_path(str(ROOT/"tools/verify_chanlun_lessons061_065.py"))["validate"]
def fixtures():
    idx=json.loads((ROOT/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    s=json.loads((ROOT/"catalog/chanlun_lessons061_065_source_layers.json").read_text(encoding="utf-8"))
    e=[json.loads((ROOT/f"knowledge/evidence/chanlun_lesson{n:03d}.json").read_text(encoding="utf-8")) for n in range(61,66)]
    m=[(ROOT/f"analyses/books/chanlun/chapters/lesson_{n:03d}.md").read_text(encoding="utf-8") for n in range(61,66)]
    summary=(ROOT/"analyses/books/chanlun/volumes/LESSONS_061_065_SYNTHESIS.md").read_text(encoding="utf-8")
    g=json.loads((ROOT/"knowledge/claims/chanlun_early_core_dependencies.json").read_text(encoding="utf-8"))
    hashes={v["volume"]:v["sha256"] for v in idx["volumes"][:3]}
    return [idx,s,e,m,summary,g,hashes]
class Audit(unittest.TestCase):
 def test_valid(self):self.assertEqual(validate(*fixtures())["claims"],35)
 def test_wrong_pdf_fingerprint(self):
    z=fixtures();z[-1][3]="bad"
    with self.assertRaises(AssertionError):validate(*z)
 def test_2010_date_must_be_distinct(self):
    z=fixtures();z[1]["provenance_flags"][0]["kind"]="pretend_single_2007_post"
    with self.assertRaises(AssertionError):validate(*z)
 def test_new_pen_note_must_be_recorded(self):
    z=fixtures();z[1]["provenance_flags"][1]["kind"]="normal_old_version"
    with self.assertRaises(AssertionError):validate(*z)
 def test_wrong_figure_claim(self):
    z=fixtures();z[2][0]["quality"]["numeric_figures_verified"]=True
    with self.assertRaises(AssertionError):validate(*z)
 def test_wrong_visual_review_page(self):
    z=fixtures();z[1]["visual_preview"]["pages"][1]=291
    with self.assertRaises(AssertionError):validate(*z)
 def test_claim_page_outside_chapter(self):
    z=fixtures();z[2][3]["claims"][0]["pdf_pages"]=[378]
    with self.assertRaises(AssertionError):validate(*z)
 def test_hypothesis_unproven(self):
    z=fixtures();next(k for k in z[2][4]["claims"] if k["kind"]=="HYPOTHESIS")["test_status"]="verified"
    with self.assertRaises(AssertionError):validate(*z)
 def test_missing_seventh_lens(self):
    z=fixtures();z[3][2]=z[3][2].replace("第七重","备注")
    with self.assertRaises(AssertionError):validate(*z)
 def test_missing_revised_pen_node(self):
    z=fixtures();z[5]["nodes"]=[n for n in z[5]["nodes"] if n["id"]!="L62-REVISED-PEN"]
    with self.assertRaises(AssertionError):validate(*z)
 def test_missing_link_target(self):
    z=fixtures();z[5]["edges"][0]["to"]="DOES_NOT_EXIST"
    with self.assertRaises(AssertionError):validate(*z)
if __name__=="__main__":unittest.main()
