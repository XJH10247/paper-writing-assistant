# 图表描述（Caption）写作规范（caption-guide.md）

供图表描述撰写模块使用。包含各类型图表的 caption 模板、位置规则与常见错误。

---

## 一、Caption 基本要素

一条合格的 caption 应自包含（不读正文也能理解该图），通常依次包含：

1. **编号**：Figure 1 / Fig. 1 / 图 1（以期刊格式为准，全文统一）
2. **标题句**：一张图一个核心主题，短语或完整句（依期刊惯例）
3. **自包含说明**：读者需要知道的条件——对象、实验设置、组别、样本量
4. **关键发现/读图引导**（结果图必备）：这条图说明什么趋势或差异
5. **统计标记解释**（有统计标注时必须）：`*P < 0.05; **P < 0.01; ns, not significant. Error bars indicate SD.`

**位置规则**：图注置于图**下方**，表注置于表**上方**；编号按出现顺序连续。

---

## 二、分类型模板

### 1. 数据图（折线/柱状/散点/箱线/热图/直方图）
```
Figure 3. Effect of temperature on model accuracy across five datasets.
Accuracy of [model] evaluated at temperatures from 10 °C to 60 °C on five
benchmark datasets (n = 5 runs per condition). Accuracy peaks at 25 °C and
declines sharply beyond 40 °C; differences among datasets remain consistent.
*P < 0.05 vs. baseline (two-tailed t-test). Error bars, s.d.
```
要素：对象与变量 → 条件与样本量 → 主要趋势/差异 → 统计标记解释。

### 2. 表格（Table）
```
Table 2. Comparison of segmentation performance on the test set.
Best results are in bold; second-best are underlined. Dice and IoU are
averaged over three runs. † indicates results reported in the original
paper. All models use the same training protocol described in Sec. 3.2.
```
要素：表的主题 → 关键列/缩写解释（或引导读者见表内缩写注释）→ 加粗/下划线含义 → 统计或复现说明。
**注意**：表注在上；缩写若未在表内注释，必须在表注中解释。

### 3. 示意图/概念图（schematic/conceptual figure）
```
Figure 1. Overview of the proposed framework.
The framework consists of a feature extractor, a fusion module, and a
prediction head. Dashed arrows indicate auxiliary losses used during
training only.
```
要素：结构组成 → 各模块作用 → 符号/线型含义（虚线、颜色、阴影）。

### 4. 流程图/框架图（pipeline/workflow）
```
Figure 2. Data processing pipeline.
Raw images (step 1) are preprocessed (step 2), segmented (step 3), and
quantified (step 4). Outputs of each stage are shown at the bottom.
```
要素：整体流程名 → 各阶段（对应子图编号 a/b/c）→ 数据流向或输出。

### 5. 子图（multi-panel figure）
```
Figure 4. Qualitative results under different lighting conditions.
(a) Input images. (b) Results of the baseline method. (c) Results of our
method. (d) Ground truth. Note the halo artifacts in (b, top row) that are
absent in (c).
```
规则：子图标注 (a)(b)(c) 与正文引用一致；每个子图单独一句；可加一句跨子图的对比性说明。

### 6. 照片/显微/实物图
```
Figure 5. Histological sections of liver tissue from the control group.
H&E staining, scale bar = 50 μm, magnification ×200. Arrows indicate
inflammatory infiltrates.
```
要素：对象与处理（染色方法、放大倍数、标尺）→ 标注符号含义（箭头、星号圈出的区域）。

---

## 三、中英文 caption 对应

- 中文期刊：`图 1 所提框架总体结构。整体框架由特征提取器、融合模块与预测头组成，虚线箭头表示仅在训练阶段使用的辅助损失。`
- 编号格式全文统一（图 1/Fig. 1 二选一）；中文 caption 用中文标点。
- 双语 caption（部分期刊要求）：先中文后英文或按期刊模板，两版语义一致。

---

## 四、数值来源与可靠性（读图场景必读）

从图片读取数值属于**目测估计**，必须按下列优先级与标注规则处理。

### 1. 来源优先级

| 情况 | 数值来源 | caption 中的写法 |
|---|---|---|
| 用户提供了数据表/正文表格/绘图脚本 | 一律取自源数据 | 直接写精确值，无需"约" |
| 仅提供图片，数值可读 | 目测估计 | `约 0.386` / `approximately 0.386`，并在交付说明中给出误差量级 |
| 仅提供图片，数值不可读 | 不猜测 | `[待补充：具体数值，见正文表3]` |

