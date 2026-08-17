---
version: 2.5.0
name: future-loop
description: FutureOS loop control plane — manage long-running goals, todo lists, human gates, monitors, and validated completion via the loop control plane. Use when the user wants a long-lived/multi-step/cross-session task tracked as a goal, asks to "keep working on X", "track this issue", "run this overnight", needs progress/status of ongoing agent work, or starts a message with "/future-loop" (treat everything after the prefix as the goal).
allowed-tools: Bash(future-loop:*)
category: tools
---

# Loop Control Plane

`future loop` turns a conversation into a durable, reviewable long-running goal:
the goal, todos, human gates, monitors, evidence, and completion are
persisted outside the chat. The agent executes one bounded turn at a time;
the loop control plane decides what should happen next.

## When to use

Load this skill when the user:
- starts a message with **`/future-loop <task>`**: treat the text after the
  prefix as a NEW long-running goal — create the goal and drive it to
  completion (do NOT treat it as a one-shot request);
- wants a **long-lived / multi-step / cross-session** task ("keep working on X",
  "track this issue", "run this overnight", "keep pushing forward");
- asks about the **status or progress** of ongoing agent work;
- needs a decision point surfaced ("waiting for my approval" scenarios);
- wants recurring observation of an external state (CI, PR, file appearing).

For one-shot conversations, just answer normally — no goal needed.

## Prerequisites

- Everything runs through the unified CLI: **`future loop <cmd>`**. Look for an
  existing install (`command -v future`; also `~/.local/bin/future`, `~/bin/future`,
  Homebrew links). If missing, point the user to
  <https://github.com/futuregene/future-os> (README install section) — do NOT
  rebuild from source on the user's behalf. State lives in the PROJECT:
  `<cwd>/.future/loop/` (run from the project dir, or pass --cwd).
- `future loop run` needs the agent server: `future agent` (gRPC
  127.0.0.1:50051). Probe with `future models`.
- **Check binary freshness before relying on newer features** — an old binary
  runs the commands but silently skips new behavior. Probe:
  `strings $(command -v future) | grep -c "max-turn-secs"` — `≥1` = current
  (blocks enforcement, mid-turn steering, turn budget, atomic claims,
  `status --format json`); `0` = stale → rebuild with `cargo build -p future-cli`.

## State layout (project-local, all under `<cwd>`)

```
<cwd>/.future/loop/registry.json                        — registry (source of truth)
<cwd>/.future/loop/goals/<id>/events.jsonl              — per-goal event ledger
<cwd>/.future/loop/goals/<id>/ACTIVE_GOAL_STATE.md      — reference-compatible projection
<cwd>/.future/loop/runs/                                — run history + <run_id>.live.jsonl
```

Runtime state is NEVER written outside the project. Add `.future/loop/` to the
project `.gitignore`.

## Binary & ledger forward compatibility

The ledger outlives binaries: a goal written by a newer `future` may be read
by an older one. Ledger reads are therefore tolerant of **unknown event
kinds** — each line is parsed as JSON first; an event whose kind the running
binary does not recognize (newer ledger) is **skipped with a warning, never a
hard "read ledger" failure**. Only structural corruption (missing fields,
wrong types, missing kind) fails closed.

- Skipped lines are recorded in a per-goal sidecar
  `<cwd>/.future/loop/goals/<id>/read_diagnostics.json` (auto-removed once the
  ledger reads clean).
- `status` / `diagnose` / `store verify` surface it as
  `note: N unknown-kind event(s) skipped — binary older than ledger, please upgrade`;
  the verify report gains `skipped_unknown_kinds` + `unknown_kinds`, and
  `--format json` status/diagnose expose `ledger_read_diagnostics`.
- Operator rule: seeing that note means the BINARY is older than the LEDGER —
  upgrade first (`cargo build -p future-cli`) before writing, or newer events
  will be skipped on replay (and `status` projections drift).

Lock files are liveness-checked too: `ACTIVE_GOAL_STATE.md.lock` records the
holder's **pid**; a conflict probes the holder via `kill -0` — a live holder is
a hard "held by pid N" error, a dead holder (or an empty lock older than
10 min) is cleared and taken over, and a fresh empty lock is refused until it
ages out. The lock is released (removed) after the projection write. Zombie
locks from killed runs no longer wedge `status`.

## Workflow

### 1. Inspect existing goals first

```bash
future loop status
```
If the user's objective already exists, continue it — never silently create a duplicate.

### 2. Confirm the plan with the user BEFORE creating anything

Present a concrete plan and get confirmation:

1. **Steps** — the todos you will execute, in order. Short and concrete.
2. **Model + thinking level** — default to the CURRENT session's model and
   thinking level (read your own environment). If the user wants a different
   model, `future models [--json]` lists options (prefer `[recommended]` /
   `[default]`); `high` thinking for reasoning-heavy goals, `off`/`low` for
   mechanical work. If the agent server is down and `future models` fails, fall
   back to the current session's model + `high` and say so.
