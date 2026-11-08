# 第88–89课：旧→新过渡与中枢/盘整的类型安全

原卷4p.384–387和卷5p.3–6，两份独立原PDF SHA锁定。

状态机在旧走势出现结束候选时，仅可进入TRANSITION_PENDING；新的完整结构到达首次确认时间后才能标为NEW_CONTEXT_CONFIRMED。过渡期间旧中枢仅作上下文引用而不改写事实。作者声称未来先形成更高级别中枢属于其理论主张，但现阶段不从单一背驰信号推出已形成中心。

类型门独立区分CENTER_COMPONENT（几何构件）和CONSOLIDATION_MOVEMENT（一个完成中枢的走势类型），要求`complete=True`后才可标整段走势，不用价格横盘外观偷换其定义。

[合成代码](../../tools/audit_chanlun_lessons088_089_transition_center.py)没有完整递归走势解析或真实行情历史检验。