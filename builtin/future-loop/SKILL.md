---
version: 3.0.3
name: future-loop
description: FutureOS loop control plane — manage long-running goals, todo lists, human gates, monitors, and validated completion via the loop control plane. Use when the user wants a long-lived/multi-step/cross-session task tracked as a goal, asks to "keep working on X", "track this issue", "run this overnight", needs progress/status of ongoing agent work, or starts a message with "/future-loop" (treat everything after the prefix as the goal).
allowed-tools: Bash(future-loop:*)
category: tools
---

# Loop Control Plane

`future loop` turns a conversation into a durable, reviewable long-running goal:
objective, todos, gates, evidence, and completion persist outside the chat.
The agent executes one bounded turn at a time; a deterministic kernel offers
the next runnable todo plus signals (it is a kanban, not a decision-maker).

## When to use

Load this skill when the user:
- starts a message with **`/future-loop <task>`**: treat the text after the
  prefix as a NEW long-running goal — create the goal and drive it to
  completion (do NOT treat it as a one-shot request);
- wants a **long-lived / multi-step / cross-session** task ("keep working on X",
  "track this issue", "run this overnight");
- asks about **status or progress** of ongoing agent work;
- needs a decision point surfaced ("waiting for my approval" scenarios);
- wants recurring observation of external state (CI, PR, file appearing).

For one-shot conversations, answer normally — no goal needed.

## Prerequisites

- Everything runs through the unified CLI: **`future loop <cmd>`** (an existing
  install: `command -v future`; also `~/.local/bin/future`, `~/bin/future`).
  State lives in the project: `<cwd>/.future/loop/` (run from the project dir,
  or pass `--cwd`). Add `.future/loop/` to the project `.gitignore`.
- `future loop run` needs the agent server: `future agent` (gRPC 127.0.0.1:50051).
  Probe with `future models`. Override the address with
  `FUTURE_LOOP_AGENT_ADDR` (e.g. a mock for tests).
- **Binary freshness**: new features need a current binary. Probe:
  `strings $(command -v future) | grep -c "max-turn-secs"` — `≥1` = current;
  `0` = stale, rebuild. A stale binary also fails to read ledgers written by
  newer binaries ("read ledger"): update it, don't fight it.

## Core model

```
goal ── todos (advancement / gate / monitor) ── kernel offers a runnable todo + signals
        │            │                                          │
        └── evidence + acceptance contracts + verify gates      └── writeback → next offer
```

- **The agent decides; the kernel provides the kanban.** Each turn the kernel
  offers a runnable todo plus *signals* (failure count, outcome-floor streak,
  oscillation pattern, monitor stall, rate-limit) in the delivery reason. The
  agent reads the signals and decides — keep going, supersede, re-split, or
  ask the operator. The kernel enforces only the **correctness floor** (verify
  gates, acceptance contracts, non-empty evidence, terminal closure), never a
  policy rule like "you are stuck → replan".
- **Terminal = validated closure**: todos done or superseded, closure intent
  declared, no acceptance gaps, no pending deferred work. Not "all todos
  checked" alone.

## Agent decision guide (you decide, the kernel doesn't)

The kernel surfaces signals in the delivery reason — it does NOT force a
replan. Read the signal, then decide:

| Signal (in the delivery reason) | Meaning | What YOU should do |
|---|---|---|
| `repair attempt N for todo X` | This todo has failed before | Re-examine the failure; if the approach is wrong, `supersede` + split; if it was a transient infra error, keep going |
| `[signal: todo X has N failed attempt(s)]` | N previous failures | Supersede / re-split / ask the operator — do NOT blindly retry the same todo |
| `[signal: outcome floor: N consecutive turns without a material outcome]` | You are spinning without landing an artifact | Change strategy or supersede a stale todo |
| `[signal: oscillation … A→V→A→V]` | Deliveries flip-flop accept/reject | Change the validator, or split the todo so the gate is simpler |
| `monitor X stalled (N consecutive no-change polls)` | The watch lane is dead | watch-lane expiry / write a blocker / supersede the monitor |
| `rate-limited (HTTP 429)` | Engine throttled — NOT your fault | Back off, then resume; never count it as a science failure |
| `[signal: N turns with no write-class tool]` | You may be stuck in a silent reasoning loop | Restart with a fresh session (context replays from the ledger) |

