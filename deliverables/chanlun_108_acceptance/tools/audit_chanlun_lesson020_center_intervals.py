#!/usr/bin/env python3
"""Pure-synthetic boundary audit for an early center and a third-buy candidate."""
from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class Interval:
    low: float
    high: float
    completed: bool = True
    def __post_init__(self):
        if self.low>self.high:raise ValueError("Interval low > high")

def triple_overlap(parts: Sequence[Interval]):
    if len(parts)!=3:raise ValueError("Exactly three consecutive segments required")
    if not all(p.completed for p in parts):
        return {"status":"pending_uncompleted_lower_level_segment"}
    low=max(x.low for x in parts);high=min(x.high for x in parts)
    status="positive_width_overlap" if low<high else "point_touch_only" if low==high else "no_overlap"
    return {"status":status,"lower":low,"upper":high}

def third_buy_candidate(center: Interval,departure_complete:bool,
                        first_retest_complete:bool,retest_low:float):
    if not center.completed or not departure_complete or not first_retest_complete:
        return "pending_completion"
    if retest_low>center.high:return "strictly_above_center_candidate"
    if retest_low==center.high:return "touching_upper_boundary_candidate"
    return "condition_not_met"

def synthetic_profit_counterexample():
    center=Interval(10.0,11.0)
    candidate=third_buy_candidate(center,True,True,11.5)
    entry=12.3
    future_executable_quotes=[12.2,12.0,11.7,10.6]
    can_sell_above_entry=any(q>entry for q in future_executable_quotes)
    assert candidate=="strictly_above_center_candidate"
    assert can_sell_above_entry is False
    return {"candidate":candidate,"entry":entry,"max_later_executable_quote":max(future_executable_quotes),
            "guaranteed_profit":False,"real_market_prices_used":False}

if __name__=="__main__":
    import json
    print(json.dumps({"example_overlap":triple_overlap([Interval(8,12),Interval(10,14),Interval(9,11)]),
                      "constructed_no_profit":synthetic_profit_counterexample()},ensure_ascii=False,indent=2))
