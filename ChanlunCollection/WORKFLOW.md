# ChanlunCollection｜本书实施工作流 v4.70.0

此文件说明《缠论》在项目[通用工作流](../docs/BOOK_RESEARCH_WORKFLOW.md)下的执行方式；其源工作流文档位于仓库根`docs/BOOK_RESEARCH_WORKFLOW.md`，本集合内部同一路径有经完整性校验的镜像。未来新书使用各自`<BookName>Collection/WORKFLOW.md`。

**v4.62.0 补查第101课强源门：**第101课作者直接提出**唯一递归分解**且宣称改变a0不损唯一性，研究者必须区分“每个固定a0/政策下唯一”与“跨a0输出完全相同”，也必须注意凯翔A016说“第三层正文未明总结”而作者第101课其实已明言唯一分解，故H5不能仅靠该段就等同他第三层。参见[本轮报告第七节](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_LESSONS_98_100_LIVE_MULTILEVEL_STATE_TREE_V462.md)。

**v4.70.0 端点触边的三重证据门：**[第20课等号与第38课触边词义、首次回抽计数的双证据审稿](deliverables/chanlun_108_acceptance/00_REVIEW/CHANLUN_L20_L38_BOUNDARY_TOUCH_RETRACE_ROLE_V470.md)。第20课三买\(L=ZG\)/三卖\(H=ZD\)符合数值不破界，但第38课「跌回中枢里」并未明确解答**恰好触边**是否属于回入；保存`P20_PRICE`（可通过）、`P38_ROLE`（等号可UNKNOWN）、`P18_DESTRUCTION`（不能由价格推出）及完整g−1回试证书、首知时间。g−2两次内部回拉只可能归同一个g−1回试，不允许自行消耗两次首次资格。端点身份`BORDER_TOUCH_UNRESOLVED`，F01/OB38/OB99 OPEN，市场NOT_RUN，凯翔100答/五卷不修改。

**v4.69.0 第38课内部两回抽不等于两次完整次级回抽＋第54课连接拓扑门：**[作者署时回复与第18/20/38/54课直接对照](deliverables/chanlun_108_acceptance/00_REVIEW/CHANLUN_L38_NESTED_RETRACE_AND_L54_SAMELEVEL_CONNECTOR_SCOPE_V469.md)。第三类点首次合格回抽按目标`g−1`**完整走势类型身份**计数；g−2两个回试可能只是同一个g−1内在成员，返回原中心内仍属震荡，不能错误“消耗第三点首次外回抽”或把两次低级回试作两个次级回抽。2007-03-21作者署时评论载历史镜像非原新浪comment法证字节；2007-02-28 13:37/13:51市场数据未重放。第54课两个同级独立中心不能无合法下级连接硬拼，且三个下级中心构更高级中心是另一个定义域；同第38课R_cut把六合法下级段分成两个**已完成g盘整类型**的情况要分开，禁止拿不同对象互证全域同一。信号应锁定`R,g,center_id,connection_id,child_retrace_id,subsub_event_ids,first_known`；ROOT-IDENTITY/EXIT和OB38 CONNECTOR_POLICY_DOMAIN未证，真实行情NOT_RUN。

**v4.68.0 第43课历史分界与后续条件证实的双时钟门：**[第38/39/40/43课原文分岔及署时2/26回复](deliverables/chanlun_108_acceptance/00_REVIEW/CHANLUN_L43_FUTURE_CENTER_BRANCH_AND_FIRST_KNOWN_BOUNDARY_V468.md)。在c内1分钟背驰t_b后作者允许未来30分钟C与旧B不重叠（30分钟原走势延续）或重叠（高级重组、30分钟同级分界可落回t_b），因此**不能凭后来C条件的真假倒填t_b当时已知该高层归组**。记录t_b_price/t_b_known、future_C_qualified/t_C_known、B_C_relation_known、historical_split_label_time、f1/R/g及策略换档选择时刻。第39课**固定R已完成Ai+1**的原作者前缀稳定性与第43课**待定跨级组**分开；第40课是否换档是交易者之后的独立选择，历史订单不可复写。2/26历史作者归属回答“之前中枢属于前一走势、只列前三段但延伸可能存在”仍需注明来源非原新浪评论字节。F01/OB38/OB99 OPEN，NOT_RUN。

**v4.67.0 2007-03-20作者历史回帖与L36跨政策双中枢门：**[第35/36课+《论语》58评论源文](deliverables/chanlun_108_acceptance/00_REVIEW/CHANLUN_F01_AUTHOR_REPLY_20070320_NONREUSE_AND_L36_POLICY_DEPENDENCE_V467.md)。原新浪《论语》58文章独立可见但原评论数据库未见，2007-03-20 17:39:28回复仅标`ARCHIVED_AUTHOR_REPLY`。该答复否认“三笔同价→直接翻转”，并明确合法组合中**归到前括号的构件不得重复归后括号**；不能把`(A+B)+(B+C)`误写成与`A+(B+C)`一样的结合式。第36课原作者亲述同一行情两个合法30分钟组合的中心[2892,2911]与[2905,2947]以及不同第三买点ZG阈值；信号计算应记录`f1/R_at_t/g/center/first_known`并禁止跨R混合。此为中心身份同式不复用的作者级证据，**非**严格逐笔所有共享滑动三笔窗口的完整唯一归属程序。ROOT-IDENTITY/ROOT-EXIT OPEN，F01/OB38/OB99 OPEN，真实市场NOT_RUN。

**v4.66.0 第35课局部成立见证/中枢身份门：**[同价三笔构造、第18课新中枢判别和第20课延伸/新生原文证明义务](deliverables/chanlun_108_acceptance/00_REVIEW/CHANLUN_F01_THREE_TRADE_SEED_WINDOWS_VS_CENTER_IDENTITY_V466.md)。冻结严格逐笔f1及R/g：同价成交`p^n`有n−2个互相重叠的长度3成立见证，**不得一见证新造一中心ID**；需另有`CENTER_ID`归属/延伸、新生与首次可知规则才能计第35课N>2前后中心。第20课例子用实用1分钟，不能直接移植为逐笔根层的去重算法；研究者的“合并重叠窗口”也不是已证的作者公式。F01=ROOT-SEED已定义/ROOT-IDENTITY未闭合/ROOT-EXIT未闭合，禁止把候选中心重复计数用于第100课完整回抽或高层三卖。OB38/OB99 OPEN、市场NOT_RUN。

**v4.65.0 最低完成的时间量词门：**[第17/18/20/35/38/84课全称完结与任意长延伸的作者语义](deliverables/chanlun_108_acceptance/00_REVIEW/CHANLUN_F01_UNBOUNDED_EXTENSION_FINITE_COMPLETION_QUANTIFIERS_V465.md)要求研究者对每条“必然结束/可以无限延伸”判据明确同一a0、R、g、走势身份和允许的完整市场轨迹论域。任意长的可能有限延伸≠存在一条实际合法无限轨迹不完成，前者足以否定由中心成立推普适固定结束时限B，却不能自动证伪全称终完美。第35课最低趋势N>2非推进后续中心**必须先合法形成**才能认定其停止条件；它不适用单中心最低盘整，且后来证据时刻不等于原价端点时刻。第84课允许不同f1不能替代完整底层盘整完成函数；第20课第三点不能在逐笔原子底层引用不存在的g-1。F01/OB38/OB99 OPEN，市场NOT_RUN。

