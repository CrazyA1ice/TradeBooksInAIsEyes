# 项目本地文件的唯一根目录及 M75 路径纠正

> 生效：2026-11-15；研究项目 CrazyA1ice/TradeBooksInAIsEyes。用户明确要求项目的全部研究文件都存放于唯一的本地根目录 D:\ChatGPT\TradeBooksInAIsEyes，禁止再创建平行的 *-Review 项目目录或把生成图表放在 D:\ChatGPT 根部。

## 唯一本地根

- Git 主工作目录：D:\ChatGPT\TradeBooksInAIsEyes。保留当前分支与任何尚未提交的修改，不使用 reset --hard / clean -fd / worktree remove --force。
- 临时文件：<repo>/work/，已经被仓库根目录 .gitignore 忽略，不提交历史分钟 OHLCV、下载缓存、临时图表与独立工作树。
- 第54课图表：<repo>/work/chanlun/lesson054/figures/L54-M74-20070518-afternoon.svg。
- 第54课图像配准：<repo>/work/chanlun/lesson054/alignment/L54-M75-original-vs-replay.html 和 L54-M75-marker-review-template.json。
- Git 管理的两个旧 Review worktrees，在不得丢失本地文件的前提下经 git worktree move 迁入 <repo>/work/review-worktrees/M73-Review、M74-Review；保留每个工作树的 HEAD 和现有文件。不得直接剪切 worktree 目录而破坏 .git 元数据。
- 项目自带规范PDF：<repo>/ChineseBooks/缠论/缠论_卷3.pdf。M75 对照器只引用已存在的本地 PDF，不将其复制出仓库或改写。
- 可追溯的项目代码与研究记录保留在 tools/、tests/、docs/、other_views/ 与 ChanlunCollection 精确镜像中，符合原 G7 集合制度。

## 为什么不合并 Review 内容到 Git 主工作树

用户主工作树此前已有未提交修改；Review 是在独立提交上创建的 detached Git 工作树。将其文件覆盖到主工作树会造成未提交内容丢失或版本串扰。因此迁移时保留 Review 工作树的独立身份，把目录搬进已忽略 work/。Git 官方 worktree move 维护内外元数据，若工作树被锁、包含子模块或文件正被占用，迁移应报错停止，由用户检查而非强制删除。移动结束须 git worktree list 和 git status 复验。

**本次不是用户 Windows 文件已经由 GitHub 自动迁移。** GitHub 仓库代码的更新无法直接写入用户D盘。需用户本机执行明确迁移命令，并用实际路径和文件SHA核验后才可标记 MIGRATION_COMPLETED。

## 工具保证

M74 的显式 --svg-output 只能落在规范项目的 work/ 下；被安排在 <repo>/work/review-worktrees/<name> 的子工作树运行时，工具自动识别规范根目录并将生成图表约束到**主项目** work/。非SVG、仓库外路径、已存在文件均拒绝，避免盖掉研究结果。

M75 工具默认 --mode preflight 完全离线。用户将已生成的 SVG 迁入上述 figures/ 后，明确执行 --mode prepare，才对规范卷三PDF SHA与已验证 SVG 关键数值/时标再检查，随后只在 alignment/ 创建一个本地HTML双图浏览入口及14点均为 UNKNOWN 的 JSON 审核模板。已存在文件拒绝覆盖；PDF仍保留规范位置，不上传外部服务。HTML显示本项目现有卷三PDF物理页170—175的导航与重放SVG，外部整理版PDF仅是供人工比较的公开出处链接，绝不默认抓取到项目外。

下一研究门槛：有了原始PDF+SVG可视对照后人工登记每个 g1—g7/d1—d7 标注的图面坐标、候选分钟、OHLC价格和误差；时间轴标记13:07(18.59)与15:00(18.03)是行情锚点，**不是已经认证的作者g/d身份**。不得把g7以后15:00数据倒灌至g7历史首次可见时刻。F01/OB38/OB99/Φ20仍OPEN，E1-E4 NOT_RUN。
