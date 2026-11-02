# 来源与许可

- 上游仓库：https://github.com/ShenShan123/r2g-skills
- 上游路径：`r2g-skills/signoff-loop`
- 固定提交：`60c2d3c176348bb5d7021e537fd82973be6ab727`（2026-10-28，Allow fixed signoff concurrency and preserve checks across queue handoff）
- 许可证：MIT（Copyright (c) 2026 Shenshan；上游 `LICENSE` 位于仓库根，随仓库再分发时保留版权与许可声明）
- 导入日期：2026-11-02
- 抽取范围：`SKILL.md`、`scripts/`、`references/`、`assets/`、`tests/`、`knowledge/`（Python 代码、`schema.sql`、`heuristics.json`、`families.json`、`eval/`）。共 333 个文件、4.36 MB。
- 未导入：`knowledge/knowledge.sqlite`（16.1 MB 二进制预训练经验库）。原因有两条：本仓库以文本形式版本化技能，二进制不可 diff 也不可合并；且该库是上游自身跑批得到的度量数据，换环境后排序权重不可直接采信。
- 我们的改动：
  1. `SKILL.md` 末尾追加一节 `Distribution note (Future Skills import)`，说明上述裁剪对正文 §10 / §10b 的影响；正文其余部分与上游逐字节一致。
  2. 新增本 `SOURCE.md` 与 `skills.json` 元数据，未改动任何脚本。

## 使用边界

- **工具链**：必需 `python3`（上游写 3.13+）、`yosys`、`iverilog` + `vvp`、`openroad`，以及 OpenROAD-flow-scripts（ORFS）检出和 PDK（sky130A、sky130hs、gf180、ihp-sg13g2、nangate45 之一，PDK 约 8 GB）；可选 `verilator`、`klayout`、`magic`、`netgen-lvs`、`opensta`。没有 ORFS + PDK，签核阶段无法真实执行。
- **平台**：流程脚本是 bash；上游 README 明确该工具链只提供 Linux x86_64 预编译包（glibc ≥ 2.35）。Windows / macOS 必须走 WSL 或一台 Linux 服务器，本机原生不可用。
- **是否依赖商业工具**：不依赖。综合与布局布线由开源 Yosys + ORFS 完成，签核由开源 KLayout（DRC/LVS）、Magic（sky130 DRC / SPICE 抽取）、Netgen（sky130 LVS）、OpenRCX（寄生抽取）完成，`references/*.json` 里是开源规则面。**但这不等于流片级签核**：上游自己写明 asap7 平台不受支持（社区 KLayout 规则存在无法消除的假违规、且没有 LVS 规则），真正的晶圆厂 signoff 仍需商业 Calibre 规则与授权工具，本技能不提供、也未验证。
- **资源与时长**：单设计 RTL→GDS 全流程分钟级到小时级；大设计 LVS 需把 `LVS_TIMEOUT` 提到 4200–7200 s；上游安装与跑批建议 ≥80 GB 可用空间（工具链安装器本身要求 ≥15 GB 单卷）。
- **配套技能**：同仓库的 `def-graph`（签核后 DEF→PyG 图数据集）与 `rtl-acquire`（设计语料扩充）本次未导入；本技能的 DRC/LVS/RCX 签核不依赖它们，只有可选的“数据集构建”阶段需要。
- **首次运行**：`knowledge/ingest_run.py` 首次运行会按 `knowledge/schema.sql` 建库，配方/候选表初始为空，`references/` 里人工整理的策略目录与失败知识库照常可用，只是没有历史经验加权。

## 本批校验

见同目录上级 `REPORT.md` 的“验证证据”一节：全部 `.py` 编译、全部 `.sh` 过 `bash -n`、4 个 argparse 入口 `-h` 实跑、上游测试套件未在本机执行（需 Linux EDA 工具链）。
