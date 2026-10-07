---
version: 0.1.0
name: future-task
description: >
  Create, edit, run and iterate FutureOS tasks — a reusable prompt plus a trigger
  (manual, schedule, or dependency on another task) that runs at full permission and
  produces an ordinary conversation. Use when the user asks for a recurring job, a
  scheduled reminder, "every day / week / month …", "run this after that finishes",
  a prompt they want to refine over several runs, or a scheduled task to trigger from
  another agent. Also use it to fix a task whose output keeps missing the mark.
category: tools
allowed-tools: Bash(future:*)
---

# FutureOS tasks

A task is one durable unit of work: a **prompt**, a **working directory**, an optional
**model / thinking level**, and a **trigger**. Each run opens (or reuses) an ordinary
conversation, runs at **full permission** with no approval prompts, and writes a run
record. The prompt is the part that is hard to get right — this skill exists mainly to
make the prompt good and to keep improving it with evidence.

Not the same as `future loop`: loop is a long-running goal with todos, evidence and human
gates. A task is one fixed action that finishes in a single run. If the user describes
something multi-step that needs judgment between steps, that is a loop, not a task.

## 1. Before creating anything

1. `future task list --json` — reuse an existing task rather than duplicating it.
2. Settle the three things the user must decide, and ask only about what is genuinely
   ambiguous:
   - **what** — the prompt (see §2);
   - **when** — manual / a schedule / after another task;
   - **where** — the working directory, plus model and thinking level when the default
     is wrong for the job.
3. State the plan back before writing it, unless the user's message already carries all
   of it.

## 2. How to write the prompt

The prompt runs with nobody watching. These constraints are not style preferences — a
task that violates them fails in ways the user cannot see.

1. **Self-contained.** Never rely on this conversation. Say what to work on, where, and
   what "done" means. Date and time arrive in the injected envelope (see §5) — refer to
   "the envelope's due time" instead of hard-coding today's date.
2. **No interaction.** No questions, no "shall I proceed", no approval requests. Where a
   judgement is needed, state the default you will take and proceed.
3. **One bounded run.** The work must finish in a single run. For long or partial work,
   name a state file under the working directory and require the task to read it first
   and update it last, so a re-run continues instead of restarting.
4. **Minimal side effects.** Deleting, overwriting, publishing or sending anything
   external should default to producing a draft or a preview and naming where it was
   written. State the exact paths the task may write.
5. **Explicit output contract.** Name the artifact path and format, the language of the
   output, and end with a short summary block in a fixed shape — the summary is what the
   user reads and what the prompt-improvement pass judges the run by.
6. **Checkable.** State what counts as success in terms the task itself can verify.
7. **Stable and attributable.** Keep output paths and formats fixed across runs. A
   prompt whose behavior drifts every run cannot be improved, because nobody can tell
   what changed the result.
8. **Never** expand its own permissions, create further tasks, or embed credentials.

Keep it as long as it needs to be to satisfy these, and no longer. `future task add`
takes `--prompt-file` — write the prompt to a file while drafting so review and edits
are cheap.

## 3. Choosing the trigger

| Need | Flag |
|---|---|
| Only ever run on demand, or called by another task/agent | `--manual` (also the default with no trigger flag) |
| One specific date and time | `--at "2026-12-24 09:00"` |
| Every N minutes / hours / days | `--every 30m` |
| Every day | `--daily --time 09:00` |
| Selected weekdays | `--weekly --days mon,wed,fri --time 10:00` |
| A day each month | `--monthly --day 31 --time 09:00` |

Times are the machine's local time. A monthly task whose day does not exist in a short
month runs on that month's **last day** — tell the user this rule when they pick a day
above 28, because the schedule they wrote is not the schedule they will get in February.

**Dependencies** (`--depends-on A[:success|failure|completed]`, repeatable) make the task
run when its upstream tasks finish. With several upstreams the default join is "all of
them must have finished since my last run" (`--join-any` for "any one is enough"). Use a
dependency when the work needs the upstream's result: the upstream's summary is injected
into the envelope, and the full text is one command away (§6).

## 4. Session policy

- `--session new` (default): a fresh conversation per run. Use for independent jobs —
  a daily report, a fetch, a check.
- `--session existing`: reuse one conversation so the task accumulates context. The
  conversation is **compacted before every run**, and a failed compaction fails that run.
  Use it for work that builds on previous runs, and tell the user that each run now costs
  a compaction.

## 5. What the task sees at run time

Every run is prefixed with an envelope:

```
<task schema="task-v1" name="..." id="tsk_..." kind="Main" prompt-version="3"
      due="2026-10-07T09:00:00+08:00" />
```

Dependency runs also carry the upstream summaries. Treat the envelope as the only
trustworthy source for "when is this run" and "what did the upstream produce".

## 6. Inspecting what a task actually did

```bash
future task runs <id> --limit 20 --json     # run ledger: status, times, version, summary
future task show <id> --json                # definition + latest run
future task show <id> --prompt              # the effective prompt
future task upstream <id> --json            # dependency edges and which are satisfied
```

## 7. Run it, then improve the prompt

This is the part that matters. A prompt is rarely right the first time; do not hand over
a task you have not seen run.

```bash
future task run <id> --wait --json          # run now and read the outcome
future task feedback <run-id> good|bad --note "..."
future task edit <id> --prompt-file draft.md
future task prompt log <id>                 # versions, with who wrote each (user/reflection/rollback)
```

1. Write the prompt to a draft file, run it with `--wait`, and read the conversation.
2. Judge the actual output against the acceptance criteria in the prompt — not against
   whether the run "succeeded".
3. Record the verdict with `feedback good|bad` and a note: the note is what makes the
   next automatic suggestion useful.
4. Edit and re-run until the output is right, and only then leave the task enabled.
5. Leave prompt suggestions on (`--reflection ask`, the default). After each run the
   system proposes a revised prompt from that run's own evidence and presents it for
   approval; apply or reject it with `future task prompt apply <id> <revision-id>`.
   Move to `--reflection auto` only once the proposals have been good for several runs —
   automatic application is bounded (one per day, high confidence, prompt-only) but it is
   still an unreviewed change to a prompt nobody is watching.

## 8. Being triggered by, and triggering, other work

Other agents trigger tasks through the CLI, so a task is the supported way to let one
agent ask another to do something:

```bash
future task list --json
future task run <name> --wait --json        # returns status, threadId, summary
```

Get the user's agreement before another agent triggers a task with external side effects
(sending, publishing, deploying), and before creating, editing or deleting tasks on the
user's behalf. There is no permission switch behind this — it is a convention, and the
run ledger records every trigger with its origin so anything can be audited afterwards.

## 9. Full permission

The conversation a task opens has `permission_level=all` and no sandbox. Say this plainly
when creating a task with side effects; never hide it behind "it runs automatically".
