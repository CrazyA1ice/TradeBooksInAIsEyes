#!/usr/bin/env python3
"""One-parameter toy EMA vs two-bar sampling; not a backtest or calibrated MACD."""
def ema(values,alpha):
    if not values or not 0<alpha<=1:raise ValueError("invalid EMA input")
    result=[values[0]]
    for x in values[1:]:result.append(alpha*x+(1-alpha)*result[-1])
    return result
def example():
    prices=[0,10,0,10]
    fast=ema(prices,.5)
    sampled=prices[1::2]
    coarse=ema(sampled,.5)
    assert fast[-1]==6.25 and coarse[-1]==10
    return {"raw_prices":prices,"raw_ema_last":fast[-1],"downsampled_closes":sampled,
            "coarse_ema_last":coarse[-1],"values_equal":fast[-1]==coarse[-1],
            "actual_macd_or_market_data_used":False}
if __name__=="__main__":
    import json
    print(json.dumps(example(),ensure_ascii=False,indent=2))
