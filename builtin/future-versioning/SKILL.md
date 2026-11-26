---
version: 0.7.0
name: future-versioning
description: >
  Do versioned work in a local Git repository: code, documents, data, analyses or other
  artifacts whose history matters. It exists for two jobs: commit every meaningful change,
  however small, so history records what changed and when; and coordinate several sessions
  on one project through Git worktrees, so they advance files in parallel without fighting
  over a checkout. Prefer it when a task writes, modifies, builds, tests or maintains
  tracked files, or when another session may be touching the same repository. Load it
  before the first edit; a read-only question, search or review that changes no tracked
  file does not need it.
category: tools
---

# Versioned development with Git

Two outcomes drive every rule below.

1. **Traceable history.** Commit each coherent change as it happens, however small. The log
   is how a later reader answers "what changed, when, and why"; a finished change left
   uncommitted does not exist for that purpose.
2. **Concurrent sessions.** When more than one session works in a repository, each change
   gets its own worktree and branch, so files in flight cannot collide and only the base
   branch is shared.

Everything else is detail. Repository instructions (`AGENTS.md`, `CLAUDE.md`, contribution
guides) are more specific than this skill and win where they differ.

## Quick path

1. `git rev-parse --show-toplevel` and `git status --short --branch`: where am I, what is
   already modified.
2. Read the repository's instructions before deciding how to work. Run `git worktree list`
   and `git branch --show-current` when another session may be in the same repository.
3. Isolate, unless the repository prescribes otherwise:
   `git fetch origin && git worktree add --no-track .worktrees/<name> -b <type>/<name> origin/<base>`
   (no remote: `git worktree add --no-track .worktrees/<name> -b <type>/<name> <base>`).
   Single-checkout repositories with declared write scopes stay where they are.
4. Edit in small coherent steps, verify with the repository's own commands, stage by path,
   and commit each step with a message that says why.
5. Review `git diff --stat`, `git diff` and `git status --short --branch`. Push, open a pull
   request or merge only when the request or the repository's convention authorizes it.
6. Finish with the guarded cleanup under *Finishing*: remove the worktree, delete the branch
   only after proving it landed, prune, and update the base in the checkout that holds it.

## 1. Establish scope

1. Treat "this is a Git repository and the task will produce files worth tracking" as the
   selection signal: source code, tests, builds, configuration, prose, data, figures,
   analyses, and debugging, refactoring or revising them. A repository alone does not make a
   read-only answer, search or review this skill's work; a review loads it only when it will
   change tracked files.
2. When artifacts worth tracking are coming but no repository exists, recommend `git init`
   plus a `.gitignore` for generated and large files, say why (history, reviewable diffs,
   reproducible or revertible state), and initialize only with the user's agreement. Do not
   turn a plain folder into a repository unasked, and do not initialize one inside a
   disposable chat or scratch workspace (see *Scratch workspaces*).
3. Read applicable instructions first. More specific repository instructions override this
   workflow, including its worktree default.
4. Decide whether the user wants an explanation, an investigation, an implementation or a
   review. A diagnosis does not authorize a fix; a review does not authorize editing.
5. Commit as the work happens (see *Commit as you go*). Committing is what makes the result
   traceable; treat a finished change left uncommitted as unfinished.

## 2. Understand before changing

Build enough understanding of where the behaviour, text or data is owned, how it is reached
and consumed, which tests and contracts define the expected result, and whether the files
already contain someone else's changes. Scale the depth to the risk, but do not edit from an
isolated search hit: search to find the owning implementation, call sites, tests and
configuration, then read enough local context to avoid edits based on isolated lines.

- `rg --files` lists candidates, `rg -n` searches text and symbols (`-C` only when
  surrounding lines help). Without `rg`, use `git grep -n` or a native tool such as
  PowerShell `Select-String`; do not install a search tool for a small task.
- Respect ignore rules; expand into generated paths only when the task needs them. Treat
  ripgrep exit code 1 as "no matches", not a tool failure.
