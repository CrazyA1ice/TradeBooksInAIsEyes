# 缠论 Phase 2 / 实验室 v1：不可前视的前缀回放与有版本的笔必要条件

> **已实现：** 原始1分钟等K线的封闭/可知时间门，单股票同周期同版本数据完整性门，固定方向有序包含合并，已完成三K线局部分型候选，笔旧版/后发新版局部必要条件审计，合成前缀回放测试。
>
> **未实现：** 方向自动判定、完整笔唯一性解析、线段、特征序列、中枢、多级别递归、真实股票历史回测、交易下单、真实成交成本收益、原书图像精确价位审查。所有输出属于研究候选而非买卖信号。

## 输入合同（单标的单频率，严格限定本期为人工合成数据）

`schemas/chanlun_synthetic_market_event_v1.schema.json` 和 `experiments/fixtures/chanlun_prefix_synthetic_v1.json` 为模型与样例。每根bar必须带：

- `start_at / end_at`：价格K线覆盖区间，必须给ISO8601显式时区。
- `known_at`：该bar最终状态确实可以得知的时刻。完整bar要求`known_at >= end_at`；正在形成的bar不参与当前前缀。
- `is_closed`：严格布尔值，未知或未闭合的bar**不能**用于判断。
- `seq/key/symbol/timeframe/source_revision_sha256`：完整顺序、唯一来源、相同标的和供数版本；间断、时间重叠、倒序可知时间和换源都失败关闭。
- `open/high/low/close/volume`：**精确十进制字符串**，不用浮点输入，必须满足OHLCV边界和有限数值。

回放时仅使用从开头开始的**连续已完成、且结束时间及可知时间不晚于当前as-of**的前缀；中间如果有未完成/延后可知的数据，不允许跳过去读取后面bar。若仅在输入末尾追加未来数据，过去as-of输出必须逐字相同。前缀摘要只用当时可见bar计算，不用包含未来的完整归档哈希。

## 有方向包含与分型候选

- `--direction UP|DOWN`是调用者**事前固定的研究情景**；v1不会通过未来的走势转折推断方向。真正变向的实时判定仍待实现。
- 仅将**相邻**有包含的bar用对应max或min规则合并；保留每根源bar的key和序号。不能由此推出唯一最优的完整K线标准化算法。
- 局部顶/底分型需要三个**完全可用的标准化bar**严格比较高低点；相等时不强制确定。当前已见三个bar只能形成可修订的`PREFIX_LOCAL_REVISABLE`候选，后续包含变化可以让候选失效，不能将确认时间追溯到中心bar，也不能称其为稳定的完成笔。

## 笔版本与证据门

`catalog/chanlun_rule_history_v1.json`中选定单独的明确原作者笔规则候选：`pen_062_original`/`pen_077_exposition`或`pen_081_later_dated_post`。其中第81课另篇显示署时为2007-09-18 22:53:57。使用该规则必须另行提供**独立时间证明（本轮样例只能用synthetic_fixture）**、资料证明标识与可知时间；不允许仅凭书内显示日期推导“历史上可交易者当时已经知晓”。

源时间未知的第62课p.295后附“新笔定义”候选被禁止自动启用，编者批注也不能伪装成作者规则。源文展示时刻与已有证明时刻分别记录；研究示例暂以中国+08:00比较显示时间下界，**这不构成真实网页上线时间的独立证明**。

- 旧版的局部必要门：不能共享源K线，分型之间应存在至少一个未被两分型使用的**合并后**bar，以及合乎顶底价格顺序。
- 后发候选版局部门：不能共享源K线，要求明确可识别原始极值中心，两极值中心间至少3根原始K线。若分型中心来自多个原始bar而极值来源不唯一，输出`UNKNOWN_RAW_EXTREMUM_PROVENANCE`，不猜测或自动判合格。
- 一律只是`LOCAL_ELIGIBLE_NECESSARY_ONLY`、`REJECT_...`或`PENDING/UNKNOWN`：**绝不输出实际买卖信号、利润、完整笔或中枢。**

## 使用方式（仓库根目录，命令均为单行）

无笔规则，只核查截至某时的局部结构：

`python -B tools/chanlun_event_lab_v1.py --asof "2007-09-20T01:35:01+00:00" --direction UP`

声明第77课旧规则已经通过**人工合成时间**单独可知：

`python -B tools/chanlun_event_lab_v1.py --asof "2007-09-20T02:00:00+00:00" --direction UP --rule pen_077_exposition --attested-known-at "2007-09-19T09:00:00+08:00" --proof-ref synthetic-publication-availability`

切换第81课后发新版本：

`python -B tools/chanlun_event_lab_v1.py --asof "2007-09-20T02:00:00+00:00" --direction UP --rule pen_081_later_dated_post --attested-known-at "2007-09-19T09:00:00+08:00" --proof-ref synthetic-publication-availability`

专项测试：

`python -B -m unittest discover -s tests -p "test_chanlun_event_lab_v1.py" -v`

数据只读，标准库执行，**不会启动股票源数据库、改写原书或发送订单**。若将来只读接入真实行情，需要先建立真正可核验的供数版本、可得时间、复权与交易日历、停牌/非交易时段、增量更正和撤回事件合同，**不能直接把合成数据`kind`改成real_market绕过门槛**。

## 下一迭代明确门槛

1. 用真实原书配图建立小规模可复核的高清几何金标准，而不是要求用户逐页OCR。
2. 实现有版本标识的变向标准化、分型候选变更事件和笔候选配对；需要不可变版本和`confirmed_at`而非事后改写过去信号。
3. 再建立线段、特征序列、中枢和多级别走势的独立必要条件门，先在合成反例集审计，再只读接入真实A股数据。
4. 对每个真实行情实验独立记录`market_asof`、`bar_known_at`、`rule_known_at`、`structural_confirmed_at`和（如果真的能成交）`filled_at`；**没有实证前不可宣称策略获利**。
