#!/usr/bin/env python3
"""Every registry entry declares a scope, and cross-school entries are documented.

`general` and `hdu` form the default set this repository ships. Anything selected for a
different university carries `cross-school:<school>` and must appear in
docs/school-scope.md, so a reader never has to compute the boundary themselves.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"general", "hdu", "cross-school:multi", "cross-school:zjut", "cross-school:zstu"}
DOC = ROOT / "docs" / "school-scope.md"


def main():
    registry = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))
    errors = []
    for name, item in registry.items():
        scope = item.get("scope")
        if not scope:
            errors.append(f"{name}: missing scope")
        elif scope not in ALLOWED:
            errors.append(f"{name}: unknown scope {scope!r}")

    doc = DOC.read_text(encoding="utf-8") if DOC.is_file() else ""
    documented = set(re.findall(r"`([a-z0-9][a-z0-9-]*)`", doc))
    cross = {n: i.get("scope") for n, i in registry.items()
             if str(i.get("scope", "")).startswith("cross-school")}
    for name, scope in sorted(cross.items()):
        if name not in documented:
            errors.append(f"{name}: scope {scope} but not listed in docs/school-scope.md")
    if not DOC.is_file():
        errors.append("docs/school-scope.md is missing")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"FAIL: {len(errors)} scope problem(s)", file=sys.stderr)
        return 1
    counts = {}
    for item in registry.values():
        counts[item["scope"]] = counts.get(item["scope"], 0) + 1
    summary = ", ".join(f"{k}={counts[k]}" for k in sorted(counts))
    print(f"PASS: {len(registry)} entries scoped ({summary}); {len(cross)} cross-school documented")
    return 0


if __name__ == "__main__":
    sys.exit(main())
