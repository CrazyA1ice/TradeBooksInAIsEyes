#!/usr/bin/env python3
"""Do not backdate final daily fractal into intraday lower-level signal."""
from decimal import Decimal
def asof_signals(trading_day_close_at,asof,lower_signal_confirmed_at=None,lower_rule_id=None):
    if asof>trading_day_close_at:
        daily="READY_TO_EVALUATE_DAILY"
    elif asof==trading_day_close_at:daily="READY_TO_EVALUATE_DAILY"
    else:daily="PENDING_DAILY_BAR"
    if lower_signal_confirmed_at is not None:
        if lower_signal_confirmed_at>asof:raise ValueError("future minute signal cannot be used")
        if not lower_rule_id:raise ValueError("rule provenance required")
        minute="LOWER_LEVEL_SIGNAL_CONFIRMED"
    else:minute="NONE"
    return {"daily_fractal_status":daily,"minute_status":minute,
            "asof":asof,"daily_close_at":trading_day_close_at,
            "daily_final_fractal_claimed":False,"orders_sent":False}
def opportunity(sell_price,later_price,shares=1):
    sell=Decimal(str(sell_price));later=Decimal(str(later_price))
    if sell<0 or later<0 or shares<0:raise ValueError("invalid prices")
    return {"sold_without_loss_of_sale_price":True,"opportunity_cost":str((later-sell)*shares),
            "no_guaranteed_profit":True}
def example():
    return {"before":asof_signals(1500,1430,1425,"minute_v1"),
            "future_rejected":True,"after":asof_signals(1500,1501),
            "sell_rises":opportunity("10","12",1),"real_market_data":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),indent=2))