3. Ask: `Plan confirmation (goal: …) Steps: 1)… 2)… 3)… Model: … Thinking: … Confirm?`

Skip this confirmation only when the user's opening message already contains the
full objective AND explicit operating constraints (model, concurrency, deadline) —
that mandate IS the confirmation; start immediately.

### 3. Create a goal (or reuse)

```bash
future loop goal init --objective "..." --cwd <project-dir> [--goal-id <id>]
```
Use the user-named directory/repo root as `--cwd`; `mkdir -p` it if missing.
`goal init` auto-creates an onboarding todo — complete it with `--no-follow-up`
during setup; it is not real work.

### 4. Break the work into todos

```bash
future loop todo add --goal <goal-id> --text "..." --priority P0
```

**Dependency chains.** When "X must finish before Y can start", add `--blocks X`
to Y. A blocked todo stays out of the runnable frontier until every predecessor
reaches Done or Superseded (an unknown predecessor id does not wedge the
frontier; `task-graph` flags it as an error instead). Without `--blocks`, open
todos are independently runnable in priority order.

```bash
future loop todo add --goal G --text "Generate the report" --priority P0 --blocks <data-todo-1>,<data-todo-2>
future loop todo add --goal G --text "Copy deliverables to project root" --priority P0 --blocks <report-todo>
```

**Todo-creation pitfalls.**

1. **Capture todo ids from the `todo add` output** (`todo todo_xxx added ✔`) —
   the only reliable source. There is no `todo list`; look ids up via
   `future loop status --goal G [--format json]` or the event ledger
   (`kind:"todo_added"` events carry the full todo). Field-name gotcha: in the
   ledger the dependency field is `blocked_by_gate` (NOT `blocks`) and the
   validator is `validator` (NOT `verify`).
2. **Verify the wiring after creation** — `future loop status --goal G`; repair
   with `todo update --blocks a,b` (replaces; `--blocks ""` clears; absent leaves
   untouched).
3. **Chain the FINAL validation todo too** — priority alone does not order
   execution; the acceptance todo MUST `--blocks` all implementation todos or it
   can run while they are still stubs.
4. **`goal delete` requires `--force` and is irreversible** — recreate via
   `goal init` afterwards.
5. **Keep cleanup/deletion words out of test-goal objectives** — the run agent
   may execute `goal delete --force` itself if the objective mentions them.
   Delete test goals yourself.
6. **CLI strictness**: unknown flags are a hard error (never silently
   ignored), and unknown todo-ids are rejected. Every subcommand renders its
   usage on `--help`. All read-only commands accept `--format json` (alias
   `--json`). A non-numeric `--resume-when` value prints an explicit
   no-deadline warning. Exact flags: `orchestration/loop/src/console.rs`
   `parse_pairs` call sites, or `future loop commands` for the grouped
   operator view.
7. **`todo archive` does NOT leave the frontier** — it only flips
   `archive_state`, which nothing in the decision/frontier code reads: an
   archived todo stays `open` in `status` and remains runnable by `run`. To
   take a todo out of rotation ("暂缓"/"先不做"), use `todo supersede`
   (Superseded unblocks dependents and exits the frontier).
8. **Successor duplicates.** Completing a todo with a successor can create a
   NEW todo that overlaps an existing open one (e.g. the agent rewrites a
   follow-up with better detail). You then hold two todos for the same work —
   supersede the stale one AND repair any `--blocks` that pointed at it:
   `todo update --todo-id <acceptance> --blocks <new-list>` (blocks are
   replaced wholesale).
9. **A turn is not one todo.** A single `run` turn may complete several todos
   in sequence (observed: one turn delivered 24 loop batches + 8 agent batches
   + a cli residual). `status`'s `spent` counter increments only when the run
   process EXITS — a mid-turn `status` still shows the old count and the old
   `next` line.
10. **The run agent can merge PRs itself.** In-turn tooling includes a shell;
    agents have run `gh pr merge` autonomously. When tracking PRs, check
    `gh pr list --state merged`, not just open PRs — and review what landed on
    main at wrap-up time.

**User gates.** When the user asks for approval before a specific action, create
a real gate — describing it in the objective is NOT enough:

```bash
future loop todo add --goal G --role user --class user_gate \
  --gate-question "<exact question>" --text "<exact question>" --blocks <action-todo>
```
Any OPEN gate freezes all work: `run` returns `AskUser`, and `todo complete`
rejects non-gate completions until it is resolved. Gates are completed via
`gate resolve`, never `todo complete`.

**Conditional iteration.** Attach an independent validator; the kernel runs it in
the goal cwd after each turn and only completes the todo on exit 0:

```bash
future loop todo add --goal G --text "Optimize until tests pass" --priority P0 \
  --verify "cargo test" --max-validation-attempts 5
```
Non-zero → repair retry up to the attempts budget, then a replan gate. The agent
can still force-complete via `todo complete --no-follow-up` (agent autonomy).

