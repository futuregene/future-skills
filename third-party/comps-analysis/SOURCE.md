# comps-analysis — 来源与边界

- 上游仓库：https://github.com/anthropics/financial-services
- 上游路径：`plugins/vertical-plugins/financial-analysis/skills/comps-analysis`
- 固定 commit：`60565064557ca77b12f62aa7877f365d111c129d`
- 许可证：Apache-2.0（版权归属：Anthropic PBC；上游 LICENSE 文件随该仓库分发，本目录不再重复放置）
- 导入日期：2026-11-02
- 分类：business（商务与金融）

## 抽取范围

导入 SKILL.md 全文（无脚本、无 references）；未导入上游同名捆绑副本。

## 我们的改动

未改动正文；数据源边界写入 SOURCE.md。

## 使用边界

正文要求优先使用 S&P Kensho、FactSet、Daloopa、Bloomberg 等付费数据 MCP，本环境均未接线、未验证；无连接器时只能用用户提供的表格或 SEC EDGAR 等公开数据。任何输出都必须标注数据来源与截止日，且不构成投资建议。

## 校验记录（导入时实际执行）

- SKILL.md 内引用的本地路径逐条存在性检查：通过
- 本技能无 .py 脚本，无可执行入口，按清单/模板技能处理
- frontmatter `name` 等于目录名

## 口径提示

通用商务方法，不含特定会计准则；涉及财务数据时以用户提供的口径为准。
