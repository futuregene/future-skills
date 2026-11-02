# lease-accounting — 来源与边界

- 上游仓库：https://github.com/GAJETOso/financeskills
- 上游路径：`skills/lease-accounting`
- 固定 commit：`8f8582432b3a9759e7100ce15533d2367c5566a4`
- 许可证：MIT（版权归属：KOMVIA / Ayotunde Oso (GAJETOso)；上游 LICENSE 文件随该仓库分发，本目录不再重复放置）
- 导入日期：2026-11-02
- 分类：business（商务与金融）

## 抽取范围

导入 SKILL.md、EXAMPLE.md、scripts/calculate.py、references/ibr-guide.md、assets/commencement-summary-template.md；未导入 evals/。

## 我们的改动

未改动正文与脚本。

## 使用边界

IFRS 16 单一模型与 ASC 842 双模型的差异在正文中并列说明；中国大陆 CAS 21 需自行对照。增量借款利率（IBR）需用户提供或按 references/ibr-guide.md 估算，不得凭空取值。

## 校验记录（导入时实际执行）

- SKILL.md 内引用的本地路径逐条存在性检查：通过
- 目录内 .py 全部 `python -m py_compile` 通过；`__main__` 自测实跑 exit 0，输出见 REPORT.md
- frontmatter `name` 等于目录名

## 交叉引用说明

正文「Related Skills」指向的上游技能本批未导入：`journal-entry`、`aro-computation`、`statement-preparation`。这些只是文字指引，不构成可调用依赖；需要时按名称回上游仓库取用，不影响本技能独立使用。

## 口径提示

上游为 US GAAP / IFRS 口径；中国大陆企业会计准则（CAS）在适用范围与判断上存在差异，description_zh 与 SOURCE.md 已注明，使用前须按 CAS 自行对照。
