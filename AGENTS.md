# AGENTS.md

本仓库是一个 **Agent Skill**（`SKILL.md` + 参考文档 + Python 脚本），不是可运行的应用程序。任何支持 Agent Skills 规范的工具（Claude Code、Codex、Trae、WorkBuddy、ZCode、Qoder 等）都可以把整个目录当作技能加载；本文件只为**在本仓库内工作的编码代理**补充上下文。

## 读什么

- 面向论文的写作任务：直接遵循 [SKILL.md](SKILL.md)，其中已写明三大模块的执行流程、交付物与退出码约定。
- 细节规范按需下探一层：`references/abstract-guide.md`、`references/caption-guide.md`、`references/citation-styles.md`。
- 面向人类的安装/使用说明：[README.md](README.md)。

## 关键约束

- **`SKILL.md` 的 frontmatter 只允许 `name` 与 `description` 两个键**，这是各工具的公共子集；加私有字段会导致某些加载器解析失败。技能目录名必须等于 `name`（`paper-writing-assistant`），改名时两处同步。
- `SKILL.md` 保持在 500 行以内，长内容拆进 `references/`，交叉引用只下探一层。
- 脚本只用 Python 标准库（`argparse`/`re`/`json`/`urllib`/`difflib`/`datetime`），**不得引入第三方依赖**——技能需要在无 pip 权限的环境可运行。
- 脚本内的相对路径不可假设工作目录：调用方（Agent）负责把 `scripts/xxx.py` 代入 `$SKILL_DIR` 绝对路径，见 SKILL.md「路径约定」。

## 仓库内可用的命令

```bash
# 语法检查（无测试框架，脚本行为由 examples 夹具 + 退出码验证）
python -m py_compile scripts/doi_check.py scripts/word_count.py

# Python 3.8 语法下限自检（不用装 3.8，标准库 ast 就能卡语法）；
# 3.9+ 的 API（str.removeprefix/removesuffix、内建泛型标注、zip(strict=) 等）要手工扫一遍
python -c "import ast;[ast.parse(open(p,encoding='utf-8').read(),feature_version=(3,8)) for p in ('scripts/doi_check.py','scripts/word_count.py')];print('py3.8 syntax ok')"

# 版本自检（应与 CHANGELOG.md 最新版一致）
python scripts/word_count.py --version
python scripts/doi_check.py --version

# 字数与中英一致性（应输出"达标"，退出码 0）
python scripts/word_count.py --zh examples/abstract_zh.md --en examples/abstract_en.md

# 离线重复条目检测（应检出 repeated_id，退出码 1）
python scripts/doi_check.py --input examples/references_gbt.txt --duplicates-only

# 联网验证（需要外发 HTTPS 请求；沙箱禁止出站时全部条目会返回 error / 退出码 3）
python scripts/doi_check.py --input examples/references_gbt.txt --gen-expect expect.json
python scripts/doi_check.py --input examples/references_gbt.txt --expect expect.json --check-duplicates --output doi_report.json
```

> 在 Windows PowerShell 5.1 里**用管道捕获子进程输出**时（`… | Select-Object`），中文结论行可能显示为
> 乱码：脚本写的是 UTF-8，而宿主用 GBK 解码，属终端侧错位，**退出码与 `--output` 落盘的 JSON 不受影响**。
> 验证时优先看退出码，要看中文就 `--output` 写文件再读，**不要据此去改脚本的编码逻辑**。

## 改动纪律

- 改了脚本的**参数语义或退出码**，必须同步三处：脚本顶部 docstring + `--help` epilog、`SKILL.md`、`README.md`（`references/` 里若也有则一并更新）。
- 改了版本号，必须同步四处：脚本内 `__version__`、CHANGELOG.md 最新条目、`SKILL.md`「版本与扩展文档」、README「项目元信息」的"当前版本"。
- 改了行为后必须实测再交付：跑上面的命令，把退出码与关键字段写进说明；**不允许只凭静态阅读声称"已验证"**。
  推送前 `.github/workflows/smoke.yml` 会跑三条离线夹具命令与退出码断言，**Python 3.8（钉 ubuntu-22.04，坐实文档
  里的 ≥ 3.8 下限）与 3.11 两个版本矩阵**（联网用例不进 CI，避免被数据源限流）。改了脚本要特别留意 3.8 兼容。
- 核心纪律不可妥协：`error`（我们查不到）与 `not_found`（权威库查不到）不得混同；无源数据时数值一律 `约`/`[待补充]`；不得为让示例好看而虚构数据。
- `expect.json`、`doi_report.json`、`word_count.json`、`__pycache__/` 是运行产物，已在 `.gitignore` 中，不要提交。

## 发布前自查（维护者的流程只写在本文件，不进 README）

- **git 提交身份**：首次 commit 前必须先在仓库内设 noreply 身份
  （`git config --local user.email "<数字ID>+<账号>@users.noreply.github.com"`）；
  全局配置往往是真实邮箱，一旦写进 commit 就永久公开、删历史要 force push。
  提交后 `git log --format="%an <%ae>"` 核对。
- **不外泄身份到三方 API**：`doi_check.py` 默认 UA 只含技能名与版本号；要留联系方式用
  `PWA_USER_AGENT` + noreply 邮箱，不写真实邮箱。
- **提交前扫索引**：命中的只能是 `you@example.org` 一类占位。
  `git grep --cached -nEi '([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})|(C:\\Users)|(1[3-9][0-9]{9})'`
- **示例只能是虚构的**：`examples/` 用保留前缀 `10.5555/…` 与不存在的 arXiv 号，`references/` 的样式
  示例 DOI 写 `10.xxxx/xxxx` 占位；不得出现看着可解析的假 DOI（会被本技能自查报成 `not_found`）。
- **结构与链接**：`SKILL.md` frontmatter 只有 `name` + `description`、技能目录名 = `name`、全文 < 500 行；
  README 目录每一项都能在正文找到同名标题；交叉引用只下探一层、无死引用。
- **换行符与产物**：`git ls-files --eol` 应全为 `i/lf w/lf`；运行产物与 `__pycache__/` 不入库。
- **版本四处同步**（重申）：脚本 `__version__`、CHANGELOG 最新条目、`SKILL.md`「版本与扩展文档」、
  README「项目元信息」；推完看 Actions 里 `smoke` 两个 Python 版本的 job 都变绿。

## 跨工具差异速查

| 缺的能力 | 影响 | 处理 |
|---|---|---|
| 无 shell / Python 执行 | 字数统计与数值比对无法程序化 | 人工估算并显式声明"未经脚本核验" |
| 沙箱禁网 | `doi_check.py` 联网验证失败 | 只做格式与一致性检查，声明"未做真实性验证" |
| 无图像输入 | 模块二读图不可用 | 要求用户提供图表源数据或文字描述 |

完整安装路径矩阵见 [README.md](README.md#安装多工具)。
