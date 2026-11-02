# inventory-forecasting — 来源与边界

- 上游仓库：https://github.com/w95/awesome-claude-corporate-skills
- 上游路径：`12-procurement-supply-chain/inventory-forecasting`
- 固定 commit：`78dbc7c719920610d5b1c60bd13d9bb52d711c7a`
- 许可证：MIT（版权归属：Enrike (w95)；上游 LICENSE 文件随该仓库分发，本目录不再重复放置）
- 导入日期：2026-11-02
- 分类：business（商务与金融）

## 抽取范围

导入 SKILL.md 全文。

## 我们的改动

未改动正文。

## 使用边界

需要 12–24 个月历史销量与提前期数据；安全库存公式假设需求近似正态，长尾/间歇需求须改用 Croston 类方法。与 financeskills 的 inventory-costing 分工：本技能定补货量，后者做存货计价。

## 校验记录（导入时实际执行）

- SKILL.md 内引用的本地路径逐条存在性检查：通过
- 本技能无 .py 脚本，无可执行入口，按清单/模板技能处理
- frontmatter `name` 等于目录名

## 口径提示

通用商务方法，不含特定会计准则；涉及财务数据时以用户提供的口径为准。
