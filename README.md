# Future Skills

A collection of AI-assisted skills for scientific research, built for FutureOS.

[中文版](README.zh-CN.md)

## What is a Skill?

A skill is a lightweight AI instruction package defined by a `SKILL.md` file that teaches an AI agent how to accomplish specific domain tasks efficiently. Each skill includes YAML frontmatter metadata (`name`, `version`, `description`) and actionable guidance.

## Directory Structure

```
future-skills/
├── builtin/          # FutureOS built-in skills
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
├── third-party/      # Curated third-party skills
├── skills.json       # Skill metadata configuration
└── README.md
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

`skills.json` maintains metadata for each skill (`category`, `enabled`, `name`, `description`, etc.), consumed by FutureOS:

```json
{
  "future-paper": {
    "category": "builtin",
    "enabled": true,
    "name": "Literature Search",
    "description": "Search academic papers across multiple databases and retrieve full-text by identifier"
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