**硬规则：数值与正文表格冲突时，以正文表格为准**，并把冲突列入"需作者确认清单"。

### 2. 目测误差参考

| 图形类型 | 典型读数误差 |
|---|---|
| 柱状图/折线图（刻度清晰、线条分离） | 约 ±0.5%~±1%，高分辨率下可到 ±0.2pp |
| 密集散点图/重叠柱/深色背景 | 可能达 ±2%~±5% |
| 无刻度轴/仅标注数据点的图 | 无法估计，应改用占位符 |

> 交付说明中必须写明本图的估算误差量级，便于作者判断是否需要用源数据替换。

### 3. 禁止行为

- ❌ 由柱高差自行推算百分比变化、倍数、提升幅度。
- ❌ 由星号推断检验方法（t检验/ANOVA/Wilcoxon）或p 值区间。
- ❌ 由误差条外观推断其代表 SD/SE/CI（须由正文或方法节确认）。
- ❌ 把图例颜色/线型对应关系凭经验写死（须逐一核对图例）。
- ✅ 任何无法从正文/图例/图面确定的信息，一律`[待补充：xxx]`。

### 4. 可读性异常的处理

若图中存在分辨率不足导致的关键信息不可辨（如浅色星号几乎与背景同色、坐标轴刻度被遮挡），**必须主动提示**，写入"需作者确认清单"，并在caption 中用 `[待补充：…]` 占位。不得因"看起来像某个符号"就自行补全。

---

## 五、硬性禁则（检查与生成时都要执行）

1. **不重复正文**：caption 不整段照搬正文句子；用更精炼的自包含表述。
2. **不引用文献**：caption 内一般不放引用编号（个别期刊允许，默认禁止）。
3. **不虚构数据**：样本量、p 值、倍数等缺失时用 `[待补充：n]`，交付时汇总"需作者确认清单"。
4. **统计标记必须解释**：图/表中的 */†/‡/ns、误差条含义，caption 或表注必须说明；无法确定检验方法时占位，不猜测。
5. **编号连续且与正文一致**：按出现顺序编号；正文引用（Fig. 3/图 3）与实际图号对应。未拿到全文时说明"Fig. X 为暂编序号"。
6. **单位与符号规范**：温度 ℃/°C、斜体 P（统计显著性）、斜体 n（样本量）按目标期刊惯例统一。
7. **目测数值必须带"约"**：见第四节，凡非源数据的数值一律加 `约`/`approximately`，且不得参与任何派生计算。
8. **不省略默认样式声明**：目标期刊未指明时，须在交付说明中写明所采用的编号格式、斜体用法、图注位置等假设。

---

## 六、交付模板（三项缺一不可）

```
## 图注正文
<主版本：完整要素>

<简短版本：一到两句，供正文内引用>

## 默认样式说明
- 编号格式：Fig. X / 暂编（实际以全文顺序为准）
- 斜体用法：*P* / *n* / 统计量
- 图表注位置：图注在下、表注在上
- 其他假设：...

## 需作者确认清单
| 占位符 | 所在位置 | 建议补法 | 数值来源 |
|---|---|---|---|
| [待补充：重复次数] | 第2 句 | "5次重复取均值" | 方法节 |
| [待补充：误差条含义] | 第3 句 | "误差条表示标准差" | 方法节 |
| [待补充：检验方法] | 统计标记 | "双尾 t 检验" | 方法节 |
| 约 0.386（目测） | 第1 句 | 请以正文表 2 数值为准 | ⚠目测，建议用源数据替换 |

## 硬性禁则自检
- [ ] 不重复正文 / [ ] 不含引用编号 / [ ] 未虚构数据
- [ ] 统计标记均已解释或已占位 / [ ] 编号连续且与正文一致
- [ ] 单位符号规范 / [ ] 目测数值均带"约" / [ ] 默认样式已声明
```

---

## 七、常见错误清单

- 标题句与内容脱节（图是对比实验，caption 只写"模型结构"）
- 缺条件信息（没写样本量/数据集/实验设置，读者无法复现理解）
- 统计标记裸奔（图上有 * 但 caption 未解释）
- 子图编号与 caption 顺序错位
- 表注写在表下方（应为上方）
- caption 出现"如下图所示"类指向性表述（caption 必须自包含，不指向）
- **把目测读数当精确值写**（如直接写 "0.386"，读者会当作精确到小数点后三位的实测值）
- **自行补全检验方法或误差条含义**（"看着像 t 检验"就写成 t 检验）
- **由柱高推算提升幅度**（图上 19.5% 与 14.2% 目测可得，但"提升 38%"属虚构）
