#!/usr/bin/env python3
"""Validate a staged import produced by a goal worker.

Usage: python stage_check.py <stage_dir>

Expected layout:
  <stage_dir>/fragment.json   list of {slug, upstream_repo, commit, license,
                                     src_path, category, name_zh, description_zh, boundary}
  <stage_dir>/REPORT.md
  <stage_dir>/<slug>/SKILL.md (+ SOURCE.md)
"""
import json
import os
import re
import sys

CATEGORIES = {
    "engineering", "computing", "life-science", "chemistry-materials",
    "research", "security", "business", "docs", "platform",
}
REQUIRED = ("slug", "upstream_repo", "commit", "license", "src_path",
            "category", "name_zh", "description_zh")


def main():
    if len(sys.argv) != 2:
        print("usage: stage_check.py <stage_dir>", file=sys.stderr)
        return 2
    root = sys.argv[1]
    errors = []
    if not os.path.isdir(root):
        print(f"FAIL: {root} is not a directory", file=sys.stderr)
        return 1
    if not os.path.isfile(os.path.join(root, "REPORT.md")):
        errors.append("REPORT.md missing")
    frag_path = os.path.join(root, "fragment.json")
    if not os.path.isfile(frag_path):
        print("FAIL: fragment.json missing\n" + "\n".join(errors), file=sys.stderr)
        return 1
    try:
        frag = json.load(open(frag_path, encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"FAIL: fragment.json invalid: {error}", file=sys.stderr)
        return 1
    if not isinstance(frag, list) or not frag:
        print("FAIL: fragment.json must be a non-empty list", file=sys.stderr)
        return 1

    seen = set()
    for item in frag:
        for field in REQUIRED:
            if not str(item.get(field, "")).strip():
                errors.append(f"{item.get('slug', '<no-slug>')}: missing {field}")
        slug = item.get("slug", "")
        if slug in seen:
            errors.append(f"{slug}: duplicate entry")
        seen.add(slug)
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
            errors.append(f"{slug}: slug must be lowercase letters, digits, hyphens")
        if item.get("category") not in CATEGORIES:
            errors.append(f"{slug}: category {item.get('category')!r} not in whitelist")
        if not re.fullmatch(r"[0-9a-f]{7,40}", str(item.get("commit", ""))):
            errors.append(f"{slug}: commit must be a hex sha")
        skill = os.path.join(root, slug, "SKILL.md")
        if not os.path.isfile(skill):
            errors.append(f"{slug}: {slug}/SKILL.md missing")
            continue
        text = open(skill, encoding="utf-8", errors="replace").read(4000)
        found = re.search(r"^name:\s*(.+)$", text, re.M)
        if not found:
            errors.append(f"{slug}: frontmatter has no name")
        elif found.group(1).strip() != slug:
            errors.append(f"{slug}: frontmatter name is {found.group(1).strip()!r}")
        if not os.path.isfile(os.path.join(root, slug, "SOURCE.md")):
            errors.append(f"{slug}: SOURCE.md missing next to SKILL.md")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    cats = {}
    for item in frag:
        cats[item["category"]] = cats.get(item["category"], 0) + 1
    summary = ", ".join(f"{k}={cats[k]}" for k in sorted(cats))
    print(f"PASS: {len(frag)} staged skills ({summary})")
    return 0


def self_test():
    """Fabricate a minimal valid stage dir and check the validator accepts it.

    Dispatched flows call this script by path, so if the file disappears the call fails
    at the worst moment. The self-test keeps the canonical copy honest.
    """
    import json as _json
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        skill = os.path.join(tmp, "demo-skill")
        os.makedirs(skill)
        with open(os.path.join(skill, "SKILL.md"), "w", encoding="utf-8") as fh:
            fh.write("---\nname: demo-skill\ndescription: demo\n---\n# demo\n")
        with open(os.path.join(skill, "SOURCE.md"), "w", encoding="utf-8") as fh:
            fh.write("source\n")
        with open(os.path.join(tmp, "REPORT.md"), "w", encoding="utf-8") as fh:
            fh.write("report\n")
        with open(os.path.join(tmp, "fragment.json"), "w", encoding="utf-8") as fh:
            _json.dump([{
                "slug": "demo-skill", "upstream_repo": "https://example.invalid/r",
                "commit": "abc1234", "license": "MIT", "src_path": "skills/demo-skill",
                "category": "engineering", "name_zh": "演示", "description_zh": "演示",
            }], fh)
        sys.argv = [sys.argv[0], tmp]
        rc = main()
    print("self-test:", "ok" if rc == 0 else "FAILED")
    return rc


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        sys.exit(self_test())
    sys.exit(main())
