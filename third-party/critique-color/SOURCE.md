# SOURCE

| 项目 | 内容 |
|---|---|
| 上游仓库 | https://github.com/Owl-Listener/designer-skills |
| 上游路径 | `visual-critique/skills/critique-color/SKILL.md` |
| 固定 commit | `9a6930cf84a822eb458624bd11c61aac5bbdf224`（2026-09-05，仓库 111 个技能时的 HEAD） |
| 许可证 | MIT License，Copyright (c) 2026 MC Dean（见上游 `LICENSE`） |
| 导入日期 | 2026-11-02 |
| 上游域 | `visual-critique`（9 个域之一） |
| 本库分类 | docs（设计方法与评审） |

## 抽取范围

整份 SKILL.md（对比度阈值、调色板一致性、语义色、色觉与强制色彩模式、输出三段式与pass/minor/major 评级、常见失败清单）。未取同域 critique-typography / critique-composition 等 6 个技能。

## 我们的改动

frontmatter 重写；删 persona 首句；原交叉引用 `accessibility-audit`、`color-system`（未接入）删除；新增按 WCAG 相对亮度公式核算过的对比度参考值（#767676=4.54:1、#949494=3.03:1，本库已用脚本复算）；中文触发词补入正文。

## 使用边界

单屏色彩评审，不做产品级 WCAG 合规审计（未接入 accessibility-audit）；对比度须实测，禁止凭目测给结论。WCAG 阈值针对不透明背景，半透明叠加色需先合成再算。

## 复核方式

- 上游为只读检出：`D:/future-os/.future/tmp/hdu-upstream/designer-skills`，未做任何修改。
- 本目录 `SKILL.md` 内引用的表、数值、流程均可在上述 `src` 路径逐条对照。
- 上游不含脚本与可执行资产（该仓库 111 个技能均为单文件 Markdown），因此本技能无可编译代码；
  校验方式为 frontmatter 与引用路径检查，见 stage 根目录 `REPORT.md`。
