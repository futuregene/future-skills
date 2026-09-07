#!/usr/bin/env python3
"""One portable entry point for builtin structure and deterministic regressions.

No model calls, account access, browser sessions or external retrievals are made.
Install dependencies with: python -m pip install -r tests/requirements.txt
"""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    ["tests/check_builtin.py"],
    ["-m", "unittest", "discover", "-s", "tests", "-v"],
    ["-m", "unittest", "discover", "-s", "builtin/future-experimental-design/tests", "-v"],
    ["-m", "unittest", "discover", "-s", "builtin/future-slides/tests", "-v"],
    ["tests/check_orchestration.py"],
    ["builtin/future-deep-research/tests/check_skill.py"],
]


def main():
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1"}
    for command in COMMANDS:
        print("CHECK:", " ".join(command), flush=True)
        result = subprocess.run([sys.executable, *command], cwd=ROOT, env=environment,
                                timeout=120, check=False)
        if result.returncode:
            return result.returncode
    print("PASS offline builtin checks; paid/live model behavior was not tested.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
