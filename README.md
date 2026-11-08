# TradeBooksInAIsEyes · 交易之书，AI 之眼

> **《缠论》全书研究成果已集中验收：** [进入五卷108课统一验收文件夹](deliverables/chanlun_108_acceptance/README.md) · [110条逐课形式化命题、36个跨课案例](deliverables/chanlun_108_acceptance/03_formal_cases/README.md) · [全书综合评述](deliverables/chanlun_108_acceptance/00_REVIEW/FINAL_BOOK_SYNTHESIS.md)。按最新需求，**停止继续开发回测实验室**，仅整理未来验证例子；全部真实市场实验状态仍为`NOT_RUN`。


> **Read deeply. Question carefully. Think independently.**  
> 深入阅读，审慎质疑，独立思考。

这是一个长期、开放的交易思想研究计划。我们让 AI 阅读交易书籍、报告及其他材料，在**忠实还原作者思想**的基础上进行逻辑审视、跨学科分析、理论比较与独立推演，并将可检验的主张转化为研究假说。项目不以机械摘要、批量生成交易策略或承诺收益为目标。

## 我们研究什么

- **人类作者的观点：**作者实际提出了什么问题、概念、假设与结论？
- **AI 的理解与质疑：**哪些论证成立，哪些有歧义、隐含前提或潜在反例？
- **市场与形式化：**理论能否用数学、算法或市场机制解释？如果不能，如何保留它的原始意义？
- **实证与独立思考：**哪些命题可以验证？AI 能否提出新的解释、问题或假说？

我们保留多种竞争性解释，允许理论与 AI 判断随着新证据修订。**AI 的解释不等于原著，AI 的假说不等于被验证的规律。**

## 研究成果

每本书逐步形成：思想地图、逐章深度解读、核心概念索引、逻辑质疑、可验证命题、AI 原创假说，以及特色评论系列《在 AI 眼中》。重要观点应能定位到原始材料的具体位置。详情见 [研究方案](docs/PROJECT_PLAN.md)。

## 当前进展

**阶段：Phase 1 — 五卷 PDF 盘点和 108 课标题自动索引已完成，第 1–108 课首轮文本研究已完成；第106课均线九类/板块轮动、第107课次级别反弹分段、第108课两种底部定义已增加有来源和纯合成边界测试；全面图像数值、理论版本和真实行情验证尚待开展。** 首批材料为 `ChineseBooks/缠论/` 中的五卷 PDF。**已完成五卷页数、哈希和文本覆盖盘点；第 1–108 课首轮文本研究稿已完成，但印刷目录逐项核对、图像可靠视觉核验及全卷研究尚未完成**；这些内容将在试点阶段开展。书籍的真实版本、目录、卷际关系及扫描质量均有待核实。

## 目录导航

| 路径 | 用途 |
| --- | --- |
| `ChineseBooks/`、`EnglishBooks/`、`Reports/` | 原始材料分类（公开分享须确认授权） |
| `catalog/` | 书籍、报告及来源登记 |
| `analyses/books/` | 单本书、卷册、章节、概念与批判解读 |
| `analyses/cross_book/` | 跨书对照与理论关系研究 |
| `ai_thoughts/` | AI 独立想法、假说、模型与思辨 |
| `experiments/` | 假说、实验协议与结果 |
| `knowledge/` | 概念、理论关系、证据索引 |
| `docs/` | 研究方案、阅读流程、分析与证据标准 |
| `schemas/`、`tools/`、`tests/` | 后续数据结构、自动化工具与测试 |
| `.github/workflows/` | 后续持续集成配置 |

## 研究规范

- [总体计划](docs/PROJECT_PLAN.md)
- [阅读与解析流程](docs/READING_PROTOCOL.md)
- [解读成果标准](docs/ANALYSIS_STANDARD.md)
- [证据、版权与结论边界](docs/EVIDENCE_STANDARD.md)
- [分阶段路线图](docs/RESEARCH_ROADMAP.md)