**Implementation todos MUST carry `--verify`** (convention, enforced by
review not by the CLI). An agent can mark a todo done while the code does not
compile — the validator is the only automatic gate against that. `todo add`
helps: when the text looks like a code task (contains `.rs`, or a token match
on worktree/commit/cargo/clippy/rustfmt/test/compile/build/lint/refactor/
patch/crate/git/merge/code/debug, or the Chinese 测试/代码/编译/修复) and no
`--verify` is given, it prints an advisory hint to stderr after the add:
`hint: 实现类 todo 建议挂 --verify "cargo check -p ..."，防不编译代码被标完成`
(pure reminder — CLI semantics never change). Templates:

```bash
--verify "cargo check -p <crate>"                                          # compile gate
--verify "cargo test -p <crate>"                                          # test gate
--verify "cargo fmt --check && cargo clippy -p <crate> --all-targets -- -D warnings"  # full gate
```

### 5. End with a deliverable-copy todo

Every goal that produces files MUST end with a final P0 todo that copies
deliverables from the loop state directory to the project root (`cp`, not `mv`),
blocked behind the producing todos:

```bash
future loop todo add --goal G --text "Copy the final deliverables to the project root (cwd)" --priority P0 --blocks <producer-todos>
```

### 6.0 Agent identity — `--agent-id` MANDATORY on every run

`run` without `--agent-id` fails fast; `--anonymous` is the legacy
uncoordinated one-shot. The agent-id is the ONLY mutual-exclusion mechanism:

- `run --agent-id <name>` auto-registers on first use; `agent list` shows who
  is registered/running.
- **Unique name per parallel worker** (e.g. `<host>-<task>`). A run sees its OWN
  leased todos as runnable, so two runs sharing one id double-execute.
- With `--agent-id`, `run` claims a lease (default 4h; `--lease-secs N`) BEFORE
  executing and hides other agents' leased todos (`claimed_by_other`) — parallel
  runs grab DIFFERENT todos. Claims are atomic (check+append under one lock; a
  lost race re-decides and takes the next runnable todo).
- Conflict-avoidance checklist before launching: `agent list` → `ps aux | grep
  "future loop run"` → `status --goal G` → `quota should-run --goal G --agent-id
  <me>` → `lease status --goal G --todo-id T --agent-id <me>`.
- **Workspace guard (write-conflict protection)**: agents declare the path set
  they write into via `agent onboard --workspace p1,p2` (comma-separated).
  Claiming a todo while a peer holds a live lease in an
  OVERLAPPING declared workspace is refused with a retry hint (degrade to
  serial) unless you explicitly override: `--force` on `todo claim`,
  `--force-workspace` on `run`. The guard is advisory and fail-open — an agent
  that declares no workspaces never blocks (legacy peers keep working).
  Successful claims by workspace-declaring agents append a
  `WorkspaceLockAcquired` event, so `agent list` shows who occupies which
  paths. Declare disjoint workspaces per parallel worker whenever they share a
  checkout.

### 6.1 Multi-agent parallel runs

N concurrent runs on the SAME goal share the ledger safely. On current binaries
the claim race is closed; for extra determinism (or old binaries), assign todos
BEFORE launching:

```bash
future loop agent register --goal G --agent-id worker-1     # … worker-2, worker-3
future loop todo claim --goal G --todo-id <T1> --agent-id worker-1 --lease-secs 14400
nohup future loop run --goal G --agent-id worker-1 --model <M> --thinking-level <L> \
  --max-turns 1 > logs/worker-1.log 2>&1 &
```

- Lease expiry frees the todo for others but does NOT abort a running turn.
  Release a parked claim with `future loop lease release` so the queue's most
  valuable todo is never walled off by a stale lease.
- Relaunch the same command (same agent-id) to continue after each turn — the
  worker keeps its claim and resumes.
- Worker count must fit the machine; agree it with the user (default 3).
- Pre-claim overrides pure-priority ordering: assign highest-value todos first.

### 6.2 Orchestration patterns for parallel workers

1. **Orchestrator-only dangerous actions.** Anything consuming a LIMITED
   external resource (submission quotas, paid calls, irrecoverable deletes)
   must not be callable by workers — a worker's *failed* attempt may still
   consume the resource. Convention: workers finalize artifacts and write a
   signal file (e.g. `logs/NEEDS_ACTION` with the payload); only the
   orchestrator executes the capped action. State it explicitly in todo text.
2. **Shared project memory as broadcast channel.** Instruct workers (in todo
   text) to re-read the project memory file at turn start; use it for
   cross-worker discoveries and infra locations. The turn envelope carries only
   todo text + last evidence.
3. **Steer by updating todo text, anytime.** `todo update --text` on a running
   todo is delivered mid-turn (see §6 mechanics).
