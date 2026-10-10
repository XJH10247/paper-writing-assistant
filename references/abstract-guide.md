# 学术摘要写作规范（abstract-guide.md）

供摘要生成模块使用。包含摘要类型、句式模板、时态规范、字数基准与自检标准。

---

## 一、摘要类型

### 1. 单段式（Indicative/Informative 合体，最常见）
一段 200-300 词（英文）或 300-500 字（中文）——与本技能默认字数区间一致（见第四节）；少数期刊短至 150 词，以投稿模板为准。信息型摘要（informative）为默认：包含方法与定量结果，而不仅是"本文讨论了……"。

### 2. 结构化摘要（Structured，IMRaD 分节）
常见于医学、临床、工程类期刊。节名以期刊要求为准，常见组合：
- Background / Objective / Methods / Results / Conclusions
- Purpose / Design / Setting / Participants / Interventions / Main Outcome Measures / Results / Conclusions（医学详式）
- 中文期刊常用：目的 / 方法 / 结果 / 结论

### 3. 图文摘要（Graphical Abstract）
用户要求时，提示需要单独视觉产物（不在本技能范围内生成图，只提供核心信息句与构图建议）。

---

## 二、句式模板（可直接套用骨架）

### 英文单段式
1. Background（1-2 句）：`X remains a critical challenge in Y.` / `Recent advances in X have enabled Y, but Z remains unclear.`
2. Purpose（1 句）：`This study aims to / This paper investigates / We propose ...`
3. Methods（2-3 句）：`We developed/collected/analyzed ... using ... on a dataset of N ...`
4. Results（2-3 句，必须含具体数值）：`Experimental results show that our method achieves X% (improving over baseline by Y), while reducing Z by ...`
5. Conclusion（1-2 句）：`These findings suggest / Our results demonstrate that ...`

### 中文单段式
1. 背景（1-2 句）：`……是……领域的关键问题。` / `随着……的发展，……日益突出。`
2. 目的（1 句）：`针对……问题，本文提出/研究了……。`
3. 方法（2-3 句）：`首先……；然后……；最后……。基于……数据集/实验平台……`
4. 结果（2-3 句）：`实验结果表明，该方法在……上达到……，相比基线提升……。`
5. 结论（1-2 句）：`结果表明/研究发现……，为……提供了参考/依据。`

### 结构化摘要
各节 1-3 句，Results 节必须含量化结果；Objective 一句话即可。

---

## 三、时态与语态规范

| 部分 | 英文时态 | 说明 |
|---|---|---|
| 背景 | 一般现在时 | 领域公认事实 |
| 目的 | 一般现在时 / This study aims to | |
| 方法 | 一般过去时 | 已完成的操作 |
| 结果 | 一般过去时 | 已得到的数据 |
| 结论 | 一般现在时 | 普适性解释 |

- 中文摘要避免"我们"开头的连续排比，多用"本文/该方法/实验"作主语；英文摘要主动语态优先（APA 与多数期刊现行风格），避免堆砌被动句。
- 禁止出现引用编号（[1]、Smith et al.）、图表编号（Fig. 3）、公式编号。
- 缩写首次出现写全称：`convolutional neural network (CNN)`，之后可用缩写。

---

## 四、字数基准

| 场景 | 常见要求 |
|---|---|
| 英文期刊（通用） | 150-250 words，上限 300 |
| 英文会议（CS） | 100-250 words |
| 中文期刊 | 200-400 字，学位论文中文摘要 500-800 字 |
| 医学结构化 | 250-350 words |
| 学位论文英文摘要 | 400-600 words（以学校模板为准） |

用户给定字数时以用户为准；未给定按下表默认并在交付时注明。**未给定区间时 `word_count.py` 采用的默认区间为：中文 300-500 汉字（`han_chars`）、英文 200-300 词（`words_en`），与 SKILL.md 一致。**

### 字数统计口径（必须显式声明，不得凭感觉判断）

"300 字"在 Word、期刊模板、纯文本编辑器下含义不同，**同一篇摘要不同口径可差出一百多字**。
本技能统一采用下表口径，**统计必须走 `scripts/word_count.py`（路径相对本 SKILL.md 所在目录，执行时代入 `$SKILL_DIR` 绝对路径），禁止手工估算**。

| 语言 | 主口径 | 含义 | 常见副报口径 |
|---|---|---|---|
| 中文 | `han_chars` | 纯汉字个数（不含标点、数字、英文词） | `word_msword`：Word「字数」= 汉字 + 西文单词 + 数字串；`chars_no_space`：字符数（不含空格） |
| 英文 | `words_en` | 词数 | `chars_no_space` |

