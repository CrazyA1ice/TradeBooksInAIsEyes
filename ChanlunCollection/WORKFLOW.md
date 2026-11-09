# ChanlunCollection｜本书实施工作流 v4.0.0

此文件说明《缠论》在项目[通用工作流](../docs/BOOK_RESEARCH_WORKFLOW.md)下的执行方式；其源工作流文档位于仓库根`docs/BOOK_RESEARCH_WORKFLOW.md`，本集合内部同一路径有经完整性校验的镜像。未来新书使用各自`<BookName>Collection/WORKFLOW.md`。

**步骤0：确定问题和理论层级。** 先查[本书研究状态](RESEARCH_STATUS.md)，确保不将`SOURCE`/编者`EDITORIAL`/AI`INFERENCE`/待证`HYPOTHESIS`混成一类。明确这次是原文核对、逻辑推演、版本比较、内容提炼还是图证复核；不能未经用户同意重启回测。

**步骤1：读原书与原有证据。** 通过`ChineseBooks/缠论/`五卷PDF与`knowledge/evidence/`定位原始页、SHA、作者身份和历史日期；先核对已有逐课研究，不重复造摘要。图像未核就标`VISUAL_LIMITED`，后附文字独立标来源。

**步骤2：做真正的理论研究。** 对命题写出定义、量词、所属级别、版本、完成/当时可知条件、作者证明过程、AI推论、反例适用范围、尚缺前提；追踪108课前后依赖，不把概念阅读边伪造成已证明的推导边。

**步骤3：更新规范成果。** 先修改根目录规范来源：`analyses/`、`knowledge/`、`catalog/`、`deliverables/`、`reports/`、`tools/`及`tests/`。相应更新全文研究报告、来源卡或[108课逻辑地图](deliverables/chanlun_108_acceptance/00_REVIEW/WHOLE_BOOK_108_LOGIC_MAP.md)的源合同；不允许独改镜像并与规范源分叉。

**步骤4：每步都修订工作流。** 同一次PR必须同步修改规范`docs/BOOK_RESEARCH_WORKFLOW.md`及书籍`WORK_LOG.md`，写明本步发现什么此前工作流未覆盖的问题、增加何种阅读/验证/证据门槛、是否适用于所有书；提升`BOOK_COLLECTIONS.json`中本书`workflow_version`，并更新本`WORKFLOW.md`中的版本。没有实际改进也应在工作日志说明复核与未改原因，不允许默默省略。

**步骤5：同步完整单书集合。** 在更新根目录规范内容之后执行：`python -B tools/book_collection.py --book chanlun --sync`（单行命令）。它会复制和登记所有在`BOOK_COLLECTIONS.json`指定源目录内的文件，包括原PDF及测试源码；**不会删除未知文件**。随后`python -B tools/book_collection.py --book chanlun --check`验收原件与集合的**每个字节及清单**。仓库中的实际CI再运行所有适用的原本测试；不要仅检查镜像数量就宣称内容正确。

**步骤6：发布与可查询状态。** 更新`RESEARCH_STATUS.md`、本文件夹`README.md`必要入口和`QUESTION_GUIDE.md`，对未完成问题保持明确状态。PR应有修改前后工作流版本和验收收据；所有GitHub Actions通过后方可合并。后续提问默认以此目录为入口，严肃主张必须回到原PDF页与来源卡。

**每次G0—G6/G7子任务都执行步骤4—6。** 文件夹是查询入口和精确镜像，不是把所有原文再版为未经授权的新出版物；还应单独核查原PDF分享权限。原书5卷、108章的存在性和镜像完整性并不证明所有图像、作者首发时间或定理已经终审。`NOT_RUN`。
