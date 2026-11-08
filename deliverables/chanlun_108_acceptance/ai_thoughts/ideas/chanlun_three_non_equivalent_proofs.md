# AI独立研究：不把规范规则、物理比喻和市场利润混成一个判断

研究编号 AI-CHANLUN-IDEA-021。来源为第五卷101–105课的原作者文稿，尤其p.233–235、241–242、269–271、290–291、325。

重要发现有三类：

- 第101课原作者本人承认第二买点可以低于第一买点，故‘第二买必然高于第一买’是过度简化，任何解析器不应使用此无条件拒绝门。事件完成与点价排序必须分开。
- 第102课把市场走势递归结构类比位值表示，提出现代数学意义下的唯一分解。数学的强主张要求输入、全部合法划分、冲突裁决、递归终止以及真实数据层固定，不能靠局部图示或算法仅输出一条路径就当作定理证明。
- 第104课当年的几何/能量类比与2010年后编者加注之间，存在明确来源时序差异；抽象几何词汇也不自然生成“市场物理学”的可测量因果机制。

第103课和105课同时提醒：简单MACD风险过滤、分型笔纪律都可能提供可测试的操作方式，但**交易规则正确 ≠ 输入行情可观测 ≠ 合规可成交 ≠ 实际盈利**。因此建议统一引入：
```text
SourceRule(pdf_sha, original_at, role, version)
StateMachine(rule_version, source_snapshot, completed_bar_asof, candidate, confirmed)
AuxiliaryFilter(period, parameters, signal_known_at)
RiskPolicy(budget, position_eligibility, compliance_gate)
ActualTrade(fill_at, filled_shares, fees, pnl, independent_evidence)
```
无完整数据以及未经样本外检验的断言全部标记为待验证。
