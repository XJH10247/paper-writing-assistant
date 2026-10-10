# 引用样式规范要点（citation-styles.md）

本文件供引用规范检查模块使用。覆盖四种样式：GB/T 7714-2015（中文默认）、APA 7th、IEEE、MLA 9th。检查时按对应小节逐条比对。命令中的 `scripts/...` 路径相对本 SKILL.md 所在目录；执行时先代入技能目录的绝对路径（`$SKILL_DIR`），不要假设当前工作目录就是技能目录。

---

## 一、GB/T 7714-2015（信息与文献 参考文献著录规则）

两种编制方式：**顺序编码制**（正文用 [1][2] 上标标注，文献表按引用顺序编号）与**著者-出版年制**（正文用 (作者, 年份)，文献表按著者字序排列）。先确认论文采用哪种。

### 1. 通用著录格式

顺序编码制基本格式：
```
[序号] 主要责任者. 题名: 其他题名信息[文献类型标识/文献载体标识]. 出版地: 出版者, 出版年: 引文页码[引用日期]. 获取和访问路径. DOI.
```

### 2. 文献类型标识（缺失即错误）
| 类型 | 标识 | | 类型 | 标识 |
|---|---|---|---|---|
| 期刊文章 | [J] | | 学位论文 | [D] |
| 专著 | [M] | | 标准 | [S] |
| 会议录/论文集 | [C] | | 专利 | [P] |
| 论文集中析出文献 | [C]//[M]// | | 电子资源 | [EB/OL] |
| 报纸文章 | [N] | | 报告 | [R] |

### 3. 期刊文章示例
```
[1] 张钹, 朱军, 苏航. 迈向第三代人工智能[J]. 清华大学学报(自然科学版), 2020, 60(12): 939-947.
[2] VASWANI A, SHAZEER N, PARMAR N, et al. Attention is all you need[C]//Advances in Neural Information Processing Systems 30. Long Beach: Curran Associates, 2017: 5998-6008.
```

要点：
- 著者姓全大写前置于名缩写（中文著者直接用姓名全称）。**人数规则：著录 3 名以内（含）全部著录；超过 3 名只著录前 3 名，后加", 等"（中文）或 ", et al."（外文）**。
- 题名后紧接类型标识，**无空格**（如 `迈向第三代人工智能[J]`）。
- 电子资源需注明[引用日期]与访问路径；有 DOI 的著录 DOI。
- 出版年、卷(期)、页码之间标点：`2020, 60(12): 939-947.`。
- 页码用连接号 `-`（如 939-947），不用 `~` 或其他符号。

### 4. 常见错误清单
- 缺文献类型标识（[J]/[M] 等）
- 超过 3 名作者未截断或截断后仍用 "and"
- 中文文献误用英文标点（GB/T 7714 中文部分用全角标点：`，` `。`）
- 缺出版地/出版者（专著、学位论文）
- 网络文献缺引用日期与访问路径
- 学位论文未注明学校所在地

---

## 二、APA 7th（American Psychological Association, 7th edition）

### 1. 期刊文章
```
Author, A. A., & Author, B. B. (2023). Title of article: Subtitle. Journal Name, 45(3), 140–156. https://doi.org/10.xxxx/xxxxx
```

### 2. 作者规则
- 姓前名后，名缩写不带句点；最后一位作者前用 `&`（正文引注中同理）。
- **1-20 名作者全部列出**；21 名及以上：列出前 19 名，省略号（…），再列最后 1 名。
- 团体作者：全称，首字母大写（如 World Health Organization）。

### 3. 大小写（APA 文章标题用 sentence case）
- 文章标题：仅首词、副标题首词、专有名词大写。
- 期刊名：每个实词首字母大写（title case）。
- 书名：sentence case，但章节作者编者信息见书章节格式。

### 4. 斜体
- 期刊名及卷号斜体；期号与页码正体。
- 书名/报告名斜体。
（在纯文本检查中，斜体要求以"标注提示"形式给出，注明该点需在排版时处理。）

