# Future Skills

Future 平台的 Skills 集合。包含 Future 平台内置 skills 和经过审核的第三方 skills。

## 目录结构

```
future-skills/
├── builtin/          # Future 平台内置 skills（Builtin）
│   ├── future-account/
│   ├── future-browser/
│   ├── future-deep-research/
│   ├── future-document/
│   ├── future-hand-drawn-posters/
│   ├── future-hand-drawn-slides/
│   ├── future-image/
│   ├── future-paper/
│   ├── future-skill-creator/
│   ├── future-subagent/
│   └── future-web/
├── third-party/      # 审核过的第三方 skills
├── skills.json       # Skill 元数据配置（category、price 等）
├── scripts/
│   └── download.sh   # 从 GitHub 下载 skill 到 pending-review/
├── Makefile
└── README.md
```

每个 skill 目录包含一个 `SKILL.md` 入口文件，带 YAML frontmatter（`name`、`version`、`description`）。前端元数据以外的字段（`category`、`price` 等）统一在 `skills.json` 中维护。

## 添加新 skill

### Future 平台内置 skill

在 `builtin/` 下创建目录，放入 `SKILL.md`（必须包含 YAML frontmatter 中的 `name`、`version`、`description`），然后在 `skills.json` 中添加元数据。

### 第三方 skill

在 `third-party/` 下创建目录，结构同上。审核通过后即可发布。

## 下载 skill 进行审核

```bash
make download https://github.com/owner/repo/tree/branch/path/to/skill
```

这会将 skill 下载到 `pending-review/<skill-name>/`。审核通过后，将其移动到 `builtin/` 或 `third-party/` 并在 `skills.json` 中添加元数据。
