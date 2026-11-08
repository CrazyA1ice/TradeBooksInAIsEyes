# 108课统一证据图谱、规则版本与时间归属（第一版）

> 本文件描述已落库的研究索引合同。**不是**完整缠论走势解析器、理论唯一性定理或真实A股策略回测。

## 统一范围与数据源

- 已有五卷原书的固定SHA-256及108课连续索引：`catalog/chanlun_lesson_index.json`。
- 108份逐课证据：`knowledge/evidence/chanlun_lesson001.json` … `chanlun_lesson108.json`；**兼容早期source.lesson_number与后来顶层lesson**，不改写原证据，也不因schema差异删掉早期内容。
- 10份可追溯的原有图谱，当前合并为**84节点、145条有方向和类型的语义关联**；原文件保持不可变，索引中每个节点仍保留其原图谱路径、原PDF卷及物理页和研究状态。
- 人工有边界整理的**16条规则/编者争议记录**在`catalog/chanlun_rule_history_v1.json`，以来源角色和独立时间为主，不把冲突消解成单一路线。
- `knowledge/claims/chanlun_unified_index_v1.json`为检查过的统一物化目录；`tools/audit_chanlun_unified_knowledge.py --verify`对原始来源重新构建并核验镜像，若以后修改图谱而未同时审核更新索引则**失败关闭**。

## 版本分歧的研究态边界

| 线索 | 关键来源 | 审阅状态 |
|---|---|---|
| 早期笔规则、附‘新笔定义’和第77课阐释 | 第62课卷3 p.292–295；第77课卷4 p.158–160 | 第62课p.295补充发表时间**未知**；不以汇编邻接推断和作者首篇同日 |
| 后发新笔条件 | 第81课汇编内**2007-09-18 22:53:57**另篇，卷4 p.241 | 与2007-09-05第77课的版本分别保留，不能在9月5日的模拟中提前引用 |
| 线段特征序列/缺口与成员类型 | 第67课卷3 p.388–389；第71/72课卷4 p.71–72、84–87 | 后期‘娇’反对非包含处理次序，来源日期不明；不覆盖作者首发 |
| 政策风险分类争议 | 第74课卷4 p.111–113 | 原作者非系统性与后期编辑系统性意见各自保留；需实证冲击范围 |
| 第100课二分路径争论 | 第100课卷5 p.224–225 | 后期编辑疑义不等于独立行情价格回放，结论保持未决 |
| 底部两份合同 | 第108课卷5 p.395 | 分型上下沿与一买/中枢/第三类点合同并列，而不是一条规则的自动升格 |

`source_displayed_at`只是**原材料中可见的署时时间**：不能证明网页精确发布时间、用户何时可见、市场数据何时可用，更不能将它作为历史真实成交的as-of时钟。未知编者时间必须填`null`；脚本仅允许按显示时间做**文献排序**，不允许将其输出伪装成可回测信号或盈利证明。

## 只读查询与自动验收

在仓库根目录使用单行命令：

`python -B tools/audit_chanlun_unified_knowledge.py --verify`

`python -B tools/audit_chanlun_unified_knowledge.py --verify --node L81-PEN-VERSION`

`python -B tools/audit_chanlun_unified_knowledge.py --verify --lesson 108`

`python -B tools/audit_chanlun_unified_knowledge.py --verify --family segment`

专项测试：`python -B -m unittest discover -s tests -p "test_chanlun_unified_knowledge.py" -v`。所有操作不修改PDF、原始行情或旧图谱；不依赖OCR人工逐页操作。

## 下一项目闸门（尚未通过）

1. 补齐所有争议版本的**独立原文与图示高清核验**，找出发表时间不可确认的页面和编辑归属；不要批量要求用户手工OCR。
2. 将文献日期与行情`market_asof`、bar的`completed_at`、信号`confirmed_at`、撮合成交`filled_at`分别建模；完成真实数据只读接口及事件流规范。
3. 实现规则版本化的完整笔→线段→中枢→多级别走势**候选解析器**，对等高、包含、停牌、缺口、修订版本作性能无关的先验反例测试。
4. 在可追溯行情上做冻结规则、逐前缀回放、样本外审计，再谈收益和实盘执行。

**报告事实与假设**：图谱连接中的`ai_analysis`是AI研究关系，不是作者原文事实；`documented_conceptual_relation`是文本概念联系，不是已验证的数学定理。所有规则版本标识`research_only_not_market_tested`。
