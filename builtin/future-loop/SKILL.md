---
version: 3.5.0
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
  `strings $(command -v future) | grep -c "max-incomplete-retries"` — `≥1` = current;
  `0` = stale, rebuild. A stale binary also fails to read ledgers written by
  newer binaries ("read ledger"): update it, don't fight it.

## Core model

```
goal ── todos (advancement / gate / monitor / coordination) ── kernel offers a runnable todo + signals
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
| `repair attempt N for todo X` / `[signal: todo X has N failed attempt(s)]` | This todo has failed N times | Re-examine the failure; if the approach is wrong, `supersede` + split; if it was a transient infra error, keep going |
| `[signal: outcome floor: N consecutive turns without a material outcome]` | You are spinning without landing an artifact | Change strategy or supersede a stale todo |
| `[signal: oscillation … A→V→A→V]` | Deliveries flip-flop accept/reject | Change the validator, or split the todo so the gate is simpler |
| `monitor X stalled (N consecutive no-change polls)` | The watch lane is dead | watch-lane expiry / write a blocker / supersede the monitor |
| `rate-limited (HTTP 429)` | Engine throttled — NOT your fault | Back off, then resume; never count it as a science failure |
| `[signal: N turns with no write-class tool]` | You may be stuck in a silent reasoning loop | Restart with a fresh session (context replays from the ledger) |

**The turn envelope also ends with a `Prior activity:` block** (goal memory,
separate from the delivery-reason signals above):

- `prior attempts on this todo: N failed; last = <classification>` — the
  classification is the failure *kind*, not just a count. Read it to decide
  retry vs fix vs supersede:
  - `infra-recoverable (retry is safe)` — HTTP 429 / disconnect / stream gap;
    retry, never a science failure.
  - `verify-gate rejected the output` — the `--verify` command failed; fix the
    gate or supersede the todo (retrying the same turn is wasted).
  - `hard error (no recoverable infra cause)` — treat as a science failure.
- `recent goal history:` — the last few turn outcomes (todo completed / run
  landed / gate resolved / …) so you don't re-derive context the goal already
  established.

The kernel NEVER converts these signals into a forced `replan`. If the same
signal repeats across turns, it is YOUR call to `supersede` / split / ask — the
loop keeps offering the runnable todo until you change the plan. A todo that
keeps failing is a **plan problem**, not a kernel problem: change the plan.

## Workflow

### 1. Inspect first

```bash
future loop status
```

Register your session once per goal so workers can push intervention reports
to you (no more polling `status` to *discover* gate/completion/failure
signals):

```bash
future loop supervisor register --goal G --session-id <your-agent-session>
```

`<your-agent-session>` is the `Current session ID` line in your own system
prompt — you are self-aware of it, so copy it verbatim. Re-register whenever
you continue from a NEW session (the id is per-session and dies with it).

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
future loop todo add --goal G --text "..." --priority P0 [--blocks T] [--verify "cmd"] [--acceptance "tok1,tok2"] [--owner A] [--class coordination]
```

- Capture todo ids from the `todo add` output; verify wiring with
  `status --goal G`.
- **Dependencies**: `--blocks` keeps a todo out of the frontier until
  predecessors are done/superseded. The final acceptance todo MUST `--blocks`
  every implementation todo, or it can run while they are still stubs.
