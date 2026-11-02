# dwsim — 来源与边界

- 上游仓库：https://github.com/fdias78git/dwsim-claude-integration
- 上游路径：`.claude/skills/dwsim (SKILL.md) + src/ + run.py + config.example.json + README.md + SETUP.md + .claude/agents/dwsim-expert.md`
- 固定 commit：`91e1f7a5f7349467e9fb8b781364a3ea65ad8713`（导入时 `git log -1` 逐一核对）
- 许可：MIT（Copyright (c) 2026 Felipe Dias）。上游 LICENSE 随该仓库分发，本目录不再重复放置。DWSIM 本体为 GPLv3，本技能不含其二进制。
- 导入日期：2026-11-02
- 分类：engineering（工程与硬件）

## 抽取范围

导入 `SKILL.md`（补 frontmatter + 移植说明）、整个 `src/` 库（23 个 .py，含 core/flowsheet、thermo、streams、unitops、visualization 五个子包）、`run.py`、`config.example.json`、`README.md`、`SETUP.md`，以及 `.claude/agents/dwsim-expert.md` → `references/dwsim-expert-agent.md`。未导入 `.claude/commands/*.md`（`/dwsim`、`/dwsim-flash`、`/dwsim-props`）、`SETUP_PROMPT.md`、`CHANGELOG.md`、`.gitignore`。

## 我们的改动

1) 补 YAML frontmatter（`name`/`description`），上游没有；2) 在 frontmatter 之后插入「移植说明」块；3) 正文 Step 2 唯一一处文字改动：把「Apply the selection table from the `dwsim-expert` agent」改为指向随本技能导入的 `references/dwsim-expert-agent.md`，因为原表在上游 agent 文件里、只导 SKILL.md 会留下悬空引用。其余正文逐字节未动。

## 使用边界

必须先在 Windows/.NET 上安装 DWSIM 桌面端并 `pip install pythonnet` 才能跑流程模拟、闪蒸与单元操作；本机两者都没有，`DWSIMAutomation()` 构造即 `ValueError`，`initialize()` 会卡在 `import clr`。无 DWSIM 时真正可用的只有物性方法推荐（22 条目录）与 21 个常见组分的内置物性，`db.search("propyl")` 这类正文示例在无引擎时会返回空表。上游按 Windows 叙述，Linux 需 Mono，macOS 未验证。模拟结果需按质量/摩尔分率守恒与相态合理性人工复核，不能当作工程定案。

## 校验记录（导入时实际执行）

1) 逐个 clone 上游并 `git log -1` 核对 commit = `91e1f7a`；`gh api` 核对 MIT 许可、23 星、2026-03-30 最后推送。
2) `py_compile` 23/23 通过；16 个模块 `import` 全通过（`clr` 只在 `initialize()` 内导入）。
3) 无引擎子集实跑：`PropertyPackageManager.recommend_for_system()` 三组输入返回合理方法链；`CompoundDatabase.list_all()` = 21 个组分，`get_info("Water")` 给出 Tc=647.14 K、Pc=22064000 Pa、ω=0.344；`search("propyl")` = `[]`；`DWSIMAutomation()` = `ValueError: DWSIM path not configured`。
4) frontmatter `name` 等于目录名 `dwsim`；`references/dwsim-expert-agent.md` 与 `src/` 均在目录内。
