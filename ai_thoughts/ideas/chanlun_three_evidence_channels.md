# AI独立研究：结构主证据、层级上下文与辅助指标的三通道账本

- 编号：AI-CHANLUN-IDEA-018
- 源：第四卷第86课p.346–353、第88课p.384–387；第五卷第89课p.3–6、第90课p.30–36。
- 当前状态：两卷SHA来源核查 + 三组纯合成局部算法；**无真实行情市场回测和完整缠论解析器**。

第86课告诉我们，即便低级别第三类卖点被同一底层模型识别，真正的经济意义仍受**上一级别已确认结构**限制。假如用事后完成的高级别中枢来决定当天的小卖点，数据泄漏就已经发生。

第88、89课则把不同结构的衔接显式化：旧结构可被判断为结束，但新结构仍可能尚未确定，中间态不能被程序偷偷抹除。中枢是结构对象，盘整是包含结构的完整走势类型，必须保留对象类型区别。

第90课把BOLL作为潜在的辅助时间提示，是可做独立统计检验的经验假说；作者的接近100%准确率缺少独立可复核统计总体，不能作为项目结论。尤其BOLL波动压缩只说明宽度变小，不逻辑决定突破方向。

因此研究系统应设置三个互不自动晋级的通道：
```text
geometric_truth: source_sha, rule_version, structure_type, confirmed_at
context_truth: parent_level, asof_parent_state, transition_pending
auxiliary_statistics: indicator_type, parameters, completed_bar_time, false_positive_rate
```
任何辅助指标可以支持**决定是否进一步核查**，不能自行将尚未完成的走势结构升级为已确认，也不能直接给出收益保证。