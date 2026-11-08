# 第39课原始机械规则的分支覆盖审计

> 来源：第二卷 p.353–354，尤其 p.354 **编者注**指出 Ai 与 Ai+2 不创新高/低情况遗漏。源文件 SHA-256 `af49aecbd363286baacbea02d3778b436df4dad797523ce0eb83846118827a66`。

## 要核查的恰好是“部分函数”

作者尝试以同方向 Ai 与 Ai+2 的力度及盘整背驰判断交易节奏，但该课文字**没有明确覆盖每一种比较结果**。规则中未注明的事件不等于自动卖出或自动买入。

本审计只做以下保守状态识别：

```text
比较 Ai 与 Ai+2 同向极值：
  new_extremum > previous_extremum     => EXTENDS
  new_extremum = previous_extremum     => EQUAL
  new_extremum < previous_extremum     => FAILS_TO_EXTEND
```

为了方便演示，以上按**上涨段高点**定义；下跌段需要反转方向。脚本还记录 `divergence` 可能是 true/false/unknown。若状态是 EQUAL 或 FAILS_TO_EXTEND，就返回 `SOURCE_UNSPECIFIED`，**不发任何真实订单**。

这样做不是声称这些边界在整个108课中永远未解答，而是防止研究者在当前课程未经原文支持的情况下臆造完整交易函数。第39课及其编者注属于不同时间层次，应分层存档。

合成代码：[工具](../../tools/audit_chanlun_lesson039_branches.py)。数学测试不推算任何真实行情胜率；若以后补充解释，要写明新规则的依据页码/版本与与原始表达的差异。
