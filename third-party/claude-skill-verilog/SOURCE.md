# 来源与许可

- 上游仓库：https://github.com/londey/claude-skill-verilog
- 上游路径：仓库根（`SKILL.md`、`README.md`、`LICENSE`）
- 固定提交：`71331ce0c9cca9ccbbb1fb6048b2ecef9b4c062f`（2026-04-21，Refactor Fixed-Point Notation and Formatting sections for clarity and consistency in SKILL.md）
- 许可证：MIT（Copyright (c) 2026 Nicholas Londey；`LICENSE` 随目录一起保留）
- 导入日期：2026-11-02
- 抽取范围：整仓库导入（3 个文件，约 14 KB）。
- 我们的改动：仅新增本 `SOURCE.md`；`SKILL.md` 正文与 frontmatter 未改写。

## 这份技能给的是什么

一份可直接照着写的 Verilog/SystemVerilog **编码规范 + Verilator 工作流**：命名（`_n` 低有效、`clk_<domain>`）、`always_ff` 只放简单非阻塞赋值、组合逻辑全进 `always_comb`、默认赋值防锁存、定点 Q/UQ 记法、同步复位与 2 级同步器 CDC、存储器推断、SVA 断言、命名端口例化、`default_nettype none`；以及按 Yosys 可综合性给出的禁忌表（`return`、`interface`/`modport`、`unique`/`priority case`、多维打包端口）。

它是规范型技能，不含脚本，命令只有 Verilator 的三条实跑形式（`verilator --binary`、`--lint-only -Wall`、推荐的仿真 flag 组合），因此不需要额外资源文件。

## 使用边界

- **需要用户自备工具**：`verilator`（lint / 仿真），可选 `yosys`（可综合性验证）。本技能只给命令与规范，不安装工具；装工具用 `eda-install` 或发行版包管理器。
- **适用范围**：可综合 RTL 与配套 testbench 的写法约定；对 UVM 验证平台、SystemC/TLM 建模、混合信号不覆盖。
- **不是自动检查器**：正文给的是人工/lint 判据，没有附带的 lint 脚本或规则文件；要机器判据需自行接 Verilator/Verible/slang。
- **风格是主张，不是标准**：例如“输出寄存器化”“模块不超过约 500 行”“所有模块必须有 testbench”是作者约定，与某些团队/开源项目（如 lowRISC 的端口后缀风格）相反；团队已有风格时以团队为准。

## 本批校验

`SKILL.md` frontmatter 的 `name` 与目录名一致；正文引用的工具命令为 Verilator/Yosys 实命令（本机无 verilator，未实跑）；详见上级 `REPORT.md`。
