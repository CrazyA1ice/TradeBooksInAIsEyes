# 如何用ChanlunCollection向AI询问《缠论》 

**询问整本书脉络**：先读[108课发表顺序/理论依赖双地图与七环闭环导读](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_READER_CONCEPTUAL_CLOSURE.md)，再追逐课SOURCE与后发版本。概念完整不等于证明/市场验证完成；无需用户手动逐页核查OCR。


**询问是否能实际生成G01局部候选或枚举G05切分时**：先读[局部生成器与11例有限穷举](deliverables/chanlun_108_acceptance/00_REVIEW/G01_G05_LOCAL_CANDIDATE_GENERATORS.md)，注意输入预标准化及G05准入片段均非作者完整规则证明。

**询问G01局部构件是否有合法身份、G05候选切分是否足以推唯一性时**：先查[证据资格与十一组边界情境](deliverables/chanlun_108_acceptance/00_REVIEW/G01_G05_EVIDENCE_ELIGIBILITY.md)，不要把外部假设和AI规范化政策冒充作者规则。

**询问G01类型状态转换、G05平局政策或是否已证明唯一性时**：优先查看[有类型规则契约与规范化边界](deliverables/chanlun_108_acceptance/00_REVIEW/G01_G05_TYPED_RULE_CONTRACT_AND_NORMALIZATION.md)以及`catalog/chanlun_g01_g05_typed_rule_contract_v1.json`，严格区分作者SOURCE约束和AI编写的政策。

**询问G01/G05边界情况与能否从有限假设推出作者证明时**：先看[十个可复现的合成条件情境](deliverables/chanlun_108_acceptance/00_REVIEW/G01_G05_CONDITIONAL_WITNESS_STUDY.md)，以及`catalog/chanlun_g01_g05_conditional_witnesses_v1.json`，特别区别原作者规则认证和AI外部假设。

**研究递归如何构造及唯一性是否真的证明时**：先读[九步构造性证明路线和六处OPEN接口](deliverables/chanlun_108_acceptance/00_REVIEW/RECURSIVE_CONSTRUCTION_TO_UNIQUENESS_PROOF_CHAIN.md)，结合`catalog/chanlun_recursive_construction_proof_chain_v1.json`核对作者SOURCE证据、时间完成条件和逻辑缺口。

**强命题问答入口**：请先读[走势终完美、买卖点安全、唯一分解和第99课未来必然的量词/证明缺口](deliverables/chanlun_108_acceptance/00_REVIEW/STRONG_THESES_QUANTIFIERS_AND_PROOF_GAPS.md)，不要把作者主张误写成数学已证。


后续在对话中直接说“根据`ChanlunCollection/`回答《缠论》第XX课……”“比较第38课和第99课……”或“重新检验这项理论的作者原文、前后逻辑和反例”。**推荐从本书[README](README.md)进入**，不要要求用户自己逐一下载五卷原书或手工校验数百个文件。

**询问“是否必然成立／什么条件才充分／能否据此操作”时**：先核对[作者论断逻辑资格索引](deliverables/chanlun_108_acceptance/00_REVIEW/AUTHOR_CLAIM_MODALITY_AND_CONDITIONS.md)及`catalog/chanlun_claim_modality_v1.json`；必要条件、经验辅助与已证明充分条件不可混同，第21/38课强断言不得默认已证。

**询问作者观点的跨课变动及编者注记时**：参照[四组核心跨课对照](deliverables/chanlun_108_acceptance/00_REVIEW/FOUR_CORE_CROSS_VERSION_METHOD_CONTRAST.md)与`catalog/chanlun_four_core_contrasts_v1.json`，区分原作者、编者及AI解释的角色。

**询问规律之间的联系时**：先读[作者规律的贯通论证主线](deliverables/chanlun_108_acceptance/00_REVIEW/AUTHOR_LAWS_ARGUMENT_MAINLINE_V1.md)及`catalog/chanlun_author_law_argument_bridges_v1.json`，核对关系性质、SOURCE证据与非蕴含限制，不将AI桥接误认为作者证明。

**询问规律与方法论时**：优先查[规律卡索引](deliverables/chanlun_108_acceptance/00_REVIEW/AUTHOR_LAW_CARDS_INDEX.md)及`catalog/chanlun_author_law_cards_v1.json`；沿`links_to`查询其他卡，随后回到来源证据卡核验。

**回答优先顺序**：先查`deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_108_LOGIC_MAP.md`定位课号/前后关系，再用`knowledge/evidence/chanlun_lessonNNN.json`核对来源卡、`analyses/books/chanlun/chapters/lesson_NNN.md`读详细研究，必要时定位`ChineseBooks/缠论/缠论_卷N.pdf#page=物理页`。争议、细价和证明命题应交叉查看`reports/source_inventory`及`catalog/`的规则版本。

每次回答涉及严肃源主张，指出**卷次、PDF物理页、SOURCE/EDITORIAL/INFERENCE/HYPOTHESIS角色、版本/时点及已证/未证状态**。不要把108课摘要、AI推测或数学玩具反例当成原作者已证定理；对未审图像、后发附注与现实市场效果注明限制。

**用户提议继续研究时**：按[本书工作流](WORKFLOW.md)执行源核验、跨课逻辑更新、工作流修订、`WORK_LOG.md`、仓库根规范文件更改以及同步/验收`COLLECTION_MANIFEST.json`。每本书有自己的`<BookName>Collection`和独立工作记录，不把新书的任何论证误归到《缠论》。
