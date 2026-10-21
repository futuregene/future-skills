# Changing this installation

Settings persist past this session and change how every future one behaves, so
they are the user's decision: propose the change and the old value, make it only
when the user agrees (or asked for it), and report what changed and when it takes
effect.

Four scopes, four commands: the agent's global settings (`future config`), the
desktop app's own store (`references/desktop-app.md`), this session
(`future session set`), and installed skills (the last section here).

## Global agent settings

```bash
future config get                                   # what is set now
future config get defaultPermissionLevel            # one value, bare
future config set defaultPermissionLevel workspace
future config set compaction.reserve_tokens 8192
future config set defaultModel future/deepseek-v4-pro
```

`future config get --help` lists every settable key. Values are validated before
the file is touched; an invalid value or an unknown key leaves the file exactly
as it was.

When a change takes effect:

| Key | Applies |
|---|---|
| `defaultModel`, `defaultPermissionLevel` | The next new session |
| `compaction.*`, `retry.*`, `maxTurns` | The next Agent start |

A setting that exists but is not in that list is not settable from the CLI — the
effect it would need is in `source.md`, which is where to look before promising
it.

## This session

```bash
# recorded with the session
future session set <id> --model <id> --thinking <level> --cwd <dir> --title <name>
future session set <id> --parent <session-id>   # lineage only; "" detaches
future session set <id> --append-system-prompt "…"   # see below; "" clears
# --cwd also files the conversation in the desktop app's workspace list — see
# `desktop-app.md`; the directory must exist for that part.

# applied to the live session; `--json` reports what landed under `updated`
future session set <id> --tools read,shell --permission workspace --sandbox manual
future session set <id> --context-files off --auto-compact off --auto-retry on
future session set <id> --system-prompt "…"

future session rename <id> <name>       # the shorter form of --title
future session compact --session <id>   # compact that session's context now
```

`--thinking` accepts `off`, `minimal`, `low`, `medium`, `high`, `xhigh`. The
model and thinking level reach the running session immediately; the title and cwd
are written straight away for a session that already has a record (`limits.md`
covers the never-run case).
`future session compact` is the on-demand counterpart of the `compaction.*`
settings, and it is **asynchronous**: it returns an acknowledgement, not a
completed summary, and the Agent reports completion or failure through its
compaction events. Active runs are rejected, and it requires an explicit
`--session <id>` — there is no "the current one" default.

`--permission` is the approval gate (`all|workspace|none`) and `--sandbox` the
OS wrapping (`off|manual|sandbox`) — independent settings, and `sandbox` is
refused when the platform cannot provide one. `future session status <id>` reads
back the permission level, the sandbox tier (`sandboxTier`), auto-compact, the
context files and the system-prompt append segment — but **not** `--auto-retry`
or the tool set, so confirm those from `session set --json`, whose `updated` map
names what it applied. Check the read-back rather than assuming a change landed.

## Rules that should keep applying

When the same instruction has to be restated in every message — an output format,
a language, a house style, a standing prohibition — put it in the session's
system prompt once instead of repeating it per turn. The user's messages stay
short, and the rule is in force from the first token of every run rather than
competing with whatever else the turn contains.

Two knobs exist and they behave differently:

| | `--append-system-prompt "…"` | `--system-prompt "…"` |
|---|---|---|
| Lands | after the project context and workspace memory | as the prompt's opening section, instead of the built-in identity and tool rules |
| Stored | with the session record | with the session record |
| Survives | an Agent restart, and applies to runs any client starts | the same |
| Cleared by | an empty value | an empty value |

Both are recorded with the session, which is what makes them worth using over
repeating an instruction in every message. **Prefer `--append-system-prompt`**
unless the built-in prompt is actively in the way: it adds rules without
removing the identity, tool and approval guidance the agent needs to behave, and
it is the narrower change to explain to the user.

`--system-prompt` replaces that opening section outright — project context,
workspace memory and the append still follow it, but the built-in identity and
tool guidance are gone. Reach for it when the user wants a genuinely different
assistant for that conversation, not to nudge a behaviour.

```bash
future session new --append-system-prompt "Answer in 中文." --json   # at creation
future session set <id> --append-system-prompt "Answer in 中文."     # or after
future session set <id> --append-system-prompt ""                    # clear it
future session set <id> --system-prompt "You review, you do not edit."  # replace
future session status <id>                                          # read both back
future session status <id> --system-prompt                          # the whole prompt
```

`status` reports the append on one line and, when set, that the prompt is
replaced; add `--system-prompt` for the full text the next run would send (tens
of kilobytes — ask for it when you need to quote or check it, not as a routine
read) and `--json` for it as an object. `--json` on its own carries
`appendSystemPrompt`, `customSystemPrompt` and `contextFilesEnabled`.
`future session info` reads the recorded values back from the journal, so it
still answers when you only want to know what was set.

