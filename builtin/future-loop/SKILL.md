---
version: 4.2.0
name: future-loop
description: FutureOS loop control plane — manage long-running goals, todos, human gates, workers, monitors, and validated completion. Use for cross-session work, ongoing task status, "keep working", "run overnight", or /future-loop. Not needed for a one-shot review or ordinary code edit.
allowed-tools: Bash(future:*)
category: tools
---

# Loop Control Plane

A durable goal and kanban, not an autonomous policy engine. The kernel enforces
state/lease/acceptance consistency; the agent chooses strategies and judges
results. Persistent evidence is authoritative; chat/session context is a cache.

## 1. Inspect and agree on the operating contract

1. Run `future loop status` in the project directory. Resume a matching goal;
   do not create duplicates. A one-shot conversation needs no loop goal.
2. State the objective, deliverables, acceptance checks, operating budget,
   escalation conditions and worker configuration. Ask for confirmation when
   these were not already specified. Default model = current session model;
   check availability with `future models`. Never change a user-pinned model,
   thinking level, budget or acceptance standard without permission.
3. Choose the smallest adequate workflow:
   - **Light:** one worker and targeted checks; no automatic research swarm.
   - **Standard:** implementation/exploration plus a separate verification task.
   - **Heavy:** genuinely different method families in parallel, synthesis and
     independent validation; justify the communication cost.
4. Set budget checkpoints in wall time, cost and/or attempts. `--max-turns`
   bounds outer loop iterations, NOT tokens or inner model/tool calls. Do not
   advertise a hard monetary cap unless the underlying runtime enforces it.

State root = process cwd + `.future/loop/`, or `FUTURE_LOOP_ROOT`. `goal init
--cwd DIR` records the project anchor; it does not relocate the ledger. Add the
state directory to `.gitignore`. Use `future loop <command> <verb> --help` for
exact flags; unsupported flags are errors. Before using this version, check that
`supervisor steer --help` lists `--interrupt` and `supervisor watch --help` exists.
If not, update the executable; do not apply the old interrupt semantics or write
new-schema events with an older binary. Agent transport discovery is shared
with the CLI; tests must use an isolated root and fresh agent endpoint.

## 2. Create and wire the work

```bash
future loop goal init --objective "..."
future loop supervisor register --goal G --session-id YOUR_CURRENT_SESSION_ID
future loop todo add --goal G --text "..." --owner worker-a --verify "cargo check -p X"
future loop todo add --goal G --text "Read work/a.md and independently verify ..." --blocks T1 --owner reviewer
future loop todo add --goal G --text "Final review and handoff" --class coordination --blocks T1,T2
```

Copy YOUR session ID from the environment, not an old worker's session. Re-register
when continuing in another session. The bootstrap todo from `goal init` is
intentional: complete its connection check or supersede it with a stated reason.

- `todo add` succeeds with `todo <id> added to <goal> ✔`, not `created`.
  Check the exit status, then extract with `todo\s+(todo_[0-9a-f]+)\s+added`.
  Require exactly one match; on failure STOP instead of passing output/empty
  variables into `--blocks`.
- `--blocks` on an advancement task names prerequisites. On a gate/blocker it
  names dependents. Create referenced todos first. Add/update reject unknown
  references, self-links and cycles before writing; do not rely on this with
  older executables. Final verification must depend on ALL producing tasks.
  `todo update --goal G --todo-id T --blocks A,B` REPLACES the set;
  `--blocks ""` clears it; omitting the flag preserves it. Repair legacy dangling
  references one todo at a time with update, then run `task-graph --goal G` before
  dispatch. A graph error is not proof that an older worker will refuse to run.
- `--owner A` is durable assignment, independent of lease expiration. Leave it
  unset only for intentionally shared work. Use a unique agent ID per concurrent
  run. `coordination` tasks are supervisor bookkeeping, never worker frontier
  items. Class is immutable; supersede and recreate a misclassified task.
- Every handoff names durable artifact paths in the successor's task text.
  Envelope snippets are bounded summaries, not full knowledge transfer. Every
  direct upstream gets an index entry, but full evidence/artifacts must be read;
  superseded work is not a verified result.
- Freeze acceptance criteria before implementation. Both automatic and manual
  advancement completion check nonempty evidence and every `--acceptance "a,b"`
  token. A normal model return cannot bypass this floor; rejected handoffs stay
  open with a diagnostic. This only checks token presence, not factual correctness.
  Keep required evidence in the final handoff, not only early narration.
  A file-existence check validates
  existence, not the quality of a report. Attach `--verify` for deterministic
  checks, and assign scientific/content correctness to a reviewer.
