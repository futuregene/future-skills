# 3-statement-model — 来源与边界

- 上游仓库：https://github.com/anthropics/financial-services
- 上游路径：`plugins/vertical-plugins/financial-analysis/skills/3-statement-model`
- 固定 commit：`60565064557ca77b12f62aa7877f365d111c129d`
- 许可证：Apache-2.0（版权归属：Anthropic PBC；上游 LICENSE 文件随该仓库分发，本目录不再重复放置）
- 导入日期：2026-11-02
- 分类：business（商务与金融）

## 抽取范围

导入 SKILL.md 与 references/（formatting.md、formulas.md、sec-filings.md）；未导入上游同名捆绑副本（与 vertical-plugins 版逐字节相同）。

## 我们的改动

插入「移植说明」块，说明 recalc.py 的来源与 LibreOffice 缺失时的替代做法，并指向 audit-xls 技能做交付前检查。正文其余内容未改动。

## 使用边界

需要用户提供模板与实际财务数据；正文的 SEC 部分只适用美股申报口径。公式重算依赖 Excel 或 LibreOffice(soffice)，本机未检测到 LibreOffice。最终报表口径需按企业适用准则（US GAAP/IFRS/CAS）复核。

## 校验记录（导入时实际执行）

- SKILL.md 内引用的本地路径逐条存在性检查：通过
- 本技能无 .py 脚本，无可执行入口，按清单/模板技能处理
- frontmatter `name` 等于目录名

## 口径提示

通用商务方法，不含特定会计准则；涉及财务数据时以用户提供的口径为准。
