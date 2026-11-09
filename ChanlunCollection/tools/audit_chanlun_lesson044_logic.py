#!/usr/bin/env python3
"""Pure propositional-logic audit of necessary-vs-sufficient: no market data."""
from itertools import product
def implication(a,b):return not a or b
def evaluate(b,t,r):
    return {"B":b,"T":t,"R":r,"necessary":implication(b and r,t),
            "incorrect_sufficiency":implication(b and t,r)}
def truth_table():
    return [evaluate(*x) for x in product((False,True),repeat=3)]
def counterexample():
    row=evaluate(True,True,False)
    assert row["necessary"] is True and row["incorrect_sufficiency"] is False
    return {"row":row,"real_market_path_constructed":False}
if __name__=="__main__":
    import json
    print(json.dumps({"counterexample":counterexample(),"rows":truth_table()},ensure_ascii=False,indent=2))