- Validators have an independent 120-second default timeout, bounded output
  capture, and process-tree cleanup. Set `FUTURE_LOOP_VALIDATOR_TIMEOUT_SECS`
  to a positive number for known longer checks. Commands use `sh -c` on Unix
  and `cmd.exe /D /S /C` on Windows; write platform-appropriate commands or call
  a portable validation program.

## 3. Dispatch without becoming a polling agent

Declare each task's complete write set with `todo add --required-write-scope`:
comma-separated file/directory paths, relative to the goal's recorded cwd (NOT
where the worker or inspecting CLI happens to run). Task scopes override the
agent's fallback `--workspace` for that task. If omitted, the agent declaration
applies; auto-registration defaults it to the entire process cwd. The guard
checks live task scopes atomically with lease acquisition, so disjoint tasks can
share a checkout without forcing. These declarations are not a filesystem sandbox.

```bash
future loop todo add --goal G --text "Write papers/a.md" --owner worker-a --required-write-scope papers/a.md
future loop todo add --goal G --text "Write papers/b.md" --owner worker-b --required-write-scope papers/b.md
```

Do not give every worker the shared parent `papers/` when they only write distinct
files: directory/descendant scopes overlap. Shared read-only resources are not
write scopes. Include ALL actual writes (logs, indexes, caches too); serialize or
separate real shared writes rather than hiding them from the declaration.

Version check: `todo add --help` must describe scopes as relative to goal cwd.
Older binaries only record `required_write_scope` and ignore it in the guard;
upgrade, or explicitly onboard each agent with its complete disjoint fallback:
`agent onboard --goal G --agent-id worker-a --workspace papers/a.md` (`--workspace`
is relative to the onboarding CLI cwd). Absolute task paths alone do not fix an
older guard. Check startup errors in worker logs, not just the `ended` status.

```bash
future loop run --goal G --agent-id worker-a --model M --thinking-level L --max-turns 1
future loop worker list --goal G
future loop worker tail --goal G --agent-id worker-a --lines 30
```

`run` detaches by default and prints its PID/log path. Verify the worker started;
then let event notifications wake you. The CLI also launches an independent,
non-LLM watchdog. It notices dead holders even if the LAST worker dies, persists
notifications before connecting to the agent, coalesces them into batches, and
retries undelivered batches. It does not choose a model, replan, or relaunch work.

- `supervisor register` also ensures this watcher exists. After a host reboot or
  a watcher failure, resume supervision with `supervisor watch --goal G` (foreground;
  run under the host service manager for boot persistence). `--once` performs one
  reconciliation. There is no promise of surviving power loss without a host service.
- `FUTURE_LOOP_NO_DETACH=1` is for foreground embedding/tests; `--detach` is an
  internal child marker, not a user request to background the command.
- Notifications are triggers, not authority. Automatic completion produces a JSON
  `task_delivery` receipt with goal/todo/agent/run/session IDs, validation, recent
  evidence, full-text journal path and `pending_other_todos` across all owners.
  It means `awaiting_review`, not a scientific pass or global completion. On
  wakeup, read current status, the batch and decisive artifacts. Old completion/
  death reports may refer to a superseded run; do not blindly restart them.
- Do not spend LLM calls on repeated sleeps and status polling. Use the watchdog,
  an external event source, or a blocking deterministic monitor. Combine necessary
  observations into one read and return until a decision is needed.
- A live log is PER TURN. `worker tail` resolves the current one. New journals
  retain full reply `text_chunk.text`; bounded memory/ledger summaries keep recent
  text, not just the opening plan. A frozen old `.live.jsonl` or its final error
  line does not prove the worker process died. Read the receipt's exact run, not
  whichever session file was most recently modified.
- Each launch defaults to a fresh session. To resume, explicitly pin that
  worker's session with `--resume-session ID`; a missing session falls back to
  fresh. Never use another worker's goal-level retention value blindly.
- `--max-incomplete-retries` bounds incomplete-stream retries (default 3).
  Infrastructure errors are not failed scientific hypotheses. Use evidence and
  failure classification to decide retry versus repair; nonzero exit is not
  necessarily a budget stop.

External scoring, remote experiment results or GPU readiness need an explicitly
owned monitor/adapter with the existing request ID, result endpoint, next check,
actual wakeup mechanism, timeout and resource allowance. The watchdog does not
query these services; `report` remains pull-only. Persist a receipt once and query
it rather than repeating a side-effecting submission. If no persistent monitor is
running, disclose that. Completed delivery plus queued scoring is still unverified.