### 5. 其他要点
- 年份跟在作者后括号内；无年份用 (n.d.)。
- 页码范围用短破折号 `–`（en dash）。
- DOI 格式固定为 `https://doi.org/10.xxxx/xxxx`（不再用 `doi:` 前缀）。
- 预印本引用：标明 [Preprint] 或仓库信息，正式版已发布时应替换为正式版。

### 6. 示例
```
Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention is all you need. Advances in Neural Information Processing Systems, 30, 5998–6008.

Smith, J. K., & Lee, M. (2021). Rethinking sample sizes in HCI experiments. Journal of Human-Computer Studies, 152, 102638. https://doi.org/10.xxxx/xxxxxxx
```

> 上例中 Vaswani et al. 是**真实已发表**文献（可核查）；Smith & Lee 是**虚构的格式例**，DOI 一律
> 写成 `10.xxxx/xxxxxxx` 占位，与 `examples/` 的约定一致：**不得用看着可解析的假 DOI 当示例**
> （拿本文件去跑 `doi_check.py` 会得到 `not_found`，也会误导读者误以为真）。

### 7. 常见错误清单
- 文章标题误用 Title Case（应为 sentence case）
- 期刊名未用 Title Case
- 用 `doi:` 或 `DOI: ` 代替 `https://doi.org/`
- 20+ 作者规则用错
- 用 `&` 连接处遗漏，或正文与文献表作者拼写不一致
- 期号后漏页码或页码用逗号

---

## 三、IEEE（IEEE Editorial Style Manual, 参考文献部分）

### 1. 期刊文章
```
[1] A. A. Author and B. B. Author, "Title of paper," Journal Abbrev., vol. 12, no. 3, pp. 140–156, Mar. 2021, doi: 10.xxxx/xxxx.2021.123456.
```

### 2. 会议论文
```
[2] C. D. Author, "Title of paper," in Proc. IEEE Conf. (Conf. Name, Location), City, Country, 2020, pp. 45–52.
```

### 3. 要点
- 编号 [1][2][3] 按正文首次引用顺序，正文中以上标或方括号标注。
- 作者名：首字母. 姓（F. M. Author），多名作者用逗号分隔，最后一位前用 "and"；超过 6 名可用 et al.。
- 文章标题用引号，期刊名用斜体并**缩写**（按 IEEE 期刊缩写表，如 IEEE Trans. Pattern Anal. Mach. Intell.）。
- 月份用三字母缩写（Jan., Feb., Mar., Apr., May, June, July, Aug., Sept., Oct., Nov., Dec.）。
- DOI 用 `doi: 10.xxxx/xxx` 格式（IEEE 惯例，区别于 APA）。
- 页码 `pp. 140–156`。

### 4. 常见错误清单
- 期刊名未缩写或缩写不符合 IEEE 缩写表
- 标题大小写错误（应为 title case，介词冠词小写）
- 漏 vol./no./pp. 前缀
- 会议论文缺 "in Proc."
- 月份未用标准缩写
- 编号顺序与正文引用顺序不一致

---

## 四、MLA 9th（Modern Language Association, 9th edition）

### 1. 期刊文章
```
Author, First Name. "Title of Article." Journal Name, vol. 45, no. 3, 2021, pp. 140–156. https://doi.org/10.xxxx/xxxxx.
```

### 2. 要点
- 作者：姓前名后，首位作者后加逗号；第二作者起名前姓后（First Last）；两位以上第三位起用 et al.。
- 文章标题用引号 + title case；期刊名斜体 + title case。
- 卷期用 vol./no.；年份在卷期之后（无卷期时直接放年份）。
- 数据库来源注明 Database Name, doi 或 URL。
- 访问日期仅在无明确出版日期时要求（Accessed Day Month Year）。

### 3. 常见错误清单
- 引号与斜体用反（文章应引号、期刊应斜体）
- vol./no. 缺失或顺序错误
- 多作者连接词错误（MLA 用 and，不用 &）
- 缺 pp. 前缀

---

