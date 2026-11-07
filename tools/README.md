# tools

未来放置文档解析、OCR 质量检查、证据索引、目录生成和研究审计工具。当前尚无可执行研究工具；先以实际《缠论》试读确定接口和质量指标。

## 已实现的只读研究工具

- `inspect_chanlun_sources.py`：五卷 PDF 页数/指纹/文本覆盖及课程标题初筛。
- `verify_chanlun_lesson_index.py`：108 课索引、实际源指纹与定位一致性检查。
- `read_chanlun_lesson_readonly.py`：按索引只读提取指定课程正文及页码；`--emit-text` 仅用于受控研究，**不要在公开运行日志中长期发布整章文字**。
- `ocr_chanlun_lesson1_page4.py`：首课第 4 页的专用 OCR 复现工具，识别结果必须审核，不能当作图表数据。
- `verify_chanlun_lesson1_analysis.py`：首课研究报告与证据档案的基本一致性审计。

图表精确识别和跨书研究仍未实现。
