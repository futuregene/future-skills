"""Offline guardrails for the loop CLI instructions (no model/tool execution)."""
from pathlib import Path
import re
import unittest

SKILL = Path(__file__).resolve().parents[1] / "builtin" / "future-loop" / "SKILL.md"


class LoopContractTests(unittest.TestCase):
    def test_documented_id_pattern_matches_added_not_created(self):
        text = SKILL.read_text(encoding="utf-8")
        pattern = re.search(r"`(todo\\s[^`\n]+)`", text).group(1)
        self.assertEqual(
            re.findall(pattern, "todo todo_012abc added to goal_123 ✔\n"),
            ["todo_012abc"],
        )
        for output in ["todo todo_012abc created", "todo garbage added", "Error: failed"]:
            self.assertEqual(re.findall(pattern, output), [])
        # Multiple matches are deliberately not collapsed to a guessed ID.
        self.assertEqual(len(re.findall(pattern,
            "todo todo_abc added to g ✔\ntodo todo_def added to g ✔")), 2)
        self.assertIn("Require exactly one match", text)

    def test_scope_fallback_and_repair_boundaries_are_explicit(self):
        text = SKILL.read_text(encoding="utf-8")
        for fragment in [
            "relative to the goal's recorded cwd",
            "Task scopes override",
            "Older binaries only record",
            'todo update --goal G --todo-id T --blocks A,B',
            '--blocks ""',
            "not a filesystem sandbox",
            "not your rationale",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
