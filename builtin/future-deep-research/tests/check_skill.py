#!/usr/bin/env python3
"""Offline checks plus opt-in, bounded retrieval and no-tools model decision tests.

No files are written. --model sends only skill documents and scenario inputs, never
expected answers. --parent-skill adds the real caller instructions without copying
private material into this repository. --live-source retrieves one public IANA page.
These are component/decision checks, not a full research or billing-enforcement test.
"""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://www.iana.org/help/example-domains"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def same_answer(actual, expected):
    if isinstance(expected, bool):
        return isinstance(actual, bool) and actual == expected
    if isinstance(expected, int):
        return type(actual) in (int, float) and actual == expected
    if isinstance(expected, list):
        return isinstance(actual, list) and all(isinstance(x, str) for x in actual) and sorted(actual) == sorted(expected)
    return type(actual) is type(expected) and actual == expected


def offline_checks():
    docs = [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]
    main = docs[0].read_text(encoding="utf-8")
    require(re.match(r"---\nname: future-deep-research\nversion: \d+\.\d+\.\d+\n", main), "Invalid identity/version header")
    require(len(main.splitlines()) < 180, "Entry file no longer concise")
    resources = main.split("## Resources", 1)[1].split("## Validation", 1)[0]
    links = set(re.findall(r"`(references/[^`]+\.md)`", resources))
    require(links == {p.relative_to(ROOT).as_posix() for p in docs[1:]}, "Missing/stale resource links")
    for path in docs:
        text = path.read_text(encoding="utf-8")
        require(text.count("```") % 2 == 0, f"Unbalanced code fences: {path.name}")
        require(not re.search(r"\b(?:TODO|FIXME)\b", text), f"Unfilled TODO: {path.name}")
        require(not any(line.rstrip() != line for line in text.splitlines()), f"Trailing whitespace: {path.name}")
    reporting = (ROOT / "references/reporting.md").read_text(encoding="utf-8")
    require(all(s in reporting for s in ("5–15", "20–40", "60–120", "at least 40%", "at least 60%")), "Full-report requirements lost")
    retrieval = (ROOT / "references/retrieval.md").read_text(encoding="utf-8")
    require("three rounds per" in retrieval and "do not reset totals" in retrieval, "Cumulative limit missing")
    require('--command "open"' in retrieval, "Explicit browser navigation missing")
    require("0.75 as a pass threshold" in main, "Self-score prohibition missing")
    cases = json.loads((ROOT / "tests/scenarios.json").read_text(encoding="utf-8"))
    require(len(cases) >= 10, "Insufficient regression coverage")
    require(len({c["id"] for c in cases}) == len(cases), "Duplicate case IDs")
    for case in cases:
        require(set(case["questions"]) == set(case["expected"]), f"Incomplete oracle: {case['id']}")
    require(same_answer([], []) and same_answer(["a", "b"], ["b", "a"]), "List comparator failed")
    require(not same_answer(1, True) and not same_answer(None, False), "Comparator accepts invalid booleans")
    print(f"PASS offline: {len(docs)} runtime documents, {len(cases)} scenarios, references and contracts")
    return docs, cases


def cli_json(command, timeout):
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("CLI wait expired; no automatic retry. This does not prove a remote/agent run stopped; inspect it before further calls.") from exc
    require(result.returncode == 0, "CLI failed: " + result.stderr[-1200:])
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("Expected structured CLI output; check --raw for tools or --mode json for runs") from exc
    require(not (isinstance(payload, dict) and payload.get("error")), "CLI returned an error")
    return payload


def live_source_case(timeout):
    payload = cli_json(["future", "tools", "call", "fetch_url", "--url", SOURCE_URL, "--timeout", "45", "--raw"], timeout)
    require(isinstance(payload, dict), "Expected a structured fetch result")
    actual_url = urlparse(payload.get("url", ""))
    require(actual_url.hostname == "www.iana.org" and actual_url.path.rstrip("/") == "/help/example-domains", "Unexpected fetched source identity")
    text = payload.get("content")
    require(isinstance(text, str) and text.strip(), "Source body unavailable")
    normalized = " ".join(text.lower().split())
    require("example.com" in normalized, "Target source content not exposed")
    phrase = "not available for registration or transfer"
    require(phrase in normalized, "IANA passage unavailable; retrieval check failed, do not fabricate a pass")
    start = normalized.index(phrase)
    excerpt = normalized[max(0, start - 220):start + len(phrase) + 120]
    print(json.dumps({"retrieval": "pass", "url": SOURCE_URL, "inspected_excerpt": excerpt}))
    return {
        "id": "live-iana-claim",
        "context": "Selected original passage returned by fetch_url for " + SOURCE_URL + ":\n" + excerpt,
        "questions": {"claim_supported": "Does the supplied original passage support the claim that IANA's example domains are available for registration or transfer? Boolean."},
        "expected": {"claim_supported": False},
    }