Two things to get right before writing one:

- **It is a standing instruction, so wording matters.** It applies to every later
  turn in that conversation, including turns the user has not asked about yet.
  Say what the user asked for, not a guess at what they would like.
- **It is the user's decision, like any other setting** (see the ground rules in
  `SKILL.md`). Propose the text and read back what landed. Prefer it over
  inventing a notes file: the rule lives where the model already reads.


## Stopping work and answering approvals

The CLI counterpart of the TUI's `/stop`, `/cancel`, `/approve` and `/reject`:

```bash
future session abort <id>                              # active run + queue
future session cancel <id> --run <run-id>              # one queued run
future session approvals <id>                          # what it is waiting on
future session approve <id> <request-id> [--allow <glob> --access read|write]
future session reject <id> <request-id> [--note <text>]
```

```bash
future session abort <id>                  # the active run and everything queued
future session cancel <id> --run <run-id>  # one run that has not started
future session approvals <id>              # what it wants, with the request id
future session approve <id> <request-id>   # or reject; add --allow <glob> to stop asking
```

## Running something long without blocking this turn

```bash
future run --no-wait --session <id> "…"                     # ack now, answer later
future session wait <id> [--run <run-id>] [--timeout 15m] [--mode json]
```

Without `--no-wait`, `future run` streams the answer and exits when the run
ends. With it, the prompt is queued and the command prints an ack carrying the
run id, so the work continues in that session whether or not this shell survives
and `future session wait` later prints the answer (a run that already finished
returns at once). `--timeout` defaults to **5m** and a timeout is an error that
still reports the run id — raise the timeout for a long run rather than polling.
`--steer` is the opposite choice: it interrupts the session's active run and asks
immediately, instead of queueing behind it. Without either flag a prompt is
appended behind whatever is running.

## Creating and branching sessions

`future session new [--cwd <dir>] [--name <text>]`, `forks <id>` →
`fork <id> --entry <entry-id>`, `clone <id>`,
`title <id> [--lang en|zh] [--apply]` and `export <id> [--out <path>]`. `new`
creates a session that stays out of `session list` until its first run; `title`
is a **model call** (it spends credits, and only renames with `--apply`).
`set --parent` records lineage only, unlike `fork`, which copies history.

"Compress this conversation" — `future session compact --session <id>`: report it
as an asynchronous request, not a finished summary.

## Trimming a session's own history

Compaction can only *project* a history: it is required to keep every user
original, so a session whose user turns alone exceed its ceiling reports
`context compaction budget exceeded` and never recovers by itself. Shortening
such a session means **deleting** part of it, which is what `future session
reset` does. Treat it as destructive: it is the one session command whose whole
purpose is to remove the user's own words.

```bash
future session reset <id> --dry-run                    # what would go (the default)
future session reset <id> --keep-last 3 --yes           # keep the 3 newest turns
future session reset <id> --keep-first 5 --keep-last 3 --yes   # head and tail
future session reset <id> --drop thinking,tool-results --yes
future session reset <id> --all --yes                   # keep the session, drop its history
```

Selectors are combinable, and at least one is required: `--all` (keep only the
session record), `--keep-first N` / `--keep-last N` (whole user turns — one user
message plus everything up to the next, the boundary `session forks` shows), and
`--drop thinking,tool-calls,tool-results,attachments,compaction` for the part that
is kept. An unknown `--drop` name is an error, never silently ignored.

What to know before running it:

- **It is a dry run unless you pass `--yes`.** The preview reports entries and
  turns before → after, an estimated token size (the compactor's estimator; the
  live `contextTokens` in `session status` only moves after the session's next
  request), the per-kind counts, and the first/last surviving entries. Show that
  preview to the user and get an explicit yes before applying.
- **Applying writes a backup first**, at
  `~/.future/agent/session-backups/<session-id>-<timestamp>.json`: the session's
  complete entry list as it was *before* the reset. It is printed, it is
  lossless (the `entries` array is the storage representation, so it is also the
  input a future restore would read), and it is the only copy of what was
  deleted — do not move or delete it.
- **An active run or a running compaction is refused**, not interrupted: finish
  or stop the work first (`future session abort <id>`).
- **The session record is untouched** — id, name, cwd, model, thinking level,
  permission, and both system-prompt segments survive every selector. Only
  entries are removed, and the deletion is reflected everywhere the history is
  read afterwards (`session transcript`, `session history`, the desktop and
  mobile timelines).
- **A user turn can be a session's context.** `--keep-last 2` on a session whose
  first turns hold standing constraints will drop those constraints; say so when
  you propose it. `--all` is only right when the request is to keep the session
  as an empty shell.

