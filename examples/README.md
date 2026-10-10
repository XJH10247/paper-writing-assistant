# examples/ 夹具说明

本目录是**教学用的合成数据**，供脚本自测与文档示例使用。**所有内容均为虚构**：

- `abstract_zh.md` / `abstract_en.md`：虚构的合成摘要，不对应任何真实研究、数据或团队，数值（如 19.5%、1.2M）
  是为了让字数统计与中英数值比对有东西可算而编造的。
- `references_gbt.txt`：虚构的 GB/T 7714-2015 文献表。人名、刊名、会议名、出版社名、DOI、arXiv ID
  **全部是编造的**，统一使用保留前缀 `10.5555/…` 与不可能存在的 arXiv 号 `2599.99999`，
  在 CrossRef / DataCite / arXiv 上必定查不到。

> 之所以全盘虚构：夹具会被公开托管，若沿用真实论文的题名与 DOI，容易被误当成"真实文献的格式示范"，
> 也让"哪些问题是故意植入的"难以分辨。

## `references_gbt.txt` 中故意植入的问题

| 条目 | 植入的问题 | 期望被哪一步检出 |
|---|---|---|
| [1] | 正常条目（虚构会议论文） | — |
| [2] | 同时给出 DOI 与裸 arXiv ID，演示两种标识写法；与 [3] 题名高度相似 | `near_title` |
| [3] | 与 [2] 是同一文献的"不同版本"（题名多一个尾巴），DOI 不同 | `near_title` |
| [4] | 正常条目（虚构期刊综述） | — |
| [5] | 中文条目且**没有任何标识** | `coverage.entries_without_identifier`（无法自动验证） |
| [6] | 与 [1] **共用同一个 DOI**，题名是 [1] 的"重复验证版" | `repeated_id` + `near_title` |
| [7] | 标识后缀明显是占位（`not-a-real-doi-9999`） | 联网验证必为 `not_found` |

对应的复现命令见 [README.md 的「示例（可直接运行）」](../README.md#示例可直接运行)：

```bash
python scripts/word_count.py --input examples/abstract_zh.md --lang zh                 # 退出码 0
python scripts/word_count.py --zh examples/abstract_zh.md --en examples/abstract_en.md  # 退出码 0
python scripts/doi_check.py --input examples/references_gbt.txt --duplicates-only       # 退出码 1（3 处重复/近似）
```

## 为什么联网验证的结果全是 `not_found`

夹具标识全部虚构，权威库里当然查不到，因此第 4 个示例会得到 `not_found × 6`——这正是**正确**行为，
也正好演示了本技能最有价值的场景：**虚构或抄错的引用会被自动揪出来**。

代价是 `valid` 与 `title_mismatch` 这两个状态无法用虚构数据演示（它们必须依赖真实注册记录才能出现）。
需要演示这两种状态时，请用**你自己真实的**文献表跑一次，不要把真实 DOI 写进本目录的夹具。