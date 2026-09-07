---
version: 3.0.0
name: future-research
description: Evidence-driven research, method comparison, optimization and feasibility assessment when the answer is not yet known. Use for scientific/engineering exploration or explicitly requested multi-worker reflection. Not for routine factual lookup, a code change with known implementation steps, or editing this skill itself.
allowed-tools: Bash(future:*)
category: tools
---

# Evidence-driven research

Choose a method from evidence, test it, reflect on the result, and verify the
final claim independently when risk warrants it. Do not confuse a completed
workflow, a written report, or exhausted attempts with achieving the objective.

## Scope and budget first

Clarify the objective, available material, deliverable format, acceptance
semantics, resource limits and irreversible actions. State assumptions and ask
only about unknowns that would materially change the work. Treat explicit user
constraints as authoritative.

Choose the smallest sufficient mode:

| Mode | Suitable work | Process |
|---|---|---|
| Light | Code mechanism review, bounded feasibility question, targeted comparison | Inspect primary evidence, compare plausible alternatives, run targeted checks; usually one agent |
| Standard | Uncertain implementation or consequential technical decision | Method map, exploratory iteration, separate verification/review |
| Heavy | Broad research frontier, expensive experiments, high-stakes scientific claim | Multiple genuinely different method families, independent synthesis, strict reproducibility audit |

Do not require a fixed paper count, arbitrary academic percentage, or a multi-worker
loop for every task. Repository source, specs and measurements are often the
primary evidence for software questions. For literature-dependent work use
future-paper/future-web/future-deep-research at a depth justified by the question;
verify key citations rather than optimizing citation count. When external research
is unavailable, identify the limitation instead of fabricating references.

Before paid worker dispatch, confirm model/thinking settings unless the user
already specified them. Default to the current session model, not a hard-coded
model roster. User-pinned configuration cannot be silently changed. Agree on time,
cost/attempt budget and review checkpoints; no universal high-thinking mandate.

## Method map and anchor

1. Inspect the task contract and existing evidence before selecting an approach.
2. List meaningfully different candidate methods, their assumptions, expected
   upside, implementation cost and falsification tests. Use fewer than three
   when fewer are genuinely plausible; never invent alternatives for a quota.
3. Define success in observable terms. Quantitative tasks need a baseline and
   justified target/bound; qualitative tasks need an explicit decision rubric.
   Label estimates as estimates. Revise an anchor only with documented evidence,
   not because the current method misses it.
4. Build only the necessary harness. Distinguish input/submitted/runtime files,
   reset/isolation semantics and permissions. Mark each critical assumption as
   specified, observed or unknown. For unknown semantics, test conservative
   scenarios and report conditional conclusions; do not silently assume favorable
   freedoms or present hypothetical restrictions as known facts.

No worker may weaken the acceptance contract or inspect a prohibited reference
solution to manufacture a passing result.

## Explore and reflect

For light work, perform the bounded investigation directly; no goal or workspace
files are mandatory. For durable or multi-worker work, load future-loop, inspect
existing goals, and keep artifacts in a task-specific directory. Use owner-scoped
todos and dependency edges, and name artifact paths in downstream task text.

Parallel workers should differ by method or hypothesis, not just arbitrary
parameters. The supervisor may reason about tradeoffs and audit evidence; it
must not substitute its intuition for missing experiments or certify its own
unsupported claims. Use independent verification for consequential claims.

Each iteration records:

- New evidence relative to the previous iteration (including negative results).
- Reproduction commands, inputs/seeds/versions, outputs and measured metrics.
- Assumptions tested or invalidated, failed approaches and counterexamples.
- Remaining gap, uncertainty, next experiment and expected resource cost.

At each checkpoint, answer:

1. Did we learn something relevant, or only generate activity?
2. Does the evidence support the method and target, or should we revisit them?
3. What observation would falsify the current explanation/strategy?
4. Is another iteration worth its expected cost, and is it authorized?

Return to breadth when a method is falsified or its ceiling is below the target;
not on an arbitrary schedule. Use a fresh reviewer when correlated assumptions
would undermine confidence. File existence is an artifact check, not scientific
validation. Avoid frequent supervisor polling and gratuitous mid-turn interrupts.

## Stop states and final verification

Stop deliberately at one of these states:

- **Achieved:** acceptance met with reproducible evidence and appropriate review.
- **Bounded infeasibility:** a justified result for a stated domain/method family;
  do not generalize it to all possible methods.
- **Budget-limited / low expected return:** target not reached; preserve the best
  result and ask before extending authorized resources.
- **Blocked / conditional:** required data, authorization or runtime semantics
  are missing; specify what would unblock the conclusion.

A proof that every conceivable method fails is NOT required to stop. None of the
last three states may be reported as successful completion. Stop/release workers
and preserve artifacts; keep acceptance gaps visible in the loop ledger. Mark a
goal cancelled only when abandonment is authorized, not to make the dashboard green.

For standard/heavy work, independently rerun the decisive checks. Reimplementation,
adversarial cases or large randomized comparisons are selected by risk, not a
universal million-case requirement. Audit both the harness and the interpretation
of its outputs. Report achieved value, target/gap, uncertainty, limitations and
reproduction steps; explain suspiciously large gains as carefully as failures.

## Integrity

Never fabricate experiments, sources, elapsed work, or worker independence. Never
claim a test was run when it was only proposed. Do not count rewriting progress
files as progress, repeated notifications as new evidence, or a passed shell exit
code as proof of an exploratory claim. Honor prohibited-source and confidentiality
constraints throughout exploration and review.
