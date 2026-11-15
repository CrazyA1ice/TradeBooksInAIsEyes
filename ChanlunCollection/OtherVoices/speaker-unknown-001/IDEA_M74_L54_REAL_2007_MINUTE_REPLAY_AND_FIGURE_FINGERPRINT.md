# M74｜第54课航天机电真实历史1分钟K线：2007-05-18 来源指纹、图像重放及作者 g/d 未证映射

> 日期：2026-11-15。此文记录用户在自己的 Windows 环境实际执行后的输出，而不是 GitHub CI 采集到的行情。CLI 与离线图形工具的存在不能冒充真实网络试验。作者原图跨来源对照来自原图复核报告（deliverables/chanlun_108_acceptance/00_REVIEW/LESSON54_SOURCE_FIGURE_AND_STRUCTURAL_VS_DECISION_AGREEMENT.md），M73.1 时间字段修复已合并主分支 PR #197。

## 1. 已经取得的真实候选文件证据

- 来源为 Hugging Face 的 OpenFinMind/stock_dataset；不是 OxFengyuan/stock_dataset 访问失败的请求。
- 唯一读取的年度文件：A股分钟/2000-2024/2007/1分钟/sh600151.csv；paths-info/main API 返回 HTTP 200、大小 2,897,499 字节、LFS SHA-256 84ae998ee80cbd13adc80759c1de6e465d57f6fe8d3e48015a02e0dd29ddc439。
- 用户以 Python/OpenSSL 只读下载，文件大小及 SHA-256 都与元数据一致；内存解析年度56,400行、2007-05-18日内240行；CSV 原列为“日期,时间,开盘,最高,最低,收盘,成交量,成交额”。
- 修复 M73 中文时间列映射后，用户真实运行 M72/M56/M69 成功：240唯一分钟、09:31—15:00，bar_end 声明下缺失0、越格0、FULL_240_DECLARED_GRID_ONLY。bar_end 是已声明但供应商未独立证明的口径。
- 价格与时间：全天最高18.59在13:07，全天最低17.61；13:21—15:00最高18.45、最低18.03；15:00低点/收盘都是18.03。
- 最后一分钟成交量原始值1917；最近5根均量1565.2，最近10根均量1498.4；最近5根收盘均价18.05，最近10根18.052（保留两位小数为18.05）。这些为同一个SHA已验文件的实际输出；未把真实原始行提交Git。

## 2. 图像身份的证据分层

外部编纂PDF图像：印刷第125页／PDF零基页128；图名“航天机电(1分钟)”，横轴“05月18日”无年；图上18.59、最右18.03，成交量末值1917.00，成交量MA5/MA10为1565.20/1498.40，价格前两条均线都显示18.05。与用户的真实CSV对应的**价格、时间、成交量及均线联合指纹**高度吻合，可将2007-05-18标为**极高置信度图像日期候选**。

但独立交易所/券商供应链、历史复权口径、软件均线与MACD跨日初始化及PDF编纂副本的相同价位调整方法未证明；图面本身不印年。因此代码标记为VERY_STRONG_CONSISTENCY_NOT_INDEPENDENTLY_AUTHENTICATED，并非独立交易所认证。

作者正文g0=18.50是分析起点，图上18.59是更早高点；只查13:21—15:00会漏掉发生在13:07的18.59。此轮观察窗口从13:01开始。

## 3. 工程交付：单文件只读重放 + 本地静态 SVG

新增 M74纯标准库历史重放器（tools/replay_chanlun_l54_real_minute_m74.py）及纯人造行情离线测试（tests/test_chanlun_l54_real_minute_m74.py），复用 M73→M72→M56/M69 的严格入场链。

- 默认 --mode preflight不联网、不读行情、不写图；仅显式--mode openfinmind-once才读取固定URL的单只股票年度CSV，限制文件字节至2,897,499+1，核对完整SHA-256，筛选一个交易日并跑原校验。
- 只输出摘要，不向控制台输出原始OHLCV逐行数据；复算用户观测到的13项时间、价格、成交量及均线指纹，逐项比对，永不将摘要匹配当做交易所证书。合成单测通过不代表新增一个真实行情来源。
- 提供仓库外--svg-output时写本地一个独立SVG，不覆盖已有文件，不写入Git。SVG显示1分钟蜡烛、收盘MA5/MA10、成交量与MA5/MA10，以及MACD12/26/9演示轨迹；可用--window afternoon（13:01—15:00，包含13:07）或--window full（整日）。MACD以本交易日第一个close初始化，不与原图软件跨日初始化相等。
- 报告 g1—g7 与 d1—d7的market_minute/price均为null，原因是原图坐标、作者文字节点、作者假设的下级别线段合法完成尚未逐项核实，禁止按局部高低点自行贴上作者标签。
- 作者两种政策仅保留文字身份：甲g5成高层中枢，g7三卖；乙g6成高层中枢，g7仍属中枢震荡。作者对方向风险的定性接近不等于结构类型、执行时刻、仓位或收益相同。

用户可在独立worktree运行离线测试后明确选择网络下载，再向仓库外路径生成SVG，例如：

    python -B tools/replay_chanlun_l54_real_minute_m74.py --mode preflight
    python -B -m unittest discover -s tests -p "test_chanlun_l54_real_minute_m74.py" -v
    python -B tools/replay_chanlun_l54_real_minute_m74.py --mode openfinmind-once --window afternoon --svg-output "D:\ChatGPT\L54-M74-20070518-afternoon.svg"

第三条写出的是本地可查看图像而非上传原始行情；要求输出父目录已存在且目标文件不存在。若网络文件内容不匹配SHA，必须拒绝生成图。

## 4. 下一步：作者标记的人工原图配准，而非凭高低点猜测

1. 在同一坐标框架下打开PDF原图与M74 afternoon SVG，冻结原图左右时间锚点与坐标变换；逐一记录g_i/d_i图示的大致分钟窗口及价格区间，标注“VISUAL_CANDIDATE”而非已证作者入场。
2. 先核对作者正文d1=g2及d2=g4的同价断言，再核对甲乙高级中枢价格上下界、g7前缀数据；分钟配准不是证明低于一分钟的线段已经合法结束。
3. 每个标记单独留source_visual_bar、proposed_market_minute、proposed_price、market_bar_close_observable_at（时间戳口径待认证）、author_text_stage、lower_level_completed_at（未知）及first_tradable_at（未知）。
4. MACD软件指标若要精确还原，需要前一交易日及更早的数据和软件初始化参数；不能把单日EMA曲线称为原图MACD。

## 5. 边界与未完成

当前为真实历史行情候选观测及图像身份一致性校验，**并非已完成真实市场回测**（E1-E4 NOT_RUN），亦未产生订单/收益证据。文件哈希不能证明交易所认证或复权，分钟OHLCV不包含分钟内H/L先后。F01/OB38/OB99/Φ20/A016/A087依旧开放；高吻合度不能取消甲乙结构分类差异。