The kernel NEVER converts these signals into a forced `replan`. If the same
signal repeats across turns, it is YOUR call to `supersede` / split / ask — the
loop keeps offering the runnable todo until you change the plan. A todo that
keeps failing is a **plan problem**, not a kernel problem: change the plan.

## Workflow

### 1. Inspect first

```bash
future loop status
```

If the objective already exists, continue it — never silently create a
duplicate.

### 2. Confirm the plan

Present steps + model + thinking level, and get confirmation before creating
anything. Default to the current session's model; `future models` lists
options. Skip confirmation only when the user's opening message already
contains the full objective AND explicit operating constraints.

### 3. Create the goal and todos

```bash
future loop goal init --objective "..." --cwd DIR [--goal-id ID]
future loop todo add --goal G --text "..." --priority P0 [--blocks T] [--verify "cmd"] [--acceptance "tok1,tok2"]
```

- Capture todo ids from the `todo add` output; verify wiring with
  `status --goal G`.
- **Dependencies**: `--blocks` keeps a todo out of the frontier until
  predecessors are done/superseded. The final acceptance todo MUST `--blocks`
  every implementation todo, or it can run while they are still stubs.
- **Hard checks beat conventions** — attach them at creation time:
  - `--verify "cmd"`: the kernel runs the command after each turn; only exit 0
    completes the todo (bounded by `--max-validation-attempts`). Attach
    `cargo check`/artifact-existence gates to every delivery todo.
  - `--acceptance "tok1,tok2"`: completion evidence must contain EVERY token
    (case-insensitive), e.g. a platform attempt id — the hard form of "done ≠
    delivered".
  - Completion itself requires **non-empty `--evidence`** (what actually
    landed: ids, paths, outputs, measurements) AND a **declared closure
    intent** — `--no-follow-up` or `--successor T2` is mandatory on every
    agent completion (the kernel enforces the completion policy). `--force`
    is the explicit operator override for mechanical closeouts.
- **User gates** are real gates, not prose:
  `future loop todo add --goal G --role user --class user_gate --text "..." --gate-question "..."`.
  (`--text` is required; `--gate-question` defaults to it.)
  Any open gate freezes all work; resolve with `gate resolve`, never
  `todo complete`.

### 4. Run — one turn at a time

```bash
future loop run --goal G --agent-id <unique-name> --model M --thinking-level L --max-turns 1
```

- `--agent-id` is mandatory and is the only mutual-exclusion mechanism: a run
  sees its OWN leased todos as runnable; two runs sharing one id double-execute.
  Unique name per parallel worker (`<host>-<task>`).
- `--max-turn-secs N` caps the turn wall-clock; timeout stops gracefully and
  context replays on relaunch. Relaunch with the same agent-id to continue.
- **Mid-turn steering**: `todo update --text` on the todo a worker is
  executing is delivered into the running session (~10s poll) — the primary
  tool for correcting a drifting or stuck worker.
