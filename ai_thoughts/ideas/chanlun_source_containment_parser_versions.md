# AI独立研究：从“有唯一图形”走向“解析规则可复核”的三层门槛

- ID：AI-CHANLUN-IDEA-013。
- 原文：第三卷p.291–295、第63课p.303–304、第64课p.311、第65课p.347–349。
- 状态：真实PDF定点来源阅读，局部合成程序验证；**未完整实现缠论分段和交易回测**。

第65课明确指出包含关系不具传递性，先合并第一、二根再判断第三根；第64课提出的小于0.5点“相近”也不具传递性。这意味着不能将‘相近价格’或‘相互包含K线’看成普通的数学等价类进行并查集合并。软件必须按事前约定的**数据时间、方向、边界和量化规则**解析。

此外，第62课正文和后面的“新笔定义”候选版，第61课2010章节署时与2007行情拼接的时间错位，分别说明**理论版本和来源版本**不能被静默覆盖。

我建议未来统一技术对象：
```text
source_document_sha
source_author_date + editorial_version
raw_bars_asof + data_frequency
quantization_policy + containment_direction_policy
fractal_rule_version + pen_rule_version + segment_rule_version
signal_first_confirmed_at + executable_after
test_status
```

只有三条门槛全部满足：源文署时可溯、局部几何运算确定、时间前视与交易执行条件可信，才允许将历史图解转为研究标签。没有任何一种“唯一分解”说法能自动替代这三条门槛。
