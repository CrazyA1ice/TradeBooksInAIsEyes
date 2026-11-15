# M70｜2006/2007两个“5月18日”候选：通达信本地LC1时间键 + QMT只读分钟来源交集

研究日期2026-11-15。研究对象第54课“航天机电(1分钟)”图，图中日期写“05月18日”而没有年份。2007-05-18是作者2007-05-24发文之前的优先候选，2006-05-18亦不可无独立证据排除。**截至本轮，用户Windows本机的任何真实TDX/QMT文件都没有在当前会话实际读取；所有测试使用明确人工构造的32字节格式记录或模拟QMT数据。**

## 真正的工程增量

M69已经让本地原生QMT查询结果经过M56时标/OHLCVA检查、240分钟网格分类及摘要。M70在TradeBooksInAIsEyes新增 tools/probe_chanlun_l54_tdx_qmt_clock_m70.py，直接复用 CrazyA1ice/AStockDataTools 仓库的 H5ParquetReconciler/tools/probe-tdx-native-readonly.py 所确认的常见TDX LC1头部布局：**每条32字节，前2字节为2004起压缩日期，随后2字节为自午夜起的分钟数**；可参阅 https://github.com/CrazyA1ice/AStockDataTools/blob/main/H5ParquetReconciler/tools/probe-tdx-native-readonly.py 。另有 https://github.com/donge/tdx_ext 作为独立格式描述。部分资料对价格/交易额单位并不一致，因此**本工具完全不解码TDX OHLCVA字段**，既不声称两供应商K线价格已一致，也不输出任何TDX原始单条分钟时刻。

1. preflight：核对合同、冻结2006/2007两个候选日及M69约束，不接触本机缓存。
2. tdx-local：仅只读用户显式路径（默认 D:\software\TDX\vipdoc\sh\minline\sh600151.lc1），扫描整个LC1文件，检查最大64MiB、32B对齐、压缩日期有效、所有记录分钟严格递增、读前/读后文件stat一致与SHA256；在内存只保留2006/2007年5月18日时间键。报告仅保留目标日条数、完整240 start或end、特殊241档等**元数据**及整文件摘要。
3. dual-local：如xtquant存在，继续用M69固化的单股单日原生get_market_data_ex只读QMT本地缓存，对内存CSV执行M56原有全部校验，**本工具不打印价位**；把TDX/QMT根据明确声明的bar_start/bar_end统一为该分钟的区间起点，报告两者共同、各自独有分钟数。若一源缺失，则输出 NOT_COMPARABLE，不根据本地缓存空认定供应商无历史。TDX完整240轮廓与声明标签冲突时明确报告冲突，不悄悄做相等认定。
4. 保护原始数据：没有任何下载、订阅、修改、覆盖、写文件或推送行情的路径；TDX内容SHA256只标识本地字节，**不是**供应商权威签名；QMT无行情时报告本地缓存未命中，不能证明2007年市场不存在。

## 现实使用的单行PowerShell

Set-Location -LiteralPath "D:\ChatGPT\TradeBooksInAIsEyes"; git pull --ff-only origin main; if($LASTEXITCODE -ne 0){throw "Git pull failed"}; python -B tools/probe_chanlun_l54_tdx_qmt_clock_m70.py --mode dual-local --tdx-file "D:\software\TDX\vipdoc\sh\minline\sh600151.lc1" --qmt-convention bar_start --tdx-convention bar_start

注意：两个bar_start参数只是**显式研究假设**而非已确认的数据商规范。若TDX 240条真实档识别为 TDX_1MIN_END_240，需将TDX参数改为 bar_end 重新验收；QMT标签另行从本地API源证确定。若xtquant不可导入，仍可分别使用 --mode tdx-local --tdx-convention bar_start 得到TDX双日期观察；不能因此宣称QMT历史不存在。

## 证据等级限制

TDX目标日存在分钟键：仅证明在本机该LC1文件中该日期和时钟位置有记录。两源交集240：最多说明某些K线**时间索引**在声明口径下一致，不代表原图年份认证，更不代表行情价格/成交量、复权、盘中高低顺序、可交易first-known、原作者M54双分解力度、合格三卖或F01根层盘整完成。实际只读观察须在用户本机进行，CI仅检查代码对假样本不越界。F01/OB38/OB99/Φ20与A016/A087继续OPEN；E1—E4真实市场NOT_RUN。原五卷PDF、108课和100条知乎答复及I82/C46/v4.101不修改。
