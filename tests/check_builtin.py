#!/usr/bin/env python3
"""Offline frontmatter, registry and code-fence validation for every builtin.

Requires PyYAML. Does not call models or validate scientific execution quality.
"""
import json
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]


class UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        keys = [self.construct_object(key, deep=deep) for key, _ in node.value]
        if len(keys) != len(set(keys)):
            raise ValueError("Duplicate YAML mapping key")
        return super().construct_mapping(node, deep=deep)


def check_fences(text):
    opened = None
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if match:
            marker, suffix = match.groups()
            if opened is None:
                opened = (marker[0], len(marker), number)
            elif marker[0] == opened[0] and len(marker) >= opened[1] and not suffix.strip():
                opened = None
        elif re.search(r"\S[ \t]+`{3,}\s*$", line):
            raise ValueError(f"Closing fence must be on its own line ({number})")
    if opened is not None:
        raise ValueError(f"Unclosed code fence from line {opened[2]}")


def validate_entry(name, text):
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    if not match:
        raise ValueError("Missing frontmatter delimiters")
    header = yaml.load(match[1], Loader=UniqueKeyLoader)
    if not isinstance(header, dict):
        raise ValueError("Frontmatter must be a mapping")
    if header.get("name") != name or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name):
        raise ValueError("Skill name must match its slug directory")
    description = header.get("description")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("A nonempty description is required")
    version = header.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?", version):
        raise ValueError("A string semantic version is required")
    check_fences(text[match.end():])
    return header


def main():
    registry = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))
    paths = sorted((ROOT / "builtin").glob("*/SKILL.md"))
    expected = {name for name, item in registry.items() if item.get("builtin") is True}
    actual = {path.parent.name for path in paths}
    errors = []
    if expected != actual:
        errors.append(f"Registry/files mismatch: {expected ^ actual}")
    for path in paths:
        try:
            validate_entry(path.parent.name, path.read_text(encoding="utf-8"))
        except (ValueError, yaml.YAMLError) as error:
            errors.append(f"{path.relative_to(ROOT)}: {error}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"PASS: {len(paths)} builtin entries, standard YAML, identity/version, registry and fences")
    return 0


if __name__ == "__main__":
    sys.exit(main())