## 4. Observe three different things

| Layer | Evidence | Interpretation |
|---|---|---|
| Liveness | PID, lease, stream connectivity | Can this worker still execute? |
| Activity | actual tool execution, usage and elapsed time | Is it doing something? |
| Progress | new artifact, validation result, measured improvement, rejected hypothesis | Is the objective advancing? |

`write/edit` starts are only an artifact-activity proxy; generic `shell` calls
are not automatically writes. Provider `input` and `execution` events must not
be double-counted. Reading/research can be productive without writes, and file
churn can be useless. No-write signals are advisory, not proof of a stuck model.

At a checkpoint, ask: what changed since the previous attempt, what evidence
supports it, what remains uncertain, and why is another attempt worth its cost?
Request a durable milestone with `future loop report` when appropriate; never
force dummy file writes to satisfy a detector. Compare supervisor overhead,
useful verified outputs, repeated work and human interventions, not raw turns.

## 5. Guide, interrupt, escalate

```bash
# Routine guidance: next boundary, no discarded in-flight reasoning
future loop supervisor steer --goal G --agent-id worker-a --instruction "Read the new measurement before retrying"
# Urgent correction / stop-loss: actually interrupts the running session
future loop supervisor steer --goal G --agent-id worker-a --interrupt --instruction "Stop using the invalid dataset; use the corrected input"
future loop worker stop --goal G --agent-id worker-a
```

Steering is recipient-scoped; broadcasts are acknowledged independently by each
worker. IDs distinguish same-second instructions. Acknowledgement follows durable
completed-turn writeback; a crash can replay guidance. Make instructions idempotent,
not "perform this irreversible action once". New instructions replace older ones
only in the same target scope. A stopped run still needs a relaunch if work remains.

Routine `todo update --text` also takes effect at the next boundary. Model/thinking
changes require a new configuration/session, not steer. Seek user consent for a
change to confirmed configuration. Preserve useful context via durable handoffs.

Worker uncertainty goes to the supervisor first. The supervisor decides whether a
human decision is needed. A gate freezes only its dependents; `--global-gate` is an
explicit goal-wide freeze. Independent work can run AND complete. Resolve gates
with `gate resolve`, not `todo complete`. Use user-actions for nonblocking requests.

`goal cancel`, `goal delete`, `todo supersede` and `worker stop` own lifecycle
cleanup; do not kill unrelated agents. Workspace guards prevent conflicting
writers; `--force-workspace` is only justified with proven disjoint write sets.
Record the exact paths and override rationale in a durable note before forcing;
the ledger records effective paths and a `forced` marker, not your rationale.
Prefer correcting declarations over bypassing the guard. Completed tasks release
leases; known-dead holders are ignored where PID probing is supported. Manual
claims without a host PID remain protected until release/expiry.

## 6. Review and close honestly

Handoff schema (put results first in the artifact, not just a notification):

- Actual task/run identity, input/candidate/validator versions and result status.
- Deliverable paths, original evidence references and reproduction commands.
- New evidence/metrics versus the previous attempt.
- Rejected approaches and why, including counterexamples.
- Assumptions, uncertainties and acceptance gaps.
- Next useful check and expected resource cost.

`todo complete` requires nonempty evidence and `--successor T` or `--no-follow-up`.
Manual completion intentionally does NOT execute `--verify`; review it as a manual
judgment/override, never claim the machine check ran. `--force` is an explicit
operator override, not a standard worker completion path. A rejected validator
means inspect the output and diagnostics; changing the validator requires a
justified contract correction, never lowering the bar to get a pass.

Delivery is initially `delivered`, not verified. Read/reproduce the artifacts and
record `delivery record --outcome verified|failed|rework`. The watcher also flags
pending verification after five minutes even when no more turns occur. A successful
review must name its evidence; receipt presence alone does not prove correctness.

Closing one slice does not invent successor edges to other runnable work.
Explicit follow-up tasks belong in the task graph; inspect all owner-scoped,
blocked/deferred and verification work before global closeout.
Use `frontier show` to verify terminal closure. If the budget expires or further
attempts have low expected value, stop workers, preserve the best artifacts, and
report **not achieved / partial / blocked / awaiting decision** with the gap. Do
not close unresolved acceptance gaps or label a paused goal successful. Obtain
approval to expand budgets. "All methods impossible" is not a prerequisite for
honestly stopping an open-ended research task.
