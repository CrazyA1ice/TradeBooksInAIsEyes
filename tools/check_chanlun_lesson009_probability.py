#!/usr/bin/env python3
"""Lesson 9 conceptual probability counterexample, NOT a market backtest."""
from fractions import Fraction as F

def demonstrate():
    # Half of all synthetic observations are failures, half successes.
    base_fail = F(1, 2)
    pass_given_fail = [F(3,10), F(7,15), F(3,10)]
    pass_given_success = [F(7,10)]*3
    # Conditional independence of screening signals given failure/success.
    indiv = [(base_fail*a)/(base_fail*a + (1-base_fail)*b)
             for a,b in zip(pass_given_fail,pass_given_success)]
    assert indiv == [F(3,10),F(2,5),F(3,10)]
    def prod(xs):
        r=F(1,1)
        for x in xs:r*=x
        return r
    joint_fail = base_fail*prod(pass_given_fail)
    joint_success=(1-base_fail)*prod(pass_given_success)
    conditional_failure=joint_fail/(joint_fail+joint_success)
    naive=prod(indiv)
    assert naive == F(9,250) # 3.6%
    assert conditional_failure == F(6,55) # 10.909...%
    assert conditional_failure != naive
    return {"single_failure_rates":[float(x) for x in indiv],
            "naive_product":float(naive),
            "joint_screen_failure_rate":float(conditional_failure),
            "exact_joint_fraction":str(conditional_failure),
            "has_real_market_data":False,
            "interpretation":"Proof by counterexample: individual screened failure rates do not multiply."}
if __name__=="__main__":
    import json
    print(json.dumps(demonstrate(),ensure_ascii=False,indent=2))
