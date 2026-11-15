# M72｜第一次外部历史1分钟来源入口：RQData优先、ARData备选，按600151/单日限额

**2026-11-15。** 第54课作者图标题“航天机电(1分钟)”，仅出现“05月18日”未标年份。M56/M57/M69/M70提供来源证验、单股单日只读QMT和TDX时标对照。用户本机实测记录显示：QMT客户端正常连接；2006-05-18不复权日线低18.01高19.07；2007-05-18不复权日线低17.61高18.59；2007-05-18分钟线从QMT本地读取为零，明确发起一次该日1m历史下载后再读仍为零；本地TDX仅见2026年的600151分钟记录而无2006/2007。这些**来自用户提供的本机命令文本**，不是本仓库独立拉取行情。2007年日高与图标18.59相同是提高核对优先级的必要线索，但2006同日的价格区间也包含18.59、18.50及18.03，无法排除。

## 1. 为什么调整路线

[RQData官方研究文档](https://www.ricequant.com/doc/quant/research.html)声明A股分钟数据覆盖自2005年；[Python API get_price](https://www.ricequant.com/doc/rqdata/python/generic-api.html)支持单股票、日期、frequency=1m、adjust_type=none、skip_suspended=True；[初始化官方说明](https://www.ricequant.com/doc/rqdata/python/manual.html)用pip install rqdatac + rqdatac.init()。官方只说明产品一般覆盖范围，**未证明用户账号有权限且具体600151于2007-05-18真实可查**。[ARData官方API](https://api.followquant.cn/docs.html)亦宣称2005起分钟数据，支持单股1m、无fq参数视为不复权；其[现行定价](https://api.followquant.cn/pricing.html)将全历史分钟数据列于专业版，实际接口可能计Credit、有账户权限限制。不得以“理论自2005”冒充收到2007年样本。

## 2. 新软件行为

[CLI](../../../tools/probe_chanlun_l54_external_minute_m72.py)四种模式：

- preflight：完全离线复核固定2006/2007两候选日期、源接口参数、M69与前F01未解约束，不导入第三方API、不查询网络。
- access-check：完全离线查看本机rqdatac模块是否安装、环境变量ARDATA_API_KEY是否存在，**只打印布尔值，不读出/显示密钥，不发起API查询**。
- rqdata-once：需要用户**显式**传此模式、日期和bar时间标签；调用自己已安装配置的rqdatac.init()，只对600151.XSHG当天执行**一次**get_price(1m, adjust_type=none, skip_suspended=True)，DataFrame必须满足同一股票、同一交易日、严格时间递增、最多300行；生成内存CSV再走M56已有逐行OHLCVA验收及M69分钟格网检查；缺包返回RQDATAC_NOT_INSTALLED，认证/授权/网络错返回已脱敏错误类型。用户必须自行有合法RQData账号。
- ardata-once：用户明确提供本机环境变量ARDATA_API_KEY后才能查询；固定https://api.followquant.cn/api/v1的HTTPS、拒绝重定向、2MB大小上限、20秒请求超时；仅一次登录换取JWT和一次单股单日get_price(1m)查询，fq参数留空/不传表示不复权。未配置key**零请求**，收到错误脱敏输出，不打印token/key，不保存行情。

所有真正源数据都**只存在于进程内存**，传入原[M56](../../../tools/audit_chanlun_l54_2007_minute_candidate_m56.py)的严格CSV验收和[M69](../../../tools/admit_chanlun_l54_local_qmt_m69.py)时间语义检查；控制台仅显示实际行数、时间槽缺失、原图价格锚点相等计数与规范CSV SHA256（**不是供货商原始文件认证**），不打印/上传原始付费OHLCV。一日若有241行，不会偷偷丢首笔让结果看似240；如果时间标签与所选约定不符，会原样报告额外/缺失分钟，而非自动调整。实体数据还需确认复权、当年交易时段与来源真实可信性。

## 3. 单行本地操作指令

先用已有Python 3.11检查，不安装也不连接外部服务：

\`\`\`powershell
Set-Location -LiteralPath "D:\ChatGPT\TradeBooksInAIsEyes"; & "D:\software\Python311\python.exe" -B tools/probe_chanlun_l54_external_minute_m72.py --mode access-check
\`\`\`

如返回rqdatac_installed=true，且用户拥有**已初始化配置的合法RQData账号及授权**，明确同意使用该账号发起可能计费的单日请求之后，再运行：

\`\`\`powershell
Set-Location -LiteralPath "D:\ChatGPT\TradeBooksInAIsEyes"; & "D:\software\Python311\python.exe" -B tools/probe_chanlun_l54_external_minute_m72.py --mode rqdata-once --candidate-date 2007-05-18 --timestamp-convention bar_end
\`\`\`

\`bar_end\`参考RQData官方09:31起的示例，仍是显式待核实标签。若RQData权限不足，可申请试用/购买前先向官方要求600151 2007-05-18一日的分钟可查询性和样本条数确认，**不要贸然订购全市场历史行情**。

如有合法ARData账户且其专业版确有分钟权限，可以在本机**私下**设置ARDATA_API_KEY环境变量（**绝不在聊天、Git或截图公开密钥**），运行：

\`\`\`powershell
Set-Location -LiteralPath "D:\ChatGPT\TradeBooksInAIsEyes"; & "D:\software\Python311\python.exe" -B tools/probe_chanlun_l54_external_minute_m72.py --mode ardata-once --candidate-date 2007-05-18 --timestamp-convention bar_end
\`\`\`

需要2006年的备选对照时只替换--candidate-date值，再发起**独立的一日请求**，不要借2007日线峰值去排除2006。所有一次实际API调用都由用户主动运行，可能计费；默认离线检查不会有外部请求。

## 4. 证据结论不能越界

读取到2007年240条只是取得“该供应商在此时此账户下返回单股日级1分钟样本”的来源证据，并**不**证明第54课图2007年、与2006对照后的原图逐根K线完全一致、供货商数据等于原始2007当时可得版本、tick高低先后、L17/L35/L60单位不同源谓词可混合、盘整完成根证书F01、OB38/OB99/Φ20/A016/A087已解、E1—E4真实历史回测已运行或产生收益。下一步只能基于真实供应商结果进一步做图像与结构对应、价格与时间列校准。没有账号/权限的机器应准确停在ACCESS_NOT_CONFIGURED，而不是再部署一个“假已取得”数据源。

原始五卷PDF、108课、100答、I82/C46/v4.101.0及镜像书籍集合保持不变。CI所有Fake RQ/ARData回复仅证明代码边界，没有从用户电脑拉取任何外部分钟样本。
