#!/usr/bin/env python3
"""Consecutive-trade base case and associative concatenation only; NOT full Chanlun parser."""
def flat(seq):
    if isinstance(seq,str):return (seq,)
    a,b=seq
    return flat(a)+flat(b)
def association_demo():
    A=("a",);B=("b",);C=("c",)
    left=(A+B)+C
    right=A+(B+C)
    assert left==right==("a","b","c")
    assert (A+B)!=(B+A)
    tree1=(("a","b"),"c")
    tree2=("a",("b","c"))
    assert tree1!=tree2
    assert flat(tree1)==flat(tree2)
    return {"flat_sequence":list(left),"different_grouping_trees":True,
            "unique_market_segmentation_proven":False,"actual_market_data_used":False}
def has_three_consecutive_equal(prices):
    return any(prices[i]==prices[i+1]==prices[i+2] for i in range(len(prices)-2))
def demo():
    a=association_demo()
    a.update({"base_case_present":has_three_consecutive_equal([10,10,10]),
              "base_case_absent_in_example":not has_three_consecutive_equal([10,11,12,13])})
    assert a["base_case_present"] and a["base_case_absent_in_example"]
    return a
if __name__=="__main__":
    import json
    print(json.dumps(demo(),ensure_ascii=False,indent=2))
