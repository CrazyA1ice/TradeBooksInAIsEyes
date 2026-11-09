#!/usr/bin/env python3
"""Synthetic economic exposure, breadth qualifier and no-fake-fill market clock."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Holding:
    shares:int
    price:float
    def __post_init__(self):
        if self.shares<0 or self.price<0:raise ValueError("invalid holding")
    def mark(self,new_price):
        if new_price<0:raise ValueError("negative price")
        return self.shares*new_price
def policy_exposure(affected_sectors,total_sectors):
    if total_sectors<=0 or affected_sectors<0 or affected_sectors>total_sectors:
        return "UNKNOWN"
    if affected_sectors>=3 and affected_sectors/total_sectors>=0.60:
        return "BROAD_MARKET_EXPOSURE"
    if affected_sectors==1 and total_sectors>=3:return "LOCAL_SECTOR_EXPOSURE"
    return "UNKNOWN"
def gap_exit(signal_time,open_time,fill_time=None,fill_confirmed=False):
    if signal_time>=open_time and fill_time is not None and fill_time<open_time:raise ValueError("bad clock")
    if fill_time is None or not fill_confirmed:return "NOT_EXECUTABLE_OR_UNFILLED"
    if fill_time<open_time:return "NOT_EXECUTABLE_OR_UNFILLED"
    return "FILLED_AT_MARKET_TIME"
def example():
    holding=Holding(shares=20,price=10)
    return {"start_wealth":holding.mark(10),"later_wealth":holding.mark(2),
            "loss":holding.mark(10)-holding.mark(2),
            "broad":policy_exposure(4,5),"local":policy_exposure(1,5),
            "gap":gap_exit(1,4),"orders_sent":False}
if __name__=="__main__":
 import json
 print(json.dumps(example(),ensure_ascii=False,indent=2))
