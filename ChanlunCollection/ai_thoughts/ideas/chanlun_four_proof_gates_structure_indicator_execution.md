# AI独立研究：有限状态的结构语法、价格中点预警与资金执行三重证明

- ID：AI-CHANLUN-IDEA-019
- 证据：第五卷第91课p.64–66、第92课p.93–96、第93课p.124–125、第94课p.143–145、第95课p.150–151。
- 研究程度：源PDF SHA与有限原文核对 + 四组纯合成算法审计。未进行完整几何解析或真实行情回测。

最清晰的算法是第91课规范四状态有限自动机：它证明特定定义内哪些相邻状态转移被作者允许，但并不证明从任何缺失/歧义/实时未完成OHLC中都能唯一求出四态。

第92课给出中心区间中点和次级区间中点的监视指标Z/Zn。其越界对第三类买卖点并不充分：**监视信号与严格几何完成事件必须是两个不同的数据表**，并各带首次可知时间。

第93课说明相同市场状态并非强制相同操作决策；第94课又明确T+1规则可以限制看似有利的退出。这使策略系统至少包含四种证据门：
1. 原始来源和定义版本；
2. 几何状态合法与首次可知；
3. 个人风险策略和确定的规则；
4. 交易所规则、流动性、实际成交及扣费盈亏。

第95课更提醒：“现金回本”不是持仓市值不会再损失。账户现金流、现有市场风险和真实已实现交易都必须分列。

研究接口建议：
```text
SourceClaim(author/editor, pdf_sha, publication_time, rule_version)
ObservedGeometry(raw_ohlc_version, asof, pen_state, center_intervals)
AuxiliaryWarning(indicator, calculated_from_completed_bars, asof)
PolicyChoice(state_known_at, risk_profile, precommitted_exit)
ExecutionEvidence(tplus1_eligible, actual_fill, fee, realized_pnl)
```
只有这种拆分能避免以理论的“有条件的结构分类”代替真实市场的可行、有成本、不保证收益的交易决策。
