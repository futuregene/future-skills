# 来源与许可

- 上游仓库：https://github.com/ShenShan123/r2g-skills
- 上游路径：`r2g-skills/eda-install`
- 固定提交：`60c2d3c176348bb5d7021e537fd82973be6ab727`（2026-10-28，Allow fixed signoff concurrency and preserve checks across queue handoff）
- 许可证：MIT（Copyright (c) 2026 Shenshan；上游 `LICENSE` 位于仓库根，随仓库再分发时保留版权与许可声明）
- 导入日期：2026-11-02
- 抽取范围：整目录导入（`SKILL.md`、`bootstrap.sh`、`references/`、`scripts/setup/`、`scripts/flow/` 的 `_env.sh` 与 `check_env.sh`、`tests/`）。共 28 个文件、约 170 KB。
- 我们的改动：仅新增本 `SOURCE.md`；脚本与正文未改写。

## 为什么和签核技能一起进

`eda-install` 不是流程技能，而是 `signoff-loop` 的前置安装器：它回答“这台机器上的 OpenROAD / Yosys / iverilog / KLayout / Magic / Netgen / PDK 在不在、不在怎么在无 root 情况下装上”，并把解析结果写进 `signoff-loop/references/env.local.sh`，让签核脚本自动发现工具链。因此它属于“验证与签核”这条线上的配套部分，而不是综合/布局布线流程本身。

脚本里写死了同级的 `signoff-loop` 目录名（`bootstrap.sh`、`scripts/flow/check_env.sh`、`scripts/setup/write_env_local.sh`、`scripts/setup/resolve_pins.sh` 都按 `<skills_root>/signoff-loop/...` 找），所以导入时保留上游目录名，不做重命名；与它同批导入的 `signoff-loop` 恰好对上。

## 使用边界

- **平台**：bash 脚本，Linux x86_64（glibc ≥ 2.35）。Windows / macOS 需 WSL 或 Linux 服务器。
- **磁盘与网络**：默认挑一块 ≥15 GB 可写的卷（PDK 约 8 GB、torch venv 另计），需要访问 GitHub、Conda、Python 软件源；上游全量安装建议 ≥80 GB。
- **权限**：无 root 时走“下载预编译包到用户可写前缀”——固定 sha256 的 r2g 工具链包（OpenROAD/Yosys/KLayout，约 220 MB）+ conda `litex-hub` 的 iverilog/verilator/magic/netgen + venv；有 root 才可能从源码构建 ORFS（`--yes` 才触发，约 30 分钟）。
- **不会自动完成的事**：不跑 PnR、不建数据集；`klayout` 的 conda 配方经常无解（依赖冲突），脚本会优先用系统包并“软失败”。`platform_rules` 层会改写 ORFS 检出（补 nangate45 的 DRC/LVS/天线规则、修 sky130hs 的 `.lyt`），属于可选层，须显式点名才会装。
- **与本次未导入部分的关系**：`graph` 层（torch / torch_geometric / pandas venv）服务于同仓库的 `def-graph` 数据集技能，本批未导入 `def-graph`，该层可按 `--tiers` 跳过。
- **安全**：`bootstrap.sh --dry-run` 只探测与出计划、不安装；上游建议先跑 dry-run。脚本会写 `signoff-loop/references/env.local.sh`（幂等，只写自动探测不到的值）。

## 本批校验

`bash -n` 全量通过（含 `bootstrap.sh` 与 12 个 `scripts/setup/*.sh`）；上游 `tests/` 未在本机执行（需要 bash 环境 + 完整工具链），详见上级 `REPORT.md`。
