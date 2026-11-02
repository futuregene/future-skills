# SOURCE

| 项目 | 内容 |
|---|---|
| 上游仓库 | https://github.com/Owl-Listener/designer-skills |
| 上游路径 | `design-research/skills/survey-design/SKILL.md` |
| 固定 commit | `9a6930cf84a822eb458624bd11c61aac5bbdf224`（2026-09-05，仓库 111 个技能时的 HEAD） |
| 许可证 | MIT License，Copyright (c) 2026 MC Dean（见上游 `LICENSE`） |
| 导入日期 | 2026-11-02 |
| 上游域 | `design-research`（9 个域之一） |
| 本库分类 | docs（设计方法与评审） |

## 抽取范围

整份 SKILL.md（适用判断、问卷结构、题型对照表、问句写法反例、Likert/NPS/SUS 量表数值、抽样与样本量、结果分析）。未取同域其余 13 个技能（interview-script、affinity-diagram 等）。

## 我们的改动

frontmatter 重写（license / category / metadata + 本库 description）；删 persona 首句；原交叉引用 `a-b-test-design`（未接入）改为在 description 中声明边界；表格与数值原样保留，中文触发词补入正文。

## 使用边界

问卷方法学，不含问卷投放平台与统计软件操作；样本量 385 等数字对应 95% 置信度、±5% 误差的大总体场景，其他设计需重算。NPS/SUS 的阈值是行业惯用基准，不是产品结论。

## 复核方式

- 上游为只读检出：`D:/future-os/.future/tmp/hdu-upstream/designer-skills`，未做任何修改。
- 本目录 `SKILL.md` 内引用的表、数值、流程均可在上述 `src` 路径逐条对照。
- 上游不含脚本与可执行资产（该仓库 111 个技能均为单文件 Markdown），因此本技能无可编译代码；
  校验方式为 frontmatter 与引用路径检查，见 stage 根目录 `REPORT.md`。
