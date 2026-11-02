#!/usr/bin/env python3
"""Validate the skill registry: parseable JSON, allowed categories, resolvable
paths, matching frontmatter identity and no duplicate names.

Runs offline; no model calls, credentials or network access.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CATEGORIES = {
    "engineering": "工程与硬件",
    "computing": "数据与计算",
    "life-science": "生命科学与医药",
    "chemistry-materials": "化学与材料",
    "research": "科研与建模",
    "security": "安全与取证",
    "business": "金融与管理",
    "docs": "文档与设计",
    "platform": "平台与工具",
}


def frontmatter_name(text):
    match = re.search(r"^name:\s*(.+)$", text, re.M)
    return match.group(1).strip() if match else None


def main():
    errors = []
    try:
        registry = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"skills.json: {error}", file=sys.stderr)
        return 1
    if not isinstance(registry, dict) or not registry:
        print("skills.json: expected a non-empty JSON object", file=sys.stderr)
        return 1

    seen = set()
    for name, item in registry.items():
        if name in seen:
            errors.append(f"{name}: duplicate registry key")
        seen.add(name)
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
            errors.append(f"{name}: slug must be lowercase letters, digits and hyphens")
        category = item.get("category")
        if category not in CATEGORIES:
            errors.append(f"{name}: unknown category {category!r}")
        elif item.get("category_zh") != CATEGORIES[category]:
            errors.append(f"{name}: category_zh {item.get('category_zh')!r} does not match {category}")
        if item.get("enabled") is not True:
            errors.append(f"{name}: enabled must be true")
        for field in ("name_zh", "description_zh"):
            if not str(item.get(field, "")).strip():
                errors.append(f"{name}: {field} is empty")

        builtin = item.get("builtin") is True
        skill = ROOT / ("builtin" if builtin else "third-party") / name / "SKILL.md"
        if not skill.is_file():
            errors.append(f"{name}: missing {skill.relative_to(ROOT)}")
            continue
        actual = frontmatter_name(skill.read_text(encoding="utf-8"))
        if actual != name:
            errors.append(f"{name}: frontmatter name is {actual!r}")

    directories = {p.name for p in (ROOT / "third-party").glob("*/SKILL.md")}
    directories = {p.parent.name for p in (ROOT / "third-party").glob("*/SKILL.md")}
    unregistered = sorted(directories - set(registry))
    for name in unregistered:
        errors.append(f"third-party/{name}: SKILL.md exists but no registry entry")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    counts = {}
    for item in registry.values():
        counts[item["category"]] = counts.get(item["category"], 0) + 1
    summary = ", ".join(f"{k}={counts[k]}" for k in sorted(counts))
    print(f"PASS: {len(registry)} registry entries over {len(counts)} categories ({summary})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
