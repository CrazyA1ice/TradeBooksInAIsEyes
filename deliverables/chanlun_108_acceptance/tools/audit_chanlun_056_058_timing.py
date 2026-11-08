#!/usr/bin/env python3
"""Synthetic as-of trading gap and pending/confirmed classification, no broker or real data."""
from dataclasses import dataclass,field
@dataclass
class SignalTimeline:
    events:list=field(default_factory=list)
    def append(self,time,kind,confirmed=False,market_open=False,filled=False):
        if self.events and time<=self.events[-1]["t"]:raise ValueError("events must be strictly chronological")
        if kind not in ("AFTER_HOURS_NEWS","OPEN_GAP","PENDING_DIVERGENCE","CONFIRM_DIVERGENCE","INVALIDATE_DIVERGENCE","SELL"):
            raise ValueError("unknown event")
        if kind=="SELL" and (not market_open or not filled):raise ValueError("cannot assume hypothetical execution")
        if kind=="CONFIRM_DIVERGENCE" and not confirmed:raise ValueError("confirmation must be explicit")
        if kind=="PENDING_DIVERGENCE" and confirmed:raise ValueError("pending is not confirmed")
        self.events.append({"t":time,"kind":kind,"confirmed":confirmed,"filled":filled})
        return self.events[-1].copy()
def example():
    a=SignalTimeline()
    a.append(1,"AFTER_HOURS_NEWS")
    a.append(2,"OPEN_GAP",market_open=True)
    pending=a.append(3,"PENDING_DIVERGENCE")
    confirmed=a.append(4,"CONFIRM_DIVERGENCE",confirmed=True)
    assert pending["confirmed"] is False and confirmed["confirmed"] is True
    assert a.events[2]["confirmed"] is False
    return {"events":a.events,"real_orders_sent":False}
if __name__=="__main__":
    import json
    print(json.dumps(example(),indent=2))
