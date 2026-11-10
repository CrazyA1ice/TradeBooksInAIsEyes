# ChanlunCollection｜本书实施工作流 v4.17.0

此文件说明《缠论》在项目[通用工作流](../docs/BOOK_RESEARCH_WORKFLOW.md)下的执行方式；其源工作流文档位于仓库根`docs/BOOK_RESEARCH_WORKFLOW.md`，本集合内部同一路径有经完整性校验的镜像。未来新书使用各自`<BookName>Collection/WORKFLOW.md`。

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

**步骤3：更新规范成果。** 先修改根目录规范来源：`analyses/`、`knowledge/`、`catalog/`、`deliverables/`、`reports/`、`tools/`及`tests/`。相应更新全文研究报告、来源卡或[108课逻辑地图](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_108_LOGIC_MAP.md)的源合同；不允许独改镜像并与规范源分叉。

**步骤4：每步都修订工作流。** 同一次PR必须同步修改规范`docs/BOOK_RESEARCH_WORKFLOW.md`及书籍`WORK_LOG.md`，写明本步发现什么此前工作流未覆盖的问题、增加何种阅读/验证/证据门槛、是否适用于所有书；提升`BOOK_COLLECTIONS.json`中本书`workflow_version`，并更新本`WORKFLOW.md`中的版本。没有实际改进也应在工作日志说明复核与未改原因，不允许默默省略。

**步骤5：同步完整单书集合。** 在更新根目录规范内容之后执行：`python -B tools/book_collection.py --book chanlun --sync`（单行命令）。它会复制和登记所有在`BOOK_COLLECTIONS.json`指定源目录内的文件，包括原PDF及测试源码；**不会删除未知文件**。随后`python -B tools/book_collection.py --book chanlun --check`验收原件与集合的**每个字节及清单**。仓库中的实际CI再运行所有适用的原本测试；不要仅检查镜像数量就宣称内容正确。

**步骤6：发布与可查询状态。** 更新`RESEARCH_STATUS.md`、本文件夹`README.md`必要入口和`QUESTION_GUIDE.md`，对未完成问题保持明确状态。PR应有修改前后工作流版本和验收收据；所有GitHub Actions通过后方可合并。后续提问默认以此目录为入口，严肃主张必须回到原PDF页与来源卡。

**每次G0—G6/G7子任务都执行步骤4—6。** 文件夹是查询入口和精确镜像，不是把所有原文再版为未经授权的新出版物；还应单独核查原PDF分享权限。原书5卷、108章的存在性和镜像完整性并不证明所有图像、作者首发时间或定理已经终审。`NOT_RUN`。