- Follow existing architecture, naming and generated-file boundaries; distinguish confirmed
  facts from hypotheses; ask only about choices that materially change the result.
- Use history (`git log -- <path>`, `git log -S`, `git log -G`, `git blame -L`) to answer a
  concrete question, not as a mandatory scan.

## 3. Make a focused change

Implement the smallest coherent change that fulfils the request; no unrelated cleanup,
speculative abstraction or dependency addition. Preserve existing user work, never revert
unrelated changes, and stop if safe integration is unclear. Prefer precise edits; use a batch
operation only for genuinely mechanical work, and inspect the diff either way. Edit
source-of-truth files, run the project's generator instead of editing its output, and add
tests where behaviour or risk needs durable coverage. For a non-code deliverable, add the
equivalent guard (a check, a script or a documented manual verification) with the artifact.

## 4. Verify proportionally

Discover the commands from repository instructions, manifests, scripts and CI; start with
checks closest to the change and broaden only when the change or policy warrants it. Account
for the shell and platform, including `.sh`, `.ps1` and `.cmd` entry points.

Never claim a check passed unless it ran successfully. Report skipped or blocked checks and
their impact, and give one short manual check when behaviour cannot be exercised. Do not
present indirect evidence as runtime validation or let a later no-match obscure an earlier
formatter, build or test result. Before retrying a failure, determine whether it comes from
the change, the environment, a missing dependency or permissions.

## 5. History and parallel work

### Commit as you go

- Prefer several small, coherent commits over one dump at the end. One intent per commit.
- Write the message for a later reader: why the change exists, not only what moved.
- Stage by path (`git add <path>`) whenever the checkout may hold another session's work;
  never `git add -A` blindly, and leave unrelated in-progress edits alone.
- Commit the change you were asked for; push, open a pull request or merge only when the
  request or the repository's convention authorizes that further step.

### Isolation: two modes

**Worktree per change — the default.** For work beyond a trivial edit, put the change in
`.worktrees/<name>` on a branch of its own. Parallel sessions can then work at once and
only the base branch is shared.

1. Branch from the current remote tip, not from a local base that may lag:
   `git fetch origin`, then
   `git worktree add --no-track .worktrees/<name> -b <type>/<name> origin/<base>`.
   `--no-track` matters: without it a plain `git push` would target the base branch. Pick
   the branch type that matches the change (`feat`, `fix`, `docs`, `refactor`, `perf`,
   `test`, `ci`, `chore`).
2. With no `origin` remote, branch from the local base instead:
   `git worktree add --no-track .worktrees/<name> -b <type>/<name> <base>`, and skip every
   fetch, push and remote-branch step below.
3. Keep `.worktrees/` untracked (add it to `.gitignore` when absent).
4. Never check out the base branch inside the worktree; that locks it for every other
   session. If you are already inside a worktree, work there — do not nest another
   (compare `git rev-parse --show-toplevel` with `--git-common-dir`).

**Single checkout with declared write scopes — when the repository says so.** Some
repositories run concurrent sessions or goal workers against one checkout and serialize
them with declared, disjoint write scopes and a guard (for example `future goal ...`).
Follow that convention: commit only paths in your scope, stage them by name, and leave
another worker's in-progress paths untouched. Do not add a worktree the repository says it
does not want; a separate checkout would fork the paths its guards and artifacts refer to.

A read-only investigation stays in the current checkout and creates neither.

### Keep the base branch current

Re-synchronize before pushing, not only at the start: fetch, merge the base into the change
branch, and re-run the checks that merge affects. A branch that is behind bounces between
"update branch" requests and re-queued checks.

Update a local base branch only in the checkout that holds it. If another worktree has it
checked out, update it there (or `git fetch origin <base>:<base>` when it is not checked
out); never move it out from under a running session. Do not fast-forward a base branch the
repository treats as long-lived except as its instructions allow.

### Recording the convention

Repository instructions are what parallel sessions share, so a repository that follows this
skill should record its delivery convention in `AGENTS.md` or `CLAUDE.md` — and name the
skill, worded for the repository:

> This repository follows the `future-versioning` skill. Load it before changing tracked files.

That line is what makes the file executable: the repository records its own decisions, and
this skill supplies the steps. Put it where a session reads it first and do not restate the
skill under it; a copy becomes a stale second source when the skill changes.

- **No recorded convention yet.** Write the one the repository should have, in a commit of
  its own, and report that commit at handoff. Cover only what the repository decides for
  itself: scope; base branch, change branch and worktree naming; commit granularity and
  message form; the exact check commands before handoff; how work is finished and what
  cleanup follows; boundaries that are easy to get wrong (files not to touch, other
  sessions' branches, secrets). Keep it readable in one sitting and link to long procedures
  instead of inlining them.
- **A convention already exists.** Add only what is missing — usually the pointer line
  above — and never restructure someone else's file. Do not duplicate the skill's defaults
  or restate a workflow the file already records.
- **Ask before writing** when the repository is not yours (a clone, an upstream you will
  send a patch to, a shared repository with maintainers), when its recorded convention
  conflicts with this workflow, or when the user does not want instructions committed
  there. Scratch work that hands nothing to a later session needs no file.

Check that it can be followed: re-read it as a session that has only that file and should be
able to cut a branch, run the checks and finish without asking what was meant.

### Review before handoff

Say where the change lives (worktree path and branch) and what the base looks like
afterwards. Before handoff run `git diff --stat` for scope, `git diff` for content,
`git diff --check` for whitespace, and `git status --short --branch` for untracked files.
Look for accidental files, generated noise, secrets and unrelated edits, and confirm the
intended work is committed rather than left in the tree.

### Finishing

Clean up only after the change has landed: the pull request is merged, or the content is
verifiably in the base. Then, in order:

```bash
# 1. A dirty worktree holds uncommitted work: commit it, or discard it deliberately.
git -C .worktrees/<name> status --short --branch
git worktree remove .worktrees/<name>   # --force only for build output you created

# 2. A squash merge leaves the branch commits in place, so `git branch -d` refuses them
#    as "not fully merged". Prove the merged content is in the base, then delete:
paths=$(git diff --name-only <base>...<branch>)   # paths with spaces need quoting
git diff --quiet <base> <branch> -- $paths && git branch -D <branch>
#    A non-empty diff, or a closed PR that was not merged, means the work is not in the
#    base: keep the branch and report it instead of deleting.

# 3. Delete the remote branch only if you pushed it and it is disposable there.
git push origin --delete <branch>
```

Then `git worktree prune`, and bring the local base up to date in the checkout that holds
it (`git fetch origin && git merge --ff-only origin/<base>`); if another worktree holds the
base, update it there rather than moving it.

Never delete a branch while its content exists nowhere else, never force-remove a worktree
that may hold another session's work, and never clean up a worktree or branch you did not
create — report it instead.

### No remote

A repository without `origin` has no fetch, push or remote-branch steps. Commit locally,
note the branch in the handoff, and do not create a remote or publish anything without an
explicit request. The same applies when the remote is unreachable: keep the local commits
and report the push as blocked rather than rewriting history.

### Scratch workspaces

Chat and thread workspaces under `~/.future/workspaces/...`, temporary directories and
other scratch locations are disposable. Do not initialize a repository there: its history
disappears with the directory. Put the repository in a durable project directory and work
there, or ask the user where it should live.

## 6. Escalate long work deliberately

Use `future-goal` for work that must continue across sessions, run for a long time, maintain
durable todos, or satisfy an explicit "keep working" request. Check for a matching goal
before creating one, define concrete completion evidence, and keep one-shot edits here.

## 7. Respect tool boundaries and hand off clearly

Use the tools actually available, quote paths safely for the active shell, and give delegated
agents bounded tasks with evidence; the supervising session owns integration and independent
verification. Finish with the outcome, the files or behaviour changed, where the work is
recorded (branch and commits, or pull request), validation performed, and remaining
limitations or manual checks.
