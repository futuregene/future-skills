# Future Skills

A collection of AI-assisted skills for scientific research, built for [FutureOS](https://github.com/futuregene/future-os/tree/main).

[中文版](README.zh-CN.md)

## What is a Skill?

A skill is a lightweight AI instruction package defined by a `SKILL.md` file that teaches an AI agent how to accomplish specific domain tasks efficiently. Each skill includes YAML frontmatter metadata (`name`, `version`, `description`) and actionable guidance.

## Directory Structure

```
future-skills/
├── builtin/          # FutureOS built-in skills (13)
├── third-party/      # Curated third-party skills (125)
├── skills.json       # Skill metadata configuration
├── README.md
├── README.zh-CN.md
└── LICENSE
```

## Skill Format

Each skill directory contains a `SKILL.md` entry file:

```markdown
---
name: future-paper
version: 1.0.0
description: Search, download, and analyze scientific papers.
---
# Future Paper

Usage guidance...
```

## skills.json

`skills.json` maintains metadata for all skills, consumed by [FutureOS](https://github.com/futuregene/future-os/tree/main):

```json
{
  "future-paper": {
    "category": "tools",
    "category_zh": "工具",
    "builtin": true,
    "enabled": true,
    "name_zh": "文献搜索与获取",
    "description_zh": "跨多数据库搜索学术文献，按标识符获取全文内容"
  }
}
```

## Contributing

New skills and improvements are welcome.

1. Create a directory under `third-party/` with a `SKILL.md` file
2. Add corresponding metadata in `skills.json`
3. Submit a PR

`SKILL.md` must include `name`, `version`, and `description` fields in its YAML frontmatter.

## License

[MIT](LICENSE)
