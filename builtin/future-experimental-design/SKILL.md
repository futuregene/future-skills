---
name: future-experimental-design
version: 0.0.1
description: >
  在数据采集之前设计实验和研究方案——选择设计类型、随机化、区组划分、处理组合布局，
  确保实验结果可解释。适用于规划研究、分配受试者/样本到分组、随机化、区组、分层、
  对照、因子/部分因子设计、DOE、筛选多因素、响应面优化、交叉/重复测量/裂区设计、
  整群随机、拉丁方、孔板布局、批次/运行顺序效应、重复 vs. 伪重复、序贯/自适应设计等场景。
metadata:
  requires:
    bins: ["python3"]
origin: K-Dense-AI/scientific-agent-skills (MIT license)
allowed-tools: Bash(future:*)
---

# 实验设计 (Experimental Design)

## 概述

研究设计——如何将实验单元分配到不同条件、哪些保持不变、哪些被操纵、以什么结构——
决定了数据能够回答什么问题。再好的分析也无法挽救一个混淆的或伪重复的设计。
本技能关注的是数据采集**之前**的决策：选择能隔离目标效应的设计，通过随机化支撑因果推断，
通过区组消除已知噪声变异，构建多因素实验使效应可估计而非纠缠不清。

几乎所有好设计背后的三条原则（Fisher 三原则）：
- **随机化（Randomization）** — 随机分配处理，使已知和未知的混淆因素在期望上平衡。这是将比较转化为因果推断的基础。
- **重复（Replication）** — 在正确的层级上独立重复，以估计变异性。最常见的致命错误是**伪重复（pseudoreplication）**：将对同一单元的多次测量当作独立重复。
- **区组/局部控制（Blocking / local control）** — 将相似单元分组（按批次、日期、地点、窝），在区组内随机化，将噪声变异从误差项中剔除。

本技能帮助你选择设计类型，生成可复现的随机化或 DOE 布局，并避免使数据不可解释的结构性错误。

## 何时使用本技能

- 规划任何比较性实验或试验，决定如何分配实验单元
- 将受试者/样本随机分配到各组（简单、区组、分层或整群随机化）
- 通过区组或分层消除噪声变异
- 设计多因素实验：全因子或部分因子、筛选设计
- 优化连续因素的响应（响应面设计）
- 受试者内/重复测量、交叉、裂区或拉丁方设计
- 整群/分组随机化设计（地点、诊所、教室、窝）
- 确定重复的数量和层级，避免伪重复
- 序贯、成组序贯或自适应设计及中期分析
- 孔板/批次布局和随机化运行顺序以避免漂移

## 安装

```bash
uv pip install "numpy>=1.26" "pandas>=2.0" pyDOE3
```

或使用 pip：

```bash
pip install "numpy>=1.26" "pandas>=2.0" pyDOE3
```

`pyDOE3` 是 pyDOE/pyDOE2 的维护版本，提供全因子、部分因子、Plackett-Burman、
中心复合、Box-Behnken 和 Latin Hypercube 生成器。附带脚本封装这些功能，
返回实际因子单位的命名列和随机化运行顺序的设计矩阵。

---

## 选择设计

从研究问题和实验单元的结构出发，而非从最喜欢的某个设计出发。

```
你想了解什么？
│
├─ 比较少数几个预定义条件（A vs B vs C）？
│   ├─ 单元独立，可能有已知噪声因素（日期、批次、地点）？
│   │     → 完全随机（无噪声）或随机区组设计。
│   ├─ 每个单元可依次接受每种条件（有洗脱期）？
│   │     → 交叉/重复测量设计（更强的统计效力，注意残留效应）。
│   └─ 只能随机化分组而非个体（学校、诊所）？
│         → 整群随机化设计（以整群为层级分析；见伪重复）。
│
├─ 筛选大量因素（5+），找出关键少数？
│     → 部分因子或 Plackett-Burman 筛选设计。
│
├─ 量化少数因素的主效应和交互作用？
│     → 全 2^k 因子设计。
│
├─ 寻找优化响应的设置（曲率很重要）？
│     → 响应面设计：中心复合或 Box-Behnken。
│
└─ 探索仿真/计算机模型的连续空间？
      → 空间填充设计：Latin Hypercube。
```

各分支的详细指南：
- **随机化、区组、分层、对照** → `references/randomization_and_blocking.md`
- **因子、部分因子、筛选、响应面、DOE 概念（别名、分辨率）** → `references/factorial_and_doe.md`
- **交叉、重复测量、裂区、拉丁方、整群、嵌套设计** → `references/design_types.md`
- **序贯、成组序贯和自适应设计（中期分析）** → `references/sequential_and_adaptive.md`

---

## 生成设计

两个脚本生成即用且可复现的布局。从本技能的 `scripts/` 目录运行或将其添加到 `sys.path`。
所有输出使用固定种子，使精确的分配方案可存档和重新生成——这是试验注册和良好实验室规范的要求。

### 随机化/分配方案 — `scripts/randomization.py`

```python
from randomization import (
    simple_randomization, block_randomization,
    stratified_block_randomization, cluster_randomization,
    assign_factorial_runs, arm_balance,
)

# 置换区组保持各组在整个入组期间平衡（适用于 n < ~100 或序贯入组——简单随机化在小样本时可能漂移失衡）
sched = block_randomization(n=60, arms=["treatment", "control"], seed=42)

# 通过在每个层内随机化来平衡已知预后变量
sched = stratified_block_randomization({"siteA": 30, "siteB": 30},
                                       arms=["drug", "placebo"], ratio=(2, 1), seed=42)

# 随机化整个群体，而非个体（群体是实验单元）
sched = cluster_randomization(["clinic1", "clinic2", "clinic3", "clinic4"], seed=42)

arm_balance(sched)            # 检查各组数量的合理性
sched.to_csv("allocation_schedule.csv", index=False)
```

