# 第59课：价格数值量化政策决定边界接触

来源：第三卷PDF p.257，SHA-256 `fad3474e103353f6f67799aefec8c9fba28c9615c0c77a5c67fcbf2b6b4f8a7a`。

作者原文给出的两个边界是3994.57和3994.21，并指出线段是否分三段取决于事先固定的价格精度。AI补充审计：**精度单位=1并不能唯一决定数值量化函数**。

用Python `decimal.Decimal`固定小数输入，检查三种不同映射：
- `TRUNCATE_TOWARD_ZERO(1)`：3994与3994，相等；
- `ROUND_HALF_UP(1)`：3995与3994，不相等；
- `EXACT_CENTS(0.01)`：3994.57与3994.21，不相等。

作者并没有明确在本课说明截断/舍入的程序算法，因此程序不应把这些合成处理方式说成已被作者指定。要求价格解析器必须记录 `policy_id`、`quantum`、`direction`、`data_adjustment_version`，若未声明返回`PRECISION_POLICY_MISSING`。

[可执行审计脚本](../../tools/audit_chanlun_lesson059_precision.py)，其结果**不是图像行情独立重演或实盘盈利证明**。
