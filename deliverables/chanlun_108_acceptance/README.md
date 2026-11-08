# 《缠论》五卷108课：最终成果验收入口（无重复副本）

> **这里仅保存可供审核的最终成果、来源索引和形式化待检验命题。** 原书五卷PDF、108课解读和原始证据保存在仓库各自唯一规范目录中，直接通过下列链接访问；不再将633份过程材料和原书额外复制一套到此处。按照要求：**停止推进回测实验室**，不宣称真实行情测试或已验证收益。

## 先看这些最终成果

0. **[5分钟快速概览与全书思想地图](01_FAST_READ.md)**：先用自己的话理解全书最值得记的主张、重点的来龙去脉及主要局限。接着打开 **[20张不该遗漏的灵感细节卡](02_SPARK_INDEX.md)**，按反直觉、小技巧、规则边界与不同观点冲突浏览，再决定要不要深入。


1. **[全书AI综合评述](00_REVIEW/FINAL_BOOK_SYNTHESIS.md)**：分八段讨论108课的核心观点、来源版本、逻辑反证、AI独立判断及剩余证据缺口。
2. **[108课验收矩阵](00_REVIEW/LESSON_ACCEPTANCE_MATRIX.md)**：逐行进入本仓库**唯一规范版本**的解读、证据和原始PDF。
3. **[110条逐课形式化命题](03_formal_cases/110_CASES_REVIEW_TABLE.md)**：每条绑定原证据ID、原书物理页；[机器可读研究协议](03_formal_cases/ALL_110_PROSPECTIVE_FORMAL_CASES.json)记录变量、对照、前提、失败条件，均`NOT_RUN`。
4. **[36个跨课形式化例子](03_formal_cases/36_CROSS_LESSON_FORMAL_EXAMPLES.json)**：涵盖笔、段、背驰、MACD、风险、行为、前视与数据修订等；[阅读指南](03_formal_cases/README.md)解释哪些命题不能只靠价量回测。
5. **[研究成果去重与完整性报告](00_REVIEW/ACCEPTANCE_REPORT.md)** 和 **[规范文件清单](00_REVIEW/FILE_MANIFEST.json)**：目录索引不存复制文件；[验收脚本](00_REVIEW/audit_acceptance.py)检查原文件内容SHA与逐课、逐案关系。

## 真实书源与完整研究材料（点击原件，不是第二份拷贝）

| 材料 | 唯一规范位置 | 已知范围 |
|---|---|---|
| **原书五卷PDF** | [ChineseBooks/缠论](../../ChineseBooks/缠论) | 5卷，逐卷SHA-256校验 |
| **108课原始逐课分析** | [analyses/books/chanlun/chapters](../../analyses/books/chanlun/chapters) | 108课首轮深读 |
| **分卷/跨课研究** | [analyses/books/chanlun/volumes](../../analyses/books/chanlun/volumes) | 分阶段论证及总览 |
| **108份结构化证据** | [knowledge/evidence](../../knowledge/evidence) | 原著、后期编辑、推论、AI假说 |
| **概念与来源关系** | [knowledge/claims](../../knowledge/claims) · [来源目录与规则版本](../../catalog) | 概念图谱及作者/编者版本 |
| **原始来源/配图审计** | [reports/source_inventory](../../reports/source_inventory) | 来源时间、图示未验证项 |
| **AI独立思考** | [ai_thoughts/ideas](../../ai_thoughts/ideas) | 不与原著断言混淆 |
| **既有研究协议与审计** | [experiments/protocols](../../experiments/protocols) · [tools](../../tools) | 研究历史和合成反例；不继续扩建回测实验室 |
| **可复现性测试** | [tests](../../tests) | 项目代码回归，不构成市场实证 |

## 如何下载完整离线验收包

**GitHub不保存第二套副本**。如需一次拿齐原书、逐课分析、证据、全书评述和形式化例子，CI会在构建时**临时从上列规范位置组装完整ZIP**，上传GitHub Actions附件；该ZIP不是再次提交到仓库的文件。入口：[验收打包工作流](../../.github/workflows/chanlun-108-acceptance-bundle.yml) · [Actions运行记录](https://github.com/CrazyA1ice/TradeBooksInAIsEyes/actions/workflows/chanlun-108-acceptance-bundle.yml)。

打包范围由 [OFFLINE_PACKAGE_SPEC.json](OFFLINE_PACKAGE_SPEC.json) 冻结，使用 [通用ZIP构建工具](../../tools/build_book_acceptance_zip.py)；解压后根目录为`TradeBooksInAIsEyes/`，保留仓库的链接相对结构。

## 去重后的目录组织

```text
deliverables/chanlun_108_acceptance/
├── README.md
├── 01_FAST_READ.md
├── 02_SPARK_INDEX.md
├── OFFLINE_PACKAGE_SPEC.json
├── 00_REVIEW/
│   ├── FINAL_BOOK_SYNTHESIS.md
│   ├── LESSON_ACCEPTANCE_MATRIX.md
│   ├── ACCEPTANCE_REPORT.md
│   ├── FILE_MANIFEST.json
│   └── audit_acceptance.py
└── 03_formal_cases/
    ├── README.md
    ├── 110_CASES_REVIEW_TABLE.md
    ├── ALL_110_PROSPECTIVE_FORMAL_CASES.json
    └── 36_CROSS_LESSON_FORMAL_EXAMPLES.json
```

## 可执行的完整性核查

在**仓库根目录**用一条命令运行：

`python -B deliverables/chanlun_108_acceptance/00_REVIEW/audit_acceptance.py`

会核对五卷原PDF的SHA-256、**625份规范研究文件**的Git blob SHA、108课与110条来源假说的逐条对应、36例完整性，并检查验收目录不再出现重复书源。审计**不会**访问真实市场行情或运行旧回测实验室。

## 下一本书照什么流程？

通用标准已写入 [docs/BOOK_RESEARCH_WORKFLOW.md](../../docs/BOOK_RESEARCH_WORKFLOW.md)：从PDF/EPUB登记→来源/OCR质量→逐章七重解读→图表证据→跨章研究→形式化待验证清单→单一验收目录→自动去重→CI临时打包。以每本书的`book_slug`复用，不再为下本书重复造同样的文件夹树。

**阅读目的**：先拥有全书大图，再自由探索容易被传统摘要删除的细节；灵感卡是已有研究的精选入口，不虚称全部插图/脚注完成第二次逐条核验。

**已知限制**：所有108课首轮研究存在，并不代表全书插图精确数字已核验；完整笔/线段/中枢唯一性、真实历史盈利与外部样本外统计均未得到证明。证据未知处必须保持未知。原书公开传播授权仍需单独确认。
