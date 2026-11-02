# thermo-package — 来源与边界

- 上游仓库：https://github.com/Soljourner/claude-engineering-skills
- 上游路径：`skills/packages/thermo-package`
- 固定 commit：`1c3340ba171b475fb0ecd7b1699e41dac6acd986`（导入时 `git log -1` 逐一核对）
- 许可：MIT（Copyright (c) 2025 Soljourner）。上游 LICENSE/LICENSE.md 随该仓库分发，本目录不再重复放置。
- 导入日期：2026-11-02
- 分类：engineering（工程与硬件）

## 抽取范围

导入 `SKILL.md`、`examples.py`、`reference.md` 三件；该目录在上游只有这三件。

## 我们的改动

仅在 frontmatter 之后插入「移植说明」块（实测版本、GBK 控制台坑、100 °C 相位坑、维护状态），`SKILL.md` 其余正文、`examples.py`、`reference.md` 逐字节未动。正文按「泵工程」组织（上游定位），混合物 VLE/EOS 部分可独立用于化工热力学，不限于泵。

## 使用边界

需要 `pip install thermo chemicals`（实测 thermo 0.6.1、chemicals 1.5.2、连带 fluids 1.3.1），是纯 Python 相关式库，不依赖 DWSIM 也不依赖 CoolProp。它给的是工程相关式（DIPPR 等）与 PR/SRK 类 EOS，精度低于 CoolProp 的状态方程物性，交叉验证时以 CoolProp/REFPROP 为基准。脚本第 567 行含 `✓`，中文 Windows GBK 控制台下需 `PYTHONIOENCODING=utf-8`。100 °C/1 atm 行同样会返回气相值。

## 校验记录（导入时实际执行）

1) clone 并 `git log -1` 核对 commit = `1c3340ba`；`gh api` 核对 MIT、97 星、2025-11-07 最后推送（建库当天，此后无提交）。
2) `py_compile` 通过；装 thermo 0.6.1 + chemicals 1.5.2 后 `examples.py` 退出码 0、324 行输出，8 个示例全过（20 °C 水 μ=1.0016 cP、ρ=998.21 kg/m³）。
3) 未设 `PYTHONIOENCODING=utf-8` 时实测复现 `UnicodeEncodeError: 'gbk' codec can't encode character '\u2713'`（第 567 行）。
4) frontmatter `name` 等于目录名 `thermo-package`。
