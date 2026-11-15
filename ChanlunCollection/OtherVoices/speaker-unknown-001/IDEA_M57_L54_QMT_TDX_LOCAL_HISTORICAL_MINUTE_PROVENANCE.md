# M57｜第54课600151历史1m本地只读QMT探针与TDX复用

日期：2026-11-15。研究仍处于数据来源验证阶段：第54课图像标注05月18日却没有年份，2007-05-18只是候选；600151.SH的当日真实1分钟或Tick尚未从用户电脑取得。不得将本轮云端CI的模拟结果宣称为实际行情。I82/C46/v4.101不变，F01/OB38/OB99/A016/A087/Φ20仍OPEN，E1–E4 NOT_RUN。

## 1. 本轮新增的实际核对

迅投官方文档将两种Python接口分开：

- QMT内置策略ContextInfo.get_market_data_ex支持subscribe=False，仅查询已下载的本地历史行情；此外应显式设置period=1m、dividend_type=none、fill_data=False。
- 原生xtquant.xtdata.get_market_data_ex支持field_list、stock_list、period、start_time、end_time、count、dividend_type、fill_data，但**没有subscribe关键字**。将内置接口的subscribe=False照搬到原生XtData，会变成参数错误。原生探针不显式调用订阅或下载；然而不能仅凭这一点断言XtQuant客户端初始化时绝不通信。
- fill_data=True可能利用旧K线填充缺口，因此在2007年历史审计中必须关闭。复权前/后也不适合直接与2007图中的18.59、18.03比较，应先用none并注明该口径。

官方依据：[QMT行情函数](https://knowledge.thinktrader.net/docs/cloud/data_function.html)、[股票数据与原生XtData示例](https://dict.thinktrader.net/dictionary/stock.html)。

## 2. 第一优先路径：已有通达信本地文件，不重新写解析器

用户另一个仓库[CrazyA1ice/AStockDataTools](https://github.com/CrazyA1ice/AStockDataTools)已有
[H5ParquetReconciler/tools/probe-tdx-native-readonly.py](https://github.com/CrazyA1ice/AStockDataTools/blob/main/H5ParquetReconciler/tools/probe-tdx-native-readonly.py)，它支持本地原生 .day/.lc1/.lc5 的只读格式审计，提供source_first_date/source_last_date，已经具备离线测试。候选文件：
D:\software\TDX\vipdoc\sh\minline\sh600151.lc1
这是基于已知TDX目录的推导位置，**并非本轮实机看过、也不能保证该文件存在或覆盖2007年**。其他本地数据集从2011年起的覆盖也不能自动解释2007年。

## 3. 新只读执行器的严格权限

[原生本地探针](../../../tools/probe_chanlun_l54_qmt_local_1m_m57.py)具有两个模式：

1. preflight（默认）：不导入XtQuant、不请求历史、不访问本地报价，仅核验M56图证和M57合同，输出NOT_PROBED_ON_LOCAL_QMT。
2. xtdata-local：只有在具备XtQuant授权与可访问本机QMT环境时，调用**一次**原生get_market_data_ex，固定600151.SH、2007-05-18 09:30—15:00、1m、不复权、不填充，不调用下载或订阅、不读取其它股票、不写价量CSV。只输出记录条数、首末北京时间、价区和未认证证据状态。

通过本地原生QMT查询也只能得到LOCAL_QMT_CANDIDATE_BARS_FOUND_UNAUTHENTICATED，不能宣称图中日期已证、供应商所供数据真实或第54课任何1分钟以下走势类型已完成。空行只说明本地查询没有该日数据，不证明服务器无历史；导入失败和查询失败须有独立状态，绝不能伪装成空数据。

规范[JSON合同](../../../catalog/chanlun_l54_qmt_tdx_local_1m_m57.json)、[定向回归](../../../tests/test_probe_chanlun_l54_qmt_local_1m_m57.py)、[专属CI](../../../.github/workflows/chanlun-m57-qmt-local-readonly-gate.yml)保证不把官方两种接口混用，也阻止伪造2007市场结论。

## 4. 本轮能确证与不能确证的事实

完成：查明原生与内置API的确切差异，冻结历史分钟只读参数，识别已有AStockDataTools通达信解析器和候选600151 .lc1路径，编写可在真正连接本地QMT的环境运行的单日探针，并在云CI对假数据做非市场单元测试。

未完成：直接访问用户Windows QMT/TDX、下载或读取任何600151的2007年真实分钟或Tick、确认图像年份、给M55六个成员补上独立完成收据、证明Φ20。M56展示的相同OHLCVA对应不同分钟内高低顺序仍然是限制。即使1m真的取得，1m以下结构仍需更高粒度证据。

下一阶段不应继续虚构价格；必须在用户授权的本地QMT/TDX计算机上执行只读探针并获取实际摘要，然后再谈是否需要一次隔离的小范围历史下载。脚本可供后续本地使用，但**本次没有执行用户Windows上的命令**。

## M57合并前CI触发兜底

新增专属工作流文件在PR #186的首次GitHub调度中未出现在执行清单，不能把既有51项成功冒称新测试成功。因此M57的默认不连接QMT预检与28条假QMT帧回归**另行接入原本已经能触发的M56工作流**（.github/workflows/chanlun-m56-l54-historical-minute-gate.yml）。只有该旧工作流在最终PR head再次实际执行、并且全部新测试成功后，才允许合并；新M57独立工作流仍保留作为未来触发入口。本说明只涉及CI覆盖路径，不改变任何真实历史数据来源结论。
