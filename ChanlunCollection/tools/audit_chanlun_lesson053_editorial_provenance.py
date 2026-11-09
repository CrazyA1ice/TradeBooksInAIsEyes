#!/usr/bin/env python3
"""Check literal later editorial insert on lesson 53 original PDF page 162."""
import hashlib,json,re
from pathlib import Path
def check(pdf_file,expected_sha,original_date="2007-05-23 08:47:18",later_date="2009-01-05 12:00:58"):
    import fitz
    if hashlib.sha256(pdf_file.read_bytes()).hexdigest()!=expected_sha:raise ValueError("PDF source fingerprint mismatch")
    with fitz.open(pdf_file) as pdf:
        original=pdf[160].get_text("text",sort=True)
        merged=pdf[161].get_text("text",sort=True)
        after=pdf[164].get_text("text",sort=True)
    assert original_date in original
    anchor=merged.find("第三类买卖点再分辨（思考贴9）")
    stamp=merged.find(later_date)
    assert anchor>0 and stamp>anchor
    assert "********************" in after
    return {"original_author_date":original_date,"later_text_starts_pdf_page":162,
            "later_discussion_date":later_date,"star_divider_pdf_page":165,
            "asterisk_is_not_true_author_boundary":True,"figure_contents_verified":False}
def main():
    root=Path(__file__).resolve().parents[1]
    idx=json.loads((root/"catalog/chanlun_lesson_index.json").read_text(encoding="utf-8"))
    v=idx["volumes"][2]
    print(json.dumps(check(root/v["path"],v["sha256"]),ensure_ascii=False))
if __name__=="__main__":main()
