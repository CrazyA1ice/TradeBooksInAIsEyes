# 第82课：后验中继/成笔与在线确认的区别

原第四卷p.266–274，SHA `ceca9ac8b7fb13106d2085253679acf1474373fb61ca38b487d8ca01cf0ad66d`。

已完成的三K线顶/底分型与它未来是否**真正延伸为一笔**是两个不同命题。顶分型可以成为中继而不是立即完成下行笔；作者用小级别买卖点和中枢状态帮助判断，但不构成独立证明某市场参与者的心理。

事件表要求`FRACTAL_OBSERVED`之后仍为`PENDING_OUTCOME`，只有在后来实际时钟出现`PEN_COMPLETED`或者`CONTINUATION_CONFIRMED`后才能变更状态；不得在旧事件中涂改源断言。

[代码](../../tools/audit_chanlun_lesson082_fractal_outcome.py)。这是一套局部状态审计，不自动从真实价格识别笔，也不是作者的盈利概率估计。
