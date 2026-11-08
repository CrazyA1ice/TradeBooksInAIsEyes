#!/usr/bin/env python3
"""Atomic per-level share allocation and reservation, pure synthetic inventory."""
class Inventory:
    def __init__(self,allocations):
        if any(not isinstance(v,int) or v<0 for v in allocations.values()):raise ValueError("share allocations must be nonnegative integers")
        self.allocations=dict(allocations)
        self.total=sum(allocations.values())
    def shift(self,from_level,to_level,qty):
        if not isinstance(qty,int) or qty<0:raise ValueError("invalid transfer")
        if self.allocations.get(from_level,0)<qty:raise ValueError("insufficient source shares")
        if from_level==to_level:return
        self.allocations[from_level]-=qty
        self.allocations[to_level]=self.allocations.get(to_level,0)+qty
        assert sum(self.allocations.values())==self.total
    def reserve_sale(self,level,qty):
        if not isinstance(qty,int) or qty<0:raise ValueError("invalid sale")
        if self.allocations.get(level,0)<qty:raise ValueError("cannot double spend stock")
        self.allocations[level]-=qty
        self.total-=qty
        assert sum(self.allocations.values())==self.total
    def snapshot(self):
        return {"allocations":dict(self.allocations),"available_total_shares":self.total}
def demo():
    b=Inventory({"5min":70,"30min":30})
    b.shift("5min","30min",20)
    after_shift=b.snapshot()
    b.reserve_sale("30min",50)
    after_sell=b.snapshot()
    return {"after_shift":after_shift,"after_sell":after_sell,"real_orders_sent":False}
if __name__=="__main__":
    import json
    print(json.dumps(demo(),ensure_ascii=False,indent=2))
