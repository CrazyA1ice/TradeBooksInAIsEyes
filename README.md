# TradeBooksInAIsEyes · 交易之书，AI之眼

> **深入阅读、审慎质疑、独立思考。** 以原书为证据，拆分作者观点、后期编者材料、AI解释与未来可检验命题。研究目的不是批量生成所谓必赢策略。

## 当前研究主线：准确解读知乎凯翔的缠论观点

**本仓库长期仍是支持多本交易书籍分别研究的 `TradeBooksInAIsEyes`，而当前研究阶段优先完成《缠论》，重点准确解读知乎用户「凯翔」（公开主页标识 `tsk-47-98`）的观点。** 未来其他书籍沿用独立 BookCollection 和通用阅读工作流；AStockResearchLab 单独承担综合知识库与研究平台。 本仓库保存原始问答、研究性解释、不同观点和未证问题；通用资料入库G0只作为将来需要时的独立辅助能力。A股跨来源知识库、OCR与研究管理平台属于另一个仓库 [AStockResearchLab](https://github.com/CrazyA1ice/AStockResearchLab)，不在本仓库复制其平台建设。

**来源覆盖核查（2026-11-12）**：此前上传到对话的文件 `answers(1).md` 是 **130,167 字节**，文件头写明「回答总数：100」，里面确有100个带URL的回答块；仓库A001—A100与其一致。**用户指出其完整收藏应有200多条；目前尚未收到或定位到这些额外回答**，因此100只是*本次已归档覆盖数*，**绝非凯翔账号历史总回答数，也不等于其全部言论、评论**。目前不可声称“完整分析了凯翔全部回答”，新增观点可能推翻旧AI综合结论。日后取得完整导出，使用 [只读增量核对工具](intake/zhihu_answer_reconcile.py) 检查 >100条来源、稳定回答ID、重复与修改，再补本人原话、来源锚及研究报告；在此之前 A087/A016 等仍保留未公开/待核实结论。

**唯一原话入口**：[凯翔人物档案](ChanlunCollection/OtherVoices/speaker-unknown-001/README.md) → [A001—A100原文](ChanlunCollection/OtherVoices/speaker-unknown-001/answers-2026-11-11.md) → [来源索引](ChanlunCollection/OtherVoices/speaker-unknown-001/answers-index.json)。100条来自用户2026-11-11提供的导出，含100个不同知乎回答URL；这可核验导出文件内部的原字节与记录，不等于我们已独立验证知乎账号历史或取得所有评论。人物目录ID沿用 `speaker-unknown-001` 以保留历史链接，不代表“仍不知道导出所写的账号名称”。

**先解决四组直接影响解读准确性的争点：**

1. **A087「级别」与“两种中枢定义”**：本人说过有两种、第二种实战更有用，**没有提供可复现的第二种计算公式**。拆开严格逐笔与实操a0、第38课两种视角、第54课同图不同分解、九段与3+3+3，不准把我们的最佳猜测写成他的私有算法。
2. **A016「走势终完美第三层」**：本人明确写出第一、第二层，但**未透露第三层的完整命题**。第99课等原文只能形成标明来源与竞争解释的研究候选；候选与本人确认严格分开。
3. **A026「不测而测」**：本人区分宏观条件概率与完成走势后的分类排除；优先澄清“已观察的局部条件、走势真正完成、当时首次可知、交易执行”不同阶段。自造K线或合成证书不是对他真实方法的证明，F01/OB38/OB99仍`OPEN`，真实行情研究`NOT_RUN`。
4. **A094/A058/A084评论上下文**：原回答提及评论的重要性，但导出中**缺少独立评论实体**。优先补实际评论原文、回复关系与时间；不能根据作者提到“评论”便捏造评论里的具体观点。

**逐条解读原则**：原话与回答ID/来源URL → 原问题与发表时间/限定语 → 原作者课文或答疑逐点对照 → 最宽容且不越界的解释 → 可能反例和相反解释 → 尚缺何种资料。不得混同凯翔原话、他引用的他人话、缠中说禅的原文及AI提出的假说。所有未知明确保留`UNKNOWN/OPEN`，不靠连续追加合成测试和版本号假装知道作者尚未说出的内容。优先研究追踪：[Issue #110](https://github.com/CrazyA1ice/TradeBooksInAIsEyes/issues/110)。


## 每本书独立研究成果文件夹（v4.0.0）

**《缠论》全部研究成果已整理到 [ChanlunCollection/](ChanlunCollection/README.md)**：五卷原PDF、108篇逐课分析、108张原文证据卡、108课统一理论主脊、深度导读、来源与版本登记、报告、测试和审计工具均在一个文件夹内可查；保留原仓库规范路径作为编辑源，由`COLLECTION_MANIFEST.json`逐文件验证精确一致。后续每本书都建立独立`<BookName>Collection/`；**每一步研究都必须同步修订[通用工作流](docs/BOOK_RESEARCH_WORKFLOW.md)、该书[工作日志](ChanlunCollection/WORK_LOG.md)和集合完整性清单**。

**同轮第101课关键原文**：作者直接称“走势必完美”的深层是递归函数的**唯一分解**，并允许a0有不同设计。各自唯一≠跨a0计算结果相同；而这一原课已明说的H5核心也不应冒充凯翔声称“第三层没有明的总结”的谜底。详见[v4.62报告第七节](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_LESSONS_98_100_LIVE_MULTILEVEL_STATE_TREE_V462.md)。

**最新v4.72《缠论》正式第53课与2007-05-22作者五段历史问答：**[高低极值≠走势端点、离开走势内中心≠整体离开、600216具体三买分段](deliverables/chanlun_108_acceptance/00_REVIEW/CHANLUN_L53_CHILD_EXTREMA_AND_CONFUCIUS65_REPLIES_V472.md)。第53课AUTHOR_MAIN说明5分钟完整走势高低价未必落在起止点；前一天《论语》65（**不是第52/53课评论**）15:58/16:30/16:35/16:49/17:36作者回帖要求分别完整的次级离开和回试、允许离开走势的小中心在旧中心内，并对600216两份历史时间窗答“对”。历史答复不能倒填交易日实时首知；逐笔F01、OB38/OB99、ZG/ZD等号继续OPEN，行情NOT_RUN。

**最新v4.71《缠论》第24课作者署时回复补出第三买点“结束位置≠整个回拉最低位置”：**[2007-01-18 22:11:08 作者600832答疑与第20/38课的价格对象、完成时间对照](deliverables/chanlun_108_acceptance/00_REVIEW/CHANLUN_L24_AUTHOR_REPLY_THIRD_BUY_ENDPOINT_VS_WHOLE_RETRACE_V471.md)。作者举2007-01-17三段30分钟回拉、最后C段不创新低及五段复杂回拉说明第三买点位置未必落在整次回拉最低价；这是ARCHIVED_AUTHOR_REPLY，不是当天15:02发表的正式课文、也不是当年行情的独立验证。**v4.70数值不破界条件未被取消，但L/H输入必须先证实是原作者判据指向的哪个完成成员/端点**，不能拿全局最低和信号结束价混算。触边端点语义、F01/OB38/OB99依旧OPEN，行情NOT_RUN。

**最新v4.70《缠论》第20课边界等号与第38课首次外回抽角色的未决接口：**[第20课等号与第38课触边词义、首次回抽计数的双证据审稿](deliverables/chanlun_108_acceptance/00_REVIEW/CHANLUN_L20_L38_BOUNDARY_TOUCH_RETRACE_ROLE_V470.md)。第20课三买低点\(L=ZG\)、三卖高点\(H=ZD\)满足价格非严格条件，但作者第38课「回中枢里」未明确裁决**恰好触及端点**算不算回入；必须将价格门、回试角色、完整次级证书和第18课中枢破坏分别留存，端点身份标`BORDER_TOUCH_UNRESOLVED`，不得伪造三买/三卖。承接v4.69、不改变A001—A100/原PDF，F01/OB38/OB99 OPEN，市场NOT_RUN。

**最新v4.69《缠论》第一次回抽的级别计数与同级中枢连接：**[第38课2007-03-21作者两条历史回帖＋第54课合法连接拓扑、第18/20课原文的联合审稿](deliverables/chanlun_108_acceptance/00_REVIEW/CHANLUN_L38_NESTED_RETRACE_AND_L54_SAMELEVEL_CONNECTOR_SCOPE_V469.md)。在第三点语境中，重新回到原中枢内是中枢震荡，**并非已经消耗首次合格外回抽**；2007-02-28 13:37/13:51被作者解释为次次级两个内部回试，而非两个独立次级完整回抽。第54课禁止同一走势内两个无合法下级连接者的独立同级中心硬拼；第38课特殊R_cut六段→两个完整g盘整的政策域须另审，不能当无条件矛盾。第54课不同R造成g7三卖/中枢震荡之差旧v4.30已记录；本轮重点是据署时作者回复纠正回抽计数与独立连接范围。F01/OB38/OB99 OPEN、市场NOT_RUN，凯翔100答与原PDF未改。

**最新v4.68《缠论》第43课原文未来中枢双路径与首知时钟：**[作者第43课B/C重叠/不重叠的后继分支、第39课已完成同级段的前缀稳定性、第40课5→30分钟换档](deliverables/chanlun_108_acceptance/00_REVIEW/CHANLUN_L43_FUTURE_CENTER_BRANCH_AND_FIRST_KNOWN_BOUNDARY_V468.md)。同样c内的1分钟背驰之后若未来C与B不重叠，原30分钟仍延续；若重叠则可能高级重组，且30分钟**历史分界可标在旧1分钟背驰价位**——分界标签所在时间不等于以后B/C关系首次能被证实时刻。第39课固定R已完成同级Ai+1仍应稳定，不要求**未来跨级组合**当时可知；第40课是否换档是另一个操作决定。新增2007-02-26作者归属回复解释前一走势中枢不归后一走势，但严格逐笔根层身份/退出算法依旧OPEN。F01/OB38/OB99 OPEN，收益NOT_RUN，原凯翔100答、五卷及108课档案不改。

**最新v4.67《缠论》原作者署时答疑与第36课双中枢案例：**[2007-03-20《论语》58评论中“三笔同价不意味着翻转／同一构件不得重复归组”与第36课两种30分钟中心核心、三买阈值对照](deliverables/chanlun_108_acceptance/00_REVIEW/CHANLUN_F01_AUTHOR_REPLY_20070320_NONREUSE_AND_L36_POLICY_DEPENDENCE_V467.md)。新源证：2007-03-20 17:39:28回帖保存在历史评论镜像，原新浪文章本体真实可核但评论原字节未取得；原第36课同一指数行情分别组合成[2892,2911]或[2905,2947]两个30分钟中心区间。固定R内**不复用构件**与跨合法R**可能不同几何/阈值**兼容。ROOT-IDENTITY严格逐笔归并/ROOT-EXIT最低盘整出口依然OPEN，不以作者一句答复冒称F01闭合。凯翔100答、原五卷PDF、108课旧研究不改，行情NOT_RUN。

**最新v4.66《缠论》严格底层中心身份研究：**[第18/20/35/38课三笔同价局部见证与新生/延伸中枢身份的原文推理](deliverables/chanlun_108_acceptance/00_REVIEW/CHANLUN_F01_THREE_TRADE_SEED_WINDOWS_VS_CENTER_IDENTITY_V466.md)。长度n笔同价串具n−2个重叠三笔种子见证，但不能据此自动计成n−2个独立新中心；第18/20课明确区分旧中心延伸与新中心发生。**F01新增上游ROOT-IDENTITY关口**：冻结f1/R/g后必须给出不同局部见证的中枢身份归属，才能合法谈第35课N>2最低趋势出口和第100课回抽完成。第20课天天同价只一低中心是实用分钟级语境，不可与第35课逐笔强行等同；“合并同价游程”仍为研究者候选政策而非已证作者原算法。F01/OB38/OB99 OPEN，实盘NOT_RUN。原100答/五卷/108课不改，多书平台路线保持。

**最新v4.65《缠论》底层完成的时间量词推理：**[第17/18/20/35/38/84课源文论域、任意长有限延伸和独立结束收据对照](deliverables/chanlun_108_acceptance/00_REVIEW/CHANLUN_F01_UNBOUNDED_EXTENSION_FINITE_COMPLETION_QUANTIFIERS_V465.md)。作者第17课“终要完成”与第18课盘整满足中枢后可继续延伸、甚至使用“无穷”措辞，须区别“任意有限n都可延伸”与“存在同一条合法无限轨迹永不完成”；后一强读法只有在相同政策/论域确证后才构成形式冲突。前一语义若同域成立已足以阻止把中心存在推成统一B分钟/B根K线必结束。第35课已有最低**趋势**后续N>2中心不再向原方向推进判据，不能替代**单中心最低盘整**退出，且结束证据要等新中心真正合法出现。第84课f1可替换不等于生成最低完成函数；F01/OB38/OB99 OPEN，真实行情NOT_RUN。多交易书籍总体路线不变。

**最新v4.64《缠论》线段与走势完成的双层收据：**[第62/65/67/71/72/78/83课和2007-07-20新浪主文对照](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_L100_LINE_SEGMENT_VS_MOVEMENT_COMPLETION_V464.md)。第67/71课的两种特征序列分型、转折第一笔待定与后续新旧段分支、第78课“笔破坏不一定线段破坏”共同表明最终端点不能事后倒填首次可知。更关键的是**缠师2007-07-20原博文亲自否认严格“线段即最低走势类型次级别”**；线段结束证书≠1分钟完整走势结束证书，仍须最低中心/合法类型/结束事件才能进入第100课三卖。凯翔A062的层次双说法因而有善意解释空间，但第二中枢与第三层未揭示。F01/OB38/OB99 OPEN，真实行情NOT_RUN。未来多交易书籍路线不变。

**最新v4.63《缠论》三卖确认首次可知研究：**[第18/20/53/100/101课最短证据链](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_L100_THIRD_SELL_FIRST_CONFIRMATION_PROOF_CHAIN_V463.md)。第18课中枢破坏定理三与第20课“次级完整离开＋第一次次级完整回抽＋高点不升破ZD”合读，**1分钟底背驰本身不足以确认5分钟三卖**；回抽峰值时刻也不能自动当成当时已能认证的完成时刻。第100课作者原例三卖后提第二个5分钟中枢，但跨全市场不能省略新中枢三个已完成低级成员。严格分离第53课作者正文与2009后附第三方文本。凯翔100答保持原状，F01/OB38/OB99 OPEN、行情NOT_RUN。

**最新v4.62《缠论》原课三级别推理：**[第98/100课实际30/5/1条件树与凯翔A026不测而测](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_LESSONS_98_100_LIVE_MULTILEVEL_STATE_TREE_V462.md)。不再以虚构价带推导原作者“未来一定”结论；直接按第100课：1分钟底背驰先出现，回拉是否构成5分钟三卖而分成两种5分钟状态，30分钟尚不自动变化，后续需要更高层完成/回试证据。第98课明确强调回拉后的分类与当下响应，支持凯翔A026/A058所强调的分层条件思维，但第100课三卖不可冒充A026三买原路径。H6为新增原课支撑的**研究者候选**，不是凯翔本人确认的“第三层”；F01/OB38/OB99 OPEN，行情NOT_RUN。长期多交易书籍架构不变。

**最新v4.61《缠论》原课区间语义研究：**[第20/99课重叠对象与凯翔A026“不测而测”源证据报告](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_THREE_OVERLAPS_AND_ASOF_ELIMINATION_V461.md)。作者第20课的中心延伸触及本中心核心、两中心外围波动交叠促成级别扩张，与第99课后继大中心位置**属于三种不同的关系**；上行扩张可以满足“核心分离而外围波动交叠”的数值条件。第99课“落在旧最后中心范围”尚不能自造全部区间包含式。凯翔A026“当前未见高层中心”不能直接等于“已证高层扩张永远不可能”。研究对象仍100答，第三层/第二算法UNKNOWN，F01/OB38/OB99 OPEN，市场NOT_RUN。

**最新v4.60《缠论》跨课推理：**[第18/20/38/99课与凯翔A026的分层证据报告](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_CROSSLEVEL_COMPLETION_AND_CENTER_RECONCILIATION_V460.md)。**第38课的两个同级盘整不自动构成第20课更高一级中心**，因为中心外沿波动及实际成员仍需验；第18课“可结束”不等于“已完成”；第99课“中阴一般分解未明”特别不排斥固定同级分析已可用，后继更高中心是未来强命题而非当下已证买点。100答基线已确认，A087第二定义/A016第三层仍未由本人揭晓，F01/OB38/OB99 OPEN，市场NOT_RUN。本仓库长期支持其他交易书籍。

**最新v4.59《缠论》原文研究：**用户已确认当前凯翔导出实际为100答；[新报告](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_POLICY_SCOPED_NEXT_TYPE_AND_THIRD_LAYER_V459.md)把A016“完成后另外两种”与作者第17及38课并对，发现**第38课固定同级政策下允许盘整+盘整**，故后继必异类的字面强全称需要R/g限定。又分别核第99课跨级后继H4与第102课递归整体表达H5，二者都**不能认证为凯翔本人第三层**；A087第二中枢计算法继续未知。未来书籍研究架构不变，F01/OB38/OB99 OPEN、市场NOT_RUN。

**最新v4.57：**[审计凯翔A026走势分析中最低级别“满足局部停止价序”到“走势真正结束”的证据缺口](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_EXIT_EVIDENCE_CONSERVATION_AND_COUNTERFACTUAL_V457.md)。此前v4.56人工`+1 tick`完成声明没有独立市场来源：t=10/19是下一合成成员价格，t=28无源价。新增[可执行退出来源守恒门](tools/audit_kaixiang_exit_evidence_v457.py)、18项伪认证拒绝测试，真实完成证书数维持0，原100篇及五卷108课不改，F01/OB38/OB99 OPEN。

**此前v4.56：**[凯翔A026排除法所需的底层价格条件首次由合成原始成交序列自主计算，而非用人工方向标签反向生成](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_RAW_TAPE_DERIVED_PREFIX_AND_EXIT_ASSUMPTIONS_V456.md)。冻结27笔虚拟原价，用[无前视重放程序](tools/audit_kaixiang_raw_tape_prefix_v456.py)核三同价中枢及其趋势非延续，且严格区别局部价格关系可知与未经认证的F01完成事件。无真实行情、盈利验证，F01/OB38/OB99 OPEN，用户100答不改。

**此前v4.55：**[修复凯翔A026合成完成图中“初始方向缺证、退出声明可能与价序相反”的两种假阳性](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_F01_INITIAL_DIRECTION_THREE_CENTER_GUARD_V455.md)。新增[最低级别三单价中心方向审计](tools/audit_kaixiang_f01_direction_three_centers.py)，原F01接受的伪方向与伪停止案例现会被拒绝；43节点/四时点/16项定向测试。依旧仅合成证据、F01/OB38/OB99 OPEN、行情NOT_RUN，原始100篇不动。

**此前v4.54：**[凯翔A026候选排除研究从三段“已完成”标签升级为带31节点依赖关系的F01结构收据检查](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_F01_DEPENDENCY_GRAPH_BRIDGE_AND_COMPLETION_LIMIT_V454.md)，新增[桥代码](tools/audit_kaixiang_f01_graph_completion_bridge.py)和负面单元测试。只证明合成依赖图满足必要结构规则，不认证真实市场完成、第二种中枢或第三层。原100篇正文不变，F01/OB38/OB99 OPEN，NOT_RUN。

**此前v4.53：**[凯翔A026排除法和第17课“连续三次级走势重叠”之间首次可执行、无前视的结构桥](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_THREE_COMPLETED_MEMBER_ASOF_BRIDGE_V453.md)。复用现有第99课`center_asof`、五组合成案例12个时点15项定向单测；正区间交叠**不证明**完整中枢、三买或赢利，原100答/五卷108课不变，F01/OB38/OB99 OPEN。

**此前v4.52：**[凯翔A026“只剩下跌”结论的封闭候选、首个可知时钟与独立风险审计](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_CANDIDATE_EXCLUSION_CLOSED_WORLD_AND_RISK_GATE_V452.md)。首次把v4.51的8条研究情境变成[可运行纯符号Python检查器](tools/audit_kaixiang_asof_candidates.py)和反前视单测；不把“清单只剩一项”伪装成行情全域已证，也不操作账户。原100答/108课不改，F01/OB38/OB99 OPEN。

**此前v4.51：**[凯翔动态排除法／趋势末端未定／级别扩张／结构止损与账户风险分开](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_ASOF_ELIMINATION_VS_STRUCTURAL_STOPS_V451.md)。在[本人观点目录](ChanlunCollection/OtherVoices/speaker-unknown-001/README.md)新增8条带A编号、首次可知时刻与禁止事后推断的研究性规则契约（非其本人盈利方法）；本轮A094/A058原帖及个人主页公开访问不可取评论，不造句。F01/OB38/OB99 OPEN、实盘NOT_RUN。

**此前v4.50：**[对凯翔100篇回答的完整交易思想合成](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_100_ANSWERS_SYSTEM_CROSSLEVEL_AND_COMMENT_GAPS_V450.md)：首次贯通A058“结构/方向/级别/势能/三级别联合”、A085六项执行标准与A014五维市场条件；指出同一人物“级别”的结构/持仓时间双义、第99课“结束→高一级中枢震荡”是“第三层”新候选，和A094/A058明确存在未收录的高价值评论区。原100篇不改，F01/OB38/OB99 OPEN，NOT_RUN。

**此前v4.49：**[缠师2007-02-05更强的“未来级别中枢必达”论述及凯翔“第二种中枢定义”的逐类排除](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_SECOND_CENTER_METHOD_TYPE_AND_FEB05_DYNAMIC_CLAIM_V449.md)。区分作者2007-01-11简化助记、03-08观察方法与严格数学定义，避免将操作便利冒充独立公式。F01/OB38/OB99 OPEN，NOT_RUN。

**此前v4.48：**[知乎凯翔100条真实回答及完整来源校验](ChanlunCollection/OtherVoices/speaker-unknown-001/README.md)已按原始SHA-256、100条回答URL/时间、31条明确缠论论述归档在原有唯一人物目录；[跨108课的真实原话与第三层再审报告](deliverables/chanlun_108_acceptance/00_REVIEW/KAI_XIANG_100_ANSWERS_FIRSTHAND_AND_THIRD_LAYER_V448.md)更正此前六条仅被转述的记录，并明确A087第二种定义和A016第三层**仍缺具体定义**；独立评论区并未包含在此次上传中。F01/OB38/OB99 OPEN，行情NOT_RUN。

**此前v4.47：**[第20课与2007-02-26答疑的“任何级别”主语、类型准入，以及第99/102课当下分类的适用范围](deliverables/chanlun_108_acceptance/00_REVIEW/LEVEL_TYPE_DOMAIN_2007_REPLY_AND_OB99_OB102_V447.md)。纠正此前把作者说法直接扩成“所有原始行情都在所有级别形成中枢”的过强形式重述，保留真实未证命题与不同级别完成事件。仍未找回高手逐字原帖，F01/OB38/OB99 OPEN，NOT_RUN。

**此前v4.46：**已建立[《缠论》其他人观点档案](ChanlunCollection/OtherVoices/README.md)：**每个人一套子文件夹**，同目录保存原话、来源、AI分析和更新；首个高手`speaker-unknown-001`因原帖未取回而标`MISSING_VERBATIM`，不伪造原文。通用镜像机制扩展为读者友好的`OtherVoices`入口，已有理论证明状态不变。

**此前v4.45：**[“某一级别有中枢”不蕴涵“每一个级别都有中枢”：第17/18/20/35/102课及2007-02-26署时答疑中的量词域](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_ANY_LEVEL_CENTER_QUANTIFIER_AND_EXIT_DOMAIN_V445.md)。定位第20课低级延伸与“任何级别”强读法的文本张力；修正盘整一般层第三类退出的早期来源；作者同域反证、高手原帖身份和F01/OB38/OB99仍OPEN，行情NOT_RUN。见[Issue #110](https://github.com/CrazyA1ice/TradeBooksInAIsEyes/issues/110)。

**此前v4.44：**[作者2007-06-19第60课已有最低可操作线段截断；2006-12-27第19课早期一字线作者答疑，严格成交与实用最低层两个证明合同](deliverables/chanlun_108_acceptance/00_REVIEW/ABSOLUTE_PAN_BASE_VS_OPERABLE_SEGMENT_CUTOFF_V444.md)。有限前缀证明义务不能只凭三笔同价中心宣告盘整终止。F01/OB38/OB99 OPEN，NOT_RUN。

**此前v4.43：**[2007年作者关于可无限延伸盘整的直接答疑、两次次次级回抽只是一段次级回抽、最低层退出需要的基础规则](deliverables/chanlun_108_acceptance/00_REVIEW/MINIMUM_PAN_END_NESTED_RETRACE_AND_BASE_GAP_V443.md)。建立带时钟的跨级有限前缀审计；F01/OB38/OB99仍OPEN，NOT_RUN。

**此前v4.42：**[第三类买点“第一次回抽”是否已被旧震荡用掉？原作者2007-03-21追问与首次资格、事件时钟的局部审计](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_FIRST_ELIGIBLE_THIRD_RETRACE_ASOF_V442.md)。内返不中断中心、首次合格外返条件标记、同中心后续不重复三买。F01/OB38/OB99 OPEN、NOT_RUN。

**此前v4.41：**[终于找到原新浪2007-07-20作者正文：理论逐笔成交a0与实操分型笔线段a0的两种递归起点](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_PRIMARY_SINA_DUAL_A0_THEORY_V441.md)。这是迄今最符合高手“第一理论第二实用”的直接作者原文，而非第54课的操作分组；同f不保证输出同值，线段不等于已完成次级走势；F01/OB38/OB99 OPEN、NOT_RUN。

**此前v4.40：**[作者2007-07-31明确指出九段直接重叠与递归3+3+3并不保证中枢区间相等；两道构造次序的真正区别](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_NINEFOLD_CENTER_333_AUTHOR_REPLIES_V440.md)。结合5月21、7月11正式署时问答及较早PDF编纂页锚互校，不将2025年第三方两定义写成作者原话。F01/OB38/OB99 OPEN、NOT_RUN。

**此前v4.39：**[高手“第二种定义”六候选排除；第54课同图两种分解、第二种局部更明确与g7标签分歧](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_SECOND_CENTER_METHOD_DISAMBIGUATION_V439.md)。区分固定前三段核心与滚动重叠、真正定义和操作政策；原高手具体指代尚未认证，F01/OB38/OB99 OPEN、NOT_RUN。

**此前v4.38：**[作者两种纯看盘方法与跨级混合更有效、老虎整理版文件名核验](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_AUTHOR_REPLY_TWO_METHODS_AND_LAOHU_V438.md)。另有2007-03-08作者2958→2858校勘；不宣称二手评论已得到新浪原发鉴定或第二种纯方法普遍更好。F01/OB38/OB99 OPEN、NOT_RUN。

**此前v4.37：**[高手补充发言：从周期到中枢、两种方法和作者教学历程](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_HISTORICAL_LEVEL_SHIFT_AND_TWO_METHODS_V437.md)。22个SOURCE课页、3条二手作者评论归档；第17/33课证明35课不是硬切换。老虎版未取得，未逐字重读108课，F01/OB38/OB99 OPEN、NOT_RUN。

**此前v4.36：**[“终要完成”和“无限延伸”是否矛盾？固定规则唯一与当下判断的量词审计](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_COMPLETION_QUANTIFIERS_V436.md)。仅作者文本与抽象逻辑；未取得高手逐字原帖，F01/OB38/OB99 OPEN、NOT_RUN。

**此前深度整书研究（v4.35）**：[高手关于缠论的六条质疑与“走势终完美”递归、完整分类、实时操作的四层综合解释](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_SIX_CRITICISMS_WHOLE_THEORY_THIRD_LAYER_SYNTHESIS.md)。逐条还原第15/17课分类变义、第35课级别体系、单中枢盘整、区间套、低级稳定性及原文图证问题；原话尚未逐字认证，F01/OB38/OB99证明前沿保留OPEN，行情NOT_RUN。

## 新增：第二本及后续书籍的 G0 本地入库预检

为避免当前《缠论》研究与未来每本书的数据混写，新增[独立 G0 来源预检程序](intake/README.md)（`intake/book_intake.py`）：**离线扫描本地 PDF/EPUB/DOCX/TXT/MD，自动记录 SHA-256、大小、重复、格式初检和版权审查状态**。默认仅在终端显示元数据，可指定本地私有 JSON 路径。不会复制/公开书籍，不会运行 OCR 或声称已完成 AI 阅读，尚不自动注册新的 BookCollection。以 13 个完全虚构样本单测覆盖格式、边界及不越界访问；后续收到真正的新书时再进入目录与 G1—G3 阅读流程。

## 从哪里开始

| 需求 | 唯一入口 |
|---|---|
| **验收已经研究的《缠论》** | [《缠论》五卷108课正式验收入口](deliverables/chanlun_108_acceptance/README.md) |
| **一篇读通《缠论》108课** | **[全书双顺序与七环闭环导读](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_READER_CONCEPTUAL_CLOSURE.md)** |
| **5分钟看懂《缠论》** | **[全书一屏速览与20分钟思想地图](deliverables/chanlun_108_acceptance/01_FAST_READ.md)** |
| **核对第39/98/100课原PDF文字与编者注** | **[七页原文核验与来源身份更正](deliverables/chanlun_108_acceptance/04_AI_GUIDE/17_第39与98至100课原PDF页级文字复核.md)** |
| **把晦涩定理和全书论证读懂（必交模块）** | **[《缠论》AI深度导读：12组核心命题、行文脉络和8张教学图](deliverables/chanlun_108_acceptance/04_AI_GUIDE/README.md)** |
| **挖掘不该错过的细节** | **[20个灵感细节切口](deliverables/chanlun_108_acceptance/02_SPARK_INDEX.md)** |
| **阅读全书综合评述** | [AI独立全书评述](deliverables/chanlun_108_acceptance/00_REVIEW/FINAL_BOOK_SYNTHESIS.md) |
| **查看108课详细解读** | [单份规范章节研究](analyses/books/chanlun/chapters) |
| **对照原始PDF** | [唯一原书来源：缠论五卷](ChineseBooks/缠论) |
| **浏览110条未来验证命题与36个跨课案例** | [形式化研究案例](deliverables/chanlun_108_acceptance/03_formal_cases/README.md) |
| **研究下一本书怎么做** | **[交易书籍AI深度研究工作流（G0—G6）](docs/BOOK_RESEARCH_WORKFLOW.md)** |
| **文件去重与核验情况** | [规范来源与清理报告](deliverables/chanlun_108_acceptance/00_REVIEW/ACCEPTANCE_REPORT.md) |
| **哪些细节仍可能遗漏或待复核？** | [11处优先复核入口与全书覆盖边界](deliverables/chanlun_108_acceptance/00_REVIEW/DETAIL_COVERAGE_GAPS.md) |

## 原仓库规范编辑源与每书独立镜像的分工

- 原书按语种与书名存入`ChineseBooks/<书名>/`、`EnglishBooks/<书名>/`，研究报告使用`Reports/`。确认版权或分享权限后再考虑公开原文。
- 原书目录、文件哈希、不同版本日期、出处保存在`catalog/`；章节研究放在`analyses/books/<book_slug>/`。
- 结构化引用证据保存在`knowledge/`；跨学科独立想法在`ai_thoughts/`；需要时保留独立数学反例、已有研究协议和测试在`experiments/`、`tools/`、`tests/`。
- **G7新约束**：每本书一套独立`<BookName>Collection/`完整镜像，原有规范目录不迁移，旧CI/引用保持可用。所有规范文件，包括PDF和工具，按相同相对路径镜像，逐文件比对Git blob SHA、大小与清单；每步变更必须更新工作流日志和镜像。
- 不在已有内容的目录保留空`.gitkeep`，不保留同一资料的“最终版再复制”或中间OCR/假说批次输出；保留唯一可信来源和Git历史即可回溯。

## 《缠论》当前研究成果

五卷共108课首轮文字研究、108份结构化证据、84个概念节点、145条关联、16条带来源身份的规则版本研究均已归档。全书已经整理**110条明确标记的AI待检验假说**与**36个跨课程形式化验证例子**，均未运行真实市场实证。详见[验收目录](deliverables/chanlun_108_acceptance/README.md)。

**已知缺口**：有些图表精确数字及后附编辑日期尚未完成独立终审；没有完整合法且唯一的笔—线段—中枢解析证明，没有真实A股无前视交易实验、样本外收益或风险实证。既有V1—V4合成研究代码仅在唯一规范目录保留以备查证，**按用户要求不继续扩建回测实验室**。

## 下一本书的标准交付：先快览、再发现细节

上传书籍 → 原书SHA和目录/图页索引 → **立即制作带覆盖状态的5分钟全书速览** → 全书逐区域同时识别CORE主干和SPARK冷门灵感 → **15—20分钟思想地图＋可浏览灵感卡** → 按兴趣深读章节、补上重要图像来源 → 全书AI独立长评 → 待验证形式化题目（`NOT_RUN`） → 去重验收和临时ZIP。

**不必读完所有逐章深度报告才能先获得全书整体认识，也不让“精简重点”吞掉那些令人意外的小细节。每一本书还必须交付独立的AI深度导读：定理/定义白话、作者行文脉络、可编辑图示、AI独立评论，不能只交摘要。**

详细验收门槛、目录模板、缺失证据处理、只读离线ZIP构建流程见 [docs/BOOK_RESEARCH_WORKFLOW.md](docs/BOOK_RESEARCH_WORKFLOW.md)；一般研究规范见 [七重解析标准](docs/ANALYSIS_STANDARD.md)、[阅读协议](docs/READING_PROTOCOL.md)、[证据与版权](docs/EVIDENCE_STANDARD.md)。

**研究免责声明**：这是可审阅的书籍研究，不构成交易建议、实盘指令或盈利承诺；未经授权不重新分发原作者受版权保护的整卷内容。
