# Paper Writing Assistant · 论文写作辅助

一个面向**学术写作场景**的 Agent Skill（可直接被 Qoder 等支持 SKILL.md 规范的编码代理加载），同时附带**可独立使用的 Python 工具脚本**。

它解决三类高频、易出错且需要"可复现证据"的活儿：

1. **学术摘要生成** —— 单段式 / 结构化（IMRaD）/ 中英双语摘要，并用脚本做多口径字数统计与中英数值一致性校验；
2. **图表描述撰写** —— figure / table caption，支持读图理解图表内容，并严格区分"目测估计值"与"源数据"；
3. **引用规范检查** —— APA 7th、IEEE、MLA 9th、GB/T 7714-2015 的格式与一致性检查，含 DOI / arXiv ID 的多源真实性验证。

> **本项目的定位是"辅助草稿 + 可核对证据"**，不是替作者做学术判断。所有生成内容都应由作者核对后使用。

---

## 项目元信息

| 项目 | 值 |
|---|---|
| 名称 / 技能目录名 | `paper-writing-assistant` |
| 当前版本 | `1.0.0`（首个公开版本；`python scripts/word_count.py --version`，发布记录见 [CHANGELOG.md](CHANGELOG.md)） |
| 作者 / 维护者 | 见 [LICENSE](LICENSE) 版权行 |
| 仓库地址 | `https://github.com/XJH10247/paper-writing-assistant` |
| 许可证 | MIT |
| 运行环境 | Python ≥ 3.8；**仅标准库**（`argparse`/`re`/`json`/`urllib`/`difflib`/`datetime`），零第三方依赖、无 `pip install` |
| 联网需求 | 仅"标识真实性验证"与 `--search` 需出站 HTTPS；字数统计、双语比对、格式检查、重复检测**全部离线** |
| 支持的引用样式 | GB/T 7714-2015、APA 7th、IEEE、MLA 9th |
| 文档语言 | 中文（生成物支持中文 / 英文） |
| 遥测 | 无。不收集任何使用数据，联网时只向 CrossRef / DataCite / arXiv 发送标识与待检索标题 |

版本号有四处必须同步：脚本 `__version__`、`CHANGELOG.md` 最新条目、`SKILL.md`「版本与扩展文档」、本文件的"当前版本"。

---

## 目录

