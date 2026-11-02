#!/usr/bin/env python3
"""Reject control characters in the documents we author ourselves.

Upstream skill bodies are left alone - they occasionally carry a literal tab or other
whitespace from their own tooling. `SOURCE.md` and `docs/` are ours, and a control
character there means text was written through a shell that expanded an escape
(a PowerShell backtick, for example), which silently corrupts commit hashes and
file names.

Allowed: tab and newline. Rejected: BEL, BS, VT, FF, CR and any other C0 control.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"\t", "\n"}
TARGETS = [ROOT / "docs"] + [p for p in (ROOT / "third-party").iterdir() if p.is_dir()]


def documents():
    for target in TARGETS:
        if target.is_file() and target.suffix == ".md":
            yield target
            continue
        if not target.is_dir():
            continue
        if target.name == "docs":
            for path in target.rglob("*.md"):
                yield path
            continue
        source = target / "SOURCE.md"
        if source.is_file():
            yield source


def main():
    errors = []
    checked = 0
    for path in documents():
        checked += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            bad = [(i, ch) for i, ch in enumerate(line) if ord(ch) < 32 and ch not in ALLOWED]
            if bad:
                shown = ", ".join(f"U+{ord(ch):04X} at column {i + 1}" for i, ch in bad)
                errors.append(f"{path.relative_to(ROOT)}:{lineno}: control character {shown}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"FAIL: {len(errors)} line(s) with control characters over {checked} documents", file=sys.stderr)
        return 1
    print(f"PASS: {checked} authored documents are free of control characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