**v4.64.0 线段与完整走势类型必须分开出具证据：**[本轮第67/71/78课原文与第100课C3接口](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_L100_LINE_SEGMENT_VS_MOVEMENT_COMPLETION_V464.md)。按作者第67课区分有/无缺口线段终止，71课转折后一笔待定及第三笔破不同位置之反向结果，78课笔破坏未必段破坏；记录`pivot_price_time`和`segment_first_known_time`，标准化线段区间不覆写原轨迹。第72课最低中心和走势类型严格在笔/线段**后面**，作者2007-07-20原新浪博文直接否认严格把线段视为最低走势类型次级别；所以只有SEGMENT_END证书不能补第100课首次1分钟回抽完整结束的G2。源文本辨析结束，F01/OB38/OB99 OPEN，市场NOT_RUN。

**v4.63.0 五分钟三卖完成资格审稿门：**[第18/20/53/100/101课的六收据、三时钟和作者案例后件限制](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_L100_THIRD_SELL_FIRST_CONFIRMATION_PROOF_CHAIN_V463.md)。每个三类卖点申请必须分别出示g级原中心的三完成低级成员与ZD、第一次向下离开之合法次级走势、底背驰后第一次合法回抽已完成、全回抽高点不升破ZD以及t_retrace_known/t_sell_known。第一次回抽尚未定型，哪怕现时价格低于ZD也只准标候选；任何一个信号不自动证明第二个g中心，更不自动改变g+1层。第53课正文与2009后人补充不得混写。不得从图上峰值倒填当时完成证书，F01/OB38/OB99 OPEN，NOT_RUN。

**v4.62.0 原作者具体多级事件顺序门：**[第98/100课30/5/1状态分支](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_LESSONS_98_100_LIVE_MULTILEVEL_STATE_TREE_V462.md)要求每个跨级解释都从课文**当时可知的分级状态**起步：当前何种级别正在震荡、哪些中心/三卖尚未确认、首次低层事件、随后的回拉是否触发5分钟三卖、为什么30分钟未立即变化、哪条后续完成与回试才有资格触发30分钟改变。第98课强调未见未来结果时不应先假设路径；第100课示范为三卖而非凯翔A026的三买。不得将原作者示例简化成通用必赢算法，不能从某一级底背驰直接出具上一级或大两级中心完成证书。F01/OB38/OB99 OPEN，NOT_RUN。

**v4.61.0 原文三区间/动态排除门：**[新原作者公式与凯翔A026推理对账](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_THREE_OVERLAPS_AND_ASOF_ELIMINATION_V461.md)。在任何走势重叠判断前先指定比较的是Zn与本级核心、相邻同级中心外围波动，还是后继高一级中心与前走势最后中心；不可把不同区间的“触及/包含/重叠”合并。第20课Zn离开中心核心只可先得到“更高级中心**或**趋势”，高级中心是否形成需同级外沿波动真正交叠。第99课“至少落在”不是已证明整个高层核心包含旧中心。对于凯翔A026的每项候选，必须输出“未观察到”或“已证失效”，不得以未出现作为排除证据。只读原文字义，本轮不碰五卷/100答、不运行市场，F01/OB38/OB99 OPEN。

**v4.60.0 跨课证明桥门：**基于[原作者第18/20/38/99课与凯翔A016/A026对照](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_CROSSLEVEL_COMPLETION_AND_CENTER_RECONCILIATION_V460.md)，今后跨级结论必须独立审核：同级分段政策R是否考虑高级别？两个中心外沿波动是否符合第20课升级条件？第18课“可以结束”有无实际完成证书？第99课未来更大中心的可知时间/区间几何是否已独立验证？第99课“中阴一般划分未明”不等于所有同级别片段不可用，二者不同命题。仅由六段两个盘整不得出具高级中心或已完成交易信号。原100答、5卷PDF、108课不改，F01/OB38/OB99 OPEN，NOT_RUN。

**v4.59.0 本书原文审稿门：**用户确认上传凯翔回答确实100条，研究样本即A001—A100。新增[第17/18/38课与凯翔第二层的分解政策核对](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_POLICY_SCOPED_NEXT_TYPE_AND_THIRD_LAYER_V459.md)：第38课明确允许同级别固定分解下盘整接盘整，故“完成后必转另外两种”若要成为强全称命题必须限定R/g/“完成”对象；不能混淆中心存在、可结束、政策截断、独立完成和相邻类型。第99课H4跨级后继、第102课H5递归整体表达均有作者原文但**均不是凯翔已说出的第三层**；A087第二中枢方法仍未披露。今后每个具体书籍都应核查看似相同的术语有没有改变分解政策、输入层级与时钟，而非以AI猜测代替作者公式。F01/OB38/OB99 OPEN、真实行情NOT_RUN。

**v4.58.0 基础设施同步：**新增仓库级G0预检CI（Windows/Linux × Python 3.11/3.12）。旧G7镜像规则覆盖根工作流，故按原规则把G0 CI与通用工作流同步进入本书集合并刷新manifest；未修改《缠论》原PDF、100答、推理结果或F01/OB38/OB99状态，未运行真实行情。下书G0材料入库只有格式/SHA与待审权限收据，不是阅读结论。

**v4.57.0 本步：**新增[源价与退出元数据来源守恒验证](tools/audit_kaixiang_exit_evidence_v457.py)、[三条人工+1 tick声明输入](tests/fixtures/kaixiang_exit_evidence_v457.json)、[18项测试](tests/test_kaixiang_exit_evidence_v457.py)与[报告](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_EXIT_EVIDENCE_CONSERVATION_AND_COUNTERFACTUAL_V457.md)。从v4.56的27笔合成价格回溯显示：t=9/18/27仅可确认**局部条件满足**，t=10/19的所谓退出时间对应**下一分组合成价格**，t=28没有新的成交；v4.55自动附上的三条退出收据都只是研究者元数据，不是独立真实完成证明。工具严格让`independently_completed_movement_count`为0，并拒绝伪造来源或交易认证；后续接入行情也必须先补合法原始逐笔完整性与退出证书，不能直接复用合成声明。F01/OB38/OB99 OPEN，市场NOT_RUN。

**v4.56.0 本步：**将v4.55反例研究由“先写好价区间及DOWN标签再生产价格”推进为[合成原始价格的前缀自算](tools/audit_kaixiang_raw_tape_prefix_v456.py)。以冻结的27个虚拟价格，从可见三同价组出发推导3个中心、方向及第三中心是否继续创新高/低；同旧F01图对照时保持明确两时钟：t=9有局部条件，t=10才有**人为给出的退出收据**，退出条件没有独立原始证据。新增[报告](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_RAW_TAPE_DERIVED_PREFIX_AND_EXIT_ASSUMPTIONS_V456.md)、[固定价带](tests/fixtures/kaixiang_raw_tape_v456.json)、[16项定向测试](tests/test_kaixiang_raw_tape_prefix_v456.py)、书籍集成CI和完整镜像。仓库自锁SHA≠真实源认证，F01/OB38/OB99 OPEN，市场NOT_RUN。

