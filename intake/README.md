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
