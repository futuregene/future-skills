---
version: 0.2.1
name: future-code
description: >
  Develop, debug, refactor, review, or maintain software in a local Git repository.
  Prefer this skill when the current working directory is inside a Git repository and
  the user's task concerns source code, tests, builds, configuration, or code review.
  For non-code work in a repository, invoke it only when this workflow materially helps.
category: tools
---

# Lightweight Code Development

Help users complete software work without assuming they are developers. Translate the
requested outcome into repository changes, explain decisions in plain language, and keep
the process proportional to the task.

## 1. Establish scope and repository context

1. Determine whether the current directory belongs to a Git repository. Treat that as a
   strong selection signal when the request involves code, tests, builds, configuration,
   debugging, refactoring, or review. A repository alone does not make an unrelated task
   a code-development task. When Git is available, locate the root and capture the initial
   state with `git rev-parse --show-toplevel` and `git status --short --branch`.
2. Read applicable instructions before deciding how to work. Check `AGENTS.md`, `CLAUDE.md`,
   README and contribution guides at the repository root and in relevant parent or child
   directories. More specific repository instructions override this general workflow.
3. Identify whether the user wants an explanation, investigation, implementation, or
   review. Preserve explicit boundaries: a diagnosis does not authorize a fix, and a
   review does not authorize editing unless the user also requests changes.

## 2. Understand before changing

Before editing, build a sufficient working understanding of:

- where the behavior is owned;
- how it is reached and consumed;
- what tests, configuration, documentation or external contracts define the expected behavior;
- whether the relevant files contain existing user changes.

Scale the depth of investigation to the risk and size of the task, but do not edit from an
isolated search result or an assumed convention. Search is a way to build understanding, not
a substitute for reading the relevant code in context.

Explore locally in stages instead of reading the repository broadly:

1. List candidate files with `rg --files`; use `-g` patterns or directory arguments to
   narrow the scope. Search text and symbols with `rg -n`, adding `-C` only when surrounding
   lines help. Ripgrep works on Windows, macOS and Linux.
2. If `rg` is unavailable, use `git grep -n` for tracked content, then an available native
   tool such as PowerShell `Get-ChildItem` or `Select-String`. Do not install a search tool
   solely for a small task when a suitable fallback exists.
3. Respect ignore rules by default. Expand into ignored or generated paths only when the
   task requires them; avoid broad `rg -uu` searches that sweep dependencies and build output.
4. Treat ripgrep exit code 1 as “no matches,” not a tool failure. Check the command and scope
   before concluding that a symbol or file does not exist.
5. Move from filenames and symbols to the owning implementation, call sites, tests and
   configuration. Read enough local context—imports, types and neighboring logic—to avoid
   edits based on isolated lines.

Run independent searches and reads concurrently when the available tools support it; keep
dependent steps sequential. Follow the existing architecture, naming, types, dependencies,
and generated-file boundaries. Distinguish confirmed facts from hypotheses when the cause is
uncertain, and ask only for choices that materially change the result.

When current code does not explain a design decision, inspect history selectively:

```text
git log -- path/to/file
git log -S 'literal or symbol'
git log -G 'pattern'
git blame -L START,END path/to/file
```

Use history to answer a concrete question, not as a mandatory scan for every change.

## 3. Make a focused change

- Implement the smallest coherent change that fulfills the request. Avoid unrelated
  cleanup, speculative abstractions, dependency additions, and broad rewrites.
- Preserve existing user work. Inspect overlapping modifications carefully, do not revert
  unrelated changes, and stop if safe integration is unclear.
- Use precise edits for focused changes and an appropriate batch operation for genuinely
  mechanical changes. Inspect the resulting diff either way.
- Prefer existing project mechanisms and edit source-of-truth files. Do not hand-edit
  generated output when the repository provides a generator; run the documented command.
- Add or update tests when behavior, regressions, or risky logic need durable coverage.
  Do not add tests that only restate static values or mirror the implementation.

## 4. Verify proportionally

Discover validation commands from repository instructions, manifests, scripts and CI; do
not assume one package manager or build system. Account for the current shell and platform,
including project-provided `.sh`, `.ps1` and `.cmd` entry points. Start with checks closest
to the changed area, then broaden only when the change or repository policy warrants it.
Relevant checks may include tests, builds, type checks, lint, formatting and snapshots.

Never claim a check passed unless it ran successfully. Report skipped or blocked checks and
their practical impact. When behavior cannot be exercised with the available tools, use other
relevant evidence where possible and give the user one short, specific manual check. Do not
present indirect evidence as runtime validation. Keep distinct validations attributable:
do not let a later search with no matches or a suppressed exit status obscure an earlier
formatter, build or test result. Preserve real failures and determine whether they come from
the change, the environment, missing dependencies or permissions before retrying.

## 5. Keep Git work visible and recoverable

- Work in the current checkout by default. If the user, repository instructions, or delivery
  workflow requires a branch or separate checkout, state its location and resulting Git state
  clearly.
- Before handoff, use `git diff --stat` to review scope, `git diff` to review content, and
  `git diff --check` to catch whitespace errors. Check `git status --short --branch` as well,
  because ordinary diffs do not show the contents of untracked files. Look for accidental
  files, generated noise, secrets, and unrelated edits.
- Commit, push, open a pull request, merge, or publish only when the request or established
  workflow authorizes that action. Report the actual outcome rather than the intended one.

## 6. Escalate long work deliberately

Use `future-loop` for work that must continue across sessions, run for a long time, maintain
durable todos, or satisfy an explicit "keep working" request. Check for a matching existing
goal before creating one, define concrete completion evidence, and keep ordinary one-shot
edits in the current session.

## 7. Respect tool boundaries and hand off clearly

Use the tools actually available in the current session. Quote paths safely, especially when
they contain spaces, and use syntax appropriate to the active shell rather than guessing from
the operating-system name. If delegation is available and appropriate, give agents bounded
code or evidence tasks; the supervising agent remains responsible for integration and
independent verification of their results.

Finish with the outcome, the important files or behavior changed, validation performed,
and any remaining limitation or manual check. Keep the explanation short for simple tasks
and detailed enough for the user to judge risk on larger changes.
