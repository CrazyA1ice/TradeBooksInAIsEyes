#!/usr/bin/env python3
"""Two synthetic mutually exclusive one-shot investments; NOT optimal-trading proof."""
def evaluate(invested,net_return_rate,occupied_days,horizon_days,other_opportunities=0):
    if not invested>0 or not 0<=occupied_days<=horizon_days or occupied_days==0:raise ValueError("invalid investment schedule")
    if other_opportunities!=0:raise ValueError("demo only supports one-shot non-repeatable opportunity")
    return {"capital":invested,"occupied_days":occupied_days,"net_return_rate":net_return_rate,
            "rate_per_occupied_day":net_return_rate/occupied_days,
            "end_wealth":invested*(1+net_return_rate),
            "assume_no_followup_opportunity":True,"real_market_data_used":False}
def example():
    a=evaluate(100,.20,10,10)
    b=evaluate(100,.05,1,10)
    assert b["rate_per_occupied_day"]>a["rate_per_occupied_day"]
    assert b["end_wealth"]<a["end_wealth"]
    return {"A":a,"B":b,"different_objectives_rank_differently":True}
if __name__=="__main__":
    import json
    print(json.dumps(example(),ensure_ascii=False,indent=2))
