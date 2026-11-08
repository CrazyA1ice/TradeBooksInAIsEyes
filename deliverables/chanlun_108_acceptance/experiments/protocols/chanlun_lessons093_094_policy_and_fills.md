# 第93–94课：同一观测下不同策略及A股T+1未完成成交

源第五卷p.124–125、p.143–145，SHA-256 `6ea9d7fb45864494d37cc7152a335d656516802f8bdf95c93509d7b742e2ec65`。

先由纯合成观察对象标记`PEN_TOP_CANDIDATE`，策略对象可据已知风险偏好选择`PARTIAL_EXIT_PLAN`、`OSCILLATION_WATCH`或`WAIT`。**同一已完成信号不能依照未来结果更改过去的政策**，所以不输入后续上涨/下跌标签。

后续订单执行门检查`shares_bought_today`和`previously_settled_shares`；如尝试卖出的数量超过已结算可卖数量，则拒绝当日卖出新购A股部分。符合T+1也不能自动认定FILLED——需明确另有实际成交证据。市场细则及股票类别可能变化，该门针对T+1受限的普通A股示范，不能代替交易所完整结算规则。

[代码](../../tools/audit_chanlun_lessons093_094_policy_fills.py)；全部为虚构账户和订单。
