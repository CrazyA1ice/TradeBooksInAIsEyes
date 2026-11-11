# 《缠论》其他人的观点档案（OtherVoices）

> **读者入口：** `ChanlunCollection/OtherVoices/`。每人一个子文件夹，原话、来源、AI分析、修订记录放在同一目录。规范编辑源为仓库根目录 `other_views/chanlun/`，由精确 SHA 镜像机制同步，不能单独改镜像。

## 人物索引

| 人物 | 原话资格 | 同目录资料 |
|---|---|---|
| [speaker-unknown-001：此前用户分享的高手（姓名未认证）](speaker-unknown-001/README.md) | `MISSING_VERBATIM` | [原话](speaker-unknown-001/quotes.md) / [AI解读](speaker-unknown-001/analysis.md) / [来源](speaker-unknown-001/sources.json) / [修订](speaker-unknown-001/updates.md) |

## 每位人物的固定五文件

`README.md` 为身份与入口，`quotes.md` 保存真正可追溯的原始发言，`analysis.md` 专门保存逐条研究与反驳，`sources.json` 保存 URL、时间、作者身份和证据等级，`updates.md` 记录全部修订；未来同一人发多段话仍归同一文件夹，逐段编号 Q001、Q002 等。新人物使用独立文件夹，不把不同人的意见混到一起。

**来源资格**：`VERBATIM_VERIFIED`（原文和上下文均可核）、`TRANSCRIPTION_UNVERIFIED`（有转录但未验原始字节）、`PARAPHRASE_ONLY`（只有研究转述）、`MISSING_VERBATIM`（原文缺失）。原话与AI解释绝不可互换；未知作者只能用匿名稳定编号，不能猜姓名。

**版权与隐私**：此仓库公开。不能未经授权上传私人消息、个人敏感信息或长篇受版权保护的转载；保留授权短引、出处链接和定位信息，完整材料在获授权位置保存。找不到原文就如实标记，不凭摘要补造原句。

**操作流程**：新增规范源 `other_views/chanlun/<speaker-id>/` → 同步 `python -B tools/book_collection.py --book chanlun --sync` → 校验 `--check` → 同步更新通用/单书工作流、日志、状态和版本 → CI。后续用户可直接让AI针对某位人物继续研究，无须自行逐页校验OCR。
