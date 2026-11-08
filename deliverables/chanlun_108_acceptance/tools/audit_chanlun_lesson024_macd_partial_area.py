#!/usr/bin/env python3
"""Synthetic common-prefix area ambiguity. This does not compute market MACD."""
def check(prefix, future_one, future_two, reference_area):
    if not prefix or reference_area<0 or any(x<0 for x in [*prefix,*future_one,*future_two]):
        raise ValueError("Expected nonnegative contributions and nonempty prefix")
    s=sum(prefix);a=s+sum(future_one);b=s+sum(future_two)
    return {"observed":s,"estimate_2x":2*s,"final_one":a,"final_two":b,
            "reference_area":reference_area,"estimate_below_reference":2*s<reference_area,
            "actual_one_below_reference":a<reference_area,"actual_two_below_reference":b<reference_area,
            "actual_macd_calculated":False}
def example():
    x=check([1,2],[],[4,4,4],10)
    assert (x["observed"],x["estimate_2x"],x["final_one"],x["final_two"])==(3,6,3,15)
    return x
if __name__=="__main__":
    import json
    print(json.dumps(example(),ensure_ascii=False,indent=2))
