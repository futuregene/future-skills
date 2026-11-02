# close-management — 来源与边界

- 上游仓库：https://github.com/GAJETOso/financeskills
- 上游路径：`skills/close-management`
- 固定 commit：`8f8582432b3a9759e7100ce15533d2367c5566a4`
- 许可证：MIT（版权归属：KOMVIA / Ayotunde Oso (GAJETOso)；上游 LICENSE 文件随该仓库分发，本目录不再重复放置）
- 导入日期：2026-11-02
- 分类：business（商务与金融）

## 抽取范围

导入 SKILL.md、EXAMPLE.md、references/close-task-library.md；未导入 evals/，本技能无脚本。

## 我们的改动

未改动正文。

## 使用边界

任务时序按 5 个工作日标准关账设计，需按企业实际日历、ERP 截止时间与集团要求调整；本技能只管编排与依赖，不含具体分录编制（见 revenue-recognition、intercompany-accounting 等）。

## 校验记录（导入时实际执行）

- SKILL.md 内引用的本地路径逐条存在性检查：通过
- 本技能无 .py 脚本，无可执行入口，按清单/模板技能处理
- frontmatter `name` 等于目录名

## 交叉引用说明

正文「Related Skills」指向的上游技能本批未导入：`journal-entry`、`automated-reconciliation`、`statement-preparation`。这些只是文字指引，不构成可调用依赖；需要时按名称回上游仓库取用，不影响本技能独立使用。

## 口径提示

上游为 US GAAP / IFRS 口径；中国大陆企业会计准则（CAS）在适用范围与判断上存在差异，description_zh 与 SOURCE.md 已注明，使用前须按 CAS 自行对照。