- **Coordination todos** (`--class coordination`): the goal's own parent /
  summary / final-validation todos are bookkeeping, NOT worker work. Mark
  them `coordination` so they never enter a worker's runnable frontier — the
  orchestrator completes them directly. Without this, a worker's `run`
  first-claim-wins them once their lease lapses ("the worker steals the
  orchestrator's summary todo").
- **Owner scope** (`--owner A`): declare *which agent this todo is for*. An
  owner-scoped todo is only runnable by that agent — and the assignment
  survives lease expiry (a lease releases the lock, never the assignment).
  `None` owner = shared pool (first-claim-wins). Use it to hand work to a
  specific worker so workers don't steal each other's slices.
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
- **Incomplete turns auto-retry**: a turn ending `incomplete` (truncated model
  stream — an infra event, never a science failure) is retried with a CONTINUE
  note in the next envelope, bounded by `--max-incomplete-retries N` (default
  3, `0` disables). Exhausting the bound stops the run; see Key semantics.
- **Mid-turn steering (interrupt)**: `supervisor steer --goal G --instruction "..."`
  aborts the in-flight run (a real interrupt) and the next turn follows the
  instruction. `todo update --text` remains the *non-interrupting* correction
  (picked up at the next turn).
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
- **Incomplete ≠ failure**: a turn ending `incomplete` (truncated model
  stream) never consumes the repair budget; `future loop run` auto-retries it
  with a CONTINUE note, bounded by `--max-incomplete-retries` (default 3).
- **TurnNoProgress**: a turn with no write-tool activity for 15 minutes is
  recorded in the ledger; interrupt a write-idle worker via
  `supervisor steer --goal G --instruction "..."`, then kill + relaunch if it
  stays idle.
- **Monitors**: not-due monitors must NOT be polled; due time comes from
  `--cadence`/`--defer-secs N`; `--resume-when N` (numeric) defers for real,
  text values are hints without a deadline.
- **Gates freeze everything** while any user gate is open; user_actions
  (non-blocking human to-dos) surface in the user channel but never freeze
  the agent — reserve user_gate for genuine user decisions.
- **Coordination vs owner (anti-steal)**: `coordination` todos (goal
  bookkeeping) and `owner`-scoped todos never enter the shared worker
  frontier — the first is never agent work, the second is single-agent work.
  Both prevent the "worker `run` auto-claims a todo that isn't theirs" failure
  mode; keep the shared pool (`advancement` + no `--owner`) for genuinely
  first-claim-wins work so backup takeover / load-balancing still work.
- **CLI strictness**: unknown flags are hard errors; unknown `--class` /
  `--priority` / role-class combo values are hard errors; every subcommand
  renders usage on `--help`; all read-only commands accept `--format json`
  (alias `--json`); a non-numeric `--resume-when` warns it has no deadline.
- **Completion is idempotent**: re-completing an already-done todo is a no-op
  (no duplicate ledger events); completing a superseded todo errors.

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
3. **Steer by updating todo text, anytime** (picked up at the next turn);
   **interrupt a running worker** with `supervisor steer --goal G
   --instruction "..."` (aborts the in-flight turn, then keeps running).
   **Stop a worker for good** (including nohup/setsid ones) with
   `worker stop --goal G --agent-id A` — unlike steer, the worker exits its
   run loop at the next turn boundary. `worker list` shows each worker's
   status (`running` = in-flight turn, `ended` = session exists but idle,
   `idle` = registered but never ran).
4. **Watch artifacts, not just loop status.** Long compute runs via nohup +
   checkpoint files; track output mtimes.
5. **Wrap-up belongs to the orchestrator.** The final/validation todo must be
   `--blocks`-chained behind everything — and mark it `--class coordination`
   so a worker's `run` can never auto-claim it once its lease lapses. Give
   each worker's slice `--owner <agent-id>` so parallel workers can't steal
   each other's work either; leave only genuinely shared work unowned.
6. **Workers report to you — you do not poll `status` for intervention
   signals.** Once you `supervisor register --goal G --session-id
   <your-session>`, a worker enqueues a note into YOUR session at each
   intervention-worthy state transition: a user gate opens, a todo completes,
   or a todo fails on a science/hard error. Enqueueing an idle supervisor
   session starts a new turn, so these reports wake you — you react to them
   instead of polling `status`.

   The kernel ALSO reports **infra stops** (a worker that died before reaching
   a writeback — its run never produced a completion/failure record, so the
   two reports above never fire). Dedup key `infra_stopped:<todo>:<kind>`:
   - `transport` — a gRPC stream error (h2 reset / non-gap disconnect) that
     propagated out of the turn before writeback.
   - `timeout` — the turn outlived `--max-turn-secs`.
   - `incomplete_budget` — the turn kept ending `incomplete` and exhausted
     `--max-incomplete-retries`.
   - `host_died` — the worker's process is gone (SIGKILL / crash / host
     failure) with no release. This one is NOT reported at the turn boundary
     (a dead process executes no code): the periodic `scheduler tick` detects
     the orphaned lease (dead holder pid) and pushes the note, so keep a
     scheduler tick running on the goal's cadence or you only learn of the
     dead worker on your next `status` poll.
   React the same way as a science failure: relaunch (the todo stays
   runnable; infra failures never consume the repair budget).

   What remains **pull, not push** (this is the loop's one-turn-per-process
   model, not a polling gap):
   - **Driving the next turn.** There is no long-lived worker — every turn is
     a `future loop run` you relaunch. A report tells you a decision is due;
     the work itself still runs because you call `run`.
   - **Confirming closure.** `terminal` (validated closure) has no dedicated
     report — it is decided inside a `run`'s decide step. The last todo's
     completion report says "closure pending", so run once more to confirm
     `terminal` and stop.

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
   refused, `agent list` to find the stale holder and `lease release`. A
   `holder dead` marker on a todo means its lease-holding process is gone — it
   does NOT mean the todo failed; a completed todo can still show a stale
   orphaned lease, and that is harmless (the lease auto-reclaims on the next
   claim).