When NOT to use it: for a session that is merely large, prefer `future session
compact --session <id>` (lossless, keeps every original) and reach for `reset`
when the request is specifically to shorten, slim down, or start the conversation
over while keeping the same session — or when compaction itself has already
refused with the budget error.

## Deleting conversations in bulk

```bash
future session prune --older-than 24h                      # preview (the default)
future session prune --older-than 24h --yes                # apply
future session prune --older-than 12h --keep <id> --yes    # protect one session
future session prune --older-than 3d --json                # the report as data
```

`<age>` is `<number><unit>` with `m`, `h`, `d` or `w` (`90m`, `12h`, `3d`, `2w`).
Idle is measured from the session's **newest history entry** — the last user turn
and what came with it — not from the file's mtime and not from `session list`'s
`UPDATED:`, which a rename or a storage upgrade rewrites without anybody using
the conversation.

- **It is a dry run unless `--yes` is given.** The preview lists every matching
  session with its age and title; show that (or at least the count) and get an
  explicit yes. This is the one command whose whole effect is deleting the user's
  own words, and a "24 hours" that is a day too wide is not recoverable.
- **An active run is skipped, never interrupted**, and the Agent refuses a
  session that starts a run or a compaction between the listing and the deletion;
  that refusal is reported per session, so the rest of the batch still goes. Each
  deletion is confirmed against the session list afterwards, so a long batch
  still reports the truth.
- **A session whose age cannot be established** (no history and no timestamp) is
  left untouched. `--keep <id>` is repeatable and is the way to protect a session
  the user names.
- **Which command the request means**: `prune` deletes whole conversations;
  `session reset` (the section above) trims one conversation's turns;
  `session compact` only projects it. "Clean up old conversations" is `prune`,
  "make this one shorter" is `reset`.
- **There is no undo.** Only a `future data backup` taken beforehand can bring a
  deleted session back — see `references/data.md` before agreeing to a large
  batch.

## Two things not to do unasked

**`future session delete`** is destructive and not recoverable from the CLI — it
is also idempotent, so it prints `Deleted session <id>` and exits 0 even for an
id that never existed, which makes it useless as an existence check — and
**`future session set --model`** silently overrides a model the user pinned. Both
need an explicit request, not an inference.

## Capabilities: skills

```bash
future skills list                     # what exists
future skills install [<name>]         # add one; with no name, all built-ins
future skills uninstall <name>         # remove one (it stays removed)
future skills update                   # upgrade installed skills
```

Installing a skill adds instructions, not permissions, but it does change what
the agent will reach for — say which one you are installing and why.
`future skills list` is a catalogue of the platform's skills, not an inventory of
this machine's: `future doctor` is the full list (`inspecting.md`).

## Hand-edited provider or model files need a registry refresh

The Agent builds its model registry at startup and does not watch the provider
files, so a hand edit to `~/.future/agent/models.json` — or a change to what a
local provider serves, such as a model added to or removed from
`~/.omlx/models` — is invisible while the Agent runs: `future models list`
keeps reporting the old set, because it reads the Agent's in-memory registry,
not the file. Two cases need nothing: with no Agent running the next start
reads the file as it is now, and an edit made through a client — the desktop
app's provider UI, or the interactive `future config` flow — refreshes the
registry itself.

To refresh a hand edit without restarting the Agent, send `reload_auth` over
the local RPC socket — the same refresh the TUI's `r` key and the desktop app's
local-write fallback trigger (no CLI subcommand exposes it):

```bash
grpcurl -plaintext \
  -import-path ~/future-os/packages/rpc/proto -proto future.proto \
  -d '{"id":"reload-auth-1","type":"reload_auth"}' \
  "unix://$HOME/.future/run/agent.sock" proto.FutureAgent/ExecuteCommand
```

A `"success": true` response rebuilds the registry, and `future models list`
shows the change immediately. Needs `grpcurl` and a future-os checkout for
`future.proto`. Two grpcurl 1.9.x traps: its `-unix` flag silently dials TCP
instead, so pass the socket as `unix://<path>`; and every flag must come before
the address.

## Worked examples

"Why did you ignore my setting?" — read the value, then the code that consumes
it, before blaming either:

```bash
future config get <key>              # what the Agent would apply
rg -n "<field_name>" agent/src       # who reads it, and when
# A value that is right but not yet in effect is the usual answer: the table
# above lists which keys wait for the next session or the next Agent start.
```

"My agent uses the wrong model": read `future config get defaultModel` and
`future models --json` first — the file may already be right and the running
session may simply be older than the change.

"Make your answers shorter from now on": a preference to write down, not a
setting. Ask where the user wants it recorded, record it there, quote it back.
