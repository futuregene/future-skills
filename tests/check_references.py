#!/usr/bin/env python3
"""Reference integrity: relative links and skill-path mentions must resolve in-repo.

Offline; no model calls, credentials or network access.

Rules:
  * a relative markdown link must exist on disk (fragment ignored);
  * `third-party/<name>/` and `builtin/<name>/` must name a real skill directory;
  * bare `skills/<name>/` is checked only in our own documents (builtin/, docs/),
    because third-party SKILL.md text often quotes its upstream repository layout,
    where `skills/` means something else entirely;
  * fenced code blocks and inline code spans are skipped, so examples are not policed.
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOTS = [ROOT / "builtin", ROOT / "third-party"]
LINK = re.compile(r"\]\(([^)\s]+)")
PATH_REF = re.compile(r"(?<![\w/-])(third-party|builtin)/([a-z0-9][a-z0-9-]*)/")
BARE_REF = re.compile(r"(?<![\w/])skills/([a-z0-9][a-z0-9-]*)/")
INLINE_CODE = re.compile(r"`[^`]*`")


def strip_fences(lines):
    inside = False
    for line in lines:
        if line.lstrip().startswith("```"):
            inside = not inside
            continue
        if not inside:
            yield INLINE_CODE.sub("", line)


def iter_markdown(skill_dir):
    for base, dirs, files in os.walk(skill_dir):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git"}]
        for name in files:
            if name.endswith(".md"):
                yield Path(base) / name


def skill_names(root):
    if not root.is_dir():
        return set()
    return {p.parent.name for p in root.glob("*/SKILL.md")}


def main():
    known = set()
    for root in SKILL_ROOTS:
        known |= skill_names(root)
    errors = []
    checked = 0

    for root in SKILL_ROOTS:
        if not root.is_dir():
            continue
        for skill in sorted(skill_names(root)):
            for path in iter_markdown(root / skill):
                rel_file = path.relative_to(ROOT)
                text = path.read_text(encoding="utf-8", errors="replace")
                ours = root.name == "builtin"
                for line in strip_fences(text.splitlines()):
                    for target in LINK.findall(line):
                        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                            continue
                        checked += 1
                        clean = target.split("#", 1)[0]
                        if not clean:
                            continue
                        resolved = (path.parent / clean).resolve()
                        try:
                            resolved.relative_to(ROOT)
                        except ValueError:
                            errors.append(f"{rel_file}: escapes the repository: {target}")
                            continue
                        if not resolved.exists():
                            errors.append(f"{rel_file}: dangling link: {target}")
                    for _, name in PATH_REF.findall(line):
                        checked += 1
                        if name not in known:
                            errors.append(f"{rel_file}: names {name}/ which does not exist")
                    if ours:
                        for name in BARE_REF.findall(line):
                            checked += 1
                            if name not in known:
                                errors.append(f"{rel_file}: mentions skills/{name}/ which does not exist")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"FAIL: {len(errors)} reference problem(s) over {checked} checked", file=sys.stderr)
        return 1
    print(f"PASS: {checked} references resolve across {len(known)} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
