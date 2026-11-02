# Future Skills

A collection of AI-assisted skills for scientific research, built for [FutureOS](https://github.com/futuregene/future-os/tree/main).

> **默认服务对象是杭州电子科技大学。** 注册表里的 `scope` 字段区分三种口径：`general`（学科通用）与
> `hdu`（按杭电 9 个一级学科博士点选取）构成默认集合；其他学校的条目带
> `cross-school:<school>`，单独列在 [docs/school-scope.md](docs/school-scope.md)，不会混进默认视图。
> 默认集合的取法与每个 `cross-school:*` 条目对应的学校/学科见该文件。

[中文版](README.zh-CN.md)

## What is a Skill?

A skill is a lightweight AI instruction package defined by a `SKILL.md` file that teaches an AI agent how to accomplish specific domain tasks efficiently. Each skill includes YAML frontmatter metadata (`name`, `version`, `description`) and actionable guidance.

## Directory Structure

```
future-skills/
├── builtin/          # FutureOS built-in skills
├── third-party/      # Curated third-party skills
├── docs/             # Coverage notes and the evaluation backlog
├── tests/            # Offline validators and regressions
├── skills.json       # Skill metadata configuration
├── README.md
├── README.zh-CN.md
└── LICENSE
```

Every skill belongs to exactly one of nine categories — `engineering`, `computing`,
`life-science`, `chemistry-materials`, `research`, `security`, `business`, `docs`,
`platform`. [docs/discipline-coverage.md](docs/discipline-coverage.md) maps them to the
disciplines we serve and lists what is evaluated but deliberately not shipped.

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
    "category": "research",
    "category_zh": "科研与建模",
    "builtin": true,
    "enabled": true,
    "name_zh": "文献搜索与获取",
    "description_zh": "跨多数据库搜索学术文献，按标识符获取全文内容"
  }
}
```

`category` must be one of the nine categories above; `tests/check_registry.py` rejects
anything else, a missing skill directory, or a frontmatter `name` that differs from the
registry key.

## Contributing

New skills and improvements are welcome.

1. Create a directory under `third-party/` with a `SKILL.md` file
2. Add corresponding metadata in `skills.json`
3. Submit a PR

`SKILL.md` must include `name`, `version`, and `description` fields in its YAML frontmatter.

## Offline validation

In a task-local virtual environment:

```bash
python -m pip install -r tests/requirements.txt
python tests/run_offline.py
```

Run this entry locally or in CI on Linux, Windows and macOS. It checks every builtin's frontmatter,
registry, fences and resource pointers, then runs scientific design, slide runner
and validator regressions. Image generation is mocked; no credentials, paid model
calls or live database/browser access are needed. Offline success is not evidence
of end-to-end model behavior or external API availability.

## License

[MIT](LICENSE)
