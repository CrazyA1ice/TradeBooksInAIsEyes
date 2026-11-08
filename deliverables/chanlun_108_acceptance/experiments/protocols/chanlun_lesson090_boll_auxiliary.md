# 第90课BOLL辅助判断：前缀数据、收口与未确认结构

原卷5p.30–36，SHA `6ea9d7fb45864494d37cc7152a335d656516802f8bdf95c93509d7b742e2ec65`。

BOLL数据来自截至`asof`的已完成收盘价，缺少窗口则返回INSUFFICIENT_WINDOW；用明确的总体标准差`ddof=0`和中心/上下轨/归一化宽度构造收口辅助标签`AUXILIARY_SQUEEZE`。收口阈值是示范预设，不是原作者未明确参数的历史复刻，也未优化参数。

即使BOLL收口，独立的`geometry_confirmed`为False仍只能输出CENTER_NOT_CONFIRMED；不得把它伪装为第三买卖点、BOLL近100%有效或实际净收益保证。代码只覆盖数值计算和标签分离，未做任何真实交易。

[纯合成代码](../../tools/audit_chanlun_lesson090_boll_asof.py)。