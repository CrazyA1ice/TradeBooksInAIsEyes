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

- `survey_chanlun_lessons041_045.py`：跨第二、三卷的原始PDF SHA锁定和有限原文线索扫描。
- `verify_chanlun_lessons041_045.py`：跨卷来源、35条主张与概念图谱的完整性检查。
- `audit_chanlun_lesson044_logic.py`：第三类买卖点必要非充分条件的命题逻辑检查，无行情。
- `audit_chanlun_lesson045_wait_state.py`：无交易状态及待确认/成交失败的合成状态机，无真实订单。

- `survey_chanlun_lessons046_050.py`：第三卷p.49–116锁定SHA的页级扫描及作者有限原文线索读取。
- `verify_chanlun_lessons046_050.py`：新五课页码、来源、假说状态和跨卷概念图谱完整性审计。
- `audit_chanlun_lesson046_day_prefix.py`：八根日内K线标签的合成前视限制检查。
- `audit_chanlun_lesson049_objectives.py`：资金占用时间与期末财富排序可能不同的纯合成审计。
- `audit_chanlun_lesson050_resampling.py`：EMA先滤波或先重采样的数值差异示例。

- `survey_chanlun_lessons051_055.py`：第三卷p.117–205的SHA锁定页级来源与有限原文读取。
- `verify_chanlun_lessons051_055.py`：35条证据、卷号页码、2009后附来源及跨课概念图谱验收。
- `audit_chanlun_lesson053_editorial_provenance.py`：真实PDF第53课p.162与2009后附讨论的时间边界核验。
- `audit_chanlun_lesson054_connections.py`：两个同级别中枢间需有次级别连接段的合成必要条件检查。
- `audit_chanlun_lesson055_ledger.py`：分批建仓与卖出的现金股份守恒合成账本，无真实订单。

- `survey_chanlun_lessons056_060.py`：第三卷p.206–277SHA锁定、文本限定片段、五页PDF渲染（运行时不修改原PDF）。
- `verify_chanlun_lessons056_060.py`：72页来源、35条证据及实际缩略图审查范围验证。
- `audit_chanlun_056_058_timing.py`：虚构隔夜跳空与未完成背驰的前视确认/成交约束。
- `audit_chanlun_lesson059_precision.py`：原文3994.57和3994.21在截断、四舍五入及分位精度下的独立Decimal算术检查。

- `survey_chanlun_lessons061_065.py`：第三卷p.278–373 SHA锁定原PDF、限定文本片段和8页图像预览。
- `verify_chanlun_lessons061_065.py`：96页来源、6页原始PDF日期与规则文字核验、35条证据和概念图谱审计。
- `audit_chanlun_lessons062_065_containment.py`：依UP/DOWN定向K线包含归并和三bar分型确认的局部合成验证。
- `audit_chanlun_lesson064_tolerance.py`：0.5点近似关系不传递的Decimal精度测试。

- `survey_chanlun_lessons066_070.py`：原始第三/四卷 SHA锁定的百页跨卷文本来源和有限预览。
- `verify_chanlun_lessons066_070.py`：100页、34条主张、六处原PDF内容、跨卷扩展依赖审计。
- `audit_chanlun_lesson067_feature_gap.py`：特征序列分型局部双情形、缺口等待反向分型。
- `audit_chanlun_lesson068_boundary_policy.py`：事前冻结的价格三段边界，拒绝未来阈值和无效价格。
- `audit_chanlun_lessons069_070_events.py`：月线候选版本追加式日志与中枢未来分类事件。

- `survey_chanlun_lessons071_075.py`：第四卷p.71–142 SHA固定来源、有限原文与10页压缩PDF预览。
- `verify_chanlun_lessons071_075.py`：72页SHA、35条主张、8处原文定位、6页实际目视范围和兼容概念图谱审计。
- `audit_chanlun_lesson071_typed_membership.py`：特征序列同一严格成员资格和简化三笔确认的纯合成门。
- `audit_chanlun_lessons073_074_exposure.py`：剩余股票市值、合成宏观/行业影响和不可成交隔夜缺口。
- `audit_chanlun_lessons072_075_attribution.py`：区分原著、编注、独立日期解盘和未验证轶事的标签。

- `survey_chanlun_lessons076_080.py`：第四卷p.143–231 SHA锁定原文、部分文字和11页预览。
- `verify_chanlun_lessons076_080.py`：89页来源与35条证据、8处原书正文、7张实际目视图范围和兼容概念图谱。
- `audit_chanlun_lesson077_pen_boundary.py`：等高低分型、独立K线和局部笔必要条件。
- `audit_chanlun_lesson078_normalized_view.py`：不改写原始线段的高层派生标准化视图。
- `audit_chanlun_lessons079_080_dual_clock.py`：盘中分钟卖点与日收盘分型确认不混淆及机会成本。

- `survey_chanlun_lessons081_085.py`：第四卷p.232–345原SHA PDF文本和13页实际目视范围清点。
- `verify_chanlun_lessons081_085.py`：114页、35证据、9处源PDF文字、后发新笔规则时间和兼容扩展图谱核对。
- `audit_chanlun_lesson081_pen_rule_versions.py`：第77课旧规则和第81课9月18日新笔建议的局部前提差异。
- `audit_chanlun_lesson082_fractal_outcome.py`：分型后续是否成笔/中继之增量状态记录。
- `audit_chanlun_lessons083_084_recursion_noise.py`：有界噪声分类及两种f1/同一f2的合成反例。
- `audit_chanlun_lesson085_provenance_roles.py`：自述合法性与外部证据角色标签，不含交易行为。

- `survey_chanlun_lessons086_090.py`：第四至五卷跨卷123页SHA锁定的真实PDF页与14张缩略图。
- `verify_chanlun_lessons086_090.py`：五课35项来源主张、10处PDF内容定位、跨卷终止页、视觉范围和依赖图谱。
- `audit_chanlun_lesson086_crosslevel_context.py`：第三卖点受上层三态影响的描述性状态门。
- `audit_chanlun_lessons088_089_transition_center.py`：不可前视的旧→新结构过渡、Center与盘整不同类型。
- `audit_chanlun_lesson090_boll_asof.py`：仅利用已完成收盘bar计算BOLL轨道宽度收口，不自动确认中枢。