- **Session retention** (resume-vs-fresh is YOUR call, never the kernel's):
  the kernel records WHY the last run was interrupted and keeps the session id
  on disk; you decide whether to resume. `--session-policy auto` (default)
  resumes only when the interruption was infra-recoverable (e.g. HTTP 429 —
  LLM state intact); `resume` always resumes the retained session; `fresh`
  always starts over. `--resume-session <id>` pins an exact session. A
  retained session that no longer exists falls back to fresh automatically.
- **Monitor live progress** via `.future/loop/runs/<run_id>.live.jsonl`
  (tee'd per run), not via hand-managed log files.
- `run` stops when: validated closure (terminal), a user gate opens, a blocker
  waits, or max-turns / max-turn-secs is reached. Non-zero exit = budget hit;
  rerun if open todos remain.

### 5. Report, reflect, steer

After each turn: report (todo, cost, new status); reflect — is the objective
still right, the decomposition optimal, new risks needing a gate/monitor?
Apply routine adjustments yourself (`todo add` / `supersede` / `update`).
Stop and ask the user only for risky/irreversible changes or user-only
decisions.

### 6. Close out

- Final deliverable todo copies artifacts to the project root (`cp`, not `mv`),
  blocked behind the producing todos.
- Completion is validated closure — one final run confirms `terminal`.

## Key semantics

- **Evidence floor**: advancement todos refuse empty `--evidence`.
- **Acceptance contracts**: declared tokens must appear in the evidence.
- **Lease liveness**: leases record the holder's pid; a killed run's leases
  are auto-reclaimed on the next claim (no manual `lease release` dance).
  Pre-liveness ledgers (no pid) keep the old hard error.
- **Workspace guard**: agents declare workspace paths; conflicting claims
  degrade to serial unless `--force-workspace`.
- **Delivery ≠ verified**: completion records a delivery in `delivered` state;
  resolve via `delivery record` (verified/failed/rework); unverified deliveries
  auto-derive a follow-up todo after 3 turns.
- **TurnNoProgress**: a turn with no write-tool activity for 15 minutes is
  recorded in the ledger; steer the worker via `todo update --text`, then
  kill + relaunch if it stays idle.
- **Monitors**: not-due monitors must NOT be polled; due time comes from
  `--cadence`/`--defer-secs N`; `--resume-when N` (numeric) defers for real,
  text values are hints without a deadline.
- **Gates freeze everything** while any user gate is open; user_actions
  (non-blocking human to-dos) surface in the user channel but never freeze
  the agent — reserve user_gate for genuine user decisions.
- **CLI strictness**: unknown flags are hard errors; unknown `--class` /
  `--priority` / role-class combo values are hard errors; every subcommand
  renders usage on `--help`; all read-only commands accept `--format json`
  (alias `--json`); a non-numeric `--resume-when` warns it has no deadline.
- **Completion is idempotent**: re-completing an already-done todo is a no-op
  (no duplicate ledger events); completing a superseded todo errors.
- **Ledger forward-compat**: unknown event kinds are skipped with a diagnostic
  (a newer binary wrote them) — only structural errors fail a read.

## Multi-agent (one goal, several workers)

```bash
future loop agent contract set --goal G --contract '<json>' | --contract-file contract.json   # peers, backup_for, handoff rules
future loop agent recipe add --goal G --name N --capabilities c1,c2 --workspace p --priority P0
future loop agent onboard --goal G --agent-id A --recipe N
future loop agent succession show --goal G                     # backup promotion status
future loop agent collective show --goal G [--format json]     # wake roster + turn ledger
```

- Contract `capabilities` on peers are **descriptive strings only** — nothing
  in the kernel enforces them.
- Role succession: a primary agent offline past the threshold auto-promotes
  its backup (event + attention alert).
- Declared workspaces feed the workspace guard.

## Orchestration patterns

1. **Orchestrator-only dangerous actions.** Anything consuming a limited
   external resource (submission quotas, paid calls, irrecoverable deletes)
   must not be callable by workers — a worker's failed attempt may still
   consume the resource. Workers finalize artifacts and write a signal file;
   only the orchestrator executes the capped action.
2. **Shared project memory as broadcast channel.** Instruct workers to re-read
   the project memory file at turn start; use it for cross-worker discoveries.
3. **Steer by updating todo text, anytime.**
4. **Watch artifacts, not just loop status.** Long compute runs via nohup +
   checkpoint files; track output mtimes.
5. **Wrap-up belongs to the orchestrator.** The final/validation todo must be
   `--blocks`-chained behind everything, or do the wrap-up outside the loop.

## Drive playbook (hard-won rules)

1. **Empty closures are the #1 failure.** Every delivery todo gets `--verify`
   or `--acceptance` (or both); evidence names the external observable.
2. **Budget external resources in the goal doc** (e.g. "submissions: 10 per
   challenge") and update a shared ledger file every turn.
3. **A large todo that 2+ worker generations close with no artifacts is a
   signal to split, not retry.** Split into sections with ONE concrete
   artifact + `--verify` each; chain an assembler todo behind all of them
   (the assembler gets a `--verify` too).
4. **Dead processes:** leases auto-reclaim via pid probe; if a claim is still
   refused, `agent list` to find the stale holder and `lease release`.
5. **Dead time is the orchestrator's fault.** Relaunch the moment a turn exits.
   Steer a write-idle worker once via `todo update --text`, then kill +
   relaunch. Escalate to a stronger model when a todo has produced NO write
   artifacts for 2 consecutive turns.
6. **Repo delivery discipline.** Deliver code waves as small PRs: cherry-pick
   ONE item commit onto the freshest main per PR; local gate = fmt + clippy
   + targeted tests; `gh pr create` + `gh pr merge --squash --auto`; when
   GitHub reports BEHIND, merge main into the PR branch and push (auto-merge
   fires). CodeQL js-ts jobs occasionally queue-stuck — an empty commit
   retriggers them.

## Command reference

```bash
future loop status [--goal G] [--format json]
future loop goal init --objective "..." --cwd DIR [--goal-id G]
future loop todo add --goal G --text "..." [--priority P0|P1|P2] [--blocks T] [--verify "cmd"] [--acceptance "a,b"]
future loop todo update --goal G --todo-id T [--text ...] [--priority ...] [--blocks T] [--acceptance ...]
future loop todo complete --goal G --todo-id T --no-follow-up | --successor T2 [--evidence "..."] [--force]
future loop todo supersede --goal G --todo-id T --reason "..."
future loop gate resolve --goal G --todo-id T --decision "..." [--note "..."]
future loop lease claim|renew|release|expire|status --goal G ...
future loop run --goal G --agent-id A [--model M] [--thinking-level L] [--max-turns N] [--max-turn-secs N] [--session-policy auto|fresh|resume] [--resume-session ID]
future loop agent onboard|list|contract|recipe|succession|collective ...
future loop scope --goal G --agent-id A        # identity-scoped runnable frontier
future loop lane --goal G --agent-id A         # lane recommendation
future loop supervisor --goal G ...            # supervisor proposal/receipt events
future loop models [--format json]             # models available from the agent
future loop frontier show --goal G [--format json]        # outcome segments / replan rules / semantic history / terminal
future loop delivery status|record --goal G               # post-delivery closure
future loop quota should-run|usage|spend|decisions --goal G
future loop scheduler tick|show|record-host-failure|ack|liveness
future loop diagnose|doctor|history|turn|todo-event|evidence-log|runs|backup|store|privacy|attention|inbox
future loop commands [--format json]                      # grouped operator view
future loop canary|task-graph|replan|authority|profile|backfill|heartbeat-prompt|worker-bridge|version|registry
```

Full surface: `future loop registry`.

## Ops & observability surface (one-liners)

```bash
future loop goal cancel|delete --goal G               # cancel ends the goal; delete removes its state
future loop todo claim --goal G --todo-id T --agent-id A   # manual claim (run claims automatically)
future loop todo archive --goal G --todo-id T         # archive a finished todo
future loop replan ack|obligations --goal G             # replan dispositions create obligations; ack clears them
future loop runs history|compact|index|retention|stale --goal G   # run-record lifecycle
future loop store ...                                 # schema migration / ledger integrity / read-model repair
future loop backfill --goal G                         # re-import markdown state into the event ledger
future loop diagnose --goal G                         # decision / gaps / runs diagnostics
future loop doctor                                    # install health check (ledger smoke + agent probe)
future loop history --goal G                          # goal run history
future loop turn --goal G --todo-id T                 # per-turn envelope for a todo
future loop todo-event --goal G --todo-id T           # event history of one todo
future loop evidence-log --goal G --todo-id T         # full evidence trail
future loop attention [--all]                         # attention-queue projection
future loop inbox --project DIR                          # operator inbox urgency
future loop privacy --goal G                          # privacy-graded projection
future loop heartbeat-prompt --goal G                 # per-turn re-entry packet
future loop worker-bridge                             # run the worker bridge
future loop authority --goal G ...                    # set authority declaration
future loop profile --goal G ...                      # set execution profile
future loop canary smoke [--profile core-control-plane|release-gate|premerge] | canary premerge   # smoke / CI gate
```