**v4.55.0 本步：**优先消除旧F01研究桥的假阳性，不再把`DOWN+NOT_LOWER`仅当作输入字符串即可采信。新[可执行三中枢方向必要条件门](tools/audit_kaixiang_f01_direction_three_centers.py)复用原F01图检查后，对最低级别三单价中枢c1/c2/c3增加**已建立原方向**和**第N个不再延续原方向**的原始价序检查，并用每中心3个同价合成源点保存证据。43节点图、四时点、16项单测中有两例旧门会放行而新门拒绝的反例；详见[完整报告](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_F01_INITIAL_DIRECTION_THREE_CENTER_GUARD_V455.md)。这不涉及真实行情、不自动认证完整走势完成/买点，F01/OB38/OB99 OPEN。

**v4.54.0 本步：**首次实际调用既存F01图收据检查器，为凯翔A026的三段价格交集附上**31节点合成证据依赖图**，并强制检验3个完成走势的价格界、首次可知时间与底层虚拟点相符。[研究报告](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_F01_DEPENDENCY_GRAPH_BRIDGE_AND_COMPLETION_LIMIT_V454.md)及[新工具](tools/audit_kaixiang_f01_graph_completion_bridge.py)、[fixture](tests/fixtures/kaixiang_f01_graph_bridge_v454.json)、[15项定向单测](tests/test_kaixiang_f01_graph_completion_bridge.py)都说明：F01图的结构正确**不是**作者原始算法、真行情完成证书或买点认证；尤其底层趋势未创新低/高比较仍是未经独立验证的声明。F01/OB38/OB99 OPEN、市场NOT_RUN。

**v4.53.0 本步：**新增[三已完成次级段合成交叠与凯翔候选清单的时点桥](tools/audit_kaixiang_center_asof_bridge.py)、[五个场景12个时点](tests/fixtures/kaixiang_center_asof_bridge_v453.json)、[15项测试](tests/test_kaixiang_center_asof_bridge.py)及[解释报告](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_THREE_COMPLETED_MEMBER_ASOF_BRIDGE_V453.md)。调用原有`audit_chanlun_lesson099_resegmentation.center_asof`，用**first_known_tick**代替回顾性`completed_at_tick`防提前使用晚知第三段；只确立局部正宽度交叠，不证真实次级走势类型完整、完整中枢或三买。v4.52原候选与账户风险状态不随交叠改写，不读取行情，F01/OB38/OB99 OPEN。

**v4.52.0 本步：**把凯翔A026的候选排除转化为可执行但严格局限于合成语义的前缀检查，继承v4.51的8个原话来源锚。新增[纯符号源代码](tools/audit_kaixiang_asof_candidates.py)、[8组时间前缀情景](tests/fixtures/kaixiang_asof_symbolic_v452.json)、[14项测试](tests/test_kaixiang_asof_candidates.py)、[审计报告](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_CANDIDATE_EXCLUSION_CLOSED_WORLD_AND_RISK_GATE_V452.md)。核心：候选只剩一个仍不是最后类型已确认；拒绝同级分解规则或具体片段身份偷换，已观察和首次可知时点分离，账户风险提示不当交易成交事实。本轮仅用合成文字事件，不读取真实行情、不运行交易；A094/A058评论仍无可认证记录、第二套中枢公式与第三层未披露，F01/OB38/OB99 OPEN。

**v4.51.0 本步：**不再只概括100答核心名词，使用A026/A073/A061/A084/A016/A074/A095逐篇原文严格区分“当前观察到的技术条件”“最终类型完成”“在当前条件下排除某候选”“交易执行与独立风险限额”；新增[无前视逻辑审核报告](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_ASOF_ELIMINATION_VS_STRUCTURAL_STOPS_V451.md)及人物文件夹[8个有来源、反例和禁止过推论字段的JSON研究契约](OtherVoices/speaker-unknown-001/decision_audit_v451.json)。特别标记A074结构解读仍有效但A095期货止损应快这一潜在风险，`Exit=结构失效OR账户风险上限`属于**研究者建议**不是凯翔隐藏“杀招”。A094/A058与主页公开取证无法取得评论（403/抓取失败），不增加C编号；F01/OB38/OB99 OPEN、真实行情NOT_RUN。

**v4.50.0 本步：**从局部“第二中枢”追问升级为100篇全集跨主题研究。归并A058十三字、A085六要素、A014五维条件，强调凯翔A087结构级别和A085计划持仓级别用词不同，不能偷成同一递归函数。第99课“完成走势→至少高一级中枢震荡及最后中枢价格区间关联”列为A016未明言的**第三层H4候选**，逐项给原文依据、否定条件与研究者推断资格。A094/A058明确指向有实质信息的评论区但上传无单列评论，优先登记评论来源缺口。详见[第50轮专题](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_100_ANSWERS_SYSTEM_CROSSLEVEL_AND_COMMENT_GAPS_V450.md)，不修改原始100答。F01/OB38/OB99 OPEN、市场NOT_RUN。

**v4.49.0 本步：**新对照原作者2006-12-28可不打开下级K线的熟练观察、2007-01-11“不够严谨”的上下上/下上下助记、2007-02-05 15:50:54中枢精确定义与16:59:23未来必达目标级别的动态强句、03-08两种看法和03-21第38课分析政策，系统排除不能当独立中心定义的候选。更正v4.47过强缩域，但不认证全量词或完成证明；凯翔第二套完整公式/第三层均缺其本人解释。详见[专题](deliverables/chanlun_108_acceptance/00_REVIEW/KAIXIANG_SECOND_CENTER_METHOD_TYPE_AND_FEB05_DYNAMIC_CLAIM_V449.md)。F01/OB38/OB99 OPEN，实证NOT_RUN。

**v4.48.0 本步：**已获得用户上传的知乎凯翔100条回答原文，在[OtherVoices单人目录](OtherVoices/speaker-unknown-001/README.md)建立原始字节、100个URL、关键短引、AI分析和评论缺失记录，避免丢失原说话者的真实语境。六点A089/A090已找到原话、第二种A087仍需具体算法、第三层A016未说出、A007引用另一交易者。全部成果见[审查报告](deliverables/chanlun_108_acceptance/00_REVIEW/KAI_XIANG_100_ANSWERS_FIRSTHAND_AND_THIRD_LAYER_V448.md)；用户导出文件可靠性与知乎在线平台认证分开，F01/OB38/OB99 OPEN、NOT_RUN。

