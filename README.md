# Future Skills

[Future](https://github.com/futuregene/future-os) 平台的 Skills 集合，面向科研场景的 AI 辅助技能库。

## 什么是 Skill？

Skill 是一个轻量级的 AI 指令包，由一个 `SKILL.md` 文件定义，告诉 AI 如何高效完成特定领域任务。每个 skill 包含 YAML frontmatter 元数据（`name`、`version`、`description`）和具体的操作指南。

## 目录结构

```
future-skills/
├── builtin/          # Future 平台内置 skills
│   ├── future-account/
│   ├── future-browser/
│   ├── future-database-lookup/
│   ├── future-deep-research/
│   ├── future-document/
│   ├── future-experimental-design/
│   ├── future-hand-drawn-posters/
│   ├── future-hand-drawn-slides/
│   ├── future-image/
│   ├── future-paper/
│   ├── future-peer-review/
│   ├── future-scientific-writing/
│   ├── future-skill-creator/
│   ├── future-subagent/
│   └── future-web/
├── third-party/      # 精选的第三方 skills
├── skills.json       # Skill 元数据配置
└── README.md
```

## Skill 格式

每个 skill 目录包含一个 `SKILL.md` 入口文件：

```markdown
---
name: future-paper
version: 1.0.0
description: Search, download, and analyze scientific papers.
---
# Future Paper

具体操作指南...
```

## skills.json

`skills.json` 维护每个 skill 的元数据（`category`、`enabled`、`name_zh`、`description_zh` 等），供 Future 平台使用：

```json
{
  "future-paper": {
    "category": "builtin",
    "enabled": true,
    "name_zh": "文献搜索与获取",
    "description_zh": "跨多数据库搜索学术文献，按标识符获取全文内容"
  }
}
```

## 贡献

欢迎提交新的 skill 或改进现有 skill。

1. 在 `third-party/` 下创建目录，放入 `SKILL.md`
2. 在 `skills.json` 中添加对应的元数据
3. 提交 PR

`SKILL.md` 必须包含 YAML frontmatter 中的 `name`、`version`、`description` 字段。

## 许可

[MIT](LICENSE)
