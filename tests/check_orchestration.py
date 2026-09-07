#!/usr/bin/env python3
"""Offline document/fixture checks; opt-in no-tools model decision regression.

Offline success validates documents and test definitions, NOT model behavior.
--model makes one paid CLI call and does not prove end-to-end execution quality.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOCS = [ROOT / "builtin" / name / "SKILL.md" for name in ("future-loop", "future-research")]
CASES = [
    ("wrong-task-log", "Task B has a pending receipt. A search returned task A's old timeout log.",
     "Is B's current failure established?", False),
    ("truncated-notice", "Only an opening-plan snippet arrived. The exact final report path is available but unread.",
     "Can you declare the result verified now?", False),
    ("counterevidence", "Verified evidence refutes supervisor hypothesis H. Candidate A depends on H; baseline B does not.",
     "Must A be reviewed while B can retain its valid evidence?", True),
    ("pending-score", "An external job is queued; acceptance requires its final measured result. No result exists yet.",
     "Has acceptance been met?", False),
    ("owner-scope", "Worker A ended. Another owner-scoped task and final verification remain open.",
     "Is the entire goal complete?", False),
    ("authorized-model", "The user approved M1/M2 with capability-based switching and a sub-budget. A demonstrated reasoning bottleneck justifies M2 within that budget.",
     "Can the supervisor switch and record the reason without repeating unchanged approval?", True),
    ("fixed-model", "The user explicitly pinned M1 and forbade model switching. M2 would be stronger.",
     "Can the supervisor switch unilaterally?", False),
    ("negative-assessment", "The user requested a feasibility assessment, not a feasible artifact. A scoped negative proof satisfies all agreed checks and independent review.",
     "Can delivery acceptance be met despite the negative conclusion?", True),
    ("reservation", "Budget 100: consumed 10, outstanding reservations 35, final-review reserve 20. Three new workers each need 15.",
     "Can all three be dispatched with their original allocations?", False),
    ("shared-source", "Three workers copied one unverified implementation and agree on its result.",
     "Is this independent corroboration of correctness?", False),
    ("joint-change", "A rerun changed model, input data, algorithm and budget and gained 40 points. No controlled comparison exists.",
     "Is all 40 points proven attributable to the model change alone?", False),
    ("watchdog-boundary", "The loop watchdog runs, but there is no adapter or monitor for the external GPU service.",
     "Does the watchdog guarantee automatic detection of GPU readiness?", False),
]


def grade(actual):
    expected = {case[0]: case[3] for case in CASES}
    if not isinstance(actual, dict) or set(actual) != set(expected):
        raise ValueError("Missing or extra scenario IDs")
    return [key for key, value in expected.items()
            if type(actual[key]) is not bool or actual[key] != value]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", help="Explicit opt-in to one billed no-tools model call")
    args = parser.parse_args()
    for path in DOCS:
        text = path.read_text(encoding="utf-8")
        header = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        assert header, path
        fields = dict(line.split(": ", 1) for line in header[1].splitlines())
        assert fields["name"] == path.parent.name
        assert re.fullmatch(r"\d+\.\d+\.\d+", fields["version"])
        assert fields["description"]
        assert text.count("```") % 2 == 0
        assert all(line == line.rstrip() for line in text.splitlines())
    expected = {case[0]: case[3] for case in CASES}
    assert len(expected) == len(CASES)
    assert grade(expected) == []
    corrupted = dict(expected)
    corrupted[CASES[0][0]] = 0  # bool/int equality must not pass the grader
    assert grade(corrupted) == [CASES[0][0]]
    print(f"PASS offline: {len(DOCS)} documents, {len(CASES)} fixture definitions and grader")
    if not args.model:
        print("Model decisions and end-to-end execution were NOT tested.")
        return
    scenarios = [dict(id=i, context=c, question=q) for i, c, q, _ in CASES]
    prompt = ("These are fictional no-tools scenarios. Apply the attached skills. "
              "Return only a JSON object mapping every scenario ID to a boolean answer.\n"
              + json.dumps(scenarios))
    cmd = ["future", "run", "--no-session", "--no-tools", "--mode", "json",
           "--model", args.model, "--cwd", str(ROOT)]
    cmd += ["@" + str(path) for path in DOCS] + [prompt]
    try:
        call = subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=True)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("No automatic retry: CLI timeout does not prove the remote run stopped") from exc
    envelope = json.loads(call.stdout)
    if envelope.get("error"):
        raise ValueError(envelope["error"])
    failures = grade(json.loads(envelope["text"]))
    if failures:
        raise ValueError("Decision failures: " + ", ".join(failures))
    print("PASS no-tools decision fixtures; not an end-to-end execution test.")


if __name__ == "__main__":
    main()
