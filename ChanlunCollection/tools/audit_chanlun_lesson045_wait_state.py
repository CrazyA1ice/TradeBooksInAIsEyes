#!/usr/bin/env python3
"""Single-position synthetic wait-state example; consumes confirmed signals, never invents them."""
from dataclasses import dataclass,field
@dataclass
class WaitState:
    position:str="HOLD_CASH"
    journal:list=field(default_factory=list)
    def step(self,signal,confirmed=False,filled=False):
        if signal not in ("BUY","SELL",None):raise ValueError("invalid signal")
        before=self.position
        if not confirmed or not filled or signal is None:
            result="NO_EXECUTION"
        elif signal=="BUY" and before=="HOLD_CASH":
            self.position="HOLD_STOCK";result="BOUGHT"
        elif signal=="SELL" and before=="HOLD_STOCK":
            self.position="HOLD_CASH";result="SOLD"
        else:
            result="INVALID_DIRECTION_NO_EXECUTION"
        self.journal.append({"signal":signal,"confirmed":confirmed,"filled":filled,"before":before,"after":self.position,"outcome":result})
        return result
def example():
    x=WaitState()
    assert x.step("BUY",False,False)=="NO_EXECUTION"
    assert x.step("BUY",True,True)=="BOUGHT"
    assert x.step("SELL",True,False)=="NO_EXECUTION"
    assert x.step("SELL",True,True)=="SOLD"
    return {"final_state":x.position,"journal":x.journal,"real_orders_sent":False}
if __name__=="__main__":
    import json
    print(json.dumps(example(),ensure_ascii=False,indent=2))
