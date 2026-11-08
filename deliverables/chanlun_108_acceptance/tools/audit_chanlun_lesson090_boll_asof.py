#!/usr/bin/env python3
"""Synthetic complete-bar population BOLL; auxiliary width squeeze is NOT center confirmation."""
from math import sqrt,isfinite
def boll(prices,bar_times,asof,window=3,k=2.0):
    if len(prices)!=len(bar_times) or len(set(bar_times))!=len(bar_times) or any(bar_times[i]>=bar_times[i+1] for i in range(len(bar_times)-1)):
        raise ValueError("invalid time series")
    if window<2 or k<=0 or not isfinite(k):raise ValueError("invalid parameters")
    if any(not isfinite(float(x)) or float(x)<=0 for x in prices):raise ValueError("nonpositive or nonfinite price")
    completed=[float(v) for v,t in zip(prices,bar_times) if t<=asof]
    if len(completed)<window:return {"state":"INSUFFICIENT_WINDOW","asof":asof}
    v=completed[-window:];mean=sum(v)/window;std=sqrt(sum((x-mean)**2 for x in v)/window)
    return {"state":"AVAILABLE","mean":mean,"upper":mean+k*std,"lower":mean-k*std,
            "width":2*k*std/mean,"asof":asof,"uses_future":False}
def classify_squeeze(previous,current,threshold=0.8,geometry_confirmed=False):
    if not 0<threshold<1:raise ValueError("threshold")
    if previous["state"]!="AVAILABLE" or current["state"]!="AVAILABLE":
        return {"auxiliary":"PENDING","geometry":"CENTER_NOT_CONFIRMED"}
    squeeze=current["width"] < threshold*previous["width"]
    return {"auxiliary":"AUXILIARY_SQUEEZE" if squeeze else "NO_SQUEEZE",
            "geometry":"CENTER_BREAK_CONFIRMED" if geometry_confirmed else "CENTER_NOT_CONFIRMED"}
def example():
    vals=[100,110,90,99,101,100];ts=[1,2,3,4,5,6]
    pre=boll(vals,ts,3);after=boll(vals,ts,6)
    return {"before":pre,"after":after,"squeeze_without_center":classify_squeeze(pre,after),
            "real_market_data":False,"orders_sent":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
