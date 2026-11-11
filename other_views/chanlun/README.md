# 《缠论》其他人的观点档案（OtherVoices）

> **读者入口：** `ChanlunCollection/OtherVoices/`。每人一个子文件夹，原话、来源、AI分析、修订记录放在同一目录。规范编辑源为仓库根目录 `other_views/chanlun/`，由精确 SHA 镜像机制同步，不能单独改镜像。

## 人物索引

| 人物 | 原话资格 | 同目录资料 |
|---|---|---|
| [凯翔｜知乎 tsk-47-98（保留ID speaker-unknown-001）](speaker-unknown-001/README.md) | `USER_SUPPLIED_VERBATIM`：100答原文+100链接，31条显式缠论；平台在线未核、评论未包含 | [完整100答](speaker-unknown-001/answers-2026-11-11.md) / [100条索引](speaker-unknown-001/answers-index.json) / [精确短引](speaker-unknown-001/quotes.md) / [深度分析](speaker-unknown-001/analysis.md) / [评论缺失说明](speaker-unknown-001/comments.md) / [来源](speaker-unknown-001/sources.json) / [修订](speaker-unknown-001/updates.md) |

## 每位人物的固定五文件

`README.md` 为身份与入口，`quotes.md` 保存真正可追溯的原始发言，`analysis.md` 专门保存逐条研究与反驳，`sources.json` 保存 URL、时间、作者身份和证据等级，`updates.md` 记录全部修订；未来同一人发多段话仍归同一文件夹，逐段编号 Q001、Q002 等。新人物使用独立文件夹，不把不同人的意见混到一起。

**本次来源更新**：用户于2026-11-11上传原文件`answers(1).md`，100条原答及其100个URL在同一人物目录按原字节保存（SHA256 3fb9f325…）。已识别其在上传资料中的公众账号名“凯翔”，但网站页面无法独立核查；没有独立评论区记录绝不表示知乎没有评论；A007引用的是另一个人。

**来源资格**：`VERBATIM_VERIFIED`（原文和上下文均可核）、`TRANSCRIPTION_UNVERIFIED`（有转录但未验原始字节）、`PARAPHRASE_ONLY`（只有研究转述）、`MISSING_VERBATIM`（原文缺失）。原话与AI解释绝不可互换；未知作者只能用匿名稳定编号，不能猜姓名。

**版权与隐私**：此仓库公开。不能未经授权上传私人消息、个人敏感信息或长篇受版权保护的转载；保留授权短引、出处链接和定位信息，完整材料在获授权位置保存。找不到原文就如实标记，不凭摘要补造原句。

**操作流程**：新增规范源 `other_views/chanlun/<speaker-id>/` → 同步 `python -B tools/book_collection.py --book chanlun --sync` → 校验 `--check` → 同步更新通用/单书工作流、日志、状态和版本 → CI。后续用户可直接让AI针对某位人物继续研究，无须自行逐页校验OCR。
