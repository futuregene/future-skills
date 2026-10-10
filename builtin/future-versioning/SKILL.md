---
version: 0.4.0
name: future-versioning
description: >
  Do versioned work in a local Git repository: code, documents, data, analyses or other
  artifacts whose history matters. Prefer this skill when the deliverable belongs in a
  repository and the task involves writing, modifying, building, testing, reviewing or
  maintaining tracked files, and when a project with no repository would benefit from one.
  For work that produces no tracked artifact, invoke it only when this workflow materially helps.
category: tools
---

# Lightweight Versioned Development

Help users complete work that should be tracked in Git without assuming they are developers.
The deliverable may be code, a document, a dataset, an analysis or a configuration: what
makes it this skill's work is that the result belongs in a repository and its history matters.
Translate the requested outcome into repository changes, explain decisions in plain language,
and keep the process proportional to the task.

## 1. Establish scope and repository context

1. Determine whether the current directory belongs to a Git repository. Treat that as a
   strong selection signal when the request produces files worth tracking — source code,
   tests, builds, configuration, prose documents, data, figures, analyses — or involves
   debugging, refactoring, reviewing or otherwise revising them. A repository alone does not
   make an unrelated task part of this workflow: a one-off question, search or retrieval that
   produces no tracked artifact is not. When Git is available, locate the root and capture
   the initial state with `git rev-parse --show-toplevel` and `git status --short --branch`.
2. When the work will produce artifacts worth tracking but no repository exists yet,
   recommend creating one and say why: version history, reviewable diffs, and the ability to
   reproduce or revert a later state. Offer a plain `git init` (plus a `.gitignore` for
   generated and large files); if the user has another tool or repository in mind, follow
   their choice. Initialize only with the user's agreement — never turn an untracked folder
   into a repository unasked.
3. Read applicable instructions before deciding how to work. Check `AGENTS.md`, `CLAUDE.md`,
   README and contribution guides at the repository root and in relevant parent or child
   directories. More specific repository instructions override this general workflow.
4. Identify whether the user wants an explanation, investigation, implementation, or
   review. Preserve explicit boundaries: a diagnosis does not authorize a fix, and a
   review does not authorize editing unless the user also requests changes.
5. Record the work in Git as it happens. Whenever the requested work changes tracked files,
   commit it: prefer several small, coherent commits over one dump at the end, keep each
   commit to a single intent, and write the message so a later reader knows why the change
   exists, not only what it touched. Leave unrelated in-progress edits alone. Committing is
   what makes the result traceable and reproducible, so treat a finished change left
   uncommitted as unfinished — unless the user is keeping their own history and asks
   otherwise.

## 2. Understand before changing

Before editing, build a sufficient working understanding of:

- where the affected behaviour, text or data is owned;
- how it is reached and consumed, or which other files and documents depend on it;
- what tests, configuration, documentation or external contracts define the expected result;
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
- Add or update tests when behaviour, regressions, or risky logic need durable coverage.
  Do not add tests that only restate static values or mirror the implementation. When the
  deliverable is not code, give it the equivalent guard — a check, a script or a documented
  manual verification — and record it with the artifact.

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

These rules apply to any tracked artifact — code, prose, data or configuration — because the
repository is the record of the work.

### Worktree-first change workflow

For work beyond a trivial edit, isolate changes in a worktree under the repository's
`.worktrees/` directory, on a branch of its own. Parallel sessions can then work in the same
repository at once without fighting over one checkout, and only the base branch is shared.
Follow this default in repositories that use it; a repository whose instructions say
differently, and a read-only investigation, stay in the current checkout.

1. Branch from the current remote tip, not from a local base branch that may lag behind:
   `git fetch origin`, then
   `git worktree add --no-track .worktrees/<name> -b <type>/<name> origin/<base>`. `--no-track`
   matters: without it a plain `git push` would target the base branch. Pick the branch type
   that matches the change (`feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `ci`, `chore`).
2. Keep `.worktrees/` untracked (add it to `.gitignore` when it is absent). It holds whole
   working copies, not source.
3. Create, edit, verify and commit inside the worktree. Do not commit to the base branch, and
   do not merge a worktree branch into the local base branch. A squash-merged pull request
   gives the same content a different commit id, so a local fast-forward creates a divergence
   that afterwards blocks every update of the base branch.
4. Re-synchronize before pushing, not only when starting: fetch again, merge the base branch
   into the worktree branch, re-run the checks that merge affects, then push. A branch that is
   behind bounces between "update branch" requests and re-queued checks.
5. Once the change lands, clean up in the same session: `git worktree remove .worktrees/<name>`,
   delete the local and remote branch, `git worktree prune`, and fast-forward the local base
   branch from its remote (`git fetch origin && git merge --ff-only origin/<base>`). Leftovers
   hand the next session a stale worktree, a stale branch, or a stale base branch.
6. Stay out of other sessions' work: never remove, reset, or force-update a worktree or branch
   you did not create. If the local base branch carries commits you did not make, identify their
   branch and report them instead of cleaning them up.

### Recording the workflow

Repository instructions (`AGENTS.md`, `CLAUDE.md`, contribution guides) are what parallel
sessions actually share. When a repository that uses this skill has no recorded delivery
convention — no branch or worktree rule, no commit or review expectation — offer to write
this one into its `AGENTS.md` or `CLAUDE.md`. Add the parts that fit the repository's
practice; do it through the same worktree and review flow, and only with the user's agreement.

### Review before handoff

- Say where the change lives — the worktree path and branch — and what the base branch looks
  like afterwards, so the user can find it and test it.
- Before handoff, use `git diff --stat` to review scope, `git diff` to review content, and
  `git diff --check` to catch whitespace errors. Check `git status --short --branch` as well,
  because ordinary diffs do not show the contents of untracked files. Look for accidental
  files, generated noise, secrets, and unrelated edits, and confirm the intended work is
  committed rather than left in the tree.
- Commit the work you were asked to do; that local commit is the durable, reviewable record.
  Push, open a pull request, merge, or publish only when the request or the established
  workflow authorizes that further step, and report the actual outcome rather than the
  intended one.

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

Finish with the outcome, the important files or behaviour changed, where the work is recorded
(the branch, and the commits or pull request if any), validation performed, and any remaining
limitation or manual check. Keep the explanation short for simple tasks and detailed enough
for the user to judge risk on larger changes.
