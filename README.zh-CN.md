# Future Skills

面向科研场景的 AI 辅助技能库，为 [FutureOS](https://github.com/futuregene/future-os/tree/main) 构建。

[English](README.md)

## 什么是 Skill？

Skill 是一个轻量级的 AI 指令包，由一个 `SKILL.md` 文件定义，告诉 AI 如何高效完成特定领域任务。每个 skill 包含 YAML frontmatter 元数据（`name`、`version`、`description`）和具体的操作指南。

## 目录结构

```
future-skills/
├── builtin/          # FutureOS 内置 skills
├── third-party/      # 精选的第三方 skills
├── skills.json       # Skill 元数据配置
├── README.md
├── README.zh-CN.md
└── LICENSE
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

`skills.json` 维护所有 skill 的元数据，供 [FutureOS](https://github.com/futuregene/future-os/tree/main) 使用：

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

## 贡献

欢迎提交新的 skill 或改进现有 skill。

1. 在 `third-party/` 下创建目录，放入 `SKILL.md`
2. 在 `skills.json` 中添加对应的元数据
3. 提交 PR

`SKILL.md` 必须包含 YAML frontmatter 中的 `name`、`version`、`description` 字段。

## 离线验证

在任务专用虚拟环境中执行：

```bash
python -m pip install -r tests/requirements.txt
python tests/run_offline.py
```

该入口可用于 Linux、Windows、macOS 的本地或 CI 环境，校验全部 builtin 的 frontmatter、
注册表、代码围栏与资源引用，并运行实验设计、slides runner 和校验器回归测试。
图像生成使用 mock，不需要账户凭证、付费模型调用或真实数据库/浏览器访问。
离线通过不代表端到端模型行为或外部 API 可用性已验证。

## 许可

[MIT](LICENSE)