**v4.47.0 本步：**[校勘“任何级别”真正主语并审第99/102课的当下分类强度](deliverables/chanlun_108_acceptance/00_REVIEW/LEVEL_TYPE_DOMAIN_2007_REPLY_AND_OB99_OB102_V447.md)。新增有类型命题V=已独立准入g级走势最终形成中心，纠正v4.45的A=所有原始行情对所有级别的过强摘句读法。第20课低级别持续不保证高一级中心，但是否已存在可独立定义的高一级走势仍未证；第99课一般划分中阴待定与第102课当下可控不宜用“纯历史分类”直接遮盖。人物档案只更新AI分析、不触动缺失的原话。F01/OB38/OB99 OPEN，NOT_RUN。

**v4.46.0 本步：**新建`OtherVoices/`独立人物索引和`speaker-unknown-001/`子档案，同目录保存发言原话、AI分析、来源、更新历史。规范源位于`other_views/chanlun/`，扩展`book_collection.py`安全镜像映射，新增测试核对目录与源身份，不破坏108课数据。现有高手的六项研究只是`PARAPHRASE_ONLY`，原话尚未恢复，禁止冒称逐字稿；进展和待办见[人物入口](OtherVoices/README.md)与[Issue #110](https://github.com/CrazyA1ice/TradeBooksInAIsEyes/issues/110)。本轮优先实现复用知识资产和新增说话者工作流，F01/OB38/OB99仍OPEN，市场NOT_RUN。

**v4.45.0 本步：**定位第20课极端只有低层中心、2007-02-26作者署时评论“任何级别最终形成中心”的量词歧义；建立E（某级别）/A（所有级别）/T（已完成类型）三种有类型谓词及严格非蕴涵模型，补齐第17、18、35、102课的完成/唯一/可知分层。修正“作者从未提供盘整出口”的过强旧判断：一般层退出已在02-26答疑见第三类点线索，最低逐笔根完成仍OPEN。新增[研究专篇](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_ANY_LEVEL_CENTER_QUANTIFIER_AND_EXIT_DOMAIN_V445.md)，关联[Issue #110](https://github.com/CrazyA1ice/TradeBooksInAIsEyes/issues/110)。本轮仅逻辑解释与来源校勘，高手原帖未获；F01/OB38/OB99 OPEN、NOT_RUN。

**v4.44.0 本步：**原作者第60课2007-06-19提前明确最低线段操作截断；2006-12-27第19课21:05作者署时二级评论谈一字线最低价值中枢，此早期措辞无法自动替换第35课严格逐笔交易三同价基例。把绝对严格交易a0与实用分型笔线段a0分别建类型合同，显式区分中心已成立、盘整可结束、盘整已在某历史时刻独立确认完结。条件性同前缀延续/退出模型证明三同价不能仅凭前缀推出唯一终结，未找到最底层全部行情退出特则，不伪称理论反证。完整[新研究报告](deliverables/chanlun_108_acceptance/00_REVIEW/ABSOLUTE_PAN_BASE_VS_OPERABLE_SEGMENT_CUTOFF_V444.md)，F01/OB38/OB99 OPEN、NOT_RUN。

**v4.43.0 本步：**找到2007-03-20 18:16:44作者正面答复“低层回试盘整可无限延伸如何完结”，连同18:55:11“可结束不等于已结束”、17:39:28“最低三笔同价不必翻转”及3月21日16:56:34“次次级两次回抽属次级一次结构内部”，从原文限定最低完成/跨级计数。源码建立1级父回抽、0级微走势的独立完成声明审查，标记t10已见微构件与t12才声明父级出口的区别。**绝对最低层第三点需要不存在的负一级已完成走势**只表示现有规则子集缺一个基础终结特则，不证明原文全局不可实现；F01/OB38/OB99 OPEN、NOT_RUN。详情[最低盘整专题](deliverables/chanlun_108_acceptance/00_REVIEW/MINIMUM_PAN_END_NESTED_RETRACE_AND_BASE_GAP_V443.md)。

**v4.42.0 本步：**按作者2007-03-21 16:19/16:29二手归档评论确认：旧中心此前向下回到中心内部属于未结束的中枢震荡，不消耗“首次合格回试”资格；首次未返之后同一中心再外返不另发三买。独立固定政策有限前缀模拟区分t10价格极值与t12完成资格首次可知。第20课low>=ZG与三月“不回”在边界等于ZG处保留分叉，不擅创唯一解析规则。完整报告[原问答与事件审核](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_FIRST_ELIGIBLE_THIRD_RETRACE_ASOF_V442.md)。实用双a0到已完成下级走势的桥仍未建成，F01/OB38/OB99 OPEN、NOT_RUN。

**v4.41.0 本步：**首次直接发现原新浪2007-07-20 08:26:20主文，并连同7月19日提问一起定位：理论实际逐笔成交a0与实用分型笔线段a0，共享向上递归形式而非全部输出同值。作者严格反对把线段当最低走势类型的次级别。作为对高手理论第一种/实战第二种的当前最强原文解答，记录[新专题](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_PRIMARY_SINA_DUAL_A0_THEORY_V441.md)；该原博客可访问不等于2007年历史字节签名，原图像素和老虎版未获。F01/OB38/OB99 OPEN、NOT_RUN。

**v4.40.0 本步：**新找到并交叉验证作者2007-05-21 16:41:03、2007-07-11 16:32:08、2007-07-31 16:43:17/16:50:47/16:55:59五条署时答疑。九段裸重叠与已完成三三组合再递归中枢结果“不一定相同”；级别内延伸固定前三段核心与跨级对象升级不可混淆，线段或次级走势未完成时绝不升级。另对2008年左右编纂PDF印刷p164—165做实际页面目检，未经版权许可不复刻整本；2025年第三方的“所有段再交”不是原作者公理。见[新专题](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_NINEFOLD_CENTER_333_AUTHOR_REPLIES_V440.md)，原高手和老虎版仍未认证，F01/OB38/OB99 OPEN、NOT_RUN。

**v4.39.0 本步：**将“第二种中枢定义”拆成6个不同对象类型，尤其核对第54课当d4对两种合法分解作者明确以实操清晰度偏选第二种、但g7两套结构标签不同。第20课回调/回升只是同一区间公式的两种方向；第18/20课固定前三段中枢核心不可被“后续全部成员再交”偷换；第38课两纯视角/跨级混合和第83课两种底层构件保持独立。完整逐句反证[六候选裁定](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_SECOND_CENTER_METHOD_DISAMBIGUATION_V439.md)，包含四个原作者图解节点和人工区间的三个函数区别。未找回原高手首帖、老虎版/新浪源字节、全理论完成证书；F01/OB38/OB99 OPEN、NOT_RUN。

**v4.38.0 本步：**以2007-03-08作者16:10/16:38完整问答为起点，区分a+B+b纯走势组合、纯中枢前三段震荡及第38课提出的**跨级混合更有效**第三条处理策略；记录作者2958更正为2858与9段五分钟的特定历史条件。老虎整理版只核实PDF/DOCX文件名，尚无SHA、全文及完整率。二手作者归档不当原新浪文件；F01/OB38/OB99 OPEN、NOT_RUN。[阅读报告](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_AUTHOR_REPLY_TWO_METHODS_AND_LAOHU_V438.md)。

**v4.37.0 本步：**从第15、16课传统K线周期视角，经第17/18课中枢定义、第33课早于35课的严格交易级别、第35课递归基例、第38课两种分析视角、第72课作者教学回顾、第83/84课底层稳定性变化，重新核对高手的断代论。区分作者真实评论、转载资料和AI推理；特别不把周期近似、两种走势观察和不同底层零件当作完全相同的“两个中枢定义”。新报告[历史时间线与两种方法](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_HISTORICAL_LEVEL_SHIFT_AND_TWO_METHODS_V437.md)。本轮非108课逐字重新通读，老虎版未认证，F01/OB38/OB99 OPEN，NOT_RUN。

**v4.36.0 本步：**拆分作者第17/18课“终完美／延伸”中的EV、UB、IN三个量词，第38/102课固定政策唯一FU与跨政策一致PI，以及第99课中阴时的在线完成确认ON。独立研究者字母串反模型仅验证逻辑蕴含，不能冒充市场或作者解析器。逐字专家原帖未认证，F01/OB38/OB99 OPEN、NOT_RUN。见[量词审计专题](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_COMPLETION_QUANTIFIERS_V436.md)。

**v4.35.0 重点补充：对那位高手的六条批评进行全书语义审计，而非无限增加局部仿真测试。** 核对第15/17课“上涨/盘整”从高低点外观变成完成走势的中枢计数；一个中心虽外观方向上移，作者仍称结构盘整（但不自动已完成）。第35课严格逐笔`f1`与第17课单位K线`f1`、第72/83课后期严格线段`f1`不同；第84课允许`f1!=f2`。第35课自下而上构造与第27/102课自上而下区间套是**证明生成和候选定位不同操作**，第44课明说小背驰/大转折只有必要非充分。第83课作者本人已承认单笔导致底层分解不稳，不能把跨级自同构当成各级噪声、交易费或胜率相同。第54/69课存档有图，但历史原发图片和子分钟行情未充分认证。尤其第99课中阴暂时不可分与第102课已完成结构的“唯一分解”要按**历史完成/在线待定**分开；作者并没有把研究者称呼的“第三层”作为第17课正式原理编号。专家原始六条逐字引文/原始网址目前未恢复，严格标`EXPERT_PARAPHRASE_NOT_ORIGINAL_QUOTE`。[整书六条批评研究](deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_SIX_CRITICISMS_WHOLE_THEORY_THIRD_LAYER_SYNTHESIS.md)、`catalog/chanlun_expert_six_criticisms_source_matrix_v1.json`和专用证据审计。F01/OB38/OB99仍OPEN；没有实际市场数据或回测，`NOT_RUN`。

**v4.34.0 重点补充：先冻结底层f1再谈任何走势完成和高层中心一致性。** 第17课把选定不可再分的**完整单位K线三段价格区间重叠**作为实用最低中枢起点，第35课则明确“最严格”以原始**连续三笔同价成交**构底层中枢。两种谓词不自动互换：六笔价格`10,14|11,15|12,16`在各根固定K线中有共同区间`[12,14]`，却无三笔同价；七笔`10,10,10|20,22|30,32`有三笔同价，却无三根K线区间相交。两条仅为**共同逐笔流及其固定bar分桶的虚构反例**，不是历史原图或作者矛盾证明。第72/83课后期允许线段初始化，第84课正式强调`f1`与`f2`可不同；第38课选定操作级别六条**已完成**次级走势分成盘整+盘整，也不能倒过来解决绝对底层单中心盘整的完成时钟。详见[完整证明](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_F1_INITIALIZERS_NON_EQUIVALENCE_AND_BASE_PAN_CLOCK.md)、`catalog/chanlun_f1_unitbar_trade_non_equivalence_v1.json`及其专项源页与双向数值审计。**一个最低中心存在不等于最低盘整当下完成**。F01/OB38/OB99继续OPEN，真实逐笔行情与回测NOT_RUN。

**v4.33.0 重点补充：第20课中心整体极值比较的部分解与最低盘整无负一级基例。** 作者的`GG/DD`来自中枢内合格Z段的最大高/最低低，`ZG/ZD`是核心区间的上/下边；[第20课](https://eczsc.com/originals/20)中心定理二给四组有条件的比较：`后DD>前GG`严格上涨，`后GG<前DD`严格下跌；`后ZD>前ZG且后DD≤前GG`上行扩展，`后ZG<前ZD且后GG≥前DD`下行扩展。即使核心同样上移，整体外沿极值不同也可使严格分离/扩展分类不同；核心相接或重叠不满足这些严格式时不得默默变成`第35课N>2不再高于`。另外第35课以每一笔成交为绝对最底`f1`，此处**不能**机械套用第20课要求“完成的下一次级别离开及首次回抽”的统一三类点出口来结束最底层单中枢盘整——没有已定义的负一级走势类型。需要补出作者明确的最低单中枢盘整终止特例或获准的f1映射。新增[研究报告](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_F01_CENTER_ENVELOPE_ORDER_AND_BASE_PAN_DOMAIN_GAP.md)、源锚四式与七套虚构四元组、数值审计及22个反向测试；只有局部`PASS_LOCAL_FORMULAS_ONLY`，F01/OB38/OB99继续OPEN，市场NOT_RUN。

**v4.32.0 重点补充：以最低真实成交为证明叶子和无循环完成收据。** 现在有第35课`CL35-SO-2`“连续三笔同价形成最低中枢”和`CL35-SO-9`“最低趋势第N个(N>2)中枢不再更高/更低，方向性结束”的原文锚点。两种规则不能互换：最低中枢存在不等于其单中心盘整终结，而`N`中心的“更高/更低”尚无原文统一数值算子。将第18课的三连续**完成**次级走势交集、20课**完整**离开/首次回试与`>=ZG/<=ZD`、2007-08-21署时评论的盘整/趋势退出按依赖边构建。任何`FINISHED_MOVEMENT`须有自身退出证据，图无环、同`f1/f2/R_g`政策、首次可知不早于依赖；原始逐笔流、真实退出声明没有独立认证时，即使代码通过也**只能说`PASS_STRUCTURE_ONLY`**，禁止当成作者理论已证明。新增[专题研究](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_F01_PROOF_CARRYING_COMPLETION_RECEIPTS_AND_BOTTOM_CASE.md)、`catalog/chanlun_f01_completion_receipt_contract_v1.json`和22项虚构结构用例。F01/OB38/OB99 OPEN，实际行情NOT_RUN。

**v4.31.0 重点补充：2007年作者答疑的走势退出条件与逐级无循环完成证书。** 已核对2007-08-21 16:20:01作者关于盘整第三类点与趋势本级背驰后回拉的**另文评论转载**，并校正某些教学材料误标“第72课正文”的归属（第72课正文同日22:37:20才发表）。同期16:27:28及17:02:26作者补答“笔破坏与线段破坏不是等价事件”；2007-05-09作者答疑还强调C2回试没结束时不能提前宣称三买。审核原则：盘整完成的三类点必须先有合法中枢和**完整的下级离开、首次回试走势**及第20课边界；趋势结束则须该级别背驰和其后实际回拉。分开历史拐点与首次可认证时刻，禁止把退出事件倒过来证明它自己依赖的下级回试已经完成。相关[新研究](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_AUTHOR_REPLY_COMPLETION_EXIT_EVENTS_AND_NONCIRCULAR_PROOFS.md)、`catalog/chanlun_author_completion_event_witnesses_v1.json`和源码闸门；未取得新浪原回帖字节、原始行情或完整解析器，`F01/OB38/OB99=OPEN`，`NOT_RUN`。

**v4.30.0 重点补充：同名线段的跨课有类型准入。** 第53课完成低层走势从上层视角可视为无内部结构的线、第54课则把子一分钟g/d段**预设为此种抽象线**，不能直接声称它们是第67/71/78课以后经过笔/特征序列/缺口/合法破坏认证的严格线段。第83课使用严格线段构成最小中枢也不自动证明第18课要求的**完成次级走势类型**。新增[原作者来源锚定的桥梁矩阵](deliverables/chanlun_108_acceptance/00_REVIEW/LESSON54_F1_F2_COMPONENT_ADMISSION_AND_UNPROVEN_BRIDGES.md)、`catalog/chanlun_l54_f1_f2_typed_bridge_v1.json`和防误升级审核脚本、13项回归测试。特别注意第38课允许各级别不同连接政策、84课f1与f2可不同：不冻结双轴，不宣称分解等价。历史原图后发重构只作RETROSPECTIVE。F01/OB38 OPEN、行情NOT_RUN。

**v4.29.0 重点补充：历史作者/编辑版本的文字校勘闸门。** 第54课`g0g3=(...)+g2d3`在老版PDF、线上存档中保留，2020整理版直接标`g0g3(d3?)`，2022整理版使用`g0d3`。验证器逐步证明右侧线段连续到d3；修复甲改左端`g0d3`与“当下到d3”兼容，修复乙加`d3g3`虽使端点相等却会使用后来的走势。两者都不冒充作者公开正式订正；全文源流和回帖：[研究报告](deliverables/chanlun_108_acceptance/00_REVIEW/LESSON54_EQUATION_VARIANTS_AND_ONE_PRICE_CENTER_AUTHORITY.md)、`catalog/chanlun_l54_equation_variant_witnesses_v1.json`。另把作者2007年5月24日16:04:41回帖存档“1个价位重叠也算”的价格边界与合法走势完成证书分开。运行`python -B tools/verify_chanlun_l54_formula_variants.py`与对应15项单测。原始新浪HTML仍未取得，行情NOT_RUN。

**v4.28.0 重点补充：作者文本叙述节点的可执行无前视回放。** 读取第54课13条`catalog/chanlun_l54_prefix_stage_evidence_v1.json`并执行`python -B tools/replay_chanlun_l54_author_prefix.py --show all`。只允许甲方案到g5才声明对应高级别中枢、乙方案到g6才声明对应中心，g7以后截图的`18.03`只能在`AFTER_G7`出现。区分作者叙述阶段`AUTHOR_TEXT_STAGE_ONLY`与真实市场时钟`market_first_knowable_timestamp=null`，保留d3上下文`g0g3/g2d3`字面端点异常的未核订正状态。运行`python -B -m unittest discover -s tests -p "test_chanlun_l54_author_prefix.py" -v`，缺原始行情不得宣称完整笔/段和第38课的唯一性已证。专题：[具体研究](deliverables/chanlun_108_acceptance/00_REVIEW/LESSON54_AUTHOR_PREFIX_REPLAY_AND_END_POINT_AUDIT.md)。

**v4.27.0 重点补充：图像与结论的四层区分。** 对作者同图多解，必须把（1）原图可见的价格、日期、标注（2）不同分解政策的中枢区间、形成时点、买卖点**结构标签**（3）作者给出的共同风险/操作方向（4）真正执行的时间、价格、仓位及利润分层记录。第54课原图已在**外部编纂PDF**印刷125页实际目视核验为航天机电1分钟K线，带成交量/MACD；不能冒称仓库原PDF像素同一，更不能拿其图像当子1分钟全部OHLC。g7在两种分解中三卖/震荡标签不同，但作者说最终结论一致，仅是本例**定性结论**。专项证据卡：[图证与双层结论](deliverables/chanlun_108_acceptance/00_REVIEW/LESSON54_SOURCE_FIGURE_AND_STRUCTURAL_VS_DECISION_AGREEMENT.md)、`catalog/chanlun_l54_cross_archive_figure_and_decision_v1.json`；独立审核及7个回归测试。证明F01/OB38/OB99仍OPEN，市场NOT_RUN。

**v4.26.0 重点补充：原作者同图多解析／跨时代不同定义的证据审计。** 先核作者第54课同一张图在甲乙方案下不同中枢形成时钟与g7第三卖点结论，再分别对照15课高低点、17课中枢分类、35课最低递归、72课笔段及84课f1/f2。每个结果注明`AUTHOR_TEXT_ASSERTED`、`OPEN`、`RETROSPECTIVE_ONLY`或`INDEPENDENT_VERIFIED`。**不把第54课两种规则解读成第38课同一固定规则下的不唯一证明**，不把作者原图事后分析冒称逐笔实盘回测。见[具体同图研究](deliverables/chanlun_108_acceptance/00_REVIEW/LESSON54_SAME_CHART_TWO_PARSINGS_AND_CROSS_ERA_LEVELS.md)。

**步骤0：确定问题和理论层级。** 先查[本书研究状态](RESEARCH_STATUS.md)，确保不将`SOURCE`/编者`EDITORIAL`/AI`INFERENCE`/待证`HYPOTHESIS`混成一类。明确这次是原文核对、逻辑推演、版本比较、内容提炼还是图证复核；不能未经用户同意重启回测。

**步骤1：读原书与原有证据。** 通过`ChineseBooks/缠论/`五卷PDF与`knowledge/evidence/`定位原始页、SHA、作者身份和历史日期；先核对已有逐课研究，不重复造摘要。图像未核就标`VISUAL_LIMITED`，后附文字独立标来源。

**步骤2：做真正的理论研究。** 对命题写出定义、量词、所属级别、版本、完成/当时可知条件、作者证明过程、AI推论、反例适用范围、尚缺前提；追踪108课前后依赖，不把概念阅读边伪造成已证明的推导边。

**步骤2.5：新增F01/F02边界论证关口（v4.4.0）。** 在跨课“中枢是否已破坏/是否有第三类点”论断之前，分别登记原作者的**非跌破/非升破（含等号）**、研究者用于严格不返回的**不含等号**、次级走势成员/首次回试/完成时钟；一点触边只能是数值边界例，绝不直接给原作者理论判定自矛盾或“中枢完成”证书。见[本轮正文](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_F01_F02_BOUNDARY_BRIDGE.md)。本次修订同时适用于下本书对作者不同阶段措辞的逻辑审查。

**步骤2.6：v4.4.0新增“形成／破坏／完成／可递归”类型证明。** 依据[本轮全文F01研究](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_F01_COMPLETION_PROOF_OBLIGATIONS.md)，分别检查最低级别中枢、笔、线段、合法反向线段、完整次级走势与高一级中枢的构件身份。不要把“至少三笔”“反向一笔”“已有完整的三段重叠区间”等最低或数字条件直接转换成真实走势完成；对第78课合法反向线段的证据不能越级写成完成趋势。保留历史笔版本，分别记录达到最低结构、终止事件、首次可知和可递归使用的时钟；缺原作者完整规则就明确标`OPEN`。

**步骤2.7：v4.4.0新增跨课同域核验与作者/AI角色隔离。** 以[第67/71/78课最新联合原文研究](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_F01_SEGMENT_TERMINATION_67_71_78.md)为样本：先按无缺口/有缺口分别检查第67课局部特征分型、等待反向分型的时点，再依第71课区分同一特征序列STRICT、AUXILIARY/UNDETERMINED的合法用途，然后将第78课反向合法线段要求作为**独立的结构资格问题**。AI为防过早确认使用的额外保守审查，不得宣称是作者原文定义。源文本歧义或版本未对齐时标`OPEN`，而不是把程序`PENDING`等价成作者“该结构不成立”。

**步骤2.8：v4.4.0新增原始PDF图证更正链。** 对依赖原书图的F01/F02结论先核查PDF物理页、源SHA、图片的真正内容；第67课卷三p.390的9月19日学习用图不能被冒充为8月1日原课当时图证；第71课卷四p.73末图的错误必须参照第81课p.232更正；第78课p.177要求B段已合法破坏前段方能使用后续示例。所有视觉检查在[新图证报告](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_F01_FIGURE_EVIDENCE_67_71_78.md)和[页级档案](catalog/chanlun_f01_source_figure_review_v1.json)中保留，明确标明微小坐标仍未验证，避免从示意图直接生成唯一性证明。

**步骤2.9：v4.5.0当前纯文字优先。** 用户已取消本阶段新的图片识别/高清复原与行情回测。依已登记的作者正文来源，建立第17/18/62/67/71/78/81课定义→条件→合法对象→结束→递归的文字依赖链，特别区分历史作者版本、编者意见及AI形式化假设。历史图证文件可回查但不作为本节点验收要求；四处缺乏原文证明之处标OPEN。研究底稿在 `deliverables/chanlun_108_acceptance/00_REVIEW/ISSUE69_F01_SOURCE_BOUNDARY_WORKING_NOTE.md`。

**步骤2.10（v4.6.0，文字递归证明）**：先核实每一条输入构件已经合法且完成，再应用17/18课的同级、连续、重叠中枢定义；不得以中枢计算结果证明原子构件合法，也不得从第78课线段破坏直接推论整个次级走势类型已完成。新研究见 `deliverables/chanlun_108_acceptance/00_REVIEW/F01_TEXTUAL_RECURSION_PROOF_CHAIN.md`。保留OPEN/NOT_RUN，不处理图像或行情。

**步骤2.11（v4.7.0，作者方法论主线）**：先提炼作者的市场规律判断、分析方法、决策条件与风险纪律，再构成“市场观→走势分类→中枢演化→力度背驰→三类点→区间套→底层语法→执行纪律”的功能性主线。逐环交代来源、适用前提、承接关系和AI归纳身份；原有证明义务作为限定项，不再代替正面思想提炼。见 `deliverables/chanlun_108_acceptance/00_REVIEW/AUTHOR_MARKET_LAWS_AND_METHOD_MAINLINE.md`。

**步骤2.12（v4.8.0）**：沿全书主线深化作者相邻规律：从中枢的延伸/离开/回试确定结构背景，按同级可比性讨论力度与背驰，区分一二三类点的不同结构阶段，并借区间套细化观察。不得把这些环节误写成无条件因果链。成果见 `deliverables/chanlun_108_acceptance/00_REVIEW/CENTER_DIVERGENCE_BUYPOINT_METHOD_CHAIN.md`。

**步骤2.13（v4.9.0）**：以作者文本对照中枢延伸、新生、扩展的不同问题，区分趋势背驰/盘整背驰的结构语境及一二三类买卖点各自的适用阶段。报告在 `deliverables/chanlun_108_acceptance/00_REVIEW/CENTER_EVOLUTION_AND_DIVERGENCE_METHOD.md`；不要写成无前提单线因果，不识图、不回测。

**步骤2.14（v4.10.0）**：沿作者方法论主线审视“走势终完美”与未完成时的当下可知区别、第33课多义性与第38课固定同级规范区别，以及第32课当下判断对预测冲动的约束。研究见 `deliverables/chanlun_108_acceptance/00_REVIEW/ASOF_NONPREDICTION_AND_MULTIPLE_DECOMPOSITIONS.md`；作者整体主张、AI方法归纳和未决数学证明分开。

**步骤2.15（v4.11.0）**：连接作者关于级别、三类点、区间套与资金和风险纪律的文字。结构条件、首次可知、仓位约束和实际动作分别论证；‘零成本’不等于‘零风险’，多级别判断共用真实仓位。见 `deliverables/chanlun_108_acceptance/00_REVIEW/STRUCTURE_CAPITAL_DISCIPLINE_METHOD.md`。不识图、不回测。

**步骤2.16（v4.12.0）**：先提炼跨课规律和方法论卡；记录SOURCE课号/证据卡、AI规律归纳、具体方法、限制与关联节点。首批见`catalog/chanlun_author_law_cards_v1.json`及`deliverables/chanlun_108_acceptance/00_REVIEW/AUTHOR_LAW_CARDS_INDEX.md`，不冒称已证规律。不识图、不回测。

**步骤2.17（v4.13.0）**：运行`python -B tools/audit_chanlun_author_law_cards.py`与`python -B -m unittest discover -s tests -p test_chanlun_author_law_cards.py -v`，按来源课号、证据文件、关联卡ID、来源身份及未实证边界逐条拒绝错误；GitHub Actions自动审核，不进行图像或行情检验。

**步骤2.18（v4.14.0）**：对重点规律卡建立`source_assertions`：逐条绑定作者SOURCE编号、原PDF物理页、研究者解释与未重新核PDF的验证边界。审计工具拒绝错ID、错页及非SOURCE角色。此轮8卡27锚点，未完成的4卡保留课级证据，不能伪称全覆盖。详见`catalog/chanlun_author_law_cards_v1.json`。

**步骤2.19（v4.15.0）**：12张规律卡全部必须有具体SOURCE编号、物理页和解释性`argument_trace`，即“作者文本线索→AI方法归纳→容易误用的案例”，禁止凭课程列表凑证明或把AI重建冒充原文直接引述。运行`tools/audit_chanlun_author_law_cards.py`和关联专项测试。见`catalog/chanlun_author_law_cards_v1.json`。

**步骤2.20（v4.16.0）**：以14条跨卡解释桥接编成完整方法论主线，明确关系的性质、SOURCE依据、操作含义、非蕴含边界。特别区分力度背驰与中枢离开后首次回试两条分析路径。成果见`catalog/chanlun_author_law_argument_bridges_v1.json`、`AUTHOR_LAWS_ARGUMENT_MAINLINE_V1.md`；新增桥接审计与CI，不识图不回测。

**步骤2.21（v4.17.0）**：把四组争议最强的跨课接口做作者前后版本与编者注对照：中枢演化/力度、两类背驰、第三买卖点条件、多级别/资金执行。保留每组SOURCE编号、论证思路、反面情景和不能推出的结论；本轮仅复用既有文字证据，不能说已经逐页重新验证原PDF。见`catalog/chanlun_four_core_contrasts_v1.json`与`FOUR_CORE_CROSS_VERSION_METHOD_CONTRAST.md`；CI专项校验。

**步骤2.22（v4.18.0）**：对主要作者断言建立逻辑资格：定义、必要条件、条件分类、经验辅助、条件分支、操作建议和原作者未证强命题；每条登记来源编号、前提、不能推出的结论与未实证状态。特别检查必要条件倒成充分条件，以及编者后注误当原作者原课。见`catalog/chanlun_claim_modality_v1.json`和`AUTHOR_CLAIM_MODALITY_AND_CONDITIONS.md`，配套严格审计与反向测试；不识图、不回测。

**步骤2.23（v4.19.0）**：研究第17/21/38课强命题及第99课未来中枢必然主张；分别限定定义域、量词、级别/规则、完成时钟及缺失的独立证明。成果`catalog/chanlun_strong_theses_proof_map_v1.json`和`STRONG_THESES_QUANTIFIERS_AND_PROOF_GAPS.md`，新CI核验SOURCE编号、页码、未证状态和非蕴含关系。AI候选公式不是作者原文定理。

**步骤2.24（v4.20.0）**：从第35课的递归定义循环问题/最低交易基例出发，逐环接第17/18课中枢和走势类型、第67/71/78课合法线段完成，以及第38课固定规范唯一性强主张。九个步骤、六条证明缺口均绑定已有SOURCE编号、物理页、AI解释和不可推结论；G01与G05优先继续。成果见`catalog/chanlun_recursive_construction_proof_chain_v1.json`、`RECURSIVE_CONSTRUCTION_TO_UNIQUENESS_PROOF_CHAIN.md`，新增专用CI审计。不得把结合律/最低门槛冒充唯一性或实时完成证明。

**步骤2.25（v4.21.0）**：对G01最低中枢到完整次级构件与G05结合律到唯一规范分解设置10个合成前提情境及状态判别。每例必须明确原书合法性未认证、规则和时刻，以及哪些结论不能推出；审计来源真实SOURCE编号/物理页并拒绝伪造证明状态。成果见`catalog/chanlun_g01_g05_conditional_witnesses_v1.json`、`G01_G05_CONDITIONAL_WITNESS_STUDY.md`和专项CI；无需用户手动核验。此步仅有限解释模型，F01/OB38保持OPEN。

**步骤2.26（v4.22.0）**：对G01特征/缺口/反向线段状态和G05完整输入/切分冲突/AI限定平局规则分别建立可执行有类型契约，12个合成情境，12次已有SOURCE锚点，所有输出必须保持条件性和未证。AI字典序政策与作者原文严格分离，不能以确定性程序输出冒称OB38数学唯一性。详见`catalog/chanlun_g01_g05_typed_rule_contract_v1.json`及`G01_G05_TYPED_RULE_CONTRACT_AND_NORMALIZATION.md`，配套CI。F01/OB38继续OPEN。

**步骤2.27（v4.23.0）**：将G01特征序列合法性布尔假设替换为逐成员的严格/辅助身份、序列来源和确认时点检查；将G05候选分解外部假设细分为切点来源、完成状态与竞争关系，拒绝AI字典序假冒作者唯一规范型。十一组有限合成测试由`catalog/chanlun_g01_g05_evidence_eligibility_v1.json`、`G01_G05_EVIDENCE_ELIGIBILITY.md`记录，专用CI核对SOURCE和未证状态。F01/OB38仍OPEN。

**步骤2.28（v4.24.0）**：不再仅依外部布尔声明G01候选，实际复用第67/71课局部分类函数对预标准化特征序列生成有限候选，并按照缺口/确认时点明确保留待定。G05穷举外部准入片段表所有完整覆盖切分，拒绝贪心单一输出冒充唯一性；准入表本身仍非原作者完整规则。成果见`catalog/chanlun_g01_g05_local_generators_v1.json`及`G01_G05_LOCAL_CANDIDATE_GENERATORS.md`，11案例、审计和CI，F01/OB38 OPEN。

**步骤2.25（v4.25.0，全书脉络收束）**：按作者发表时间与理论构件依赖两种顺序分别梳理108课，用[全书双地图、七环与八道门槛](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_READER_CONCEPTUAL_CLOSURE.md)将上层理论及后发低层笔线段规则、时点和决策约束串起。逐步声明SOURCE/AI、已完成/待定、历史版本与哪些结论不能越级推出；完成的是读者级CONTENT_CONNECTED，而不是F01—F08形式证明或行情验证。

**步骤3：更新规范成果。** 先修改根目录规范来源：`analyses/`、`knowledge/`、`catalog/`、`deliverables/`、`reports/`、`tools/`及`tests/`。相应更新全文研究报告、来源卡或[108课逻辑地图](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_108_LOGIC_MAP.md)的源合同；不允许独改镜像并与规范源分叉。

**步骤4：每步都修订工作流。** 同一次PR必须同步修改规范`docs/BOOK_RESEARCH_WORKFLOW.md`及书籍`WORK_LOG.md`，写明本步发现什么此前工作流未覆盖的问题、增加何种阅读/验证/证据门槛、是否适用于所有书；提升`BOOK_COLLECTIONS.json`中本书`workflow_version`，并更新本`WORKFLOW.md`中的版本。没有实际改进也应在工作日志说明复核与未改原因，不允许默默省略。

**步骤5：同步完整单书集合。** 在更新根目录规范内容之后执行：`python -B tools/book_collection.py --book chanlun --sync`（单行命令）。它会复制和登记所有在`BOOK_COLLECTIONS.json`指定源目录内的文件，包括原PDF及测试源码；**不会删除未知文件**。随后`python -B tools/book_collection.py --book chanlun --check`验收原件与集合的**每个字节及清单**。仓库中的实际CI再运行所有适用的原本测试；不要仅检查镜像数量就宣称内容正确。

**步骤6：发布与可查询状态。** 更新`RESEARCH_STATUS.md`、本文件夹`README.md`必要入口和`QUESTION_GUIDE.md`，对未完成问题保持明确状态。PR应有修改前后工作流版本和验收收据；所有GitHub Actions通过后方可合并。后续提问默认以此目录为入口，严肃主张必须回到原PDF页与来源卡。

**每次G0—G6/G7子任务都执行步骤4—6。** 文件夹是查询入口和精确镜像，不是把所有原文再版为未经授权的新出版物；还应单独核查原PDF分享权限。原书5卷、108章的存在性和镜像完整性并不证明所有图像、作者首发时间或定理已经终审。`NOT_RUN`。
