# v4.91｜第70课整理版“原作者回复数”与原宿主错位的可证反例

**2026-11-13｜依据公开第三方定版Git blob交叉核对。** v4.90确认`stockServ/chzhshch-108-plus`完整108篇课文并不等于108课评论完整；本轮找到更具体的问题：即使某整理版把原作者署名回复放在“第70课”之后，这些问答可能实际上属于**另一天的其他原博客文章**，不能在未标记时作为第70课原始评论或该版相对收录完整度计数。

## 1. 三篇不同宿主及两条可定位的错归属

这里分别核定评论的**实际宿主**与整理者在教学文档中的展示位置，两者不得合并为一个字段。

| 真正的文章宿主与发表时间 | 作者署时评论 | 别的整理版如何摆放 | 研究解释 |
|---|---|---|---|
| **《41与1，本ID对二级市场兴趣已失》**；2007-08-13 21:26:14 | **2007-08-13 21:56:16**，回复“深潜江湖”关于特征序列与分段 | 却混入`GtXin/TDS/references/chan_theory/070.md`第70课整理文；这条**发生在第70课发表之前两天** | 问答真实宿主不是第70课；旧编者可能按相关问题归入，**不得升级为第70课作者原评论** |
| **《教你炒股票70：一个教科书式走势的示范分析》**；2007-08-15 22:41:35 | 其raw风格HTML的当前快照中，未出现任何`class="divReplyIsHostTrue"`的真实回复区块 | `stockServ/108/...-070.md`同样报告0个UID格式记录；但是`GtXin/TDS/070.md`尾随多条作者署名记录 | **快照0≠2007年原作者从未在第70课下回复**，只表明这两个来源未收录可核的原宿主记录 |
| **《全球化，没有市场可与世隔绝》**；2007-08-16 15:41:56 | **2007-08-16 15:50:48**，回复“新浪网友”关于笔、线段/中枢的疑问 | 同样被`GtXin/TDS/070.md`（甚至一些其他教学转写）挪到第70课文本之后 | 作者署时回复确实能在另一篇文章的raw风格HTML`divReplyIsHostTrue`区块直接找到，**是跨文章的知识重组而不是第70课原评论** |

### 固定到Git文件而不是网站关键词摘要

以下均是第三方历史转载快照，**不是经认证的2007年新浪服务器原字节**：

- [第70课raw风格原文及空的回复容器](https://github.com/fangj/chan/blob/9a0d1d08f3455e096a7aa37adb766d8555e16253/raw/sina_blog/chan_fenlei/jiaonichaogupiao/681.html)；blob `d0b0891704a0b1c1c561ad87d5510dd73ed7f1ad`；别把CSS里出现的`divReplyIsHostTrue`当作真正回复，真实区块必须有`class="divReplyIsHostTrue"`并含`author/pubtime`。
- [8月13日《41与1》原样式转载及21:56:16作者回复](https://github.com/fangj/chan/blob/9a0d1d08f3455e096a7aa37adb766d8555e16253/raw/sina_blog/chan_fenlei/shizhengjingji/584.html)；blob `ac9e3b569cfdf5fc4a9ca49f21e51c9ebe84bfbd`。
- [8月16日《全球化》原样式转载及15:50:48作者回复](https://github.com/fangj/chan/blob/9a0d1d08f3455e096a7aa37adb766d8555e16253/raw/sina_blog/chan_fenlei/shizhengjingji/680.html)；blob `06ffc2f7781e8e15725cf63621fbcb8dbdd48a81`。
- [含跨文章附加回复的“第70课”整理转写](https://github.com/GtXin/TDS/blob/3cf72d2fcd077d9db287765806ba2c28dd1dd99b/references/chan_theory/070.md)；blob `fc4e936b515de4c0e28bb5f7ba1182813fd29ff0`。
- 另可核[第70课独立网页显示版](https://github.com/gavfu/chzhshch-blog-site/blob/99e927024091b92cadd9c17d8880a52518e4390a/stocks/070/index.html)与[8月16日另一篇文章的网页显示版](https://github.com/gavfu/chzhshch-blog-site/blob/99e927024091b92cadd9c17d8880a52518e4390a/stocks/20070816/index.html)。

**证据限度：** 我们确切证实的是*这两条*跨文章归属错位，**没有给整理版中的全部署名回复逐条找到原宿主**。因此不能声称“该版所有回复都是假的”或“15条都错归属”；更不能因第70课快照零回复就推断原Sina服务器在2007年绝无其他评论。后期按主题编排是合理的阅读方式，但必须留“原发表宿主”和“编者收录主题”两种不同字段。

## 2. 对“第二种”搜索的直接影响

2007-08-13一条明确讨论特征序列及线段的第二种分段情况，8月16日一条讨论同级中枢与笔的界限。**它们不是独立“第二种中枢定义”公式**，也未得到凯翔A087本人指认。若未来在老虎版或其他版本检索到它们，应先看作者原宿主、再判断是课程评论还是其他文章移植；不能把“出现在第70课相关文集里”当成原作者在该课评论区多次亲口确认。

## 3. 可执行的来源归属门

[冻结台账](../../../catalog/chanlun_l70_comment_host_adjudication_v491.json)记录课文、整理转写及两条回复在其他宿主下的原样式HTML位置、日期、固定Git blob与未认证标志位。[离线审计](../../../tools/audit_chanlun_l70_comment_hosts_v491.py)默认只核这些既有证据/历史v4.90先例；`--snapshot-dir`可选读取合法取得的`lesson70.html`、`aug13.html`、`aug16.html`以及`editorial70.md`，核验三篇文章标题/发表时间、真实`divReplyIsHostTrue`标签里的署时，以及编辑转写是否同时包含两条回复。CI采用自主合成的短页面进行反例测试，不会爬取或再分发外部版权全文。

**结论：** 未来版本对比至少要同时保存`original_post_id`、`original_reply_time`、`editorial_location`、`provenance_status`。若拿不到原宿主，就只能标`EDITORIAL_LOCATION_ONLY`，不得把记录纳入“本课原作者评论覆盖率”分母。老虎版PDF/DOCX仍未取得；F01/OB38/OB99与A016/A087仍OPEN，E1—E4真实行情NOT_RUN。
