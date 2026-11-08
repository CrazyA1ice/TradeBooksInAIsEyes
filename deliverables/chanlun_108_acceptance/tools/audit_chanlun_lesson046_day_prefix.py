#!/usr/bin/env python3
"""Synthetic intraday triple-overlap window detection; NOT a full Chanlun center parser."""
def overlap_windows(bars):
    if len(bars)>8:raise ValueError("single day maximum 8 bars in this simplified model")
    if any(len(bar)!=2 or bar[0]>bar[1] for bar in bars):raise ValueError("invalid low/high pair")
    out=[]
    for i in range(len(bars)-2):
        lo=max(bar[0] for bar in bars[i:i+3])
        hi=min(bar[1] for bar in bars[i:i+3])
        if lo<=hi:out.append({"start_index":i,"overlap":[lo,hi]})
    return out
def inspect(bars):
    overlap=overlap_windows(bars)
    return {"status":"FULL_DAY_OBSERVED" if len(bars)==8 else "PENDING_FULL_DAY",
            "confirmed_three_bar_windows":overlap,"complete_day_any_overlap":bool(overlap) if len(bars)==8 else None,
            "full_center_classification_implemented":False,"real_market_data_used":False}
def example():
    shared=[[0,1],[2,3],[4,5]]
    a=inspect(shared+[[4,5]]*5)
    b=inspect(shared+[[6,7],[8,9],[10,11],[12,13],[14,15]])
    assert inspect(shared)["complete_day_any_overlap"] is None
    assert a["complete_day_any_overlap"] and not b["complete_day_any_overlap"]
    return {"prefix":inspect(shared),"future_a":a,"future_b":b}
if __name__=="__main__":
    import json
    print(json.dumps(example(),ensure_ascii=False,indent=2))
