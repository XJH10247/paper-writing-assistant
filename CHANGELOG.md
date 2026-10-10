# Changelog

本文件记录 paper-writing-assistant 的重要变更，格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

> 版本号的单一事实来源：脚本内的 `__version__`（`python scripts/xxx.py --version`）、本文件最新条目、
> 以及 `SKILL.md`「版本与扩展文档」与 README「项目元信息」中的版本标注。四处必须同步。

## [1.0.0] - 2026-10-10

首个公开版本。技能本体（三大模块 + 两个脚本）、跨工具适配、文档与可运行夹具一次性到位；
此前的内部迭代没有公开发布，因此没有更早的版本记录 —— 本节即完整的初始发布说明。

### 能力

- **模块一 学术摘要生成**：单段式 / 结构化（IMRaD）/ 中英双语；强制声明字数统计口径，
  交付附 `self_check.md` 核对依据。
- **模块二 图表描述撰写**：按图型给模板，硬性区分"目测估计值"与"源数据"，
  禁止由柱高推算百分比/倍数/显著性；每次交付主版本 + 简短版本 + 默认样式声明 + 需作者确认清单。
- **模块三 引用规范检查**：APA 7th / IEEE / MLA 9th / GB/T 7714-2015 的格式与一致性检查，
  输出汇总表、修正后文献表、新旧编号映射、验证证据四件套。
- **`scripts/word_count.py`**：字数多口径统计（中文主口径 `han_chars`，副报 `word_msword` /
  `chars_no_space`；英文主口径 `words_en`）+ 中英数值与术语一致性比对。
- **`scripts/doi_check.py`**：DOI / arXiv ID 经 CrossRef → DataCite → arXiv 多源回退验证、
  标题相似度比对、离线重复条目检测（`repeated_id` / `same_title` / `near_title`）、
  按标题检索候选标识。

### 关键设计约束

- **`error` ≠ `not_found`**：网络/限流/解析失败一律记为 `error`（"我们查不到"），
  只有权威库明确返回查不到才记 `not_found`（"疑似虚构或抄错"）。批量验证按 0/1/2/3 分级返回退出码。
- **目测值永不冒充精确值**：只能读图时数值一律带 `约` / `approximately`，并给出读数误差量级；
  显著性标记与误差条含义不可猜，一律 `[待补充]`。
- **字数不靠感觉**：统计必须走脚本并显式声明口径；不同口径结论冲突时必须提示歧义。
- **零第三方依赖**：两个脚本只用 Python ≥ 3.8 标准库，可在无 pip 权限的环境运行。

### 脚本正确性（已修复的问题）

- `doi_check.py`：网络/限流失败曾被误判为 `not_found` 并输出"疑似虚构或抄错"（原按精确等值匹配错误串，
  而实际串带详情后缀，永远匹配不上）；改为按前缀归类，网络失败一律 `error`。
- `doi_check.py`：无编号文献表（APA/MLA 著者-出版年制、Word 导出）曾被合并成 1 条，导致重复检测与题名提取全部失效；
  改为按"表内是否有编号"分流。
- `doi_check.py`：`--sources` 参数此前不生效、`sources_used` 复述的是请求值而非实际请求值；现真正生效，
  并新增 `sources_requested` 与逐条 `tried_sources` 区分。
- `doi_check.py`：批量验证模式退出码恒为 0；`--duplicates-only` 缺 `--input` 时静默返回"0 条"；
  输入文件读取失败抛裸 traceback。现分别为退出码 1 / 2 / 结构化错误。
- `doi_check.py`：**Windows 简体中文（GBK）控制台下打印含 emoji 的提示会抛 `UnicodeEncodeError`**，
  进程以退出码 1 终止且输出被截断（`--gen-expect` 本应返回 0）。现导入阶段即把 stdout/stderr 切到 UTF-8，
  终端输出串不再含 emoji。
- `word_count.py`：只给 `--min` 不给 `--max` 时崩溃、只给 `--max` 被静默忽略；现支持单边限制。
- `word_count.py`：数值抽取正则把"至少/超过/约"写成字符集，导致"减少25%"被抽成 `少25%`；现改为选择式。
- `word_count.py`：英文侧曾用字符数与词数区间比较，产生量纲误报；现仅对同量纲副报口径判越界。
- 两脚本：新增 `--version`，User-Agent 由 `__version__` 拼接，消除版本号散落各处的不一致。

### 跨工具可移植性

- frontmatter 只用 `name` + `description`（Agent Skills 开放规范的公共子集），技能目录名 = `name`。
- 修正一处会直接导致脚本报错的路径假设：旧文档要求"工作目录 = SKILL.md 所在目录"，
  而多数工具的 shell 工作目录是**用户的项目仓库**；现统一改为先定位技能目录再代入 `$SKILL_DIR` 绝对路径。
