# tools

未来放置文档解析、OCR 质量检查、证据索引、目录生成和研究审计工具。当前尚无可执行研究工具；先以实际《缠论》试读确定接口和质量指标。

## 已实现的只读研究工具

- `inspect_chanlun_sources.py`：五卷 PDF 页数/指纹/文本覆盖及课程标题初筛。
- `verify_chanlun_lesson_index.py`：108 课索引、实际源指纹与定位一致性检查。
- `read_chanlun_lesson_readonly.py`：按索引只读提取指定课程正文及页码；`--emit-text` 仅用于受控研究，**不要在公开运行日志中长期发布整章文字**。
- `ocr_chanlun_lesson1_page4.py`：首课第 4 页的专用 OCR 复现工具，识别结果必须审核，不能当作图表数据。
- `verify_chanlun_lesson1_analysis.py`：首课研究报告与证据档案的基本一致性审计。

图表精确识别和跨书研究仍未实现。

- `verify_chanlun_lessons002_005.py`：校验第 2–5 课的指纹、页码、未验证假说、图像不确定性及跨课关系。

- `survey_chanlun_lessons006_010.py`：原始 PDF 的只读页级盘点和限定片段；研究性一次运行，不公开完整书籍正文。
- `verify_chanlun_lessons006_010.py`：第 6–10 课证据/页码/源版本校验。
- `check_chanlun_lesson009_probability.py`：合成概率反例验证，**不是市场回测**。

- `survey_chanlun_lessons011_015.py`：第 11–15 课 PDF 只读页级结构核验和有界片段示例。
- `verify_chanlun_lessons011_015.py`：逐课源指纹、页码、编辑层次与研究主张审计。
- `audit_chanlun_lesson015_early_classification.py`：**早期**走势字面定义的相等边界与极值确认时间合成测试；不是市场回测。

- `survey_chanlun_lessons016_020.py`：第 16–20 课的只读页级扫描，仅输出有界原文线索和结构数据。
- `verify_chanlun_lessons016_020.py`：研究稿、证据页码、图像缺口和原始 PDF 指纹的自动验收。
- `audit_chanlun_lesson020_center_intervals.py`：三个已完成区间交集和第三买点位置条件的合成测试，不是历史市场回测。

- `survey_chanlun_lessons021_025.py`：跨第一/二卷双 SHA 只读来源扫描，报告卷内页码与图像缺口。
- `verify_chanlun_lessons021_025.py`：跨卷研究报告、证据定位、假说状态与 PDF 指纹校验。
- `audit_chanlun_lesson024_macd_partial_area.py`：仅用合成非负柱面积演示固定倍数预测的边界，不计算真实 MACD。

- `survey_chanlun_lessons026_030.py`：SHA 锁定的第二卷原文页级扫描与有界文本抽样。
- `verify_chanlun_lessons026_030.py`：第 26–30 课证据、来源指纹、编纂分界和未验证假说核验。
- `audit_chanlun_lesson027_nested_intervals.py`：仅对纯合成有限嵌套区间和信号确认时间作数学审计，不计算市场收益。

- `survey_chanlun_lessons031_035.py`：第二卷 SHA 固定的 113 页来源和有限原文片段只读核查。
- `verify_chanlun_lessons031_035.py`：卷号、页码、原文日期、图像缺口和概念依赖图验收。
- `audit_chanlun_lesson031_zero_cost.py`：本金回收与剩余持仓市值风险的合成账本，不是回测。
- `audit_chanlun_lesson035_recursion_and_associativity.py`：逐笔基例和拼接结合律边界检查，非完整走势分解程序。

- `survey_chanlun_lessons036_040.py`：第二卷p.305–377的SHA锁定来源与有限原文片段读取。
- `verify_chanlun_lessons036_040.py`：五课证据、图像缺口、编者修订和跨卷概念图依赖验收。
- `audit_chanlun_lesson039_branches.py`：明确标记第39课原文未覆盖的比较分支，不生成订单。
- `audit_chanlun_lesson040_inventory.py`：多级别仓位共享库存守恒的合成检查，无真实交易。
