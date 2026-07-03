#!/usr/bin/env python3
"""
Adapt generate_schematic_ai.py for FutureOS — replace the file with the
canonical FutureOS version that uses future CLI tools.

The canonical source is:
    builtin/future-scientific-writing/scripts/generate_schematic_ai.py

Usage:
    python adapt_schematic_ai.py /path/to/skill/scripts/generate_schematic_ai.py
    python adapt_schematic_ai.py /path/to/skill/scripts/generate_schematic_ai.py --canonical-source /custom/path
    python adapt_schematic_ai.py --dry-run /path/to/skill/scripts/generate_schematic_ai.py
"""

import argparse
import shutil
import sys
from pathlib import Path


CANONICAL_SOURCE = Path(__file__).resolve().parents[3] / "builtin" / "future-scientific-writing" / "scripts" / "generate_schematic_ai.py"


def main():
    parser = argparse.ArgumentParser(
        description="Adapt generate_schematic_ai.py for FutureOS by replacing with canonical version"
    )
    parser.add_argument("target", help="Path to the generate_schematic_ai.py file to adapt")
    parser.add_argument(
        "--canonical-source",
        default=str(CANONICAL_SOURCE),
        help="Path to canonical FutureOS generate_schematic_ai.py",
    )
    parser.add_argument("--dry-run", action="store_true", help="Check only, don't write")
    args = parser.parse_args()

    target = Path(args.target)
    source = Path(args.canonical_source)

    if not target.exists():
        print(f"Error: Target {target} not found")
        sys.exit(1)
    if not source.exists():
        print(f"Error: Canonical source {source} not found")
        sys.exit(1)

    # Quick check: does the target actually need adaptation?
    target_content = target.read_text()
    has_openrouter = "openrouter" in target_content.lower()

    if not has_openrouter:
        print("Target is already adapted (no OpenRouter references found).")
        return

    # Backup original
    backup_path = target.with_suffix(target.suffix + ".bak")
    if not args.dry_run:
        shutil.copy(target, backup_path)
        print(f"Backup saved to: {backup_path}")

    if args.dry_run:
        print(f"[Dry run] Would replace {target} with {source}")
        return

    # Replace with canonical version
    shutil.copy(source, target)
    print(f"✓ Replaced {target}")
    print(f"  Original backed up to: {backup_path}")


if __name__ == "__main__":
    main()
