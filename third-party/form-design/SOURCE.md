# SOURCE

| 项目 | 内容 |
|---|---|
| 上游仓库 | https://github.com/Owl-Listener/designer-skills |
| 上游路径 | `interaction-design/skills/form-design/SKILL.md` |
| 固定 commit | `9a6930cf84a822eb458624bd11c61aac5bbdf224`（2026-09-05，仓库 111 个技能时的 HEAD） |
| 许可证 | MIT License，Copyright (c) 2026 MC Dean（见上游 `LICENSE`） |
| 导入日期 | 2026-11-02 |
| 上游域 | `interaction-design`（9 个域之一） |
| 本库分类 | docs（设计方法与评审） |

## 抽取范围

整份 SKILL.md（布局、标签与辅助文本、输入类型对照表、校验时机与错误位置、多步流程、无障碍关联属性）。未取同域 state-machine / error-handling-ux / onboarding-design 等 21 个技能。

## 我们的改动

frontmatter 重写；删 persona 首句；原交叉引用 `error-handling-ux`、`onboarding-design`（未接入）删除；输入类型表与 on-blur 校验规则原样保留；中文触发词补入正文。

## 使用边界

设计规范，不含具体前端框架的表单库用法；ARIA 关联仅给出属性名，落地需按框架文档实现。高风险的支付/医疗/法务表单仍需人工合规评审。

## 复核方式

- 上游为只读检出：`D:/future-os/.future/tmp/hdu-upstream/designer-skills`，未做任何修改。
- 本目录 `SKILL.md` 内引用的表、数值、流程均可在上述 `src` 路径逐条对照。
- 上游不含脚本与可执行资产（该仓库 111 个技能均为单文件 Markdown），因此本技能无可编译代码；
  校验方式为 frontmatter 与引用路径检查，见 stage 根目录 `REPORT.md`。
