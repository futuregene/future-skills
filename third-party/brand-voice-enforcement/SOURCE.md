# brand-voice-enforcement — 来源与边界

- 上游仓库：https://github.com/w95/awesome-claude-corporate-skills
- 上游路径：`04-marketing/brand-voice-enforcement`
- 固定 commit：`78dbc7c719920610d5b1c60bd13d9bb52d711c7a`
- 许可证：MIT（版权归属：Enrike (w95)；上游 LICENSE 文件随该仓库分发，本目录不再重复放置）
- 导入日期：2026-11-02
- 分类：business（商务与金融）

## 抽取范围

导入 SKILL.md 与 references/（before-after-examples.md、voice-constant-tone-flexes.md）。

## 我们的改动

未改动正文；读取路径的替代方式写入 SOURCE.md 与 boundary。

## 使用边界

上游按 .claude/brand-voice-guidelines.md 与 /brand-voice 插件命令读取指南，本环境无这些命令：改为由用户指定指南文件路径或直接粘贴，找不到指南时先问，不得臆造品牌口吻。

## 校验记录（导入时实际执行）

- SKILL.md 内引用的本地路径逐条存在性检查：通过
- 本技能无 .py 脚本，无可执行入口，按清单/模板技能处理
- frontmatter `name` 等于目录名

## 口径提示

通用商务方法，不含特定会计准则；涉及财务数据时以用户提供的口径为准。