交付摘要时必须给出：**主口径计数 + 要求区间 + 是否达标 + 口径声明句**。示例：

> 中文摘要按纯汉字计 397 字，落在 300-500 区间；Word「字数」口径为 436，字符数（不含空格）为 536。
> 三种口径计数不同，请以目标期刊模板的要求口径为准。

**若同量纲的不同口径给出相反结论**（如纯汉字达标但 Word 字数口径超限），必须显式提示歧义，不得只报告达标的口径。脚本只对同量纲的副报口径判越界（中文比 `word_msword`）；`chars_no_space` 是字符数，与字数/词数区间量纲不同，仅在 `counts` 中列出供声明时引用。

```bash
# 下例统一写成 "$SKILL_DIR/scripts/word_count.py"：多数 Agent 工具的 shell 工作目录是
# 用户的项目仓库而非技能目录，$SKILL_DIR 指 SKILL.md 所在目录的绝对路径，勿直接跑相对路径。
# Windows PowerShell 写作 python "$SKILL_DIR\scripts\word_count.py"。

# 中文摘要（要求 300-500 纯汉字）
python "$SKILL_DIR/scripts/word_count.py" --input abstract_zh.md --lang zh --min 300 --max 500

# 英文摘要
python "$SKILL_DIR/scripts/word_count.py" --input abstract_en.md --lang en --min 200 --max 300

# 双语一致性：分别给两侧区间（--min/--max 管中文侧，--min-en/--max-en 管英文侧）
python "$SKILL_DIR/scripts/word_count.py" --zh abstract_zh.md --en abstract_en.md \
  --min 300 --max 500 --min-en 150 --max-en 250 \
  --terms "自适应稀疏注意力=adaptive sparse attention" --output word_count.json

# 单边限制（如学位论文只要求不少于 500 字）
python "$SKILL_DIR/scripts/word_count.py" --input abstract_zh.md --lang zh --min 500

# 查看脚本版本（应与 CHANGELOG.md 最新版一致）
python "$SKILL_DIR/scripts/word_count.py" --version
```

脚本退出码：`0` 全部通过 / `2` 字数越界或用法错误（如 `--min` 大于 `--max`、输入文件不存在）/ `3` 中英数值数量不一致。`1` 为预留位，当前不使用。双语模式下字数越界与数值不一致同时发生时返回 `3`（数值不一致属实质性信息差，严重度更高）。

---

## 五、双语摘要注意事项

- **术语一致**：中英文摘要的术语必须一一对应（如"卷积神经网络"↔"convolutional neural network"），不得一个用音译一个用意译。
- **数字一致**：中英文摘要中的数值、单位、百分比必须完全一致。
  - 用 `word_count.py --zh ... --en ...` **程序化比对**，不要靠通读肉眼核对。
  - 脚本比对的是**数值数量**：中文有而英文没有的数值（如某个消融结果、某个百分数）会被判为不一致，属实质性信息差，必须补齐。
  - 仅单位/精度写法不同（如 `5次` vs `5 times`）不算错误，脚本会单独提示建议统一写法。
  - 脚本不判断**语义**一致性：结论方向、限定条件（"在ETTh1 上"、"当样本量低于 500 时"）是否一致，仍须人工通读确认。
- **不逐字直译**：中文长句在英文中拆分重组；英文定语从句在中文中转为短句。
- **英文版不自创结论**：中文版没有的表述，英文版不得新增（反之亦然）。
- **定量信息零删减**：中文版保留的全部数值（主结果 + 消融 + 显著性）英文版必须同样保留。压缩只能压背景与方法，**不得删结果数值**。

---

## 六、自检清单（交付前逐条核对）

交付时附`self_check.md`，逐条写出**核对依据**（数值一致性须写明"程序化比对 + 脚本输出摘要"），供作者复核。

1. [ ] 所有数据与结论均来自用户材料，无新增断言、无夸大（"首次""突破"需有依据）
2. [ ] 关键定量结果已保留（数值、百分比、显著性），消融结果未被删减
3. [ ] 无引用编号、图表编号、公式编号
4. [ ] 缩写首次出现已展开
5. [ ] 时态/语态符合第三节规范
6. [ ] 字数符合要求，**已用脚本统计**，且交付时注明了口径与实际计数（见第四节）
7. [ ] （双语）中英术语与数值一致：数值经`word_count.py` 比对通过，语义经人工通读确认
8. [ ] 未出现"数据显示""实验表明"之外的无来源断言句
