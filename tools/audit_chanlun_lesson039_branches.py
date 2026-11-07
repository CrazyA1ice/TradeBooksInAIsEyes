#!/usr/bin/env python3
"""Source-faithful gap detector for early lesson 39. No trading actions."""
def classify_upward_comparison(previous_high,current_high,divergence):
    if divergence not in (True,False,None):
        raise ValueError("divergence must be bool or None")
    if current_high == previous_high:
        return {"relation":"EQUAL","source_coverage":"SOURCE_UNSPECIFIED","order":None}
    if current_high < previous_high:
        return {"relation":"FAILS_TO_EXTEND","source_coverage":"SOURCE_UNSPECIFIED","order":None}
    return {"relation":"EXTENDS","source_coverage":"NEEDS_FURTHER_CONDITIONS" if divergence is not None else "PENDING_DIVERGENCE","order":None}
def synthetic_example():
    return {"extends":classify_upward_comparison(10,12,False),
            "equal":classify_upward_comparison(10,10,False),
            "not_new_high":classify_upward_comparison(10,9,True),
            "uses_real_market_data":False}
if __name__=="__main__":
    import json
    print(json.dumps(synthetic_example(),ensure_ascii=False,indent=2))