## 怎样加入材料

优先登记来源、版本、语言、卷册及公开授权状态。对于不具备公开再分发授权的 PDF，请保存在私有资料位置，仅在公开仓库提交原创研究、必要的短引文和来源链接。**项目当前为公开仓库，现存五卷 PDF 的再分发权限仍待核对。**

## 重要说明

项目仅供学习、研究与方法论探索，不构成投资建议、收益保证或交易指令。仓库尚未选择适用于原创代码和文档的许可证；不要推定第三方书籍内容可以随项目自由再许可。

## 108课统一索引（第一版）

第1–108课首轮研究覆盖之后，已经将**108份逐课证据、10份关系图谱（84个研究节点、145条关系）以及16条有来源角色的规则/编辑争议记录**整合到[只读统一索引](knowledge/claims/chanlun_unified_index_v1.json)。[来源与定义版本工作规范](docs/CHANLUN_UNIFIED_KNOWLEDGE.md)规定日期和证据边界：附编、后发新笔、作者原文及AI解释不可无来源合并；有原书时间不等于真实行情当时可用。可用`python -B tools/audit_chanlun_unified_knowledge.py --verify`复查，或按课号、节点和规则家族查询；**未实现完整走势解析器或真实收益验证**。

## 走势结构实验室：无前视前缀回放 v1（仅合成数据）

已开始[时间门、固定方向K线包含、三K线分型候选及旧/新笔必要条件](docs/CHANLUN_PREFIX_REPLAY_LAB_V1.md)的真实可运行程序，并提供[多前缀版本差异审计](tools/audit_chanlun_prefix_version_comparison_v1.py)。不会从未来K线偷取确认，不强行把未知编注当作历史已发布规则。**该版本只接受显式人工合成行情**，不是完整笔/线段/中枢解析器，也不是实证回测或可交易策略。

## 增量结构事件实验室 V2（2026-11-08）

已建立[不可变分型/笔候选事件与严格特征序列必要条件](docs/CHANLUN_INCREMENTAL_EVENTS_V2.md)：逐根已完成合成K线生成`OPEN / REVISE / RETRACT / REOPEN`，追踪每个候选真实观察时刻和前缀SHA；第67/71课无缺口、有缺口待反向确认、独立序列STRICT/AUXILIARY成员的反例均可审计。它只是在上一版V1局部候选之上增加**证据修订与边界**，**未**实现完整笔、线段、走势中枢或真实回测。可运行`python -B tools/audit_chanlun_incremental_witnesses_v2.py`查看纯合成审计。

## 缠论笔候选前沿 V3（只读人工合成）

在[增量事件V2](docs/CHANLUN_INCREMENTAL_EVENTS_V2.md)基础上新增[保守笔前沿与线段类型隔离](docs/CHANLUN_PEN_FRONTIER_V3.md)：同类分型替换极端值，等价极值显式待定、相反分型需通过冻结规则的局部必要门；新版终点出现时撤销旧候选且不更改历史事件。仅将局部笔投影为`UNDETERMINED`特征，**禁止在没有完整笔证明时将它转入正式线段**。对应[独立合成审计](tools/audit_chanlun_pen_frontier_witnesses_v3.py)。完整笔、线段、中枢、真实行情和收益仍未完成。

## V4：历史行情订正双时钟与完整笔证据闸门

[缠论市场订正时间轴及完整笔认证所需证据V4](docs/CHANLUN_REVISION_PROOF_GATES_V4.md)已增加实际可执行的**合成来源版本**变更实验：更正发生前后，`as-of`快照分别保持原价/修订价，旧候选带旧版本来源指纹，修订后的新来源不得复用旧候选身份。任何自报“证据已验”只能提交审核请求，**一律不能升级完整笔或STRICT线段成员**；没有接入真实市场数据或交易。可单行运行`python -B tools/audit_chanlun_revision_causal_witness_v4.py`。
