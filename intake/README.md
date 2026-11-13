# G0：下一本交易书籍的本地资料入库预检（首版）

这是一个**不联网、默认只读、只输出元数据**的 G0 辅助工具，服务于 [通用阅读研究工作流](../docs/BOOK_RESEARCH_WORKFLOW.md) 的“来源登记”阶段。当前 BOOK_COLLECTIONS.json 只登记了 chanlun；此工具不会自动生成另一套 Collection、写入注册表、导入受版权保护的原文或修改现有《缠论》研究成果。

## 用法

在仓库根目录执行一行 PowerShell 命令：

    python -B intake/book_intake.py --input "D:\Books\待分析书籍" --book-id "example-book" --title "待分析书籍" --language zh --rights UNKNOWN --output "$env:TEMP\tradebook-g0.private.json"

不提供 --output 时，只在终端输出 JSON（不写文件）。输出路径须位于输入资料目录之外，且父目录已存在。使用空白资料夹会直接报错，而不是生成“已扫描成功”的假收据。

可选字段：--author、--edition。--language 取 zh/en/mixed/other/unknown；--rights 为**用户声明**，取 UNKNOWN/OWNED_OR_LICENSED/PUBLIC_DOMAIN/PERMISSION_REQUIRED。即使用户声明许可，工具也**不会**自动公开原文或替用户确认版权资格。

支持文件：PDF、EPUB、DOCX、UTF-8 的 TXT/MD；不支持的其他格式在 ignored_files 中提示，**不会静默当作已阅读**。每个支持的文件记录相对路径、格式、字节数、SHA-256、容器签名初检、重复内容、OCR/页码/图证的未执行状态。重复只报告，**绝不删除原文件**。为避免误读 Windows 文件夹与越界源文件，拒绝符号链接和大小写路径冲突。

工具不会解析 PDF 全文、推断物理页码、OCR、理解论点、验证作者身份、比较版本或下载外部资源。PDF_HEADER_ONLY_NOT_FULLY_PARSED 表示仅检查了 PDF 头标识，**不是完整 PDF 结构已验真**；EPUB/DOCX 也只做容器初检。文件指纹只能标识用户本地文件，不能证明版权、原作者归属或发表时间。

## G0 审核之后才有后续阶段

1. 查看清单、确认书名/作者/版次/来源路径及文件复本，审查可发布权限；版本不明时保留 UNKNOWN。
2. 只在明确获准后，登记这本书的规范来源与 Collection；不得将未经授权的整本 PDF 提交公开 GitHub。
3. 对**真实书籍内容**建立目录、物理页、章节覆盖和图像审核计划；然后按 G1 五分钟全书快览、G2 CORE+SPARK 扫读、G3 深度导读推进。不能把 G0 预检称为已经完成了阅读或 AI 分析。

## 离线测试

    python -B -m unittest discover -s intake/tests -p "test_*.py" -v

首版以虚构测试样本覆盖容器、SHA/去重、编码、无源输入、格式、符号链接、大小写冲突、输出边界等场景。已通过单独的 [G0跨平台 GitHub Actions](../.github/workflows/g0-source-intake.yml)纳入自动化校验：Windows/Linux 与 Python 3.11/3.12 四个组合，执行命令行帮助检查和离线单测。该CI只以程序自动生成的虚构格式/文本作为输入，不包含真实交易书籍；是否通过以该PR准确head SHA的运行结果为准。它不替代《缠论》精确镜像和其他47项专题检查，下一阶段才是实际第二本书接入。


## 当前《缠论》研究：知乎凯翔回答覆盖与增量对账

这是**独立于未来新书G0资料扫描**的特定来源质量门，复用同一个仓库的`intake/`离线工具区；不改变本项目未来逐书研究的目标。2026-11-11 用户上传的 `answers(1).md` **仅有100个回答块，文件头也声称100**，对应目前的 A001—A100，并不构成“凯翔全部答复”认证。用户指出原始收藏/预期应为200多条，但尚未得到可独立重读的更长版本。

后续有200+条完整MD文件时，在仓库根目录运行**一行 PowerShell**（自行替换新文件路径）：

    python -B intake/zhihu_answer_reconcile.py --base-md "other_views/chanlun/speaker-unknown-001/answers-2026-11-11.md" --base-index "other_views/chanlun/speaker-unknown-001/answers-index.json" --incoming-md "D:\Downloads\answers-full.md" --speaker-token "tsk-47-98" --min-incoming-answers 200 --output "$env:TEMP\kaixiang-coverage-review.private.json"

也可省略 `--output`，只在终端返回 JSON（不写文件）。路径默认只能是**已经存在的**本地普通文件，不随 symlink 读取外部文件；文件必须是 UTF-8、有知乎回答 URL、发布时间、当前用户主页标识、声明总条数，实际解析数量必须一致。测试支持 215 条乃至更多项，**没有旧版的100条程序上限**。若用户明确要求至少200条而传入100条，**直接拒绝**，不会继续以100条生成“完整覆盖”的研究结果。

