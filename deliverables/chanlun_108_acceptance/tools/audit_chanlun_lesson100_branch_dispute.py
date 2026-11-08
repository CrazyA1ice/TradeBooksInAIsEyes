#!/usr/bin/env python3
"""Preserve author classification vs later editor counterclaim. No fabricated adjudication."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Claim:
    role:str
    published_at:str
    pdf_page:int
    text_label:str
    def __post_init__(self):
        if self.role not in ("AUTHOR_ORIGINAL","EDITOR_LATER"):
            raise ValueError("role required")
        if self.pdf_page not in (224,225):raise ValueError("outside sourced pages")
def adjudicate(author,editor,independent_market_check=False):
    if author.role!="AUTHOR_ORIGINAL" or editor.role!="EDITOR_LATER":
        raise ValueError("source roles mismatch")
    if author.published_at>editor.published_at:raise ValueError("later editor chronology inverted")
    if author.text_label not in ("THIRD_SELL_YES_OR_NO","BIFURCATION"):
        raise ValueError("unknown original claim")
    if editor.text_label!="OUTSIDE_TWO_BRANCHES":
        return "NO_RECORDED_COUNTERCLAIM"
    if not independent_market_check:return "REVIEW_REQUIRED_NO_INDEPENDENT_DATA"
    return "INDEPENDENT_REVIEW_REQUIRED"  # independent check flag alone has no result/provenance
def example():
    a=Claim("AUTHOR_ORIGINAL","2008-02-25 16:32:23",224,"THIRD_SELL_YES_OR_NO")
    e=Claim("EDITOR_LATER","2008-02-26 15:14:39",225,"OUTSIDE_TWO_BRANCHES")
    return {"author":a.__dict__,"editor":e.__dict__,
            "dispute":adjudicate(a,e),"actual_market_backtest":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),ensure_ascii=False,indent=2))
