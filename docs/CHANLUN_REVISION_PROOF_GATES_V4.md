# 缠论研究 V4：市场更正双时间轴与完整笔证据资格审查

> **当前可交付**：只读人工合成K线的更正日志、每个as-of所能看到的来源快照、必要条件笔候选的证据义务明细。**不能据此输出任何真实“完整笔认证”或将候选线段元素升格为STRICT。** 目前没有真实市场访问、交易或收益验证。

## 为什么不能直接将V3候选宣布成完整笔

V3已经实现不依赖未来K线的局部笔候选及事件撤回，但第77/81课所列局部必要门不等于全部笔定义与唯一分解算法。第102课尤其要求在宣布唯一分解前完整描述条件、等值裁决及不同合法候选的消歧证明。真实行情文件后来更正某根旧K线时，用更正值去重新跑一遍2007年的走势，不能声称该更正价格在当年原始bar完成时就可见。

V4增加**更正事件接收时间**与**原始bar完成/可知时间**的显式区分，不直接修改V1–V3的代码或使用真实行情源。

## 两个时钟与不可变更正

- 原始行情数据固定`known_at`和`end_at`，原始记录均来自标为`synthetic_non_market_fixture`的人工合成数据。
- 每个更正事件包含`ordinal`、`bar_key`、`received_at`（更正真正进入数据源可用视图的时刻）、`expected_old_digest`、**完整五字段十进制字符串OHLCV**、`source_proof_kind`、`source_proof_ref`及内容计算的`event_id`。
- 更正日志以严格递增`received_at`追加；每条必须满足**旧记录SHA连续链**、完整OHLCV边界和已经存在的原始bar。禁止无变更更正，禁止更改K线key、时间、seq、symbol、timeframe，禁止混用跨来源文件或浮点。
- `asof_restatement`仅将`received_at <= market_asof`的更正应用到副本；之后新增的有效更正不能改变以前as-of的快照/候选ID。每个有效视图有独立的`effective_source_revision_sha256`、`snapshot_sha256`与其适用的更正事件ID。
- 更正后的OHLCV虽可在**事后修订视图**重算完整过去价格序列，但旧bar的原`known_at`没有变成更正价格真实可知时间。因此V4**不对外发布更正视图下V3重算出的历史事件日志**；只输出当前版本的**暂定笔候选**并明确`historic_replay_events_may_not_be_claimed_live=True`。历史真实当时的已知信号需未来独立的按更正接收时间逐事件回放，而不是用修订后数据重写过去。

## 完整笔证据资格：逐项列明但一律不越过闸门

`pen_proof_obligations(snapshot,candidate_id,proof_claims)`为当前活动候选列出6组待审证据：

1. `raw_extreme`：原始K线分型极值来自哪根bar、包含合并后的唯一来源。
2. `direction_and_containment`：事前方向、包含运算、冲突/等值裁决及其适用版本。
3. `rule_sufficiency`：所选第77课或81课**完整规则**而非仅必要条件。
4. `unique_decomposition`：局部配对和全局分解的独立唯一性/歧义处理证据。
5. `actual_market_availability`：真实市场数据原始文件、供应商修订记录、接收时间及版别可知性。
6. `original_chart`：有页码和原文件指纹的图例对应、复原的真实几何/价格证据。

提交仅含`proof_ref`、`reviewed_at`的字符串**不构成独立认证**。即使调用方伪造填写所有6条“已经验证”，V4仍输出`BLOCKED_NOT_CERTIFIED`、`certifies_complete_pen=False`、`segment_role=UNDETERMINED`。没有已连接的独立行情字节核验者、正式完整笔规则证明、原图交叉审计机制之前，任何程序都不能用这些字段“自行宣布认证”。

同样，更正后旧候选ID如果不在新快照活动集合里，也会被显式标`NOT_ACTIVE_IN_THIS_SNAPSHOT`，防止把已过期候选的证据转移给新版本。

## 单行命令（仓库根目录）

模拟更正可知**之前**：

`python -B tools/chanlun_revision_proof_gates_v4.py --asof "2007-09-20T01:40:50+00:00"`

模拟更正可知**之后**：

`python -B tools/chanlun_revision_proof_gates_v4.py --asof "2007-09-20T01:41:01+00:00"`

切换后发笔规则：

`python -B tools/chanlun_revision_proof_gates_v4.py --asof "2007-09-20T02:00:00+00:00" --rule pen_081_later_dated_post`

专项测试：

`python -B -m unittest discover -s tests -p "test_chanlun_revision_proof_gates_v4.py" -v`

**绝不**修改`AStockDataTools`真实A股Parquet/H5、原始交易书PDF、原有知识图谱，也不发送订单。当前模拟价格、校验哈希及更正证据均由合成程序生成，不代表外部真实性。

## 接下来真正需要的进展

1. 用独立可信的`MarketDataSource`只读适配器检验真实市场文件字节、交易日历、时间区间、复权/停牌和供应商接收版本；在单独审计完成前不得开放真实行情输入。
2. 建立按更正接收时间的**增量正向观察日志**：让更正触发`source_version_update`并在该时刻撤销/更新候选，而不是重算历史观察事件。
3. 对旧/新完整笔版本做逐条源条款映射、冲突反例与极值来源审核，再把候选证书变成真正可验证的证明材料，而不是自报状态。
4. 笔认证后才允许向第67/71课正式`STRICT`特征序列传递；再实现线段、中枢、多级别走势。**当前零笔完成认证、零真实策略收益。**
