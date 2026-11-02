# SOURCE

| 项目 | 内容 |
|---|---|
| 上游仓库 | https://github.com/Owl-Listener/designer-skills |
| 上游路径 | `design-systems/skills/motion-system/SKILL.md` |
| 固定 commit | `9a6930cf84a822eb458624bd11c61aac5bbdf224`（2026-09-05，仓库 111 个技能时的 HEAD） |
| 许可证 | MIT License，Copyright (c) 2026 MC Dean（见上游 `LICENSE`） |
| 导入日期 | 2026-11-02 |
| 上游域 | `design-systems`（9 个域之一） |
| 本库分类 | docs（设计方法与评审） |

## 抽取范围

整份 SKILL.md（时长 token 表、缓动曲线表、编排/错峰规则、prefers-reduced-motion 处理、实现建议）。未取同域 design-token / component-spec / localization-design 等 10 个技能。

## 我们的改动

frontmatter 重写；删 persona 首句；原交叉引用 `animation-principles`（未接入）删除；新增可直接抄用的 CSS 自定义属性与 reduced-motion 覆盖代码块（原文仅为文字描述）；时长与 cubic-bezier 数值原样保留。

## 使用边界

规范与取值，不含具体动画库实现；时长数值是起点而非绝对标准，须在低端设备上实测；reduced-motion 只覆盖 CSS 层，原生端（iOS/Android）需各自实现。

## 复核方式

- 上游为只读检出：`D:/future-os/.future/tmp/hdu-upstream/designer-skills`，未做任何修改。
- 本目录 `SKILL.md` 内引用的表、数值、流程均可在上述 `src` 路径逐条对照。
- 上游不含脚本与可执行资产（该仓库 111 个技能均为单文件 Markdown），因此本技能无可编译代码；
  校验方式为 frontmatter 与引用路径检查，见 stage 根目录 `REPORT.md`。
