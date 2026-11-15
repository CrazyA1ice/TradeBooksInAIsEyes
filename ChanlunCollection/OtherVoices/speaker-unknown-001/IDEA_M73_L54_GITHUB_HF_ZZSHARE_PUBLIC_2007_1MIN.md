# M73｜2007年600151分钟历史公开仓库核验

## GitHub Actions公网实测（PR #196，2026-11-15，UTC 09:03）

- HF数据集根目录HTTP 200；“A股分钟/2000-2024/2007/1分钟”目录HTTP **200**，目录确实包含若干单股CSV，例如sh600000.csv/sh600004.csv/sh600006.csv；这验证年份和1m目录真实存在，却尚未验证sh600151.csv本身。
- 请求较大目录清单HTTP **401**；减小列表页并在被拒后直试单个“sh600151.csv”仍HTTP **401**。目前是**读取权限/访问方式受阻，具体文件是否存在仍未核实**，切勿误判没有2007年A股1m存档。
- zzshare免Token请求`600151.SH / 20070518 / 1min`成功解析API答复，记录为**0条**。这只说明这次免费查询未返回目标分钟线，不能证明后台从未收录2007年。
- 第一次CI **30项无网络Fake安全测试通过**，但**真实2007年数据0条已获得**。任何下一步仅针对文件访问/许可和数据来源身份，不要继续反复空请求。
- HF目录列表失败时，M73代码已采用最多一个≤30MiB的直接文件请求作为后备；两种方式均失败则如实报告HTTP 401，不保存任何文件。脚本绝不应声称已完成第54课的真实K线重建。

日期：2026-11-15。根据用户实测，QMT在2007-05-18单次1m历史补下载后仍返回0条；2006-05-18和2007-05-18日线都包含第54课图上的18.03、18.50、18.59。作者原图只印“05月18日”而未印年份，2007当日最高18.59只是线索，不能认证图年份。

## 实际发现的第三方来源

**首选Hugging Face数据集**：[OxFengyuan/stock_dataset](https://huggingface.co/datasets/OxFengyuan/stock_dataset)。数据集卡说明有2000—2024年A股1/5/15/30/60分钟CSV行情，目录采用“ A股分钟/2000-2024/年份/1分钟/股票.csv ”，约309495个分钟文件、总计216GB。只需要2007年度600151一份，不能下载整个数据集。HF公开目录/真实2007文件是否存在、是否含五月十八日及是否未复权尚未验证。

**第二条免费独立API**：[GitHub zzquant/zzshare](https://github.com/zzquant/zzshare)。从官方client.py/core.py源码确认可以匿名GET https://api.zizizaizai.com/v3/market/kline/minute/600151.SH ，参数freq=1min、trade_time=20070518、Header sdk-key: anonymous。README的2005历史范围明确与日线关联，不能据此认定1m也含2007年。

**GitHub网盘存档备选**：[aitech17/A_history](https://github.com/aitech17/A_history)声称2005—2021年1m+tick网盘，链接https://pan.baidu.com/s/1W2TMPTHLWblKy1gBwMCIEQ ，码i4ru；[waizao/StockApiJava](https://github.com/waizao/StockApiJava)提供1/5/15/30/60分钟网盘，链接https://pan.baidu.com/s/1JrIFmzPmiVYehRSqctfNdA ，码vdes。两者GitHub仅代码/README，当前检索网络打不开百度网盘目录，不能确认分享有效或2007年600151确有文件。

**明确排除误判**：tiantianlaolao/astock-data-toolkit说明TDX免费1min窗口约90交易日；newlife0007/go_tdx2db说明TDX不提供完整旧历史分钟。因此不再重复QMT/TDX旧日期空下载。hello245m/free-stockdb有EXE文件、不透明复权数据，此阶段不运行未知二进制程序。

## M73 只读检查

脚本 tools/probe_chanlun_l54_public_archive_m73.py 使用Python3.11标准库，仅复用现有M72与M56/M69验证，不装外部SDK、不上传行情、不保存文件。默认preflight完全离线。

用户明确执行hf-once时，仅枚举HF一个候选年份的1分钟目录，限定12页x1000项、最多单个30MiB年度文件，只按文件名找600151，内存读取并校验年度文件SHA256及可用LFS哈希，筛出2007-05-18一天至多300条，递交M56 OHLCV审计和M69时间格网。不打印原始数据行，也不宣称SHA256证明原图真实性。zzshare-once仅一次匿名公共单股单日HTTP请求，返回零行只算本次未取得，不能推断数据商永久无历史。

只有真实文件存在、日内行数>0且价格/时间/来源进一步核验后，才能考虑图中13:21—15:00的结构对照；年份未定、可能复权未定、分笔先后不可从1m还原；F01/OB38/OB99/Φ20/A016/A087依旧未解，E1-E4 NOT_RUN。禁止将未认证数据直接并入AStockDataTools Parquet主库。

## 本机执行（合并main后）

单行PowerShell先静默更新Git，再用已存在的Python3.11执行一个公开数据源查询：

Set-Location -LiteralPath "D:\ChatGPT\TradeBooksInAIsEyes" -ErrorAction Stop; git -c http.sslBackend=schannel -c http.version=HTTP/1.1 fetch --quiet origin main; if($LASTEXITCODE -ne 0){throw "Git fetch failed"}; git -c merge.stat=false merge --ff-only --quiet FETCH_HEAD; if($LASTEXITCODE -ne 0){throw "Git merge failed"}; & "D:\software\Python311\python.exe" -B tools/probe_chanlun_l54_public_archive_m73.py --mode hf-once --candidate-date 2007-05-18 --timestamp-convention bar_end

若HF失败，可将mode改为zzshare-once试免费匿名接口。两个模式都不会自行装包、买账号、写文件或下载全市场。GitHub CI如执行公开查询属于一次外部访问，不代表本机已成功取得该数据。
