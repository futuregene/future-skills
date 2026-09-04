---
version: 3.13.0
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
  State lives in the project: `<cwd>/.future/loop/`, where `<cwd>` is the
  directory the command is RUN from — there is no `--cwd` flag that relocates
  the ledger; the state root is the process cwd, or `FUTURE_LOOP_ROOT` when
  set (`root_dir()` in `orchestration/loop/src/console.rs`). Run every
  `future loop` command from the project dir, and add `.future/loop/` to the
  project `.gitignore`.
- `future loop run` needs the agent server: `future agent` (gRPC 127.0.0.1:50051).
  Probe with `future models`. Override the address with
  `FUTURE_LOOP_AGENT_ADDR` (e.g. a mock for tests).
- **Binary freshness**: new features need a current binary. Probe with a
  string that only a recent build embeds — the detached-run fix (PR #473)
  added `verify gate rejected (exit …)` to the supervisor failure report, so
  it exists only in binaries built from that fix onward:
  `strings $(command -v future) | grep -c "verify gate rejected (exit"` —
  `≥1` = includes the detached-run + verify-fail-report + token-accounting
  fixes; `0` = stale, rebuild. Do NOT rely on the older `max-incomplete-retries`
  probe: it only confirms one feature flag exists and passes even on a binary
  that still ships the detached-run re-exec bug. A stale binary also fails to
  read ledgers written by newer binaries ("read ledger"): update it, don't fight it.

## Core model

```
goal ── todos (advancement / gate / monitor / coordination) ── kernel offers a runnable todo + signals
        │            │                                          │
        └── evidence + acceptance contracts + verify gates      └── writeback → next offer
```

- **The agent decides; the kernel provides the kanban.** (Design principles:
  `orchestration/loop/ARCHITECTURE.md` in the future-os repo — this skill is
  the driving manual, not the architecture doc.) Each turn the kernel offers
  a runnable todo plus *signals* (failure count, outcome-floor streak,
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

| Signal (delivery reason / envelope `signals:` block) | Meaning | What YOU should do |
|---|---|---|
| `repair attempt N for todo X` / `[signal: todo X has N failed attempt(s)]` | This todo has failed N times | Re-examine the failure; if the approach is wrong, `supersede` + split; if it was a transient infra error, keep going |
| `[signal: outcome floor: N consecutive turns without a material outcome]` | You are spinning without landing an artifact | Change strategy or supersede a stale todo |
| `[signal: oscillation … A→V→A→V]` | Deliveries flip-flop accept/reject | Change the validator, or split the todo so the gate is simpler |
| `monitor X stalled (N consecutive no-change polls)` | The watch lane is dead | watch-lane expiry / write a blocker / supersede the monitor |
| `rate-limited (HTTP 429)` | Engine throttled — NOT your fault | Back off, then resume; never count it as a science failure |
| `[signal: N turns with no write-class tool]` | You may be stuck in a silent reasoning loop | Restart with a fresh session (context replays from the ledger) |

**The turn envelope also carries goal memory and signals.** A `Prior
activity:` block (goal memory):

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
- `signals: [signal: …] …` — the same advisories the delivery reason carries
  (failure count, outcome floor, oscillation, no-progress), recomputed from
  the ledger for THIS todo, so you see them even without the packet.
- `Upstream evidence:` — for a fan-in (synthesis) todo, each done/superseded
  `--blocks` predecessor contributes a **truncated evidence snippet** (the
  combined block is capped at ~1200 chars, each predecessor's evidence is
  itself capped at 4000 chars when stored, and the supervisor completion
  report shows only ~300 chars). This is a *pointer/summary*, NOT a full
  hand-off of the predecessor's work. For real cross-worker knowledge
  transfer, the worker MUST write a durable artifact (e.g. `work/rN-*.md`)
  and you must name that file path in the successor todo's text (`Read
  work/rN-w2.md …`) so the successor *reads the file* — never rely on the
  envelope alone to carry conclusions between rounds. Wire the dependency or
  the reader sees nothing.

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
future loop goal init --objective "..." [--goal-id ID]
future loop todo add --goal G --text "..." --priority P0 [--blocks T] [--verify "cmd"] [--acceptance "tok1,tok2"] [--owner A] [--class coordination]
```

- `goal init` registers the goal in the ledger at the state root of the
  PROCESS cwd (`<cwd>/.future/loop/`, or `FUTURE_LOOP_ROOT`) — run it from
  the project dir. Its optional `--cwd DIR` only records the goal's project
  directory (the anchor for agent sessions, `GOAL.md`, and liveness inbox
  alerts); it does NOT relocate the ledger.
- Capture todo ids from the `todo add` output; verify wiring with
  `status --goal G`.
- **`goal init` auto-adds a bootstrap todo** — a P1 advancement with
  `action_kind=onboarding_connection_validation` ("Run `future loop status`
  for this goal … or declare an explicit no-follow-up rationale"). This is
  expected, not a stray todo: it forces the first turn to prove the
  loop↔agent connection before real work. Either complete it (run `status`,
  record the goal count as evidence) or supersede it with an explicit
  no-follow-up — never treat it as a mystery. Re-running `goal init` on an
  existing goal does NOT duplicate it.
- **Dependencies**: `--blocks` keeps a todo out of the frontier until
  predecessors are done/superseded. The final acceptance todo MUST `--blocks`
  every implementation todo, or it can run while they are still stubs.
- **Coordination todos** (`--class coordination`): the goal's own parent /
  summary / final-validation todos are bookkeeping, NOT worker work. Mark
  them `coordination` so they never enter a worker's runnable frontier — the
  orchestrator completes them directly. Without this, a worker's `run`
  first-claim-wins them once their lease lapses ("the worker steals the
  orchestrator's summary todo"). **`--class` is immutable after creation**
  (`todo update` rejects the flag): a mis-classed todo is fixed by
  `todo supersede` + re-`todo add` with the right class/owner — never in
  place.
- **Owner scope** (`--owner A`): declare *which agent this todo is for*. An
  owner-scoped todo is only runnable by that agent — and the assignment
  survives lease expiry (a lease releases the lock, never the assignment).
  `None` owner = shared pool (first-claim-wins). Use it to hand work to a
  specific worker so workers don't steal each other's slices.
- **Hard checks beat conventions** — attach them at creation time:
  - `--verify "cmd"`: the kernel runs the command after each *turn* (in the
    `run` boundary); only exit 0 lets that turn's todo complete (bounded by
    `--max-validation-attempts`). It is a *machine-checkable* gate for
    deterministic deliverables (`cargo check`, `Test-Path report.md`).
    **Do NOT hang `--verify` on exploratory todos** — a research/report todo
    produces files whose *correctness* the kernel cannot judge; only YOU (the
    orchestrator) can, by reading the artifact. Note the deliberate asymmetry:
    `--verify` fires at the `run` turn boundary, NOT on a manual
    `todo complete` — that manual path is YOUR judgement call overriding the
    machine gate, which is exactly what you want when you (not a shell script)
    decide an exploratory result is good enough. `--force` is the explicit
    escape hatch either way.
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
  An open gate **freezes the gated work** (its dependents) and pushes a
  decision report to the registered supervisor; gate-independent work keeps
  running (escalate-not-freeze — ARCHITECTURE.md "Workers escalate"). Resolve
  with `gate resolve`, never `todo complete`.

### 4. Run — one turn at a time, detached by default

```bash
future loop run --goal G --agent-id <unique-name> --model M --thinking-level L --max-turns 1
# ⏏ detached run pid=... — log <root>/detached/<goal>/<agent-id>-<ts>.log
```

- **`run` detaches ITSELF by default** (ARCHITECTURE.md "Runs are detached"
  is now kernel-enforced): the parent prints the child pid and returns
  immediately; the child runs the turn loop with its own log under
  `<root>/detached/<goal>/`. Tail the log with
  `worker tail --goal G --agent-id A` (below) — not by reading the file.
- **⚠ Detached mode has a known re-exec bug when the only installed entry
  point is the unified `future` binary.** The detached child re-execs
  `current_exe` but (before the fix) forgot to re-prepend the `loop` group,
  so `future loop run …` spawned `future run …` — the unrelated one-shot
  command — which rejects `--goal` (`Unknown option: --goal`) and exits
  instantly while the parent still prints a fake pid. **After every detached
  launch, verify the child actually started** before moving on: either
  `ps -o pid,command | grep 'future loop run'` must show a live process, or
  `worker tail --goal G --agent-id A` must show turn events. If you see only
  `Unknown option: --goal` in `<root>/detached/<goal>/*.log` (or nothing is
  running), do NOT trust the pid — relaunch in the foreground-background
  wrapper:
  `FUTURE_LOOP_NO_DETACH=1 nohup future loop run --goal G --agent-id A … > <log> 2>&1 &`
  (that env var is not just for tests/embedders; it is the working bypass for
  this bug). The standalone `future-loop` binary does not have the bug.
- **Do NOT opt back into blocking**: `--detach` runs the child in the
  foreground and `FUTURE_LOOP_NO_DETACH=1` disables dispatch. If you catch
  yourself waiting on a run, stop — while you block you cannot watch other
  workers, answer gates, or read signals; the goal's dead time is your fault.
  A completed/failed run is a prompt to act on, not a result to wait for.
- **No per-turn token/cost budget — watch for silent token burn.** `run` has
  wall-clock and no-progress limits but NO token/cost cap. A strong model at
  `high` thinking can spend 5M+ tokens in a single turn without writing a
  single artifact (deep-reasoning loops). The `TurnNoProgress` signal fires
  only after 1 hour of no write-class tool — plenty of time to burn a
  large budget. **Distinguish two idle modes — they need different handling:**
  - **Truly dead (few minutes of *nothing*):** `worker tail` shows no new
    events at all — no `tool_start`, no `[usage]` growth, no thinking/text in
    `--raw`. The worker is stuck or the process is gone. Act immediately:
    `supervisor steer --goal G --instruction "..."`, then
    `worker stop --goal G --agent-id A` + relaunch if it stays silent.
  - **Write-idle but still thinking (the common case):** `worker tail --raw`
    shows a continuous `thinking_delta` stream and `[usage]` tokens climbing,
    but no write-class `tool_start`. This is deep reasoning, not a hang — it
    is what the 1-hour `TurnNoProgress` window is meant to tolerate. Do NOT
    steer it as if dead: lower the thinking level, tighten the todo text to
    demand a written file, or split the todo. The `TurnNoProgress` ledger
    record (1h) is the *fallback* signal for this case, not the trigger for
    the "dead worker" drill.
  **Escalating to a stronger model is often the WRONG move in the
  write-idle case** — the problem is usually "thinking too long", not
  "thinking too weak"; lower the thinking level or split the todo.
  **Not every model accepts every level** — some reasoning-only models reject
  `off`/`minimal` with an HTTP 400 ("该模型始终思考，不支持关闭思考"); the
  floor is per-model. When `high` spins without writing, drop one level at a
  time and watch for the write signal (`worker tail` → `tool_start`), rather
  than guessing a level that the model then rejects.

- `--agent-id` is mandatory and is the only mutual-exclusion mechanism: a run
  sees its OWN leased todos as runnable; two runs sharing one id double-execute.
  Unique name per parallel worker (`<host>-<task>`). Its one alternative,
  `--anonymous`, runs an **uncoordinated one-shot**: no `agent-id → session-id`
  binding, no lease claim, no workspace guard, no steer targeting — for a
  single throwaway turn that must not interact with other workers (or when
  you genuinely need no identity in the ledger). Never use it for work you
  will steer / stop / resume later.
- `--lease-secs N` (default 4h) sets how long a claimed todo stays locked to
  this worker before another agent may steal it. Shorten it for fast reclaim
  after a crash, lengthen it for a long slice that must not be stolen
  mid-flight. A dead holder is still auto-reclaimed on the next claim via the
  pid probe regardless of this value — the lease is a *priority window*, not
  a deadlock.
- `--max-turns N` (default 6) caps the number of **turn iterations in this one
  `run` process** — it is NOT a token/LLM-call limit. One turn = one
  decide-then-prompt; a single prompt may itself drive many internal
  LLM+tool rounds (that inner bound is the agent settings `max_turns`, default
  0 = unlimited). A run that hits `--max-turns` without validated closure
  exits with an error; rerun to continue.
- `--model M` / `--thinking-level L` pin the session's model / reasoning level
  for this run (transparent pass-through to the agent). They are fixed at
  spawn — changing them means respawn, not steer (see Orchestration
  patterns §6).
- **Incomplete turns auto-retry**: a turn ending `incomplete` (truncated model
  stream — an infra event, never a science failure) is retried with a CONTINUE
  note in the next envelope, bounded by `--max-incomplete-retries N` (default
  3, `0` disables). Exhausting the bound stops the run; see Key semantics.
- **A transport `error` also keeps the run going.** When the model stream dies
  (`[UPSTREAM_DISCONNECTED]`, connection reset, idle timeout), the agent emits
  a `type:"error"` event and the loop commits the turn as `terminal_state =
  error`; `classify_failure` sees the `upstream_disconnected` marker and
  classifies it `InfraRecoverable`, so the todo stays runnable and the SAME
  `run` process starts the next turn immediately (fresh `run_id` + fresh
  `.live.jsonl`). Two log-reading gotchas:
  - The `error` is the **last line** of that turn's `.live.jsonl` (the tee
    stops writing the file on the error event) — "nothing after the error" is
    normal and does NOT mean the worker stopped.
  - The `error` line carries only `{type, idx, wall_ts}` — the tee adds extra
    fields only for `tool_start`/`usage`, so the message is NOT in the file.
    To see WHY it errored: the loop's detached log line shows `state=error`;
    the agent session journal `~/.future/agent/sessions/<session>.jsonl` has a
    `run_terminal` event whose `truncation.detected_by` is
    `upstream_disconnected` / `model_response_error` / `eof_no_terminal`
    (note: the agent commits it as `state=incomplete`, the loop as
    `terminal_state=error` — same event, two names).
- **Mid-turn steering (interrupt)**: `supervisor steer --goal G --instruction "..."`
  aborts the in-flight run (a real interrupt) and the next turn follows the
  instruction. `todo update --text` remains the *non-interrupting* correction
  (picked up at the next turn).
- **Session retention** (resume-vs-fresh is YOUR call, never the kernel's):
  the kernel records WHY the last run was interrupted and keeps the session id
  on disk; you decide whether to resume. **Every `run` starts a FRESH session
  by default — there is no `--session-policy` flag at all.** The ONLY way to
  resume is an explicit pin: `--resume-session <id>` resumes that exact
  session (a dead id falls back to fresh automatically). The explicit pin is
  mandatory because the goal-level retention is a SINGLE field (whatever run
  wrote back last) — with parallel workers, an unpinned "resume the retained
  session" would hand one worker's session to another. Multi-worker recovery =
  one `--resume-session <旧id>` per worker, old ids taken from `worker list` /
  the run logs.
  **A session from a *normally completed* run is NOT resumable** — when a
  worker finishes its turn without an infra failure (`failure_kind = None`),
  the kernel marks the session non-resumable and the backing agent session is
  gone, so a later `run` on the same `--agent-id` starts a FRESH session
  (the default). Do NOT rely on session memory to carry context across turns:
  put cross-turn state in a durable artifact (the report file, a shared
  ledger, the goal doc) that each turn re-reads. Resume only helps after an
  *infra interruption* (429 / disconnect / operator stop), where the LLM
  context is genuinely still alive. Before deciding resume-vs-fresh, CHECK
  THE DISK: does `~/.future/agent/sessions/<id>.jsonl` still have real
  content, and did the kernel print "retained (resumable)"? Then pin-resume;
  only relaunch without the pin if the resumed session immediately dies again.
- **Watch a worker live** with `future loop worker tail --goal G
  [--agent-id A] [--lines N] [--raw]` — it renders the worker's
  `.live.jsonl` turn stream as a condensed tool/usage view (`--raw` dumps the
  verbatim log). This is the loop's own observability window into what a
  worker is *actually doing* so you can steer / stop / let it run — no
  hand-tailing files.
- **The `.live.jsonl` is PER-TURN, not per-worker.** Every turn in one `run`
  process gets a fresh `run_id` and a fresh `run_<run_id>.live.jsonl`; the
  previous turn's file freezes the instant that turn ends (terminal event or
  a transport `error`). `worker tail --agent-id A` resolves the worker's
  *latest* run file for you. **Never hard-code a `run_<id>.live.jsonl` path
  in a polling script** — after an `error` (or any turn end) the worker keeps
  running in the NEXT turn's file, so a script watching the old file sees
  zero new events and mis-reports the worker as dead ("error 后无任何活动").
  If you must read a file directly, resolve the current run via `worker tail`
  first; "last line is `error`" is a turn boundary, not the worker's death.
- A `run` executes one decision at a time and exits as soon as the kernel
  stops offering executable work — then YOU relaunch. `run` stops when:
  - **validated closure** (`terminal`) — all todos done, no acceptance gaps;
    the goal is closed;
  - **a user gate opens** (`ask_user`) — the gate report is pushed; with a
    gate-independent fallback the run KEEPS RUNNING it, otherwise it stops
    until the gate is resolved (`gate resolve`), then relaunch;
  - **quiet wait** (`wait_monitor`) — nothing is executable right now and the
    run exits cleanly (NOT a budget hit): a monitor exists but is not due (or
    is stalled), a blocker waits with no runnable fallback, deferred work is
    not yet due, or the open advancement work is leased to other agents.
    Relaunch when the wait clears (due time / blocker resolved / lease
    released);
  - **a replan obligation** (`replan`) — e.g. a completion that never declared
    a successor / `--no-follow-up`, or an acceptance gap with no runnable
    work: no auto path, stop and fix the plan (see `status`);
  - **worker stop / goal cancel / goal delete / todo supersede** — lifecycle
    commands stop the runs they invalidate: the same in-band ledger signal
    exits the run client at its next turn boundary (session retained) and the
    in-flight turn is aborted. `goal delete` stops BEFORE removing state (the
    run client tails events.jsonl — deleting first would strand it); a todo
    superseded mid-run stops its holder. You never need to hunt worker pids
    yourself;

  - **budget bounds** — max-turns reached (error exit). Non-zero exit = budget
    hit; rerun if open todos remain.

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
- **Lifecycle owns the process**: `goal cancel`, `goal delete`, and
  `todo supersede` automatically stop affected detached runs (ledger signal +
  gRPC abort, the same channel as `worker stop`) — never pkill. A superseded
  todo's late writeback can also NOT resurrect it (replay guard: terminal
  states are monotonic).
- **Workspace guard**: agents declare workspace paths; conflicting claims
  degrade to serial unless `--force-workspace`. The guard keys on the *cwd*,
  not on which agent is writing — so it ALSO fires when the same orchestrator
  re-runs with a *different* `--agent-id` on the same project (the first
  worker's lease is still held). When you know no parallel writes race (e.g.
  serial re-drive, or workers on disjoint subdirs), pass `--force-workspace`.
- **Delivery ≠ verified**: completion records a delivery in `delivered` state;
  resolve via `delivery record` (verified/failed/rework); unverified deliveries
  auto-derive a follow-up todo after 3 turns. A `--outcome verified` ALSO
  satisfies the terminal validator-receipt floor for that todo — the close-out
  path for validator-todos whose run history predates the receipt mechanism.
  At close-out, a stuck `terminal: false` with `closure_proof=valid` means a
  validator-todo has no passed receipt: re-run its `--verify` command (if it
  passes now), then `delivery record --outcome verified`.
- **Incomplete ≠ failure**: a turn ending `incomplete` (truncated model
  stream) never consumes the repair budget; `future loop run` auto-retries it
  with a CONTINUE note, bounded by `--max-incomplete-retries` (default 3).
- **TurnNoProgress**: a turn with no write-class tool (`write`/`edit`/`shell`)
  started for 1 hour is recorded in the ledger — the *fallback* signal for a
  **write-idle-but-thinking** worker, NOT the trigger for the dead-worker
  drill. Do not wait a full hour before looking: a worker that is **truly
  dead** (no events at all for a few minutes — see the token-burn note above)
  needs `supervisor steer --goal G --instruction "..."`, then
  `worker stop --goal G --agent-id A` + relaunch immediately. A worker that
  is thinking but not writing needs the *opposite*: lower the thinking level
  / split the todo, not an interrupt.
- **Monitors**: not-due monitors must NOT be polled; due time comes from
  `--cadence`/`--defer-secs N`; `--resume-when N` (numeric) defers for real,
  text values are hints without a deadline.
- **Gates freeze gated work, not the goal**: an open user gate blocks its
  dependents and reports up-channel, but gate-independent fallback work keeps
  running and the orchestrator decides whether a hard stop is wanted
  (`worker stop`). user_actions (non-blocking human to-dos) surface in the
  user channel and never freeze anything — reserve user_gate for genuine
  user decisions.
- **Coordination vs owner (anti-steal)**: `coordination` todos (goal
  bookkeeping) and `owner`-scoped todos never enter the shared worker
  frontier — the first is never agent work, the second is single-agent work.
  Both prevent the "worker `run` auto-claims a todo that isn't theirs" failure
  mode; keep the shared pool (`advancement` + no `--owner`) for genuinely
  first-claim-wins work so backup takeover / load-balancing still work.
- **CLI strictness**: unknown flags are hard errors; unknown `--class` /
  `--priority` / role-class combo values are hard errors; every subcommand
  renders its *own* exact usage on `--help` (`future loop supervisor steer
  --help` → the verb's flags, not the merged top-level line; `<command>
  --help` also lists a multi-verb command's subcommands); all read-only commands accept `--format json`
  (alias `--json`); a non-numeric `--resume-when` warns it has no deadline.
- **Completion is idempotent**: re-completing an already-done todo is a no-op
  (no duplicate ledger events); completing a superseded todo errors.
- **Dead-worker safety net is owned by the run path**: every `run`, on
  exit, sweeps dead-holder leases (a holder whose pid is gone) and pushes
  `host_died` to the supervisor — no cron needed. `scheduler tick` / `show` /
  `liveness` / `record-host-failure` / `ack` are the host-automation
  adapter's surface (backoff cursor + heartbeat), normally not needed in the
  single-process model.

## Multi-worker (one goal, several workers)

```bash
future loop agent onboard --goal G --agent-id A [--workspace p1,p2]   # register a peer + declare the workspace-guard write set
future loop agent list --goal G [--format json]                        # registered agents + live lease status
future loop scope --goal G --agent-id A [--exclude X]                  # identity-scoped runnable frontier
future loop lane --goal G --agent-id A                                 # lane recommendation
```

- Declared workspaces feed the workspace guard.
- **Launching N workers at once**: the workspace guard sees N runs claiming
  the same cwd and degrades to serial unless each passes `--force-workspace`
  (legitimate when workers write to disjoint subdirs). They also contend on a
  single `ACTIVE_GOAL_STATE.md.lock` at session-retention time — harmless
  (best-effort) but noisy; stagger launches by a second or two if it bothers
  you.

## Orchestration patterns

0. **The orchestrator schedules; workers do the heavy lifting.** When you are
   driving this skill, your own session is the supervisor - keep it that way.
   Do NOT run the heavy work (large reads, code edits, long analyses,
   multi-step tool chains) inside the orchestrating session: every token you
   spend there bloats the context you need for watching workers, reading
   signals, answering gates, and replanning - the actual scheduling job.
   Instead: express the work as todos, dispatch detached workers (`run`
   returns immediately), observe via `worker tail` / artifacts / supervisor
   reports, and steer from the board. Direct work in the orchestrator session
   is reserved for small glue actions: CLI calls, a quick file glance, a gate
   decision, a PR merge. If you catch yourself mid-implementation in the
   scheduling session, stop: write the todo, dispatch a worker, go back to
   watching.

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

   **`worker stop` reaches the actual agent session, even an orphaned turn.**
   Every `run` records an `agent-id → session-id` binding in the goal ledger
   (`worker_session_bound` event) BEFORE its first prompt. `worker stop`/
   `worker list` read that binding, then issue a real `abort` over gRPC — the
   abort interrupts the in-flight turn AND any running tool call (the shell
   tool polls the interrupt flag and kills the child). The binding is written
   first so a turn whose prompt failed (or whose `run` client was killed)
   before its `.live.jsonl` run_header was written is still discoverable and
   abortable — the run_header alone (written only after the prompt ack) cannot
   see that orphan window.
4. **Watch artifacts, not just loop status.** Long compute runs via nohup +
   checkpoint files; track output mtimes.
5. **Wrap-up belongs to the orchestrator.** The final/validation todo must be
   `--blocks`-chained behind everything — and mark it `--class coordination`
   so a worker's `run` can never auto-claim it once its lease lapses. Give
   each worker's slice `--owner <agent-id>` so parallel workers can't steal
   each other's work either; leave only genuinely shared work unowned.
6. **Iterate after a result — extend, revise, interrupt, or respawn.** A
   worker is NOT a long-lived process: "keep working on it" means re-`run`
   the SAME `--agent-id` — the *work* is expressed as todos, and context is
   replayed from the ledger, not from session memory (a re-`run` starts a
   FRESH session by default; resume only via an explicit `--resume-session
   <id>` pin, see Session retention above). When a result lands and you want
   a new direction, pick the lever that matches:

   - **Extend** (new direction = new work): `todo add --owner <same-agent>
     --blocks <old>` for the new slice, then close the old one with
     `todo complete --successor <new>`. `--owner` keeps it on the same worker
     (survives lease expiry); completion REQUIRES `--successor` or
     `--no-follow-up`, so a silent stop is rejected. Then `run --goal G
     --agent-id <same>` keeps driving the same worker (fresh session by
     default; context replays from the ledger either way).
   - **Revise** (same work, new angle): `todo update --text` (non-interrupting,
     picked up next turn) or `todo supersede` + re-split into finer todos.
   - **Interrupt** (redirect a running worker now): `supervisor steer --goal G
     --agent-id A --instruction "..."` aborts the in-flight turn and injects the
     instruction into the next envelope; for a paused worker it persists as
     `pending_steer` and is consumed on the next `run`.
   - **Respawn** (change what it RUNS ON — model / thinking level): steer
     changes the *task*; model and thinking level are session configuration,
     fixed at spawn and not hot-updatable ("steer changes the task; respawn
     changes the worker" — ARCHITECTURE.md). Changing them retires the worker
     and spawns a fresh one on the new configuration: `worker stop --goal G
     --agent-id A --delete` (reclaim the old session so the respawn is a true
     cold start), then `run --goal G --agent-id A --model M --thinking-level
     L` (fresh is the default; do NOT pass the old session id); the fresh
     session cold-starts its context from the ledger.

   The kernel only signals (replan rule set, oscillation / outcome-floor
   signals in `frontier show`); it never chooses the lever — you do.
7. **Workers report to you — you do not poll `status` for intervention
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
   - `incomplete_budget` — the turn kept ending `incomplete` and exhausted
     `--max-incomplete-retries`.
   - `host_died` — the worker's process is gone (SIGKILL / crash / host
     failure) with no release. This one is NOT reported at the turn boundary
     (a dead process executes no code): it is detected by the **post-run
     supervision sweep** — every `run`, on exit, sweeps dead-holder leases
     (a holder whose pid is gone) and pushes the note, so you do NOT need a
     separate `scheduler tick` running; the run path owns it (a manual
     `scheduler tick` still exists for the operator to force a sweep on
     demand).
   React the same way as a science failure: relaunch (the todo stays
   runnable; infra failures never consume the repair budget).

   **Worker mid-run progress (`future loop report`)** is the opposite of the
   push channel above: it is **projection-only, never pushed**. A worker
   calls `future loop report --goal G --agent-id A [--todo-id T]
   --message "..."` mid-turn (a tool call between LLM steps — submitted an
   attempt, waiting on a score) and the note lands as a `ProgressReported`
   ledger event. It deliberately does NOT prompt your session: no gate, no
   status transition, no dedup beyond the content-derived event id (an
   identical note within the same second is a no-op; distinct moments always
   append). Read it from the projection: `supervisor events --goal G` shows
   a `progress` array (agent_id / todo_id / message / ts). This is the
   pull-side companion to the push notifications — use it when a worker's
   intermediate milestones matter but don't warrant waking you.

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
   (the assembler gets a `--verify` too). `--verify` is per-todo and fires
   only on that todo's own turn — it does NOT re-run when a later todo edits
   a shared file. The terminal assembler's `--verify` is therefore your only
   regression net: make it run the full check (`cargo test` / full suite),
   not just the assembler's own artifact.
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
   consecutive turns. **But if the worker IS thinking (non-empty
   `worker tail`, active tool/thinking events) yet still produces nothing,
   the fix is usually the opposite: a strong model at high thinking can spin
   for millions of tokens without landing an artifact. Lower the thinking
   level, tighten the todo text to demand a written file, or split — do not
   escalate the model.**
   **Do not trust the push channel 100%.** Infra-stop reports are best-effort
   (they ride a gRPC prompt and can be lost if the agent is down), and the
   orchestrator's own session can die too. Keep a light fallback: every few
   minutes, confirm each claimed todo still maps to a live process and has a
   recent run record; treat a claimed-but-silent todo as a dead worker.
   **Push reports only wake an IDLE supervisor — an active orchestrator gets
   them late (or never).** If you stay active polling `status`, the workers'
   completion/failure reports queue up and arrive only after you go idle, so
   you will still need to poll. Polling `status` is a legitimate fallback,
   not a smell.
6. **Repo delivery discipline.** Deliver code waves as small PRs: cherry-pick
   ONE item commit onto the freshest main per PR; local gate = fmt + clippy
   + targeted tests; `gh pr create` + `gh pr merge --squash --auto`; when
   GitHub reports BEHIND, merge main into the PR branch and push (auto-merge
   fires).
7. **Supervisor waits without burning (the dispatch-wait discipline).** When
   workers are out on a slice and you must wait for them, the cost comes from
   HOW you wait, not the waiting itself. Each `sleep N && check` shell is a
   FULL LLM turn in your own session — high-frequency short polls are the
   single most expensive pattern in an orchestrating session (measured: 55
   `sleep ~95s` polls = 81 min wall time, ~10.9M input tokens, last_prompt
   ballooned to 158K). Three rules, in priority order:
   - **Event-driven first.** Once you `supervisor register`, completion /
     failure / gate / infra-stop reports push into YOUR session and wake you.
     Only poll for what push cannot deliver: worker *progress* (no event) and
     closure confirmation.
   - **Merge into ONE turn.** Never `sleep 95` then check, then `sleep 110`
     then check — each is a separate turn. Batch into one long shell:
     `sleep 240 && future loop status --goal G && sleep 100 && for w in …; do future loop worker tail --goal G --agent-id $w; done`.
     Fewer turns = fewer LLM calls = smaller context.
   - **Lengthen the interval.** Poll on a 3–5 min cadence, not ~90s. A worker
     writing artifacts needs minutes between meaningful writes; polling faster
     than it writes only re-reads the same state.
   - **Poll for the write signal, not the prose.** The one thing that matters
     is whether a worker is producing write-class activity (`worker tail` →
     `tool_start`/`write`). Active = let it run; silent for a few minutes =
     `supervisor steer` / `worker stop` + relaunch. Everything else is noise.

## Command reference

```bash
future loop status [--goal G] [--format json]
future loop goal init --objective "..." [--goal-id ID]   # state root = process cwd / FUTURE_LOOP_ROOT
future loop todo add --goal G --text "..." [--priority P0|P1|P2] [--blocks T] [--verify "cmd"] [--acceptance "a,b"] [--owner A] [--class coordination]
future loop todo update --goal G --todo-id T [--text ...] [--priority ...] [--blocks T] [--acceptance ...] [--owner A]   # no --class: class is immutable (supersede + re-add instead)
future loop todo complete --goal G --todo-id T --no-follow-up | --successor T2 [--evidence "..."] [--force]
future loop todo supersede --goal G --todo-id T --reason "..."
future loop gate resolve --goal G --todo-id T --decision "..." [--note "..."]
future loop lease claim|renew|release|expire|status --goal G ...
future loop run --goal G --agent-id A [--model M] [--thinking-level L] [--max-turns N] [--max-incomplete-retries N] [--lease-secs N] [--force-workspace] [--resume-session ID] [--anonymous]   # detached by default; --detach / FUTURE_LOOP_NO_DETACH=1 to run foreground
future loop agent onboard|list ...
future loop scope --goal G --agent-id A        # identity-scoped runnable frontier
future loop lane --goal G --agent-id A         # lane recommendation
future loop supervisor register|steer|events --goal G ...   # bind your session / interrupt a worker / read the supervisor event projection
future loop report --goal G --agent-id A [--todo-id T] --message "..."       # worker mid-run progress note (ledger event; read via supervisor events)
future loop worker list --goal G [--format json] # registered workers + backing session + running/ended/idle
future loop worker tail --goal G [--agent-id A] [--lines N] [--raw]  # watch a worker's live turn (condensed tool/usage view)
future loop worker stop --goal G --agent-id A | --all [--delete]  # stop worker(s) cleanly (ledger signal + gRPC abort)
future loop models [--format json]             # models available from the agent
future loop frontier show --goal G [--format json]        # outcome segments / replan rules / semantic history / terminal
future loop delivery status|record --goal G               # post-delivery closure
future loop quota should-run|usage|spend|decisions --goal G
future loop scheduler tick --goal G [--agent-id A] [--progression 15,30,60] [--action A]   # advance the backoff cursor; bootstrap-only on first tick
future loop scheduler show --goal G [--agent-id A] [--format json]   # persisted scheduler state
future loop scheduler liveness --goal G [--agent-id A] [--threshold-secs N] [--format json]  # heartbeat silence check (default 2h)
future loop scheduler record-host-failure --goal G --target-rrule R [--observed-rrule R] --failure-kind K [--failure-count N]
future loop scheduler ack --goal G --action A [--agent-id A] [--cadence-class C] [--rrule R] [--source S]
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