- `SKILL.md` 新增「跨工具适配与能力降级」表：无 shell / 无联网（沙箱禁出站）/ 无读图 / 无落盘
  四种缺失能力各自的降级做法与必须声明的内容。
- 新增 `AGENTS.md`：供不实现 Skills 机制但会自动读它的代理（Codex、Cursor、Windsurf、Gemini CLI、Aider 等）
  获取仓库上下文与运行命令。
- README 安装章节为多工具路径矩阵（Claude Code、Codex CLI、TRAE 国内/国际版、WorkBuddy、ZCode、Qoder、
  `.agents/skills/` 共享目录），含"一次装到所有已安装工具"的循环脚本、重载机制、ZIP 分发约定，
  以及不支持 Skills 机制时的两种兼容做法；矩阵已标注资料来源与"以官方文档为准"的免责说明。

### 工程与合规

- 新增 `.github/workflows/smoke.yml`：离线冒烟（编译、`--help`/`--version`、三条夹具命令与退出码断言），
  矩阵跑 **Python 3.8（钉 ubuntu-22.04，因 24.04 不再提供 3.8 预编译包）与 3.11**，用来坐实文档承诺的 ≥ 3.8 下限；
  联网用例不进 CI，避免被三方 API 限流导致假红。
- 新增 `.gitattributes`（统一 LF，脚本含 shebang，避免 Windows 检出为 CRLF 后在类 Unix 环境执行失败）；
  `.gitignore` 覆盖 `__pycache__/`、IDE 目录与脚本运行产物。
- 把“管道捕获时中文乱码”的归因写进文档（两脚本 docstring、`SKILL.md`、README、AGENTS.md 四处）：
  脚本输出 UTF-8，而 PowerShell 5.1 按 GBK 解码子进程输出，属终端侧错位，**退出码与 `--output`
  落盘的 JSON 不受影响**；需要人读结论时 `--output` 写文件再读，不要为此去改脚本的编码逻辑。
- **`examples/` 全盘虚构**：两份摘要与 GB/T 7714 文献表（人名、刊名、会议名、出版社、DOI、arXiv ID）
  均为编造，标识统一用保留前缀 `10.5555/…` 与不存在的 `2599.99999`；逐条植入的问题与预期检出方式
  记录在 `examples/README.md`。代价是 `valid` / `title_mismatch` 状态无法用夹具演示（需真实注册记录），
  已在文档中写明。
- **不把身份外泄到三方 API**：`doi_check.py` 的默认 User-Agent 只含技能名与版本号
  （`paper-writing-assistant/<version>`），不携带仓库地址、账号或邮箱；按 CrossRef 礼貌抓取
  政策留联系方式属可选项，由调用方设 `PWA_USER_AGENT`。
- 修正文档自相矛盾：SKILL.md 的命令示例曾写作 `python scripts/xxx.py`，与它自己的 `$SKILL_DIR` 约定冲突；
  另修正一处能力过度声明（脚本只处理纯文本文献表，不能直接解析 `.bib`）。
- 统一默认字数区间为中文 300–500 汉字 / 英文 200–300 词（此前 SKILL.md、参考文档与脚本默认值三处不一致）。
- MIT 许可证；去个人化与发布前自查的步骤只写在 AGENTS.md「发布前自查」（供在本仓库工作的代理读取），
  不作为面向使用者的 README 内容；README 只保留安装、使用、脚本参数与隐私说明。

### 已知限制（随 v1.0.0 一并公开）

- 标识验证只能证明"标识可解析且元数据与著录信息匹配"，不能证明文献内容支持论点，也不能替代作者核对原文。
- `--gen-expect` 的题名为启发式提取，必须人工校正后再用于 `--expect`，否则会误报 `title_mismatch`。
- 题名提取与文献切分均为启发式；`doi_check.py` 只处理纯文本文献表，`.bib` / LaTeX 需先转换。
- 样式规范有版本依赖，以 `references/citation-styles.md` 所载版本为准，期刊有专属 style file 时以期刊为准。

### 复测记录

Python 3.14.7 / Windows：`examples/` 三条离线命令退出码为 `0` / `0` / `1`（重复检测 `count: 3`）；
`--gen-expect` 退出 `0`；无参调用退出 `2`；联网验证
`{"total":6,"valid":0,"title_mismatch":0,"not_found":6,"error":0,"duplicates":3}`，退出码 `1`；
`--search` 用虚构题名返回 3 个低相似度无关候选，退出码 `0`。