- [项目元信息](#项目元信息)
- [功能特性](#功能特性)
- [目录结构](#目录结构)
- [环境要求](#环境要求)
- [安装（多工具）](#安装多工具)
- [使用方法](#使用方法)
- [脚本参考与输入输出约定](#脚本参考与输入输出约定)
- [示例（可直接运行）](#示例可直接运行)
- [边界与已知限制](#边界与已知限制)
- [数据源与隐私](#数据源与隐私)
- [贡献指南](#贡献指南)
- [许可证](#许可证)
- [致谢与参考](#致谢与参考)

---

## 功能特性

| 模块 | 触发场景 | 关键产出 |
|---|---|---|
| 学术摘要生成 | 写摘要 / abstract / 中英双语摘要 / 结构化摘要 | 摘要正文 + 字数统计（含口径声明）+ 自检清单 |
| 图表描述撰写 | 写图注 / 表注 / figure caption / 为这张图写说明 | caption 主版本与简短版本 + 默认样式声明 + 需作者确认清单 |
| 引用规范检查 | 检查参考文献格式 / 核对 DOI / 文献表校对 | 问题报告 + 修正后文献表 + 新旧编号映射 + 验证证据 |

设计上刻意强调的几点（也是它与"让大模型顺手写一下"的区别）：

- **字数不靠感觉**：中文按纯汉字数（`han_chars`）、英文按词数（`words_en`）为主口径，同时副报 Word「字数」与字符数口径；不同口径结论冲突时必须显式提示歧义。
- **双语数值程序化比对**：中英摘要的数值集合由脚本抽取比对，数量不一致视为实质性信息差（翻译时最容易漏掉消融结果、某个百分数）。
- **目测值永不冒充精确值**：只能读图时，数值一律带 `约` / `approximately`，并给出读数误差量级；禁止由柱高自行推算百分比、倍数或显著性。
- **`error` ≠ `not_found`**：网络失败是"我们查不到"，权威库返回查不到才是"疑似虚构"。脚本把两者严格分开，不会把网络异常降级为"文献有问题"。
- **离线优先**：重复条目检测（同一标识重复、题名实质相同、题名高度近似但标识不同）不联网即可确定，应先处理。

---

## 目录结构

```
paper-writing-assistant/
├── SKILL.md                       # 技能主文件（Agent 读取的指令，含 YAML frontmatter）
├── README.md                      # 本文件
├── AGENTS.md                      # 供不兼容 Skills 机制的代理读取（Codex/Cursor/Windsurf 等会自动加载）
├── LICENSE                        # MIT
├── CHANGELOG.md                   # 版本变更（版本号单一事实来源之一）
├── .gitignore                     # 忽略 __pycache__、IDE 目录与脚本运行产物
├── .gitattributes                 # 统一 LF，避免 Windows 检出产生 CRLF
├── .github/workflows/smoke.yml    # CI：离线冒烟（编译 + --help/--version + 夹具退出码断言），Python 3.8 / 3.11 双版本
├── references/                    # 渐进式披露的细节规范，按需读取
│   ├── abstract-guide.md          # 摘要：句式模板、时态、字数基准与口径、自检清单
│   ├── caption-guide.md           # 图表：分类型模板、数值来源优先级、硬性禁则、交付模板
│   └── citation-styles.md         # 引用：四种样式要点 + 跨样式检查项 + 验证结果解读
├── scripts/                       # 仅依赖标准库的工具脚本
│   ├── word_count.py              # 字数多口径统计 + 中英数值/术语一致性
│   └── doi_check.py               # DOI/arXiv 多源验证 + 标题比对 + 重复条目检测
└── examples/                      # 可跑通的夹具（**内容全部虚构**，逐条说明见 examples/README.md）
    ├── README.md                  # 夹具说明：每条故意植入了什么问题、期望被哪一步检出
    ├── abstract_zh.md
    ├── abstract_en.md
    └── references_gbt.txt
```

`SKILL.md` 保持在 500 行以内，细节放在 `references/` 按需读取；`references/*` 只被 `SKILL.md` 直接引用（一层深），`scripts/` 由 `SKILL.md` 与 `references/` 共同引用。

**本仓库有意不包含的东西**：没有 `assets/`（本技能不需要模板、字体或图片素材，
`README.md` / `AGENTS.md` / `SKILL.md` 也不引用任何 `assets/` 路径），也没有
`requirements.txt` / `pyproject.toml`：零第三方依赖，加了反而误导。

---

## 环境要求

| 项目 | 要求 |
|---|---|
| Python | **3.8+**（脚本只用标准库：`argparse`/`re`/`json`/`urllib`/`difflib`/`datetime`；下限由 CI 在 3.8 上实际跑住） |
| 第三方依赖 | 无，不需要 `pip install`（因此没有 `requirements.txt`） |
| 联网 | 仅"标识真实性验证"与 `--search` 需要；格式检查、重复检测、字数统计完全离线 |
| 终端编码 | 脚本已自行把 stdout/stderr 切到 UTF-8。Windows 简体中文（GBK）控制台下若仍报 `UnicodeEncodeError`，加环境变量 `PYTHONIOENCODING=utf-8` 重跑；若是**用管道捕获输出**（PowerShell 5.1 的 `… | Select-Object`）时中文乱码，那是宿主按 GBK 解码 UTF-8 字节，退出码与 `--output` 落盘的 JSON 不受影响，要看结论就写文件再读 |
| CI | GitHub Actions 离线冒烟（`.github/workflows/smoke.yml`），跑 **Python 3.8**（钉 ubuntu-22.04，因 24.04 不再提供 3.8 预编译包）与 **3.11** 两个版本；不跑联网用例以免被数据源限流 |
| Agent | 任何支持 Agent Skills 规范（`SKILL.md` + YAML frontmatter）的工具，见[安装（多工具）](#安装多工具) |

查版本：`python scripts/word_count.py --version`、`python scripts/doi_check.py --version`（输出应与 CHANGELOG 最新版一致）。

---

## 安装（多工具）

本技能只依赖 `SKILL.md` + 普通文件，不含任何工具专有的注册/构建步骤。**把整个目录放进对应工具的 skills 目录即可**，目录名必须等于 frontmatter 里的 `name`（`paper-writing-assistant`），不要随意改名。

```bash
git clone https://github.com/XJH10247/paper-writing-assistant.git
```

### 各工具安装位置

| 工具 | 用户级（全局生效） | 项目级 / 工作区级 |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `<项目>/.claude/skills/` |
| Codex CLI | `~/.codex/skills/` | `<项目>/.agents/skills/` |
| TRAE（国内版） | `~/.trae-cn/skills/` | `<项目>/.trae/skills/`；v3.3.44+ 亦支持 `<项目>/.agents/skills/` |
| TRAE（国际版） | `~/.trae/skills/` | 同上 |
| WorkBuddy | `~/.workbuddy/skills/`（Windows：`%USERPROFILE%\.workbuddy\skills\`） | `<项目>/.workbuddy/skills/` |
| ZCode | `~/.zcode/skills/` | `<项目>/.zcode/skills/` |
| Qoder | `~/.qoder-cn/skills/` | `<项目>/.qoder/skills/` |
| **跨工具共享目录** | `~/.agents/skills/` | `<项目>/.agents/skills/` |

> ⚠️ 上述路径按 2026 年 10 月的公开资料与各工具 changelog 整理，不同版本差异较大（例如部分 Codex 版本的项目级路径是
> `.codex/skills/` 而不是 `.agents/skills/`）；以各工具官方文档为准。**拿不准时的最稳做法**：同时放入
> `<项目>/.agents/skills/paper-writing-assistant/`（多家共读）与该工具自己的目录。

### 装到哪里、怎么装

```bash
# 以 Claude Code 用户级为例，其他工具同理，只改目标路径
git clone https://github.com/XJH10247/paper-writing-assistant.git
mkdir -p ~/.claude/skills
cp -r paper-writing-assistant ~/.claude/skills/paper-writing-assistant
ls ~/.claude/skills/paper-writing-assistant/SKILL.md   # 能看到这个文件就说明装对了
```

**一次装到所有已安装的工具**（只拷入父目录已存在的工具，未安装的自动跳过）：

```bash
SRC=./paper-writing-assistant
for d in ~/.claude/skills ~/.codex/skills ~/.agents/skills \
         ~/.workbuddy/skills ~/.zcode/skills ~/.trae/skills ~/.trae-cn/skills ~/.qoder-cn/skills; do
  [ -d "$(dirname "$d")" ] && mkdir -p "$d" && rm -rf "$d/paper-writing-assistant" \
    && cp -r "$SRC" "$d/paper-writing-assistant" && echo "installed -> $d"
done
```

安装后需**重启会话或重载技能**才会被索引（各工具机制不同）：Claude Code / Qoder / TRAE / WorkBuddy 重开会话或重启 IDE；
Codex CLI 可用 `codex skill reload`（或 `/skills` 查看已加载列表）。

### 不支持 Skills 机制的工具

两种兼容做法（任选）：

1. **让规则文件指向 SKILL.md**：在该工具的项目规则里写一行“处理论文摘要/图表/参考文献任务时，先读取
   `<绝对路径>/SKILL.md` 并严格按其执行”，例如 TRAE 的 `.trae/rules/`、Cursor 的 `.cursor/rules/*.mdc`。
   仓库根部的 `AGENTS.md` 已经能被 Codex、Cursor、Windsurf、Gemini CLI、Aider 等自动读取，多数情况下无需额外配置。
2. **当前工具不能执行 Python 时**：仍可使用提示词部分（摘要/图表/格式规则），但需按 SKILL.md「跨工具适配与
   能力降级」表声明降级，不得把人工估算当成程序化核验结果交付。

### 以 ZIP 形式分发（WorkBuddy 等支持“上传技能”的工具）

打包前确认已排除运行产物（`__pycache__/`、`doi_report.json`、`expect.json`、`word_count.json`）：

```powershell
Compress-Archive -Path paper-writing-assistant -DestinationPath paper-writing-assistant.zip -Force   # 压缩包内为一层同名目录
```

部分工具要求“压缩包顶层直接能看到 `SKILL.md`”，此时改用：`Compress-Archive -Path paper-writing-assistant\* -DestinationPath ...`。
两种约定都存在，以目标工具的上传提示为准。

### 只当命令行工具用

脚本可独立运行，无需安装任何东西（注意先 `cd` 到含 `scripts/` 的这一层，或用 `$SKILL_DIR` 绝对路径，见下节）：

```bash
cd paper-writing-assistant
python scripts/word_count.py --help     # Linux/macOS 若提示找不到命令，改用 python3
```

---

## 使用方法

### 对 Agent

直接用自然语言提出需求，说明**目标样式（期刊/会议/学位论文）、语言、字数限制**三要素；未说明时，Agent 会按默认执行并显式告知所用默认：

- 中文论文 → GB/T 7714-2015 + 中文摘要 300–500 字
- 英文工程/计算机 → IEEE，摘要 200–300 词；英文社科/心理 → APA 7th；英文文学 → MLA 9th

示例请求：

- "根据下面这段方法+结果，写一段中文摘要，要求 300–400 字，并给英文对照版"
- "帮我给这张图（附图）写 IEEE 风格的图注"
- "按 GB/T 7714-2015 检查这份参考文献，并核对 DOI 是否真实存在"

### 自己跑脚本

见 [示例（可直接运行）](#示例可直接运行)。

**路径约定（跨工具兼容的关键）**：文档里的 `scripts/xxx.py` 与 `references/xxx.md` 都相对技能目录（`SKILL.md` 所在目录）。
人工单独运行时的两种正确做法：

```bash
# 做法一：先 cd 到技能目录
SKILL_DIR="$HOME/.claude/skills/paper-writing-assistant"
cd "$SKILL_DIR" && python3 scripts/word_count.py --input /abs/path/abstract.md

# 做法二：不切目录，直接代入绝对路径（Agent 应采此方式，因为它的 shell 工作目录通常是用户的项目仓库）
python3 "$SKILL_DIR/scripts/word_count.py" --input /abs/path/abstract.md
```

解释器名：Linux/macOS 可能只有 `python3`；Windows 通常是 `python`。PowerShell 中路径写法为
`python "$SKILL_DIR\scripts\word_count.py"`，CMD 为 `set SKILL_DIR=...` 后用 `%SKILL_DIR%\scripts\word_count.py`。

---

## 脚本参考与输入输出约定

### `scripts/word_count.py`

| 参数 | 说明 |
|---|---|
| `--input <file>` | 单语模式：摘要文件（UTF-8，Markdown/纯文本均可） |
| `--lang zh\|en` | 单语模式语言，默认 `zh` |
| `--min` / `--max` | 区间限制（含端点）；**双语模式下作用于中文侧**；可只给一端 |
| `--min-en` / `--max-en` | 双语模式下英文侧区间 |
| `--zh <file>` `--en <file>` | 双语模式，同时统计两版并比对数值 |
| `--terms "中文=英文"` | 术语对照，可重复传入（写成 `"中文术语=英文术语"`，两侧须同时出现） |
| `--output <file>` | JSON 报告落盘（默认打印到 stdout），末尾仍会输出人读结论行 |
| `--version` | 打印脚本版本（应与 CHANGELOG 最新版一致） |

**主口径与默认区间**：中文 `han_chars`（纯汉字，默认 300–500）；英文 `words_en`（默认 200–300）。副报 `word_msword`（Word「字数」）与 `chars_no_space`（字符数）只在 `counts` 中列出，其中仅 `word_msword` 参与越界判定（与字数同量纲）。

清洗规则：剥离 Markdown 结构噪声与代码块、去掉链接 URL（保留链接文字）、去掉"摘要：/Abstract:"标签前缀、整行剔除"关键词/Keywords:"行、移除零宽字符。

输出字段（节选）：

```json
{
  "lang": "zh",
  "counts": {"han_chars": 371, "word_msword": 379, "chars_no_space": 416, "chars_with_space": 429, "words_en": 0},
  "primary_metric": "han_chars",
  "primary_count": 371,
  "primary_range": [300, 500],
  "primary_range_text": "300-500",
  "within_range": true,
  "alternative_metrics_out_of_range": [],
  "note": "主口径 han_chars=371，要求 300-500，达标",
  "numbers": ["1.2M", "19.5%", "25%", "3.2个", "4个", "5年", "5次"]
}
```

双语模式额外返回 `bilingual`：`numbers_zh` / `numbers_en` / `numbers_only_in_zh` / `numbers_only_in_en` / `numbers_consistent` / `term_issues` / `message`。

### `scripts/doi_check.py`

| 参数 | 说明 |
|---|---|
| `--input <file>` | 文献表文件；自动提取 `DOI: 10.x/…`、`https://doi.org/…`、`arXiv:1706.03762`、裸 arXiv ID 等写法 |
| `--dois "a,b"` | 直接验证若干标识 |
| `--gen-expect <file>` | 从输入生成"标识 → 题名"对照 JSON 后退出。**题名为启发式提取，必须人工校正**，否则误报 `title_mismatch` |
| `--expect <file>` | 用对照文件做标题比对 |
| `--check-duplicates` | 验证同时附加离线重复检测 |
| `--duplicates-only` | 只做重复检测（不联网，必须配 `--input`） |
| `--search "标题"` | 无标识条目按标题检索候选 DOI（CrossRef + DataCite，top3） |
| `--sources` | 逗号分隔，可选 `crossref,datacite,arxiv`，默认全部 |
| `--interval` | 请求间隔秒数（默认 1.0，被限流时调大） |
| `--output` | 报告落盘路径 |
| `--version` | 打印脚本版本（应与 CHANGELOG 最新版一致） |

**路由规则**：带 `10.` 前缀的标识依次走 CrossRef → DataCite（覆盖期刊/会议/图书与数据集、软件、`10.48550/arXiv.*` 预印本）；裸 arXiv ID 走 arXiv API。

**状态语义**：

| 状态 | 含义 | 报告用词 |
|---|---|---|
| `valid` | 标识可解析（比对通过时相似度 ≥ 0.85） | 通过 |
| `title_mismatch` | 标识有效但题名不符（相似度 < 0.85） | 高风险：疑似张冠李戴，请人工复核 |
| `not_found` | 所配置数据源均明确返回查不到 | 高风险：疑似虚构或抄错，请核对原文 |
| `error` | 网络/限流/解析失败，或被 `--sources` 排除 | 不作结论：本条未能验证，请重试 |

报告字段：`results[]`（含 `tried_sources` 实际请求过的源、`source` 实际命中源、`registry_title/year/journal/authors/type`）、`summary`（各状态计数）、`duplicates` 与 `coverage`（仅 `--check-duplicates` / `--duplicates-only` 时出现）、`sources_used`（本轮实际请求源的并集）、`sources_requested`。

### 退出码

| 脚本 | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| `word_count.py` | 字数达标且中英数值一致 | （预留，当前不使用） | 字数越界 / 用法错误 | 中英数值数量不一致 |
| `doi_check.py` | 无高风险项与重复项 | 命中 `not_found`/`title_mismatch` 或重复条目（含 `--search` 无候选） | 用法/输入错误 | 有 `error` 条目因网络未验证，需重试 |

非 0 都应"报告并处置"，而不是吞掉：`word_count.py` 的 3 表示中英存在实质信息差，必须修好再交付。
**双语模式下字数越界与数值不一致同时发生时返回 `3`**（数值不一致属实质性信息差，严重度高于字数越界），
字数问题仍要在交付说明中交代——不要因为退出码是 3 就漏报字数。

---

## 示例（可直接运行）

以下输出为 **2026-10-10 在本仓库实测**的结果（Python 3.14.7 / Windows / PowerShell）。
前三条离线命令的输出与退出码是稳定的；第 4、5 条依赖 CrossRef / DataCite / arXiv 的公开 API，
相似度与命中源可能随时间小幅变化。

> 复现时请用**直接运行**（不接管道）以便中文结论行正常显示；PowerShell 5.1 下用 `| Select-Object` 等
> 管道捕获时，宿主会按 GBK 解码脚本写出的 UTF-8 字节，**中文看起来是乱码但退出码与报告内容不变**；
> 需要机器可读结果就加 `--output` 落盘再读文件。

先核对版本再复现——若 `--version` 与 CHANGELOG 最新版不一致，说明本地副本与文档不同步：

```bash
python scripts/word_count.py --version    # word_count.py 1.0.0
python scripts/doi_check.py --version     # doi_check.py 1.0.0
```

> 下面各例的相对路径假设**当前目录是仓库根目录**（即能看到 `scripts/` 与 `examples/` 的那一层）。
> 若你是从 skills 目录调用（如 `~/.claude/skills/paper-writing-assistant`），同样 `cd` 到该目录即可；
> 不想切目录时请把 `scripts/` 换成 `$SKILL_DIR/scripts/`，参见[使用方法](#使用方法)的路径约定。

**⚠️ 关于 `examples/`**：该目录下的内容**全部是虚构的**——两份摘要是编造的合成文本，
`references_gbt.txt` 里的人名、刊名、会议名、出版社、DOI、arXiv ID 也全是编造的
（统一用保留前缀 `10.5555/…` 与不可能存在的 `2599.99999`），其中被"植入"的问题条目是教学设计。
逐条说明见 [`examples/README.md`](examples/README.md)。**请勿把它们当作真实文献引用。**

### 1. 中文摘要字数（默认区间）

```bash
python scripts/word_count.py --input examples/abstract_zh.md --lang zh
```

```
主口径 han_chars=371，要求 300-500，达标          # 退出码 0
```

### 2. 中英双语数值一致性

```bash
python scripts/word_count.py --zh examples/abstract_zh.md --en examples/abstract_en.md \
       --terms "稀疏注意力=sparse attention"
```

```
主口径 han_chars=371，要求 300-500，达标
主口径 words_en=240，要求 200-300，达标
双语比对：数值数量在中英两侧一致（仅单位/精度写法不同：中文独有 ['3.2个', '4个', '5年', '5次']，
英文独有 ['3.2percentagepoints', '4', '5']），建议统一单位写法      # 退出码 0
```

若英文版漏掉某个数值（例如删掉 "25%"），比对会返回 `numbers_consistent: false` 并给出**退出码 3**——这正是人工通读最容易漏的情形。

### 3. 离线重复条目检测（先做这步）

```bash
python scripts/doi_check.py --input examples/references_gbt.txt --duplicates-only
```

实测检出 3 处问题（`count: 3`，退出码 `1`）：

| 类型 | 涉及条目 | 说明 |
|---|---|---|
| `repeated_id` | [1]、[6] | 标识 `10.5555/mif.2021.0142` 在两条中重复出现，应合并为一条 |
| `near_title` | [1]、[6] | 题名相似度 0.86，同一文献的会议版与期刊版 |
| `near_title` | [2]、[3] | 题名相似度 0.86，疑似同一文献的不同版本 |

```json
{
  "duplicates": [
    {"type": "repeated_id", "identifier": "10.5555/mif.2021.0142", "entries": ["1", "6"],
     "message": "标识 10.5555/mif.2021.0142 在条目 ['1', '6'] 中重复出现，应合并为一条"},
    {"type": "near_title", "titles": ["Adaptive sparse attention routing for long-horizon forecasting",
     "Adaptive sparse attention routing for long-horizon forecasting: a replication study"],
     "similarity": 0.861, "entries": ["1", "6"], "message": "…需人工判断"},
    {"type": "near_title", "titles": ["Hierarchical compression of attention maps for streaming forecasting",
     "Hierarchical compression of attention maps for streaming forecasting with local enhancement"],
     "similarity": 0.855, "entries": ["2", "3"], "message": "…需人工判断"}
  ],
  "count": 3,
  "coverage": {"entries_parsed": 7, "entries_without_identifier": 1,
               "message": "共解析 7 条，其中 1 条未发现 DOI/arXiv ID，无法自动验证真实性"}
}
```

（为便于阅读，两条 `near_title` 的 `message` 做了截断；实际输出为完整中文说明。）

### 4. 生成对照 → 人工校正 → 联网验证

```bash
python scripts/doi_check.py --input examples/references_gbt.txt --gen-expect expect.json
#   ↓ 打开 expect.json 校正 title 字段（关键步骤）
python scripts/doi_check.py --input examples/references_gbt.txt --expect expect.json \
       --check-duplicates --output doi_report.json
```

```
report written: doi_report.json
{"total": 6, "valid": 0, "title_mismatch": 0, "not_found": 6, "error": 0, "duplicates": 3}
```

退出码 `1`。逐条结论（实测）：

| 标识 | 状态 | 实际请求过的源 | 说明 |
|---|---|---|---|
| `10.5555/mif.2021.0142` | `not_found` | crossref → datacite | 夹具标识是虚构的，权威库查不到 |
| `10.5555/mif.2022.0311` | `not_found` | crossref → datacite | 同上 |
| `10.5555/mif.2022.0312` | `not_found` | crossref → datacite | 同上 |
| `10.5555/jmir.2023.0087` | `not_found` | crossref → datacite | 同上 |
| `10.5555/not-a-real-doi-9999` | `not_found` | crossref → datacite | 后缀明显是占位符 |
| `2599.99999`（裸 ID） | `not_found` | arxiv | 裸 arXiv ID 只走 arXiv API |

**这个"全军覆没"的结果恰恰是正确的**：夹具里的标识全是虚构的，脚本把每一条都标成高风险，正是它该做的。
反过来说，`valid` 与 `title_mismatch` 这两个状态**无法用虚构数据演示**（它们必须依赖真实注册记录才会出现）——
需要看这两种状态时，请拿自己的真实文献表跑一次，不要把真实 DOI 写进本目录的夹具。

### 5. 为缺标识条目检索候选 DOI

```bash
python scripts/doi_check.py --search "Adaptive sparse attention routing for long-horizon forecasting"
```

用夹具里的虚构题名检索，实测返回 3 个**无关**候选（相似度 0.63 / 0.58 / 0.34，来源 crossref 与 datacite 混合），退出码 `0`：

```
0.63  | crossref | Gate^2-VLA: Regulating Attention Routing for Long-Horizon VisionLanguage-Action Model
0.576 | crossref | TriAtt-STNet: Channel-Temporal-Spatial Attention with Seasonality-Aware Embedding …
0.341 | datacite | Stratospheric Signatures in Monsoon Cloud Composition: A Re-evaluation of …
```

这正是 `--search` 的正确用法示范：**它只给候选、不给结论**。相似度普遍低于 0.8 时基本可以判定"都不是你要找的文献"，
必须由人工核对题名后再决定是否补录；`--search` 完全无候选时退出码为 `1`。

---

## 边界与已知限制

- **不评判引用是否恰当支持论点**：属内容审查，需要全文且用户明确要求时才尝试，且以提示形式给出。
- **输入文体的边界**：`doi_check.py` 只处理**纯文本文献表**。BibTeX（`.bib`）、LaTeX `thebibliography`、
  EndNote/Word 导出需先转成"一行一条"的纯文本（保留 DOI/arXiv 标识与题名）再交给脚本；
  它**不会**解析 BibTeX 字段。题名提取同样是启发式的，`--gen-expect` 的结果必须人工校正。
- **标识验证的能力边界**：只能证明"标识可解析且元数据与著录信息匹配"，**不能**证明文献内容支持你的论点，也不能替代作者核对原文。
- **验证按标识去重**：同一 DOI 在多条文献中出现时只验证一次，标题比对结果反映其中一条题名；这类问题由 `repeated_id` 重复检测负责发现。
- **题名提取是启发式的**：`--gen-expect` 生成的题名必须人工校正后再用于 `--expect`，否则会产生误报的 `title_mismatch`。
- **样式规范有版本依赖**：以 `references/citation-styles.md` 所载版本为准（APA 7th、IEEE Editorial Style Manual、MLA 9th、GB/T 7714-2015）；期刊有专属 style file 时以期刊为准，本仓库输出作为基础修正。
- **读图数值只能是估计**：柱状图/折线图按图幅分辨率通常有 ±0.2pp 量级读数误差，密集散点更大；有源数据时必须以源数据为准。
- **数据源可用性**：CrossRef / DataCite / arXiv 偶发限流或超时，脚本按 `--interval` 礼貌限速（默认 1 请求/秒），失败条目报 `error` 并建议重试。

---

## 数据源与隐私

- 联网验证只会把你文献表中的**标识（DOI / arXiv ID）与检索用的标题字符串**发送给 CrossRef、DataCite、arXiv 的公开 API；**不会**上传论文全文，不发送任何作者个人信息。
- 这三个服务均为免费公开的元数据接口，使用受各自服务条款约束；请勿用于高频批量爬取。
- 不联网即可完成：字数统计、中英数值比对、格式检查、重复条目检测。若涉及未公开稿件且不愿外发标题，请只做离线部分，并在交付中说明"未做真实性验证"。
- **默认 User-Agent 不携带任何身份信息**：`doi_check.py` 未设 `PWA_USER_AGENT` 时只用
  `paper-writing-assistant/<version>`，不含仓库地址、账号与邮箱，因此三方 API 的访问日志里
  查不到你的身份。留下自己的邮箱是可选项（用 GitHub 的 noreply 邮箱即可）。
- **建议设置 `PWA_USER_AGENT`**：CrossRef 的礼貌抓取政策希望调用方留下可联系的邮箱。

```bash
export PWA_USER_AGENT="paper-writing-assistant/1.0.0 (mailto:you@example.org)"    # Linux/macOS
set PWA_USER_AGENT=paper-writing-assistant/1.0.0 (mailto:you@example.org)         # Windows CMD
$env:PWA_USER_AGENT = "paper-writing-assistant/1.0.0 (mailto:you@example.org)"    # PowerShell
```

---

## 贡献指南

欢迎 Issue 与 Pull Request。

**Issue** 请尽量给出：复现命令、脚本退出码、`--output` 生成的 JSON（可脱敏）、期望行为与实际行为。涉及引用规范争议时请附规范出处与版本。

**Pull Request** 请遵循：

1. 一个 PR 只做一件事；行为变更同步更新 `CHANGELOG.md` 并提版本号——版本号须在**四处**同步：
   脚本 `__version__`、CHANGELOG、`SKILL.md`「版本与扩展文档」、本文件"当前版本"。
2. **改动脚本后必须跑通**：`examples/` 下三条命令（字数单语、双语、`--duplicates-only`）+ 一次联网验证，
   并把退出码写进 PR 描述。CI（`.github/workflows/smoke.yml`）会自动跑其中三条离线用例与退出码断言，
   **PR 需先让 CI 变绿**。
3. 保持 `SKILL.md` < 500 行，细节写进 `references/`，交叉引用只下探一层。
4. 术语统一：全文用"主口径/副报口径""标识（identifier）""条目（entry）""高风险（not_found / title_mismatch）"，不要混用"文献/论文/条目"。
5. 遵循本项目的核心纪律：**不得为让示例好看而虚构数据**；无法确定的信息用 `[待补充：xxx]` 占位；`error` 与 `not_found` 不得混同。
6. 不提交运行产物（`doi_report.json`、`word_count.json`、`expect.json` 已在 `.gitignore` 中）。

**代码风格**：Python 标准库优先，不引入第三方依赖（脚本需在无网络安装权限的环境中可运行）；每个脚本顶部 docstring 承担 `--help` 之外的完整用法说明，参数语义变更要同步更新 docstring、`SKILL.md` 与本 README 三处。

---

## 许可证

本项目以 **MIT License** 发布，详见 [LICENSE](LICENSE)。

`references/citation-styles.md` 中整理的样式要点基于 APA 7th、IEEE Editorial Style Manual、MLA 9th、GB/T 7714-2015 等公开规范的通行约定，属于作者原创摘要与检查清单；各官方手册的商标与版权归各自组织所有，本仓库不声称代表任何官方机构。


---

## 致谢与参考

字数口径设计参考 Microsoft Word「字数 / 字符数（不含空格）」两套统计的实际差异；标识验证数据源为 [CrossRef REST API](https://api.crossref.org/)、[DataCite REST API](https://api.datacite.org/)、[arXiv API](https://info.arxiv.org/help/api/index.html)；样式要点依据 APA Publication Manual (7th)、IEEE Editorial Style Manual、MLA Handbook (9th)、GB/T 7714—2015《信息与文献 参考文献著录规则》。