5. **Dead time is the orchestrator's fault.** Relaunch the moment a turn exits.
   Interrupt a write-idle worker once via `supervisor steer --goal G
   --instruction "..."`; if the worker must not continue, stop it with
   `worker stop --goal G --agent-id A` (clean in-band stop: the run client
   exits at the next turn boundary, the session is retained and resumable;
   `--delete` also reclaims the session), then relaunch when ready. Escalate
   to a stronger model when a todo has produced NO write artifacts for 2
   consecutive turns.
   **Do not trust the push channel 100%.** Infra-stop reports are best-effort
   (they ride a gRPC prompt and can be lost if the agent is down), and the
   orchestrator's own session can die too. Keep a light fallback: every few
   minutes, confirm each claimed todo still maps to a live process and has a
   recent run record; treat a claimed-but-silent todo as a dead worker.
6. **Repo delivery discipline.** Deliver code waves as small PRs: cherry-pick
   ONE item commit onto the freshest main per PR; local gate = fmt + clippy
   + targeted tests; `gh pr create` + `gh pr merge --squash --auto`; when
   GitHub reports BEHIND, merge main into the PR branch and push (auto-merge
   fires).

## Command reference

```bash
future loop status [--goal G] [--format json]
future loop goal init --objective "..." --cwd DIR [--goal-id G]
future loop todo add --goal G --text "..." [--priority P0|P1|P2] [--blocks T] [--verify "cmd"] [--acceptance "a,b"] [--owner A] [--class coordination]
future loop todo update --goal G --todo-id T [--text ...] [--priority ...] [--blocks T] [--acceptance ...] [--owner A]
future loop todo complete --goal G --todo-id T --no-follow-up | --successor T2 [--evidence "..."] [--force]
future loop todo supersede --goal G --todo-id T --reason "..."
future loop gate resolve --goal G --todo-id T --decision "..." [--note "..."]
future loop lease claim|renew|release|expire|status --goal G ...
future loop run --goal G --agent-id A [--model M] [--thinking-level L] [--max-turns N] [--max-turn-secs N] [--max-incomplete-retries N] [--session-policy auto|fresh|resume] [--resume-session ID]
future loop agent onboard|list|contract|recipe|succession|collective ...
future loop scope --goal G --agent-id A        # identity-scoped runnable frontier
future loop lane --goal G --agent-id A         # lane recommendation
future loop supervisor register|steer|propose|receipt|events --goal G ...   # bind your session / interrupt a worker / proposal-receipt events
future loop worker list --goal G [--format json] # registered workers + backing session + running/ended/idle
future loop worker stop --goal G --agent-id A | --all [--delete]  # stop worker(s) cleanly (ledger signal + gRPC abort)
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
future loop worker list|stop --goal G                 # worker observability + clean stop (see Orchestration patterns)
future loop authority --goal G ...                    # set authority declaration
future loop profile --goal G ...                      # set execution profile
future loop canary smoke [--profile core-control-plane|release-gate|premerge] | canary premerge   # smoke / CI gate
```