4. **Watch artifacts, not just loop status.** Long compute runs via nohup +
   checkpoint files; the orchestrator tracks output mtimes. Killing a worker's
   run process and relaunching with the same `--agent-id` is always safe —
   context replays from the ledger.
5. **Wrap-up belongs to the orchestrator.** A final/validation todo left
   unchained can be picked early and close the goal prematurely — `--blocks` it
   behind everything, or do the wrap-up outside the loop.
6. **Orchestrator takeover mode.** When a worker's output is untrustworthy
   ("worker says done" ≠ "compiles" — faithful ports carrying in garbage:
   non-existent std APIs, orphan helpers with no call sites, broken mod.rs
   wiring), stop steering and take over in the orchestrator's own session:
   (a) run the full gate yourself:
   `cargo fmt -p <crate> && cargo clippy -p <crate> --all-targets -- -D
   warnings && cargo test -p <crate>`; (b) **treat dead code as real
   findings** — delete orphan helpers instead of keeping them; (c) verify the
   worker's structural claims against main (module wiring, structs intact);
   (d) mechanical closeout (fmt/clippy/test/commit/`todo complete`) is faster
   done by the orchestrator than waiting for worker retries. Review what the
   worker committed (`git show`) before trusting its "done".

### 6. Run the agent — one turn at a time

**Always `--max-turns 1`** and loop manually for visibility:

```bash
future loop run --goal G --agent-id <unique-name> --model <M> --thinking-level <L> --max-turns 1
```

Run mechanics:
- **`--max-turn-secs N`** — per-turn wall-clock budget; timeout stops the run
  gracefully (session cleaned up, context replays on relaunch).
- **Mid-turn steering** — `todo update --text` on the todo a worker is executing
  is injected into the running session (~10s poll; delivered at the agent's next
  step boundary).
- **Session id in the envelope** — the turn message starts with `session: <id>`
  so in-turn tooling can find the real session file deterministically.
- **Live run logs** — streamed events tee to `.future/loop/runs/<run_id>.live.jsonl`.
- **`status --format json`** — machine-readable goal + todos projection.

**Launch pattern — nohup + poll (foreground blocking dies with shell timeouts):**

```bash
nohup future loop run --goal G --agent-id <me> --max-turns 1 > logs/worker-<me>.log 2>&1 &
tail -f .future/loop/runs/<run_id>.live.jsonl
```

**Monitoring a long turn** (multi-hour turns are normal for big tasks):
poll the pid (`kill -0 <pid>`), tail `.future/loop/runs/<run_id>.live.jsonl`
for `tool_start`/`tool_end` liveness, and watch the worktree's `git log` for
commit progress — `status` alone lags (see pitfall 9). **Do NOT rely on
`logs/` for monitoring**: it is shared with parallel sessions and gets
cleaned externally; worker stdout redirects belong in `/tmp` when they must
persist. If the turn must be stopped, `kill <pid>` is safe: the session
writes back and the next `run` replays from the ledger.

**Idle-turn detection (`TurnNoProgress`).** The kernel detects turns that end
with no write-class tool (`write` / `edit` / `shell`) started inside the
no-progress window (default 15 min; `FUTURE_LOOP_NO_PROGRESS_SECS` overrides)
and appends a `TurnNoProgress {goal_id, todo_id, agent_id, idle_secs,
tool_calls_total}` event to the ledger — **detect + record only**: the kernel
never auto-injects gates or kills the run on its own. The record folds into
`goal.turn_no_progress` on replay and surfaces in `status` (human + JSON) and
`todo-event`. Orchestrator response to an idle worker (e.g. an exploration
loop with zero writes):
1. Steer first: `todo update --goal G --todo-id T --text "<concrete rewrite>"`
   — delivered mid-turn at the agent's next step boundary (~10s poll). For an
exploring worker, rewrite the todo with concrete data structures / function
signatures to push it into implementation state.
2. If it stays idle, `kill <pid>` + relaunch with the same `--agent-id` —
context replays from the ledger, always safe.

**PR merge troubleshooting** (when turns produce PRs you must merge):
- `BEHIND` — branch protection requires up-to-date: `git merge origin/main`
  on the PR branch + push, wait for CI, merge.
- A required check stuck at **skipping** — the CI paths-filter probably misses
  the changed directory (e.g. `orchestration/**` was absent from
  `rust_workspace` once, so loop-only PRs could never merge). Fix the filter
  in `.github/workflows/ci.yml` on the same branch; editing the workflow
  re-triggers every suite.
- The `CodeQL` rollup check shows **skipping** while `Analyze (*)` jobs are
  still pending — that is an intermediate state, not a failure; wait.
- GitHub API flakes (SSL/EOF): wait and retry; don't re-push to "fix" it.

**Session lifecycle:** each `run` creates a fresh scratch session and deletes it
on every exit path — nothing durable lives in `~/.future/agent/sessions/`. A
stray `⚠ session cleanup failed` line or accumulated sessions = stale binary
(see Prerequisites) or leftover from other tools; clean with `future session
list` / `future session delete <id>`.