结果仅包括来源文件SHA、声明/解析数量、现有A编号保留、新增A编号建议、旧回答正文或题目发生变化的复核数量、以及新版本缺少哪些旧ID；不输出回答原文、不会覆盖旧MD、不会实际导入或修改任何研究结论、不会访问知乎或抓取评论。100条与200多条版本不同不等于作者删除或改过帖子：可能是导出范围、分页、页面可见性或不同时刻所致，需保留两个版本。旧A001—A100绝不重新编号；新增先按原回答ID分配A101+建议号，**来源与原作者身份仍待独立确认**。即使新的导出包含200+条，也只能证明该次文件自身达到200+，**不能证明已完整抓取某知乎用户所有历史回答或评论**。

**数据质量门的重要性**：`answers-index.json` 中的 `source_sha256` 必须与既有规范原文的字节SHA精确相符，A001—A100回答ID、URL与规范原文必须逐项对应；任一不一致拒绝做映射。历史答案修改与新答案添加分开列出，不自动覆盖研究者过去的引文。第三人引用、评论区、回答后续编辑和账号平台身份需要另外的证据，不能从回答个数推断。

相关合成离线测试：`python -B -m unittest discover -s intake/tests -p "test_zhihu_answer_reconcile.py" -v`。纳入现有 G0 `intake/tests` 跨平台CI扫描；它只是来源覆盖质检，并非新书解析或缠论理论突破。


## 凯翔评论区资料：离线证据接收和增量复核（独立、只读）

新增 [zhihu_comment_reconcile.py](zhihu_comment_reconcile.py)，用于将未来**用户合法取得且具备独立评论 ID 的结构化 JSON**与已固定的 A001—A100 回答索引关联。它不联网、不抓取知乎、不从回答正文伪造评论、不独立认证账号身份、不修改研究原文，也不把评论正文输出到报告。当前未提供独立评论实体导出；A094、A058、A084 仍为待获取，**不能从本轮的缺失判断平台没有评论**。

输入必须是下述 UTF-8 JSON 交换格式；这**不是**任意爬虫（包括 ZHVision）的原生格式。若取得其他格式，需要先在本地明确映射字段并复核来源/评论层级，不得凭“正文提到评论”补造 ID。以下仅为**虚构格式示例，并非凯翔真实评论**：

~~~json
{
  "schema": "tradebooks-zhihu-comments-export-v1",
  "profile_url": "https://www.zhihu.com/people/tsk-47-98",
  "captured_at": "2026-11-13T18:00:00+08:00",
  "comments": [
    {
      "comment_id": "123456789",
      "answer_url": "https://www.zhihu.com/question/305010512/answer/3478727755",
      "parent_comment_id": null,
      "author_label": "虚构示例用户",
      "reported_author_role": "UNKNOWN",
      "published_at": "2024-05-23T10:00:00+08:00",
      "content": "格式示例，非任何真实用户原话"
    }
  ]
}
~~~

在仓库根目录使用**一行 PowerShell**；仅输出来源哈希、A 编号、评论/父评论 ID、作者标签及正文哈希、待审状态，不把正文写到仓库：

    python -B intake/zhihu_comment_reconcile.py --answers-md "other_views/chanlun/speaker-unknown-001/answers-2026-11-11.md" --answers-index "other_views/chanlun/speaker-unknown-001/answers-index.json" --incoming-json "D:\Downloads\zhihu-comments.json" --speaker-token "tsk-47-98" --output "$env:TEMP\kaixiang-comments-review.private.json"

省略 --output 则只在终端输出 JSON；提供路径时只能创建此前不存在的 .private.json，禁止覆盖原输入。comment_id 必须保留导出中的原数字 ID 字符串，parent_comment_id 指向真实父评论 ID 或为 null。时间须有时区（如 +08:00）；published_at 缺失可以保留 null，但该条被阻止分配候选 C 编号直到补齐。若父评论未导出或未在旧台账中、对应回答不在现有 A 索引中，同样隔离复核；重复 ID、跨回答父子关系、循环回复、错误答帖 URL、时间晚于导出采集时点会拒绝。

reported_author_role 只能是 ANSWER_AUTHOR、OTHER 或 UNKNOWN，表示**文件中的声称角色，不等于平台验证作者身份**。报告按 A094、A058、A084 优先显示本次导出的证据覆盖；EXPORTED_UNVERIFIED_NOT_RESEARCH_APPROVED 只表示本次文件有条目，NOT_OBSERVED_IN_THIS_EXPORT 只表示这次文件没观察到条目，均不证明整个知乎历史。

如果日后经**人工审核**已有 C 编号台账，可传 --existing-ledger "D:\...\approved-comments.json"。其 schema 为 tradebooks-zhihu-comment-ledger-v1、speaker_token 与输入一致，comments 为批准的记录数组，每条包含 stable_id（如 C001）、comment_id、answer_ref、parent_comment_id、published_at、reported_author_role、content_sha256、author_label_sha256。工具将保留旧 C 编号，识别同 ID 文本变化、仅部分导出的缺失与新增候选；没有已批准台账时，C001+ 仅是**本次建议号，不是入库事实**。

离线验证：python -B -m unittest discover -s intake/tests -p "test_zhihu_comment_reconcile.py" -v 。现有 G0 Actions 自动在 Windows/Linux、Python 3.11/3.12 执行 intake/tests；其中一项只读集成测试会用仓库真实 A001—A100 索引进行空评论导出核对，不会暴露答帖正文。
