#!/usr/bin/env python3
"""Synthetic cost-recovery vs remaining market risk (no real securities traded)."""
from dataclasses import dataclass
@dataclass(frozen=True)
class PositionLedger:
    initial_shares: int
    purchase_price: float
    sold_shares: int
    sale_price: float
    later_price: float
    def calculate(self):
        assert 0 < self.initial_shares and 0 <= self.sold_shares <= self.initial_shares
        assert min(self.purchase_price, self.sale_price, self.later_price) >= 0
        capital=self.initial_shares*self.purchase_price
        cash=self.sold_shares*self.sale_price
        remaining=self.initial_shares-self.sold_shares
        sale_mark=remaining*self.sale_price
        later_mark=remaining*self.later_price
        return {"initial_capital":capital,"cash_recovered":cash,
                "initial_capital_fully_recovered":cash>=capital,
                "remaining_shares":remaining,
                "wealth_at_sale":cash+sale_mark,
                "wealth_after_price_move":cash+later_mark,
                "remaining_market_value_drawdown":sale_mark-later_mark,
                "no_remaining_stock_price_exposure":remaining==0,
                "actual_market_data_used":False}
def demo():
    r=PositionLedger(100,10,50,20,4).calculate()
    assert r["initial_capital_fully_recovered"] is True
    assert (r["wealth_at_sale"],r["wealth_after_price_move"])==(2000,1200)
    assert r["remaining_market_value_drawdown"]==800
    assert r["no_remaining_stock_price_exposure"] is False
    return r
if __name__=="__main__":
    import json
    print(json.dumps(demo(),ensure_ascii=False,indent=2))
