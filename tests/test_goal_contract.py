"""Offline guardrails for the goal CLI instructions (no model/tool execution)."""
from pathlib import Path
import re
import unittest

SKILL = Path(__file__).resolve().parents[1] / "builtin" / "future-goal" / "SKILL.md"


class GoalContractTests(unittest.TestCase):
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


    def test_worker_model_and_thinking_defaults_are_not_inherited(self):
        # The CLI inherits nothing from the launching session; the skill must say
        # so, or a supervisor silently runs workers on the registry default and
        # "medium". Guard the claim (and its verifiable pointers) against edits.
        text = re.sub(r"\s+", " ", SKILL.read_text(encoding="utf-8"))
        for fragment in [
            "inherits NOTHING",
            "not inherited from the active session",
            'DEFAULT_THINKING_LEVEL = "medium"',
            "making a worker match this session REQUIRES both flags",
            "Omitting a flag is silent",
        ]:
            self.assertIn(fragment, text)

    def test_explicit_invocation_dispatches_instead_of_inlining(self):
        # Measured failure: a task ending in a bare `/future-goal` was answered in
        # the same session — no goal, no worker — while the verbatim sentence
        # "使用 /future-goal 技能启动多个 worker" reliably dispatched. The token alone
        # read as "load this file", and the old description plus "a one-shot
        # conversation needs no goal" licensed skipping the goal entirely. Guard
        # both halves: the token is enough, and inlining is not an option.
        raw = SKILL.read_text(encoding="utf-8")
        text = re.sub(r"\s+", " ", raw)
        for fragment in [
            "**Dispatch rule",
            "not a request to read this file and then answer inline",
            "a bare `/future-goal` appended to a task is a full invocation",
            "choose the smallest workflow that still puts the work in a worker session",
            "sets the minimum number of workers",
            "Do not claim an `advancement` todo and finish the work in this session",
            "Only two things justify doing the work inline",
            "still run one worker and say in one line why",
            "A goal with todos and no `future goal run` is a plan, not progress",
            "Light is one worker, not this session",
        ]:
            self.assertIn(fragment, text)
        # The escape hatch that contradicted dispatch must stay gone from the
        # model-facing description.
        self.assertNotIn("Not needed for a one-shot review", raw.split("---")[1])
        self.assertIn("dispatches that work to workers", raw.split("---")[1])

    def test_ensemble_workflow_is_recognizable_and_bounded(self):
        # A cross-model ensemble (one brief, different models, blind judge, merge)
        # is a supported goal shape. Losing the trigger turns it into a plain goal;
        # losing the guards turns it into N copies of one model or an unaudited
        # "best of" merge that never beats a single candidate.
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("ensemble", text.split("---")[1])
        for fragment in [
            "**Ensemble:**",
            "## 7. Ensemble across models",
            "Freeze the brief before dispatch",
            "Roster genuinely different models",
            "Judge blind, then synthesize",
            "Require the synthesis to beat the best candidate",
            "references/ensemble.md",
        ]:
            self.assertIn(fragment, text)
        self.assertTrue((SKILL.parent / "references" / "ensemble.md").is_file())


if __name__ == "__main__":
    unittest.main()
