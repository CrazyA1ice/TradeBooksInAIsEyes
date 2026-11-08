# 第97–98课：理论→市场已知观察→计划→可成交四层时间门

第五卷PDFp.172–173、192–194，SHA `6ea9d7fb45864494d37cc7152a335d656516802f8bdf95c93509d7b742e2ec65`。

程序在确认条件尚未来到时输出`WAIT_FOR_EVIDENCE`。当续升与回探被同时标记则`CONFLICT_REVIEW`；仅出现一个且其`observed_at<=decision_at`才可选择对应方案。其次，`SIGNAL_CONFIRMED`与`PLAN_ACCEPTED`之间还有适当风控审批；`eligible_to_sell`不足时`EXECUTION_BLOCKED`，即使合法可下单也不能在缺成交证据时写`FILLED`。

这里不实现真正的缠论背驰/线段检测，不覆盖市场各证券特别制度，也未触发真实买卖。[代码](../../tools/audit_chanlun_lessons097_098_evidence_gate.py)。