## 五、跨样式通用检查项（任何样式都要查）

1. **重复条目**：同题名（忽略大小写与标点差异）出现多次 → 提示合并。
   用脚本离线检测（不联网即可确定，`--duplicates-only` 必须配 `--input`）：
   `python "$SKILL_DIR/scripts/doi_check.py" --input refs.txt --duplicates-only`（`$SKILL_DIR` 为 SKILL.md 所在目录的绝对路径）
   可识别三种情形：同一标识在多条文献中重复（`repeated_id`）、题名实质相同（`same_title`）、题名高度相似但标识不同（`near_title`，同一文献的不同版本/不同出处）。
   退出码：`1` 发现重复条目，`0` 未发现，`2` 用法/输入错误。有编号（`[1]`/`1.`）与无编号（APA/MLA 著者-出版年制）文献表均能正确切分。
2. **同文异式**：同一篇文献在不同位置著录信息不一致（如页码不同、年份不同）。
3. **预印本未更新**：条目为 arXiv/SSRN 版本，但该文已正式发表（标识验证返回正式版元数据时提示，并给出正式版标识）。
4. **作者姓名格式统一性**：全表扫描姓名风格是否一致（注意"占位作者"如 `[1]`、`Author et al.`、`XXX` 等未填占位）。
5. **文中标注与文献表对应**（需用户提供正文）：顺序编码制编号连续且首引顺序一致；著者-出版年制拼写一致。
6. **引用质量提示**（不判内容，仅提示）：大量引用同一作者/年份跨度异常等，作为"建议项"提示。

### 出处（venue）真实性核对
除标识外，**出处本身也可能被写错**（如把 CVPR 论文标注为 TPAMI、把某会议论文写成期刊论文）。核对方式：
- 标识验证返回的 `registry_journal` / `registry_type` 与用户著录的出处、文献类型比对，不一致即标记为高风险。
- 预印本（arXiv/SSRN/E-print）与正式发表版并存时，提示作者按目标期刊要求选择版本。
- 无法自动判定的（如会议论文集名称的具体拼写），列入"需作者确认清单"。

---

## 六、修正输出格式要求

每条修正后的条目必须：按目标样式完整重写（不写"同上/略"）；保留原条目号便于对照；无法确定的字段（如缺失的页码）用 `[待补充]` 标注而不是猜一个填上。

**重编号时必须附新旧编号映射表**：顺序编码制下编号变动会连带影响正文标注，缺映射表极易导致正文引用错位。建议同时给出"保留原编号对照版"与"重编号整洁版"两份。

---

## 七、标识验证结果解读（避免误判）

| 状态 | 含义 | 报告用词 |
|---|---|---|
| `valid` | 标识可解析，元数据与题名匹配 | 通过 |
| `title_mismatch` | 标识有效但题名不符 | **高风险**：疑似张冠李戴，请人工复核 |
| `not_found` | 所配置数据源均明确返回查不到 | **高风险**：疑似虚构或抄错，请核对原文 |
| `error` | 网络/限流/解析失败，或被 `--sources` 排除 | **不作结论**：本条未能验证，请稍后重试 |

批量验证模式退出码：有 `not_found`/`title_mismatch` → `1`；`--check-duplicates` 检出重复条目 → `1`；`--search` 无候选 → `1`；仅有 `error` → `3`；均无 → `0`；用法/输入错误 → `2`。

**易错点：`error` 不是"文献有问题"。** 网络失败只说明"我们查不到"，绝不能写成"该文献不存在"。脚本已将两类失败分开，不会把网络异常降级为 `not_found`。

数据源覆盖：带 `10.` 前缀的标识依次走 CrossRef（期刊/会议/图书）→ DataCite（数据集/软件/预印本，含 `10.48550/arXiv.*`）；裸 arXiv ID 走 arXiv API。逐条的 `tried_sources`/`source` 与报告顶层 `sources_used`（本轮实际请求源的并集）共同构成证据。报告须写明各状态计数，并说明哪些条目因无标识而无法自动验证。
