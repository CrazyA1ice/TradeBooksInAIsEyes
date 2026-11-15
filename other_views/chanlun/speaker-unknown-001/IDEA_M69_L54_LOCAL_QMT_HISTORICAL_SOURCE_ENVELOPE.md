# M69｜600151 历史1分钟真实来源的本机入场门：QMT本地缓存 → M56原样逐行验收 → 时间网格 → 私有证据摘要

> 2026-11-15。本轮把M57已经存在的**单股票/单候选日只读QMT缓存调用**接到M56已有CSV逐行校验，第一次允许真正QMT本机frame在内存生成相同规范CSV，再以它做时间网格诊断和SHA256来源标记；非首次发现L54图、非M56首次提出候选年份，也不假装已经读取用户电脑。仓库不储存任何付费行情。原5卷/108课/100条知乎回答及I82/C46/v4.101.0不动，F01/A016/A087/OB38/OB99/Φ20继续未解，真实市场E1–E4 `NOT_RUN`。

## 1. 现有实证真正的阻塞点，不再用合成MACD去冒充突破

- [第54课图源M56](../../../catalog/chanlun_l54_600151_historical_minute_admission_m56.json)已从后期书籍PDF核对图题“航天机电(1分钟)”、图内**05月18日无年份**、正文2007-05-24才发表；`600151.SH / 2007-05-18`是优先验证假设、**不是日期确证**。图中峰值18.59、右18.03、正文g0=18.50都不能凭日内价区命中就认证原图身份。
- [M57](../../../tools/probe_chanlun_l54_qmt_local_1m_m57.py)已冻结原生`xtdata.get_market_data_ex`请求：单股`600151.SH`、period=`1m`、日期窗口2007-05-18、`dividend_type=none`, `fill_data=False`, `count=-1`；旧探针只返回合成数据经测试的统计结构，本地真实数据未运行。本轮继续**只有本机已有缓存读取**，不自动下载历史、不订阅、不连接交易接口。
- [官方XtData文档](https://knowledge.thinktrader.net/docs/dictionary/stock.html)支持1m与请求历史时窗，但不保证用户账号、本地缓存或具体2007年600151分钟数据存在。东方财富分钟常见接口近5个交易日限制，不能当2007真实供应方。
- 用户此前Parquet库已知历史最早2011，分钟更晚；**不借它冒充2007数据**。也不擅自读取或改变其Windows本地文件。
- 关键缺口：旧M56 `inspect_candidate_csv(path,...)`只能从路径读，M57本机frame从未进入逐行入口；而一个单纯`rows=240`既不验证时标语义，更不能证明行情真伪或当时逐笔路径。

## 2. M69新工具做了什么

[只读本地入场工具](../../../tools/admit_chanlun_l54_local_qmt_m69.py)支持三种确定模式：
- `preflight`：核对与M57相同的请求合同，不导入xtquant、不读取用户行情、不写文件；
- `qmt-local`：在用户**自己的Windows QMT Python环境**中只调用一次已冻结的原生`get_market_data_ex`；若无数据，返回本地缓存为空（**不能证明供应商无2007历史**）；若有数据，读取DataFrame列、转换为内存UTF-8规范CSV，再调用M56新的纯内存`inspect_candidate_csv_bytes(...)`（原M56路径函数完全兼容不变），检查时戳、OHLCVA、单日、单股候选。
- `csv`：如用户已从合法的数据来源取得规范`time,open,high,low,close,volume[,amount]`CSV（UTF-8，上海时区，裸价/复权声明另存），可不经过QMT直接执行既有M56逐行检查；该模式支持明确的`2006-05-18`备选年份对照，**不会**因数据能通过就宣称两年份谁是图例真值。

**独立时间规范**：运行时必须显式声明`--timestamp-convention bar_start`或`bar_end`。工具只把两种候选网格严格列出：起始标记`09:30..11:29`、`13:00..14:59`；结束标记`09:31..11:30`、`13:01..15:00`，理论均240槽。如果本地数据索引与声明时标不符，返回`TIMESTAMP_CONVENTION_CONFLICT_OR_SPECIAL_PROVIDER_BAR`，如果有缺时则为`PARTIAL_1M_GRID_OR_VALID_NONTRADING`；**缺时可能停牌或供应商口径，不可直接定性数据坏/行情历史不存在**。即便240/240也仅为`FULL_240_DECLARED_GRID_ONLY`，不是供应商验签或当时完整行情的严格证明。

**可复核私有摘要**：默认不写文件；只有显式给`--private-evidence-dir`（必须位于Git仓库**外**）才保存原生QMT转出的CSV和同源SHA-256/诊断报告。已有同名私有文件不覆盖，既不自动提交GitHub，也不保存账号/token。CSV模式仅只读用户已存在原文件不复制。所有输出明确标`chart_identity_authenticated=false`、`historical_bar_close_first_known_at=UNKNOWN`、`intraminute_high_low_order_known=false`、`F01=OPEN`与`NOT_RUN`。

## 3. M68与M69的界面：不能凭事后读到历史分钟线推导2007年“当下已完成”

M68已对**人工逐笔**实现完整K线闭合证书先到才能认定L17单位K线共同价格区，L35逐笔三同价独立于bar收盘；M69只是将**本地候选真实一分钟OHLCVA的存在与文件摘要**规范化，并不凭2007年历史文件自动产生当时供应商`bar_close_first_known_at`，或将1分钟OHLC倒推出任何真实tick顺序。因此即使拿到2007-05-18的完整240行，也只是升级“候选行情文件已观测且形态合规”，**不升级**`作者原图日期认证`、`真实1分钟以下线段完成`、`MACD双R实盘验证`、`严格F01根层PAN_EXIT`或收益率。

可验证的下一步，是让用户在本机执行一次只读QMT采样，将**文本状态摘要**贴回研究记录；如有候选数据并获得用户许可，再考虑私人哈希比对供应商/独立交易所与第54课图峰值/端点。仓库CI只能跑假的QMT frame和CSV，不可能连接用户电脑。

## 4. 单行 Windows PowerShell 命令

在已经安装QMT或xtquant的Python环境中：

```powershell
Set-Location -LiteralPath "D:\ChatGPT\TradeBooksInAIsEyes"; git pull --ff-only origin main; python -B tools/admit_chanlun_l54_local_qmt_m69.py --mode qmt-local --timestamp-convention bar_start
```

如果QMT本地实际采用结束时刻索引，应把末尾`bar_start`改`bar_end`再核验；**这里不是替供应商预先认定实际约定**。需要保留证据时，另加`--private-evidence-dir "D:\stock\ChanlunPrivateEvidence"`，工具只向该Git仓库外目录创建文件。若现实中QMT无2007数据，不要调用任何自动下载或以空缓存宣称确无市场历史。

## 5. 源头、重复验证与未决

新[结构化来源/网格合同](../../../catalog/chanlun_l54_local_qmt_market_envelope_m69.json)与[21项单元测试](../../../tests/test_chanlun_l54_local_qmt_m69.py)复用旧M56 29项、M57 28项、M68 13项及其CI；真实历史行情与付费数据绝不进入Git repo，合成frame的结果不构成供应商验真。2007年QMT本地数据能否提供、当年该股是否存在该分钟时间网格、图年份/真实交易量/复权一致性、子分钟盘背/段完成、OB38/OB99/Φ20/F01、A016/A087均保持未决。此轮的**新成果是单次本机真实数据查询的完整来源接入接口**，不是市场分析已运行。