如何选择：**简单随机化**在大样本时没问题，但小样本可能不均衡；**区组随机化**保证整个过程中平衡；
**分层区组随机化**额外平衡已知预后因素；**整群随机化**当干预在群体层面交付时必须使用。
参见 `references/randomization_and_blocking.md`。

### DOE 矩阵 — `scripts/doe_designs.py`

```python
from doe_designs import (
    full_factorial, two_level_factorial, fractional_factorial,
    plackett_burman, central_composite, box_behnken, latin_hypercube,
)

# 因素以实际（低, 高）范围定义 -> 设计返回实际单位
factors = {"temp_C": (20, 60), "conc_mM": (1, 10), "pH": (6, 8)}

# 全 2^3：所有主效应 + 所有交互（8 次运行），运行顺序已随机化
design = two_level_factorial(factors, seed=42)

# 低成本筛选 7 个因素（仅主效应）
many = {f"factor_{i}": (0, 1) for i in range(7)}
design = plackett_burman(many, seed=42)

# 对 2 个连续因素进行带曲率的优化（响应面）
design = central_composite({"temp_C": (20, 60), "conc_mM": (1, 10)}, seed=42)

design.to_csv("experimental_runs.csv", index=False)
```

运行顺序默认随机化，避免因素与时间/漂移混淆（设备预热、试剂老化）。
参见 `references/factorial_and_doe.md` 了解如何选择生成元、解读别名结构和选择分辨率。

---

## 毁掉研究的错误

这些是结构性的——无法在分析阶段修复，只能在设计阶段避免。

1. **伪重复。** 将一个单元的重复测量当作独立重复：3 只老鼠各测 100 个细胞，
   对施加给老鼠的处理来说，n = 3（老鼠），而不是 n = 300（细胞）。
   重复必须在处理被随机化的层级上进行。这一错误导致大量已发表实验无效。
   在正确的层级随机化和重复；分析时尊重嵌套结构（混合模型）。见 `references/design_types.md`。
2. **噪声变量混淆。** 所有处理样本周一运行，所有对照周二运行——处理与日期完全混淆。
   对所有你能列举的噪声因素（批次、日期、孔板、技术员、仪器、位置）进行随机化或区组化。
3. **缺失或破坏的随机化。** 便利分配（先来的→处理组）让混淆因素趁虚而入。使用带种子的方案并严格执行。
4. **缺少适当的对照。** 没有并行对照（以及相关的载体/假手术和盲法），
   你无法将处理效应与时间、安慰剂或操作效应区分开。
5. **批次效应被误认为生物学效应。** 尤其在组学中，跨批次以随机化/区组顺序处理样本；
   绝不让批次与条件对齐。
6. **孔板边缘/位置效应。** 蒸发和温度梯度使孔板边缘位置不同。
   随机化或区组化样本位置；不要把所有对照放在第 1 列。
7. **忽略部分因子中的别名效应。** 低分辨率部分因子设计将主效应与交互作用混淆；
   在断言某个因素"无效"之前，先了解你的别名结构。
8. **有曲率却不用响应面。** 二水平因子设计无法检测弯曲的响应；你会错过内部最优值。
   使用响应面设计。

---

## 工作流

1. **陈述研究问题、实验单元和响应变量。** 什么是被随机化的？测量什么？什么层级才是真正的独立重复？这决定了后续一切。
2. **列出噪声因素**（批次、日期、地点、操作员、位置）——计划对每个因素进行区组、分层或随机化。
3. **使用决策树和参考文件选择设计**。
4. **在正确层级确定重复次数**（使用标准功效分析方法计算所选设计所需的样本量 n）。
5. **使用 `randomization.py` / `doe_designs.py` 生成布局**，使用固定种子。
6. **随机化运行/处理顺序**和孔板/批次位置。
7. **记录**设计、种子和方案（尽可能预注册），使分析具有验证性、布局可审计。
8. **将分析与设计匹配**——区组、分层、整群和嵌套必须反映在模型中（在分析模型中反映区组、分层、整群和嵌套结构）。

---

## 资源

### 脚本
- `scripts/randomization.py` — 带种子的分配方案：`simple_randomization`、
  `block_randomization`、`stratified_block_randomization`、`cluster_randomization`、
  `assign_factorial_runs`、`arm_balance`。
- `scripts/doe_designs.py` — 实际单位的 DOE 矩阵：`full_factorial`、
  `two_level_factorial`、`fractional_factorial`、`plackett_burman`、
  `central_composite`、`box_behnken`、`latin_hypercube`。

### 参考文档
- `references/randomization_and_blocking.md` — 随机化方法、区组、分层、对照、盲法、批次/孔板布局。
- `references/factorial_and_doe.md` — 因子和部分因子设计、分辨率和别名、筛选和响应面方法论。
- `references/design_types.md` — 完全随机、随机区组、交叉、重复测量、裂区、拉丁方、整群和嵌套设计；伪重复问题深入探讨。
- `references/sequential_and_adaptive.md` — 成组序贯设计、alpha 消耗、中期停止和自适应样本量重估计。

### 经典参考文献
- Fisher, R. A. (1935). *The Design of Experiments*.
- Montgomery, D. C. (2019). *Design and Analysis of Experiments* (10th ed.).
- Hurlbert, S. H. (1984). Pseudoreplication and the design of ecological field
  experiments. *Ecological Monographs*, 54(2), 187–211.
- Lazic, S. E. (2016). *Experimental Design for Laboratory Biologists*.
