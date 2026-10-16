# TODO: future-experimental-design 依赖问题

> 来源：从 K-Dense-AI/scientific-agent-skills 原样迁移时发现的依赖工程问题。
> 创建日期：2026-06-30

---

## 1. 核心 Python 依赖未在 pyproject.toml 中声明（高优先级）

两个脚本 `scripts/randomization.py` 和 `scripts/doe_designs.py` 依赖以下包：

| 包 | 用途 | 使用脚本 | 声明位置 |
|---|---|---|---|
| **numpy** | 随机数生成（`default_rng`）、数组操作、排列 | 两个脚本 | ❌ 未声明 |
| **pandas** | DataFrame 构建、`concat`、`groupby`、`value_counts` | 两个脚本 | ❌ 未声明 |
| **pyDOE3** | DOE 矩阵生成（`fullfact`、`ff2n`、`fracfact`、`pbdesign`、`ccdesign`、`bbdesign`、`lhs`） | `doe_designs.py` | ❌ 未声明 |

现状：`future-skills` 没有集中的 Python 依赖管理文件。`SKILL.md` 中以自然语言描述了安装命令（`uv pip install numpy pandas pyDOE3`），但没有机器可读的依赖声明。

**需要做的事：**
- [ ] 决定依赖声明方式（`requirements.txt`、`pyproject.toml` 中的 `[project.optional-dependencies]`，或 skill 级别的 `pyproject.toml`）
- [ ] 将 numpy、pandas、pyDOE3 声明为 `future-experimental-design` 的依赖
- [ ] 确保最小版本约束：`numpy>=1.26`、`pandas>=2.0`（与原始 SKILL.md 一致）

---

## 2. Python 版本约束冲突（中优先级）

| 来源 | 要求 |
|---|---|
| SKILL.md（原始） | Python >= 3.10 |
| scientific-agent-skills `pyproject.toml` | Python >= 3.13 |
| Future 平台当前约束 | 未定义 |

影响分析：
- Python 3.13 不支持 numpy 1.x，必须使用 numpy >= 2.x
- pandas >= 2.0 兼容 Python 3.10-3.13
- pyDOE3 兼容 Python 3.10+

**需要做的事：**
- [ ] 确定 Future 平台支持的最低 Python 版本
- [ ] 统一 SKILL.md 中的版本声明
- [ ] 在 CI/验证中加入 Python 版本检查

---

## 3. 无 skill 级依赖隔离（中优先级）

现状：所有 skill 共享同一个仓库环境，没有 skill 级别的依赖隔离机制。

影响：
- 用户无法按需安装单个 skill 的依赖（如 `pip install future-skills[experimental-design]`）
- 如果某个 skill 的依赖与其他 skill 冲突，无法独立管理

**需要做的事：**
- [ ] 考虑是否为每个 skill 添加独立的 `pyproject.toml` 或 `requirements.txt`
- [ ] 或者使用 `uv` 的 workspace 特性按 skill 分组依赖

---

## 4. pyDOE3 供应链风险（低优先级）

`pyDOE3` 是社区 fork，维护活跃度一般。如果它停止维护：

- `doe_designs.py` 中的所有 6 个 DOE 生成函数将失效：
  - `full_factorial`
  - `two_level_factorial`
  - `fractional_factorial`
  - `plackett_burman`
  - `central_composite`
  - `box_behnken`
  - `latin_hypercube`（也依赖 pyDOE3 的 `lhs`）

影响：中高（7 个函数全部受影响），但概率低（pyDOE3 仍在 PyPI 上可用）。

**需要做的事：**
- [ ] 评估是否将关键 DOE 算法内联/替换为标准库实现
- [ ] 或者 pin pyDOE3 的精确版本以防 breaking changes
- [ ] 添加回归测试，确保升级 pyDOE3 后结果一致

---

## 5. 与下游 Skill 的引用需要对齐

`SKILL.md` 中引用了以下 Future 平台尚未实现的 skill：

| 引用名称 | Future 平台状态 |
|---|---|
| `future-statistical-power` | 未确认是否存在 |
| `future-statistical-analysis` | 未确认是否存在 |

原始引用为 `statistical-power` 和 `statistical-analysis`，已在 SKILL.md 中改名为 Future 命名约定。但这些下游 skill 尚未在 `future-skills/` 中创建。

**需要做的事：**
- [ ] 确认 `future-statistical-power` 和 `future-statistical-analysis` 是否需要创建
- [ ] 如果暂不创建，在 SKILL.md 中标注为"计划中"

---

## 6. 安装指令硬编码了 uv

`SKILL.md` 中的安装指令使用 `uv pip install`，但：
- Future 平台用户可能使用 `pip`、`pipx` 或其他包管理器
- Future 平台可能需要自动处理依赖安装，而非依赖用户手动操作

**需要做的事：**
- [ ] 添加替代安装指令（`pip install`）
- [ ] 考虑在 Future 平台的 skill 加载流程中自动安装依赖

---

## 优先级总结

| # | 问题 | 优先级 | 预计工作量 |
|---|---|---|---|
| 1 | 核心依赖未声明 | 🔴 高 | 小 |
| 2 | Python 版本约束冲突 | 🟡 中 | 小 |
| 3 | 无 skill 级依赖隔离 | 🟡 中 | 中 |
| 5 | 下游 skill 引用未对齐 | 🟡 中 | 取决于是否创建下游 skill |
| 4 | pyDOE3 供应链风险 | 🟢 低 | 中 |
| 6 | 安装指令硬编码 | 🟢 低 | 小 |
