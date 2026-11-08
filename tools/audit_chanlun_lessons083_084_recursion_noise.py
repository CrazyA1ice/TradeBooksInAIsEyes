#!/usr/bin/env python3
"""Recursive shape initialization varies even when higher-order recursion f2 is fixed."""
def threshold_feature(value,boundary):
    return 1 if value>boundary else 0
def near_boundary_sensitivity(x,eps,boundary):
    if eps<0:raise ValueError("negative perturbation")
    return {"before":threshold_feature(x,boundary),"after":threshold_feature(x+eps,boundary),
            "relative_segment_robustness_proven":False}
def high_level(start,f2,levels):
    if not isinstance(start,int) or levels<0:raise ValueError("bad recursion input")
    current=start
    path=[current]
    for _ in range(levels):
        current=f2(current)
        if not isinstance(current,int):raise ValueError("f2 output not integer")
        path.append(current)
    return path
def example():
    f2=lambda x:x+1
    a=high_level(1,f2,2)
    b=high_level(2,f2,2)
    sensitivity=near_boundary_sensitivity(9.99,.02,10)
    return {"f1_a":1,"f1_b":2,"same_f2_a":a,"same_f2_b":b,
            "noise":sensitivity,"real_market_data":False,"full_segment_parser":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
