# v4.89｜三条2007年原作者署时问答的原样式网页与多镜像核对

> **v4.90后续全108课源覆盖审计：** 已实际逐文件扫描既知`stockServ/chzhshch-108-plus`固定版本的108篇原课MD，记录2,541个UID格式评论，其中953个同时匹配作者UID+昵称，分布58课；第61—108课中45课无作者UID匹配。这是**单一第三方整理源覆盖率**，不等于原作者全部留言量或老虎版覆盖率。第54课两处“第二种+中枢”自动命中均来自整段作者回复中引用的网友问题，而非作者提出了独立第二中枢公理。详见[全108课冻结证据与未来版对比协议](IDEA_108_AUTHOR_REPLY_COVERAGE_BASELINE_V490.md)。


**核对日期2026-11-13。** 上轮v4.88定位的2007-02-09、02-12两条问答，及早由v4.38登记的2007-03-08两种看法，本轮进一步找到 [fangj/chan](https://github.com/fangj/chan) 保存的Sina样式**raw HTML**、[gavfu/chzhshch-blog-site](https://github.com/gavfu/chzhshch-blog-site)生成的另一HTML版，以及针对每篇分别由[stockServ/chzhshch-108-plus](https://github.com/stockServ/chzhshch-108-plus)或[figozhu/chzhshch_The_Analects](https://github.com/figozhu/chzhshch_The_Analects)提供的Markdown转写。新增的是**多格式可逐条核对的原回复署时与上下文**，而非首次发现第17/35课定义、7月20日双a0理论或3月8日观点。

## 三条精确匹配的问答与原作者博文归属

| 作者回复（当地时） | 提问者及提问时刻 | 宿主文章 / 原Sina主文 | 答复所能支持 |
|---|---|---|---|
| **2007-02-09 16:20:18** | “袖手旁观”，15:55:07 | [第29课](https://blog.sina.com.cn/s/blog_486e105c010008la.html) | 若将1分钟视作底层，以三根1分钟K线重叠初始化；逐笔成交视为底层时另行处理（B1a；并非已给出新中枢公理） |
| **2007-02-12 16:07:02** | “温柔的股客”，15:43:32（包含转引15:17:41提问） | [《论语》详解（52）**已核到真实原Sina文章**](https://blog.sina.com.cn/s/blog_486e105c010008n0.html) | 非最低层中枢不等于固定数目的K线，底层`A0`与`An+1=F(An)`递归（B1a；**不属于第29课评论**） |
| **2007-03-08 16:38:56** | “缠文观止”，15:34:28 | [《论语》详解（55）**已核到真实原Sina文章**](https://blog.sina.com.cn/s/blog_486e105c0100090r.html) | 同一中枢观察有`a+B+b`走势组合分析与前三段成中枢、后续为震荡分析（**B2V视角**，不等同第54课B2R合法分解政策） |

### 可复核的镜像具体地址与Git blob

| 案例 | 仿新浪“原样式”HTML（raw源码） | 另一HTML归档 | Markdown转写 |
|---|---|---|---|
| FEB09 | [fangj/chan raw/460.html](https://github.com/fangj/chan/blob/9a0d1d08f3455e096a7aa37adb766d8555e16253/raw/sina_blog/chan_fenlei/jiaonichaogupiao/460.html) | [gavfu/029](https://github.com/gavfu/chzhshch-blog-site/blob/99e927024091b92cadd9c17d8880a52518e4390a/stocks/029/index.html) | [stockServ/029](https://github.com/stockServ/chzhshch-108-plus/blob/d2a87d5bd9c84baac2918edca668b9f82a20be52/108/0456-486e105c010008la-029.md) |
| FEB12 | [fangj/chan raw/458.html](https://github.com/fangj/chan/blob/9a0d1d08f3455e096a7aa37adb766d8555e16253/raw/sina_blog/chan_fenlei/wenshizhexue/458.html) | [gavfu/论语52](https://github.com/gavfu/chzhshch-blog-site/blob/99e927024091b92cadd9c17d8880a52518e4390a/confucius/52/index.html) | [figozhu/论语52](https://github.com/figozhu/chzhshch_The_Analects/blob/d2c92038f5060d7d36b6f3f6f8e8ff7287d2de0a/The%20Analects/0458-486e105c010008n0-%2860%29.md) |
| MAR08 | [fangj/chan raw/442.html](https://github.com/fangj/chan/blob/9a0d1d08f3455e096a7aa37adb766d8555e16253/raw/sina_blog/chan_fenlei/wenshizhexue/442.html) | [gavfu/论语55](https://github.com/gavfu/chzhshch-blog-site/blob/99e927024091b92cadd9c17d8880a52518e4390a/confucius/55/index.html) | [figozhu/论语55](https://github.com/figozhu/chzhshch_The_Analects/blob/d2c92038f5060d7d36b6f3f6f8e8ff7287d2de0a/The%20Analects/0474-486e105c0100090r-%2893%29.md) |

上述路径、每个被检查blob SHA、案例角色、提问者及署时均在[JSON登记台账](../../../catalog/chanlun_archived_html_crosswalk_v489.json)。现存 `raw` HTML 有 `divReplyIsHostTrue` 宿主容器和作者名及时间；公开Sina目前**只显示文章正文**，没有相应的2007历史评论原始记录。所谓raw是**第三方仓库存档的文件名**，不能把Git快照当成2007年新浪服务器原始字节或作者实名法证，更不能把几个镜像仓库当成三个可证明**独立采集链**。相同文字存在共同上游复制可能，不能以镜像数量作为历史真实性的数量统计。

## 与凯翔A087指认、老虎版、历史版本的界限

1. **v4.88来源追证增强而不是推翻：** 两条早期问答都比第35课早，3月8日回帖也可从raw样式HTML找到。一条明显改善是v4.88中《论语》52的`original_sina_parent_article:null`如今已补上准确可访问的Sina文章URL，且《论语》55的具体文章原Sina URL也可验证。不要误将两个《论语》回帖附在教你炒股票29/35主文之下。
2. **已登记来源照旧：** v4.38已知道3月8日两种看法及stockServ的部分35/38课源码；v4.41已知道7月20日双a0作者博文；v4.88已知道2月的问答。v4.89的增量是这三段精确对应到raw风格HTML、其他HTML/Markdown及博文URL的**交叉证据链**；B1a/B2V/B2R/B3各自变量和已有未证承诺不变。
3. **没有得到凯翔A087本人对这些回复的明确指认，没有拿到完整“108课老虎整理版.pdf/docx”字节。** 两份资源目录只证明有该文件名，不能比较作者回复覆盖率、真实性或编辑夹注。这也意味着不能把B1a、B2V、B2R直接指定为“第二种好用的定义”；B3独立公式是否存在依然未知。
4. **其他研究不升级：** 市场没有进行真实回放、A016第三层未知、F01/OB38/OB99未闭环、E1—E4依然NOT_RUN。原100答、5卷108课、证据卡不修改。

## 只读、离线复核的实际能力

[校验脚本](../../../tools/audit_chanlun_archive_crosswalk_v489.py)有两层：`--check`对仓库自带台账与v4.38/v4.87/v4.88既有记录做精确关联、Git blob字符串、评论时钟、类型变量及未认证状态校验；可选`--snapshot-dir`支持把三个**合法获取的**HTML原文分别命名为`feb09.html`、`feb12.html`、`mar08.html`，离线逐个解析真正的`divReplyIsHostTrue`区块，核验作者、回复时间、提问者和短锚点。**不需要抓网、不导入/分发外部版权原文，默认也不伪称已在CI重新下载校验。** 对应测试使用自主构造的小型HTML负例，验证冒名、评论宿主错位、时间错乱、错配原文、伪raw外部纯文本等均不能通过。

**下一优先级：** 取得可核的老虎版**实际文件字节**（版权合规）与准确版本，并逐条对读这三条回复及第54课；或取得凯翔本人的原回答后续评论明确确认所指出处。此两项未发生前，A087_REFERENT_OPEN。
