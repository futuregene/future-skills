# dcf-model — 来源与边界

- 上游仓库：https://github.com/anthropics/financial-services
- 上游路径：`plugins/vertical-plugins/financial-analysis/skills/dcf-model`
- 固定 commit：`60565064557ca77b12f62aa7877f365d111c129d`
- 许可证：Apache-2.0（版权归属：Anthropic PBC；上游 LICENSE 文件随该仓库分发，本目录不再重复放置）
- 导入日期：2026-11-02
- 分类：business（商务与金融）

## 抽取范围

导入 SKILL.md、TROUBLESHOOTING.md、requirements.txt、scripts/validate_dcf.py；未导入上游 agent-plugins/ 下同名的捆绑副本（内容与 vertical-plugins 版逐字节相同，已用 MD5 比对）。

## 我们的改动

在 frontmatter 之后插入「移植说明」块：指出 recalc.py 的实际来源、LibreOffice 缺失时的替代校验路径，以及 openpyxl data_only 的缓存值陷阱；并记录导入时实测到的 validate_dcf.py 两处缺陷（含 =1/0 的工作簿仍判 PASS、WACC 区间检查抛 AttributeError）。正文其余内容未改动。

## 使用边界

输出是待人工复核的模型草稿，不构成投资建议或估值结论。财务数据由用户提供或取自公开渠道；正文提到的 Daloopa、S&P 等 MCP 连接器属可选付费服务，本环境未接线。正文的 recalc.py 不随本技能分发，需已安装的 xlsx 技能提供，且依赖 LibreOffice(soffice)——本机未检测到，改用本技能自带的 validate_dcf.py 做公式与逻辑校验。openpyxl 不重算公式，data_only=True 读到的只是缓存值：实测含 =1/0 的 openpyxl 工作簿仍被判 PASS，WACC 区间检查会抛 AttributeError 退化为 warning，因此该脚本只能当结构/逻辑自检，公式正确性须以 Excel 重算结果为准。

## 校验记录（导入时实际执行）

- SKILL.md 内引用的本地路径逐条存在性检查：通过
- `scripts/validate_dcf.py` 的 `python -m py_compile` 通过
- 无参运行打印用法（exit 1，符合预期）；对自造的 smoke.xlsx 端到端跑通，输出见 REPORT.md 第 2.1 节
- frontmatter `name` 等于目录名

## 口径提示

通用商务方法，不含特定会计准则；涉及财务数据时以用户提供的口径为准。
