# 第100课：原作者二分与后期娇注反例式质疑的证据对照

源第五卷p.224–225，SHA `6ea9d7fb45864494d37cc7152a335d656516802f8bdf95c93509d7b742e2ec65`。

原作者把后续行情按是否出现5分钟第三类卖点划分两条路径，后期娇注则在p.225指出后续出现另一些中枢扩展路径，认为不属于原分类。程序需要**分别保存**`AUTHOR_ORIGINAL_BRANCH`与`LATER_EDITORIAL_COUNTERCLAIM`，给来源日期、页码和状态，而不是让后来注释直接覆盖历史作者文本。

当编辑质疑且没有经独立历史行情/规则版本复查时输出`REVIEW_REQUIRED`；不能据此证明作者已经错或仍完全正确。对于一条未落在原两支的真实候选应保留`OUTSIDE_ORIGINAL_CLASSIFICATION`，而不是删除异常观察。

[代码](../../tools/audit_chanlun_lesson100_branch_dispute.py)；没有真实行情交易回放。
