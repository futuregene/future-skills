#!/usr/bin/env python3
"""Offline structural validation for a custom skill. Requires PyYAML."""
import argparse
from pathlib import Path
import re
import sys

import yaml


class UniqueLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        keys = [self.construct_object(key, deep=deep) for key, _ in node.value]
        if len(keys) != len(set(keys)):
            raise ValueError("Duplicate YAML key")
        return super().construct_mapping(node, deep=deep)


def validate(directory):
    text = (directory / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    if not match:
        raise ValueError("Missing frontmatter delimiters")
    data = yaml.load(match[1], Loader=UniqueLoader)
    if not isinstance(data, dict) or data.get("name") != directory.name:
        raise ValueError("Frontmatter name must match the skill directory")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", directory.name):
        raise ValueError("Name must use lowercase letters, digits and hyphens, under 64 characters")
    if not isinstance(data.get("description"), str) or not data["description"].strip():
        raise ValueError("Nonempty description required")
    if not isinstance(data.get("version"), str) or not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?", data["version"]):
        raise ValueError("A semantic version string is required")
    flags = [key for key in ("disable-model-invocation", "disable_model_invocation", "disableModelInvocation") if key in data]
    if len(flags) > 1 or any(type(data[key]) is not bool for key in flags):
        raise ValueError("Use one invocation-policy alias with a boolean value")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        validate(args.directory.resolve())
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: skill structure and frontmatter (workflow behavior not tested)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
