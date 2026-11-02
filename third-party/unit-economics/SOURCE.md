# unit-economics — 来源与边界

- 上游仓库：https://github.com/anthropics/financial-services
- 上游路径：`plugins/vertical-plugins/private-equity/skills/unit-economics`
- 固定 commit：`60565064557ca77b12f62aa7877f365d111c129d`
- 许可证：Apache-2.0（版权归属：Anthropic PBC；上游 LICENSE 文件随该仓库分发，本目录不再重复放置）
- 导入日期：2026-11-02
- 分类：business（商务与金融）

## 抽取范围

导入 SKILL.md 全文。

## 我们的改动

未改动正文。

## 使用边界

指标定义为行业通用近似（ARR、NRR、LTV/CAC），必须按用户业务口径校准；正文的 LTV/CAC>3× 等阈值是经验基准，不是普适标准。无外部依赖，不构成估值结论。

## 校验记录（导入时实际执行）

- SKILL.md 内引用的本地路径逐条存在性检查：通过
- 本技能无 .py 脚本，无可执行入口，按清单/模板技能处理
- frontmatter `name` 等于目录名

## 口径提示

通用商务方法，不含特定会计准则；涉及财务数据时以用户提供的口径为准。