def model_checks(model, timeout, docs, cases):
    inputs = [{k: case[k] for k in ("id", "context", "questions")} for case in cases]
    prompt = (
        "Act as the researcher following the attached skills for these test situations. "
        "Do not execute research, call tools, or modify files. Treat each context as the given facts; "
        "do not invent authorization or evidence. Return only a JSON array of objects: "
        "{\"id\":case ID,\"answers\":{question key:answer},\"reason\":one short sentence}. "
        "Follow the question's requested answer types. Cases:\n" + json.dumps(inputs)
    )
    command = ["future", "run", "--no-session", "--no-tools", "--mode", "json", "--model", model,
               "--cwd", str(ROOT), "--system-prompt", "This is a no-tools decision test. Apply the supplied skill instructions and return the requested JSON."]
    command.extend("@" + str(p) for p in docs)
    command.append(prompt)
    payload = cli_json(command, timeout)
    text = payload["text"].strip()
    if text.startswith("```json\n") and text.endswith("```"):
        text = text[8:-3].strip()
    try:
        replies = json.loads(text)
    except json.JSONDecodeError as exc:
        terminal = [event for event in payload.get("messages", [])
                    if isinstance(event, dict) and any(word in str(event.get("type", ""))
                                                      for word in ("end", "error", "incomplete", "complete"))]
        raise ValueError("Model returned no parseable decision JSON; text prefix=" + repr(text[:200])
                         + "; terminal events=" + json.dumps(terminal, ensure_ascii=False)[-2000:]) from exc
    require(isinstance(replies, list), "Model did not return an array")
    require(all(isinstance(r, dict) and isinstance(r.get("id"), str) for r in replies), "Invalid response records")
    by_id = {r["id"]: r for r in replies}
    require(len(by_id) == len(replies) and set(by_id) == {c["id"] for c in cases}, "Response ID mismatch")
    failures = []
    print("Model reported by CLI:", payload.get("model", "unknown"))
    for case in cases:
        response = by_id[case["id"]]
        answers = response.get("answers", {})
        require(isinstance(answers, dict), "Invalid answer mapping")
        bad = {key: {"expected": expected, "actual": answers.get(key)} for key, expected in case["expected"].items()
               if key not in answers or not same_answer(answers[key], expected)}
        print(json.dumps({"id": case["id"], "pass": not bad, "answers": answers, "reason": response.get("reason")}, ensure_ascii=False))
        if bad:
            failures.append({"id": case["id"], "mismatches": bad})
    require(not failures, "Decision failures: " + json.dumps(failures))
    print(f"PASS decisions: {len(cases)}/{len(cases)}. Not end-to-end research validation.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", help="Opt into one billed, ephemeral no-tools model call")
    parser.add_argument("--parent-skill", type=Path, help="Optional real caller skill directory for composition testing")
    parser.add_argument("--live-source", action="store_true", help="Opt into one public-source fetch; may incur tool cost")
    parser.add_argument("--timeout", type=int, default=180, help="CLI wait limit, not a remote spending guarantee")
    args = parser.parse_args()
    require(args.timeout > 0, "Timeout must be positive")
    docs, cases = offline_checks()
    if args.parent_skill:
        require(bool(args.model), "--parent-skill needs --model to test composition")
        parent = args.parent_skill.resolve()
        require((parent / "SKILL.md").is_file(), "Parent skill entry missing")
        docs = [parent / "SKILL.md", *sorted((parent / "references").glob("*.md")), *sorted((parent / "assets").glob("*.md")), *docs]
        print("Composition mode: real parent skill documents included; expectations withheld")
    if args.live_source:
        cases.append(live_source_case(min(args.timeout, 60)))
    if args.model:
        model_checks(args.model, args.timeout, docs, cases)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, IndexError, OSError, RuntimeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