**Session event-stream gaps self-heal.** `run_turn` survives the agent's
DataLoss "event stream gap" termination: it reconnects ONCE after a 2s
backoff on the same session with an atomic attach resuming from the last
observed event idx (strictly `idx > cursor` — nothing double-counts). Only a
second CONSECUTIVE gap terminates the turn, carrying the ORIGINAL error.
Non-gap transport errors fail immediately as before. If turns keep dying
with "event stream gap", suspect a busy shared agent server (several workers
on one 127.0.0.1:50051) — falling back to the takeover pattern (§6.2) is
faster than waiting out worker retries.

`run` stops when: validated closure (terminal), a human gate opens, a blocker
waits (unresolved `--blocks`), or max-turns/max-turn-secs is reached.

**After each turn:**
1. Report what was done (todo, cost, new status).
2. **Reflect & improve** — what did the turn reveal? Is the objective still
   right? Is the decomposition still optimal (split/merge/reorder)? New risks
   needing a gate/monitor/`--verify`? Every ~3–5 turns, deep-replan the
   remainder as if planning fresh. Apply routine adjustments yourself:
   `todo add` / `todo supersede --reason` / `todo update` / `todo archive`.
3. Check the plan still holds: `future loop status --goal G`.
4. Stop and ask the user ONLY when absolutely necessary (risky/irreversible
   changes, user-only decisions, or you cannot determine the adjustment).
5. Non-zero exit = max-turns hit; rerun only if open todos remain.

### 7. Handle replan gates — resolve routine ones yourself

**PLAN_REVIEW gates** (kernel-injected when validation budget is exhausted,
outcome floor hit, acceptance gaps remain, or the oscillation guard fires —
delivery outcomes flip-flopping accept/reject A→V→A→V across the post-ACK
run history) are the agent's to resolve:
review (`status` / `diagnose --goal G`) → adjust todos via CLI → resolve and
resume:

```bash
future loop gate resolve --goal G --todo-id <gate> --decision "agent replan: <summary>" --note "..."
future loop run --goal G --agent-id <unique-name> ...
```

**Genuine user gates** (approvals, scope changes, risky/irreversible actions):
STOP, quote the exact question and gate id IN THIS CONVERSATION, and wait.
Never guess. After the user decides, `gate resolve` with their decision and
resume.

### 8. Report progress

After each turn: `future loop status --goal G` (+ `quota should-run`). Report
todo state, next action, gates, cost. Close stale open todos the agent did
inline:

```bash
future loop todo complete --goal G --todo-id <stale-id> --no-follow-up --evidence "..."
```

### 9. Close the loop on deliveries — delivered ≠ verified

Completing an advancement todo records a DELIVERY in the pending `delivered`
state — not a verified outcome. Resolve every delivery to a terminal outcome:

```bash
future loop delivery status --goal G [--format json]     # who is delivered / resolved / overdue
future loop delivery record --goal G --todo-id T --outcome verified|failed|rework [--note "..."]
```

- A delivery left unverified for 3 turns auto-derives a follow-up todo (the
  run path does this; `delivery followthrough --goal G [--turns N]` runs the
  scan manually) — an unverified delivery can never silently age out of the
  frontier. Fires exactly once per delivery cycle.
- `rework`/`failed` resolutions should feed a replan (successor todo), not a
  silent retry of the same todo.

## Long-drive playbook (multi-hour goals, competitions, overnight runs)

Hard-won patterns from a 24h multi-agent competition drive (37 turns, 30
agents, 38 todos). Each rule below maps to a measured failure mode.

### Completion contracts — `--evidence` floor + `--acceptance` tokens

`todo complete` enforces non-empty `--evidence` for advancement todos and,
when declared, the `--acceptance` token contract:

```bash
future loop todo add --goal G --text "submit the payload" --acceptance "attempt,scored"
# evidence must contain EVERY token (case-insensitive) or completion is refused:
future loop todo complete --goal G --todo-id T --no-follow-up \
  --evidence "ATTEMPT 12345 SCORED 99 on the platform"
# --force is the operator's explicit override for mechanical closeouts.
future loop todo update --goal G --todo-id T --acceptance "a,b"   # retrofit mid-flight
```

- The #1 drive failure was the **empty-evidence closure**: 11/33 completions
  carried <60-char evidence (several fully empty), each silently removing a
  todo from the frontier. Every delivery todo must therefore carry a hard
  gate — a `--verify` artifact check, `--acceptance` tokens, or both.
- External-delivery todos (submit / scored / attempt …) without a contract
  get an advisory hint at `todo add`; heed it.
- “done” ≠ “delivered scored”: the evidence must name the external
  observable (attempt id, file path, measurement) that proves delivery.

### External-action budgets (submissions, paid calls, deletes)

Anything consuming a LIMITED external resource is orchestrator-only in
practice; encode the budget in todo text AND gate the completion:

- Declare the budget explicitly in the goal doc: `submissions: 10 per
  challenge, X left after each use`; update a shared ledger file (e.g.
  `ops/SCORES.md`) every turn.
- Workers finalize artifacts and write a signal file; only the assembler /
  orchestrator executes the capped action. A worker's failed attempt still
  consumes the resource — never let workers submit directly.
- Measured: one drive burned 8/10 submissions on one challenge (3 of them
  method="test") and 10/10 on another with zero scores, because two workers
  submitted in parallel without a budget check.

### Hard-task splitting

A single large todo that 2+ worker generations close with no artifacts is a
signal to split, not to retry:

- Split into s1..sN section todos, each with ONE concrete artifact
  (`work/s1/matching.json` + a verify script) and a `--verify` gate on that
  file — empty closures become physically impossible.
- Chain an assembler todo behind all sections (blocked); the assembler
  merges artifacts, runs the contract checker, and submits. Give the
  assembler a `--verify` too — it closed empty once.
- Measured: 9 generations of whole-task todos produced zero files; the
  split-with-verify version produced 3 verified sections in 54 minutes.

### Dead-process lease cleanup

Killed/killed-mid-turn runs leave 4h leases that refuse new claims:

```bash
future loop agent list --goal G          # find stale holders
future loop lease release --goal G --todo-id T --agent-id <dead-agent>
```

Release every lease the dead agent holds before relaunching workers, or the
workspace guard degrades the whole relaunch to serial.

### Orchestrator dead-time

`--max-turns 1` means every turn end is a manual relaunch point — the
orchestrator must relaunch immediately, not after diagnosis:

- Keep the agreed worker count running at all times; relaunch the moment a
  turn exits (same `--agent-id`, context replays from the ledger).
- A worker that stays write-idle (TurnNoProgress) should be steered once via
  `todo update --text`, then killed + relaunched — not left to idle.
- Escalate the model when a todo has produced NO write artifacts for 2
  consecutive turns (e.g. deepseek-v4-pro → kimi-k3). Measured: one
  hard-science challenge went 0 → 99.5 on the first stronger-model turn.

### Repo delivery discipline (code waves)

When a wave produces code commits on a worktree branch, deliver them as
small PRs instead of one mega-PR:

- Cherry-pick ONE item commit onto the freshest origin/main per PR;
  resolve conflicts by keeping both sides (new main features + your wiring).
