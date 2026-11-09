#!/usr/bin/env python3
"""As-of completed MACD zero-axis defensive flag, not MACD or portfolio optimizer."""
from math import isfinite
def filter_zero_axis(dif,dea,completed_at,asof,period_minutes):
    if period_minutes<=0:raise ValueError("invalid timeframe")
    if completed_at is None or completed_at>asof:return {"state":"PENDING_COMPLETED_BAR","order":None}
    if not isfinite(dif) or not isfinite(dea):raise ValueError("nonfinite indicator")
    if dif<0 and dea<0:state="DEFENSIVE_RISK_FLAG"
    elif dif>0 and dea>0:state="ABOVE_ZERO"
    else:state="MIXED_UNCERTAIN"
    return {"state":state,"period_minutes":period_minutes,"order":None,"backtest":False}
def example():
    return {"negative":filter_zero_axis(-1,-.5,10,10,60),
            "mixed":filter_zero_axis(-1,.5,10,10,60),
            "future":filter_zero_axis(-1,-.5,11,10,60)}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
