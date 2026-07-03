#!/usr/bin/env python3
"""
Adapt SKILL.md frontmatter — remove OPENROUTER_API_KEY references.

Usage:
    python adapt_skill_md.py /path/to/skill/SKILL.md
    python adapt_skill_md.py --dry-run /path/to/skill/SKILL.md
"""

import argparse
import re
import sys
from pathlib import Path


def adapt_skill_md(content: str) -> tuple[str, list[str]]:
    """Adapt SKILL.md content, returning (new_content, changes)."""
    changes = []

    # 1. Remove required_environment_variables line entirely
    if re.search(r'required_environment_variables:', content):
        content = re.sub(
            r'required_environment_variables:\s*\[.*?\]\s*\n',
            'required_environment_variables: []\n',
            content,
            flags=re.DOTALL,
        )
        changes.append("Replaced required_environment_variables with empty list")

    # 2. Remove OPENROUTER_API_KEY from metadata.operclaw.envVars
    content = re.sub(
        r'"openclaw":\s*\{[^}]*"primaryEnv":\s*"OPENROUTER_API_KEY"[^}]*\},?\s*',
        '',
        content,
        flags=re.DOTALL,
    )
    # Clean up trailing comma in metadata if openclaw was removed
    content = re.sub(r',\s*\}', '\n}', content)

    # 3. Replace OPENROUTER_API_KEY setup block
    if re.search(r'OPENROUTER_API_KEY', content):
        setup_pattern = r'export OPENROUTER_API_KEY=.*?(?:Get (?:a key|one) at: https?://openrouter\.ai/keys.*?)?(?:\n\n|\n```)'
        replacement = (
            "Authentication is automatic via `~/.future/agent/auth.json`.\n"
            "Run `future auth login` to authenticate. No API key needed.\n\n"
        )

        # Try to replace the export + get key block
        new_content, count = re.subn(
            r'export OPENROUTER_API_KEY=.*?\n(?:.*?openrouter\.ai/keys.*?\n)?',
            '',
            content,
            flags=re.DOTALL,
        )
        if count > 0:
            content = new_content
            changes.append(f"Removed {count} OPENROUTER_API_KEY setup block(s)")

        # Also remove standalone "Get a key at openrouter.ai/keys" lines
        new_content, count = re.subn(
            r'.*?openrouter\.ai/keys.*?\n',
            '',
            content,
        )
        if count > 0:
            content = new_content
            changes.append(f"Removed {count} OpenRouter URL reference(s)")

    changes.append("Done")
    return content, changes


def main():
    parser = argparse.ArgumentParser(description="Adapt SKILL.md for FutureOS")
    parser.add_argument("path", help="Path to SKILL.md")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes only")
    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"Error: {target} not found")
        sys.exit(1)

    original = target.read_text()
    adapted, changes = adapt_skill_md(original)

    print("Changes:")
    for c in changes:
        print(f"  - {c}")

    if original == adapted:
        print("\nNo changes needed — file is already adapted.")
        return

    if args.dry_run:
        print("\n[Dry run] Would write adapted content.")
        return

    target.write_text(adapted)
    print(f"\n✓ Adapted {target}")


if __name__ == "__main__":
    main()
