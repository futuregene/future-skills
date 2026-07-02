# Future Skills

Future 平台的 Skills 管理仓库。统一管理 Future 平台专属 skills 和经过审核的第三方 skills，并提供一条命令发布到 `future-server`。

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
│   └── publish.sh    # 发布脚本
├── Makefile
└── README.md
```

每个 skill 目录包含一个 `SKILL.md` 入口文件，带 YAML frontmatter（`name`、`version`、`description`）。前端元数据以外的字段（`category`、`price` 等）统一在 `skills.json` 中维护。

## 快速开始

### 发布单个 skill

```bash
make publish SKILL=future-account
```

这会将指定的 skill 打包为 zip、复制到 `future-server/data/skills/`，并自动重新生成 `skills-insert.sql`。

### 发布所有 Future 平台专属 skills

```bash
make publish-all
```

### 清理

```bash
make clean   # 删除 future-server/data/skills/ 中的 zip 和 SQL
```

## 添加新 skill

### Future 平台专属 skill

在 `builtin/` 下创建目录，放入 `SKILL.md`（必须包含 YAML frontmatter 中的 `name`、`version`、`description`），然后在 `skills.json` 中添加元数据。

### 第三方 skill

在 `third-party/` 下创建目录，结构同上。审核通过后即可通过 `make publish SKILL=<name>` 发布。

## 发布流程

`make publish` 会执行以下步骤：

1. 从 `SKILL.md` frontmatter 读取 `name`、`version`、`description`
2. 从 `skills.json` 读取 `category`、`price`、`formats`、`limit`、`enabled`
3. 将 skill 目录打包为 `{name}-{version}.zip`
4. 复制 zip 到 `../future-server/data/skills/`
5. 生成幂等 SQL（`INSERT ... ON CONFLICT DO UPDATE`）
6. 重新扫描所有已发布的 zip，生成完整的 `skills-insert.sql`

SQL 中的 `skill_versions.id` 使用确定性 UUID v5（namespace + `{skill_id}:{version}`），同一 skill 同一版本每次生成的 UUID 相同，确保 SQL 可安全重复执行。
