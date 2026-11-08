# 第54课：同级别中枢的连接段是额外的语义要求

真实PDF第三卷 p.170–175；SHA `fad3474e103353f6f67799aefec8c9fba28c9615c0c77a5c67fcbf2b6b4f8a7a`。作者用标记g0,d1,g1等描述同一走势的两种合法分解，但p.172强调：**两个同级别中枢之间必须有次级别走势连接。**

纯合成局部语法：
```text
CENTER(level=1), LINK(level=0), CENTER(level=1)   => 连接约束满足
CENTER(level=1), CENTER(level=1)                  => INVALID_SAME_LEVEL_ADJACENCY
CENTER(level=1), HIGHER_LEVEL_EXTENSION, CENTER(level=1) => 仅标记另一种语义，不能自动视为原同级别分解
```

完整缠论分解还需验证中心区间如何确定、叶子走势是否完成、连接段方向及级别、不同高层扩展规则，**局部语法通过不等于完整合法走势**。图示页仍有未核的数字和定义版本，不能把此合成程序写作图1完整复刻。

[执行脚本](../../tools/audit_chanlun_lesson054_connections.py)。
