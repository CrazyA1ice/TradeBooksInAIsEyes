#!/usr/bin/env python3
"""Audit the *early lesson-15 literal definition*, not later revisions."""
def classify_early(high_prev,high_now,low_prev,low_now):
    dh=high_now-high_prev
    dl=low_now-low_prev
    if dh==0 or dl==0:return "underdetermined_equal_extremum"
    if dh>0 and dl>0:return "up"
    if dh<0 and dl<0:return "down"
    return "consolidation"

def local_high_confirmation(prices,index,right=1,left=1):
    if index-left<0 or index+right>=len(prices):
        return None
    val=prices[index]
    if val>max(prices[index-left:index]) and val>max(prices[index+1:index+right+1]):
        return {"occurrence_index":index,"earliest_confirmation_index":index+right}
    return None

def example():
    return {"states":[
         classify_early(10,11,5,6),
         classify_early(10,9,5,4),
         classify_early(10,11,5,4),
         classify_early(10,9,5,6),
         classify_early(10,10,5,6)],
         "pivot":local_high_confirmation([10,12,9,14,8],3),
         "uses_market_history":False}
if __name__=="__main__":
    import json
    print(json.dumps(example(),ensure_ascii=False,indent=2))