- Local gate before push: cargo fmt --check, clippy --workspace
  --all-targets -- -D warnings, targeted crate tests (full workspace is
  CI's job).
- gh pr create + gh pr merge --squash --auto; when GitHub reports
  BEHIND/BLOCKED (main moved), git merge origin/main into the PR branch,
  push, and let auto-merge fire. CodeQL js-ts jobs occasionally queue-stuck:
  an empty commit retriggers them.
- Each squash-merged PR lands as one commit on main; the original worktree
  branch stays as the archive.

## Key semantics (do not misuse)

- **Terminal ≠ all todos checked.** Completion is validated closure (todos done
  + closure intent + no acceptance gaps). Check `closure_proof`.
- **Never silently complete agent work**: `todo complete` requires
  `--no-follow-up` or `--successor`.
- **Gates freeze ALL work** while any user gate is open (not just linked todos);
  gates complete via `gate resolve`, never `todo complete`.
- **Not every gate is the user's**: `PLAN_REVIEW` checkpoints are agent-resolved;
  genuine human decisions are surfaced and awaited.
- **Monitors**: not-due monitors must NOT be polled (run returns `wait`). Due
  time comes from `--cadence`/`--defer-secs N`; `todo update --resume-when N`
  (numeric) defers N seconds for real, a text value is only a hint with NO
  deadline.
- **Evidence honesty**: report real outputs (paths, test results) — the control
  plane readbacks key results.
- **Deliverables to CWD**: the final todo copies user-facing artifacts to the
  project root.
- **Delivered ≠ verified**: `todo complete` records a delivery in the pending
  `delivered` state; an operator/validator must resolve it via
  `delivery record` (`verified`/`failed`/`rework`). Unverified deliveries
  auto-derive a follow-up todo after 3 turns (see §9).

## Multi-agent topology (G12)

Beyond independent parallel workers (§6.1–6.2), a goal can declare a
**multi-agent contract** — the single declarative surface for its multi-agent
topology: peers (each with an optional `backup_for` succession edge,
descriptive-only capabilities, and workspaces), handoff rules (event → role),
and named
collectives. Everything downstream (succession, wake roster, turn ledger) is
a PROJECTION over the event ledger — goal state is never mutated by it.

```bash
future loop agent contract set --goal G --contract '<json>'   # or --contract-file PATH
future loop agent contract show --goal G [--format json]
```

The contract is `multi_agent_contract_v0` JSON:

```json
{
  "schema_version": "multi_agent_contract_v0",
  "peers": {
    "worker-a": {"capabilities": ["shell"], "workspaces": ["repo"]},
    "worker-b": {"backup_for": "worker-a", "capabilities": ["github"], "workspaces": []}
  },
  "handoff_rules": [{"from_event": "lease_expired", "to_role": "worker-b"}],
  "collectives": {"c1": ["worker-a", "worker-b"]}
}
```

`capabilities` on each peer is descriptive metadata only — nothing in the
kernel enforces or consumes it (the capability framework and its gate were
removed); `workspaces` feeds the workspace guard.

Contract validation **fails closed** — an untrustworthy topology is never
recorded. Rejected: empty/self `backup_for`, unknown backup targets, backup
chains with a cycle (would oscillate succession), unknown handoff `to_role`,
duplicate handoff rules, unknown/duplicate collective members, and an agent
appearing in more than one collective. `contract show` re-surfaces validation
issues for a drifted on-disk contract.

**Agent recipes** (`agent recipe add|show --goal G`) are named onboarding
profiles — descriptive capabilities + workspaces + default priority — applied
by `agent onboard --recipe NAME` (the recipe owns the profile, so `--recipe`
conflicts with an explicit `--workspace`). Re-adding a name is
allowed; lookups resolve the latest (latest wins).

**Role succession** (`agent succession show|apply --goal G`) promotes a
declared backup when the primary's live lease expires (`lease_expired`) or
its scheduler heartbeat goes silent past the offline threshold (`offline`,
default 30 min; `FUTURE_LOOP_SUCCESSOR_OFFLINE_SECS` overrides, mainly for
tests). `show` lists recorded successions + currently-met (unrecorded)
triggers; `apply` records them (`SuccessionOccurred`, idempotent per
primary/backup/reason episode). Recorded successions surface as
high-severity `role_succession` attention items until the primary heartbeats
again (recovery suppresses the item).

**Collectives** (`agent collective show --goal G [--collective NAME]`)
project per-agent turn counts (from `TodoClaimed` events — a claim = one
bounded turn opportunity) plus the round-robin **wake roster** (contract
order rotated by completed turns; `full_participation_rounds` = min claims
across members).

## Goal frontier (G13)

`future loop frontier show --goal G [--format json]` composes the frontier
projection with four deepening layers over it:

1. **Outcome continuity** — outcome-streak segmentation over run history. A
   segment is a maximal run of same-kind turns (`surface_only` vs `material`;
   material = tools invoked + non-empty evidence). A segment resets when the
   turn kind flips OR a frontier-changing event (todo add/complete/supersede,
   gate resolve, frontier-delta replan ack, todo archive) landed between two
   runs. Pure projection — never a second source of truth.
2. **Replan rules** — the ordered disposition→decision policy table. The first
   matching rule (in policy order) is the decision, carrying
   `derives_obligation` + `obligation_kind` when a replan obligation is owed
   (`succession_gap`, `vision_acceptance_gap`, `monitor_no_change_streak`,
   `surface_only_progress_streak`). The default rule set is the builtin
   ordered list; `replan rules set --goal G --rule-ids R1,R2,...` declares a
   full-replace custom set (the caller's order wins; unknown ids are skipped)
   and `--rule-ids ""` resets to the default. `replan rules show` renders the
   active set with the selected rule marked.
3. **Semantic history** — a goal-level bounded ring (N=50, oldest dropped) of
   semantic event summaries folded from the ledger (run landed / todo
   completed / superseded / acceptance-gap satisfied / replan acked / monitor
   poll / gate resolved / delivery outcome / role succession / turn
   no-progress). Summaries are truncated to 200 chars at write time
   (public-safe).
4. **Terminal judgement** — the single authoritative terminal gate (decide()
   step 6): closure validated from complete sources (structured todos +
   acceptance gaps + closure-intent contract), every remaining blocker
   enumerated as an explicit gap (`open_todo` / `open_monitor` /
   `pending_deferred` / `unsatisfied_acceptance` / `succession_gap`), each
   unsatisfied acceptance gap carrying its id + description +
   `satisfied:false`. `terminal == gaps.is_empty()` matches
   `Goal::is_terminal()` exactly.

## Command reference

```bash
future loop status [--goal G] [--format json]
future loop goal init --objective "..." --cwd DIR [--goal-id G] [--goal-doc "..."]
future loop todo add --goal G --text "..." [--priority P0|P1|P2] [--blocks T] [--verify "cmd"] [--role user --class user_gate --gate-question "..."]
future loop todo update --goal G --todo-id T [--text "..."] [--priority ...] [--blocks T]
future loop todo claim --goal G --todo-id T --agent-id A [--lease-secs N]
future loop todo complete --goal G --todo-id T [--no-follow-up | --successor T2] [--evidence "..."]
future loop todo supersede --goal G --todo-id T --reason "..."
future loop gate resolve --goal G --todo-id T --decision "..." [--note "..."]
future loop quota should-run --goal G [--agent-id A] [--format json]
future loop agent register --goal G --agent-id A        # run auto-registers
future loop agent onboard --goal G --agent-id A [--workspace p1,p2] [--recipe NAME]
future loop agent list --goal G [--format json]
future loop agent contract set|show --goal G [--contract 'json'|--contract-file P] [--format json]
future loop agent recipe add|show --goal G [--name N] [--capabilities c1,c2] [--workspace p] [--priority P0]
future loop agent succession show|apply --goal G [--primary P] [--reason R] [--format json]
future loop agent collective show --goal G [--collective NAME] [--format json]
future loop lease claim|renew|release|expire|status
future loop delivery status|record|followthrough --goal G ...   # delivered ≠ verified closure
future loop frontier show --goal G [--format json]             # G13 goal-frontier projection (4 layers)
future loop replan rules show|set --goal G [--rule-ids R1,R2,...]   # G13 replan policy table
future loop run --goal G --agent-id A [--model M] [--thinking-level L] [--max-turns N] [--max-turn-secs N] [--lease-secs N] [--force-workspace]
future loop backup --goal G [--list | --restore DIR]
future loop serve-status [--port 8791]                  # browser dashboard
future loop models                                      # same catalog as `future models`
future loop commands [--format json]                    # grouped operator command reference
```

### Full command surface (`future loop registry`, `future loop commands`)

`future loop commands` renders the same registry grouped by operator journey
(Start here / Daily operator / Loop driver / Setup & automation / Maintainer &
adapter) — the fastest way to rediscover a command. Notable extras beyond the
workflow commands:

- **todo graph**: `task-graph` (dependency DAG, fails closed on unknown refs);
  `lease claim|renew|release|expire|status`.
- **gates & replan**: `gate resolve`; `replan ack|obligations`;
  `replan rules show|set` (G13 ordered disposition→decision policy table).
- **goal frontier (G13)**: `frontier show --goal G` — the composed frontier
  projection + outcome segments + replan rule decision + terminal judgement
  + semantic history (see the Goal frontier section).
- **agents**: `agent list|register|onboard` (onboard declares the `--workspace`
  path set — the workspace guard refuses conflicting claims — plus
  `--recipe NAME` to apply a named recipe); `agent
  contract|recipe|succession|collective` (G12 multi-agent topology, see
  below); `scope`; `lane`; `supervisor propose|receipt|events`.
- **quota/scheduler**: `quota should-run|usage|spend|decisions`;
  `scheduler tick|show|record-host-failure|ack|liveness`.
  - Every quota decision carries a machine-readable `reason_code` alongside
    the prose reason (stable snake_case wire codes — consumers must NOT
    substring-match prose). `quota decisions --goal G [--limit N]` projects
    the decision receipts (decision_summary read model).
  - `scheduler liveness --goal G [--threshold-secs N]` (default 2h) answers
    "is the host automation itself alive?": every `scheduler tick` lands a
    heartbeat; silence beyond the threshold records a liveness alert and the
    `attention` projection escalates the goal until a fresh tick recovers it
    (re-alert cooldown 1h). This is the overnight-unattended-goal safety net.
  - `scheduler tick` also projects the monitor poll plan (due / waiting /
    stalled per open monitor) and reschedules monitors cadence-aware — a
    `--cadence 1h` monitor reschedules 1h out, not on the fixed no-change
    backoff.
- **ops**: `diagnose [--format json]`; `doctor`; `runs
  history|compact|retention|stale`; `backup`; `evidence-log`; `todo-event`;
  `turn`; `privacy`; `store verify|migrate|bridge`; `authority`; `profile`;
  `version`. `store verify --goal G` checks ledger integrity AND run-history
  index drift (read-model self-diagnosis); `--repair` rebuilds a drifted
  index non-destructively (the event ledger is never rewritten) and records a
  `ProjectionRepaired` audit event. Separately, every should-run decision is
  annotated with `decision_freshness` (how stale the read model it decided
  against was).
- **work-items & handoff**: `attention`; `inbox`; `handoff --write`;
  `delivery status|record|followthrough` (see §9).
- **benchmark/replay/canary**: `benchmark protocol|run|ledger`; `replay
  record|run`; `canary smoke [--profile
  core-control-plane|release-gate|premerge]`; `canary
  premerge [--json]` — the fast deterministic CI merge gate: isolated
  temporary state root, seeded fixture goal, gate verdict from the smoke run.
  CI runs it as the `loop-canary` job whenever loop code changes; run it
  locally before opening a loop PR (plain `canary smoke` for a quick check).
- **coverage ratchet (repo hygiene)**: `scripts/coverage.sh [--check]`
  measures per-crate coverage and the `coverage-ratchet` CI job enforces the
  checked-in floors (`scripts/coverage-baseline.json`) — line coverage may
  only go UP. A drop fails CI unless the PR itself edits the floor file;
  that diff IS the explicit ratchet-down approval.
