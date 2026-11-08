# TradeBooksInAIsEyes · 交易之书，AI之眼

> **深入阅读、审慎质疑、独立思考。** 以原书为证据，拆分作者观点、后期编者材料、AI解释与未来可检验命题。研究目的不是批量生成所谓必赢策略。

## 从哪里开始

| 需求 | 唯一入口 |
|---|---|
| **验收已经研究的《缠论》** | [《缠论》五卷108课正式验收入口](deliverables/chanlun_108_acceptance/README.md) |
| **5分钟看懂《缠论》** | **[全书一屏速览与20分钟思想地图](deliverables/chanlun_108_acceptance/01_FAST_READ.md)** |
| **把晦涩定理和全书论证读懂（必交模块）** | **[《缠论》AI深度导读：12组核心命题、行文脉络和8张教学图](deliverables/chanlun_108_acceptance/04_AI_GUIDE/README.md)** |
| **挖掘不该错过的细节** | **[20个灵感细节切口](deliverables/chanlun_108_acceptance/02_SPARK_INDEX.md)** |
| **阅读全书综合评述** | [AI独立全书评述](deliverables/chanlun_108_acceptance/00_REVIEW/FINAL_BOOK_SYNTHESIS.md) |
| **查看108课详细解读** | [单份规范章节研究](analyses/books/chanlun/chapters) |
| **对照原始PDF** | [唯一原书来源：缠论五卷](ChineseBooks/缠论) |
| **浏览110条未来验证命题与36个跨课案例** | [形式化研究案例](deliverables/chanlun_108_acceptance/03_formal_cases/README.md) |
| **研究下一本书怎么做** | **[交易书籍AI深度研究工作流（G0—G6）](docs/BOOK_RESEARCH_WORKFLOW.md)** |
| **文件去重与核验情况** | [规范来源与清理报告](deliverables/chanlun_108_acceptance/00_REVIEW/ACCEPTANCE_REPORT.md) |
| **哪些细节仍可能遗漏或待复核？** | [11处优先复核入口与全书覆盖边界](deliverables/chanlun_108_acceptance/00_REVIEW/DETAIL_COVERAGE_GAPS.md) |

## 一份内容只保存一个规范文件

- 原书按语种与书名存入`ChineseBooks/<书名>/`、`EnglishBooks/<书名>/`，研究报告使用`Reports/`。确认版权或分享权限后再考虑公开原文。
- 原书目录、文件哈希、不同版本日期、出处保存在`catalog/`；章节研究放在`analyses/books/<book_slug>/`。
- 结构化引用证据保存在`knowledge/`；跨学科独立想法在`ai_thoughts/`；需要时保留独立数学反例、已有研究协议和测试在`experiments/`、`tools/`、`tests/`。
- **最终验收文件夹**`deliverables/<book_slug>_acceptance/`只保存综合研究、章节索引、形式化待验证案例和验收证明；**不复制**原书、逐课源报告、工具或整个仓库。需要离线整包时，由CI从唯一规范位置**临时打包**，并不把ZIP或第二套原文件写进Git。
- 不在已有内容的目录保留空`.gitkeep`，不保留同一资料的“最终版再复制”或中间OCR/假说批次输出；保留唯一可信来源和Git历史即可回溯。

## 《缠论》当前研究成果

五卷共108课首轮文字研究、108份结构化证据、84个概念节点、145条关联、16条带来源身份的规则版本研究均已归档。全书已经整理**110条明确标记的AI待检验假说**与**36个跨课程形式化验证例子**，均未运行真实市场实证。详见[验收目录](deliverables/chanlun_108_acceptance/README.md)。

**已知缺口**：有些图表精确数字及后附编辑日期尚未完成独立终审；没有完整合法且唯一的笔—线段—中枢解析证明，没有真实A股无前视交易实验、样本外收益或风险实证。既有V1—V4合成研究代码仅在唯一规范目录保留以备查证，**按用户要求不继续扩建回测实验室**。

## 下一本书的标准交付：先快览、再发现细节

上传书籍 → 原书SHA和目录/图页索引 → **立即制作带覆盖状态的5分钟全书速览** → 全书逐区域同时识别CORE主干和SPARK冷门灵感 → **15—20分钟思想地图＋可浏览灵感卡** → 按兴趣深读章节、补上重要图像来源 → 全书AI独立长评 → 待验证形式化题目（`NOT_RUN`） → 去重验收和临时ZIP。

**不必读完所有逐章深度报告才能先获得全书整体认识，也不让“精简重点”吞掉那些令人意外的小细节。每一本书还必须交付独立的AI深度导读：定理/定义白话、作者行文脉络、可编辑图示、AI独立评论，不能只交摘要。**

详细验收门槛、目录模板、缺失证据处理、只读离线ZIP构建流程见 [docs/BOOK_RESEARCH_WORKFLOW.md](docs/BOOK_RESEARCH_WORKFLOW.md)；一般研究规范见 [七重解析标准](docs/ANALYSIS_STANDARD.md)、[阅读协议](docs/READING_PROTOCOL.md)、[证据与版权](docs/EVIDENCE_STANDARD.md)。

**研究免责声明**：这是可审阅的书籍研究，不构成交易建议、实盘指令或盈利承诺；未经授权不重新分发原作者受版权保护的整卷内容。
