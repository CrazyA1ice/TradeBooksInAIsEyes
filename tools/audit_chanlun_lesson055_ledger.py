#!/usr/bin/env python3
"""Synthetic cash/share ledger with no brokerage execution or T+1 assumptions."""
from dataclasses import dataclass
@dataclass
class Ledger:
    cash:float
    shares:int=0
    def buy(self,quantity,price):
        if not isinstance(quantity,int) or quantity<=0 or price<=0:raise ValueError("bad buy")
        amount=quantity*price
        if self.cash<amount:raise ValueError("insufficient cash")
        self.cash-=amount
        self.shares+=quantity
    def sell(self,quantity,price):
        if not isinstance(quantity,int) or quantity<=0 or price<=0:raise ValueError("bad sale")
        if self.shares<quantity:raise ValueError("insufficient shares")
        self.shares-=quantity
        self.cash+=quantity*price
    def mark(self,price):
        if price<0:raise ValueError("invalid marking price")
        return self.cash+self.shares*price
def example():
    account=Ledger(cash=1000)
    account.buy(20,10)
    after_buy={"cash":account.cash,"shares":account.shares,"wealth":account.mark(10)}
    account.sell(10,20)
    after_sell={"cash":account.cash,"shares":account.shares,"wealth":account.mark(20)}
    later={"cash":account.cash,"shares":account.shares,"wealth":account.mark(5)}
    assert (after_buy["cash"],after_buy["shares"])==(800,20)
    assert (after_sell["cash"],after_sell["shares"])==(1000,10)
    assert after_sell["wealth"]-later["wealth"]==150
    return {"after_buy":after_buy,"after_sell":after_sell,"after_stock_decline":later,
            "market_orders_sent":False}
if __name__=="__main__":
    import json
    print(json.dumps(example(),ensure_ascii=False,indent=2))
