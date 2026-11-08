# 第92课Z/Zn中轴监视器：价格区间越界不充分确认第三买卖点

源第五卷p.93–96、原PDF SHA-256 `6ea9d7fb45864494d37cc7152a335d656516802f8bdf95c93509d7b742e2ec65`。

中心区间`[A,B]`定义`Z=(A+B)/2`，次级完整区间`[an,bn]`中点定义`Zn=(an+bn)/2`。这两个式子只是价格区间性质，不用未来bar。合成中心10–20、次级区间19–25导致Zn=22>B，代码只标记`OUTSIDE_WARNING`，且在另一个独立`third_point_confirmed=False`条件下返回`CENTER_THIRD_POINT_NOT_CONFIRMED`。

真实第三买卖点须由独立、已完成的次级走势离开及回试等严格结构和确认时间证据提供；此函数既不是完整中枢解析器，也没有证明作者关于Zn变化后“最终必越界”的普适论断。

[代码](../../tools/audit_chanlun_lesson092_midpoint_monitor.py)。
