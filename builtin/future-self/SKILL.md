---
version: 1.7.1
name: future-self
description: Inspect and adjust this FutureOS installation — global agent settings, the desktop app's own settings, sessions, skills, tools and models, the account and credit balance, the user's recorded conversations, and the source that implements the agent — to answer "how am I configured", "why do I behave this way", "what do I know about you", "what did we do before", "how is my account" or "show me my balance", and to personalise or proactively help. Use for self-inspection, cross-session recall of past conversations, slicing one session's own records (including thinking and tool inputs/outputs), reading or changing global agent or desktop-app settings, understanding the code behind a behaviour, or account profile and credit balance. Never for reading credentials, and not for ordinary task work on the user's project.
allowed-tools: Bash(future:*)
category: tools
---

# Knowing yourself and the user

Everything this installation knows is local and readable through the `future`
CLI: how the agent is configured, which skills and tools are installed, every
conversation that was recorded, what it cost — and, where a source checkout is
present, the code that produces all of it. The account and credit balance are the
one part that comes from the Future platform instead of this disk. This skill is
the entry point for using all of it, so the agent can adapt instead of asking for
something that is already available, and explain a behaviour instead of guessing
at it.

Read state before acting; ask before changing anything that outlives this turn.

## 1. Ground rules

- **Never read or print `~/.future/agent/auth.json`.** It holds API keys. The
  CLI reads it for you (§3), `future config get` deliberately returns no
  credential material, and `future auth credential` exists for shell scripts,
  not for browsing — do not run it to "see what is configured".
- **Never report a negative you cannot prove.** History search covers a bounded
  window of sessions and is literal matching (see §8). "We never discussed
  that" is only defensible when the response says `truncated: false` and
  `hasMore: false`.
- **Changes to settings are the user's decision.** They persist past this
  session and change how every future session behaves. Propose the change and
  the old value; make it only when the user agrees (or when they asked for it).
  Report what you changed and when it takes effect.
- **Reading code is for understanding, not for patching.** Never edit the
  FutureOS source to change your own behaviour: that forks the installation from
  the release the user actually has, and the change disappears at the next
  update. Behaviour that has a knob goes through `future config set` / `future
  desktop settings set` / `future session set` / skills (§6); anything else is a
  bug to report, not to fix
  behind the user's back.
- **Reading history is reading the user's own record, and it is appropriate —
  but stay purposeful.** Search for what answers the question; do not page
  through conversations to satisfy curiosity.
- **Quote, do not paraphrase, when the distinction matters.** A stored
  preference is a quotation from the user; a pattern you noticed is your
  inference. Keep them apart when you report back.

## 2. Reading this installation

| Command | What it answers |
|---|---|
| `future config get [<key>] [--json]` | The effective global settings, defaults included |
| `future config get --help` | Every settable key, its values and its default |
| `future desktop settings [<key>] [--json]` | The desktop app's own settings (approval tier, hidden models, …), defaults included |
| `future desktop settings --help` | Every desktop setting, its values and its default |
| `future version --json` | Which build this is: version, **commit**, target, dirty |
| `future doctor` | Whether login, agent, sandbox, providers, sessions and skills are healthy |
| `future models --json` | Which models are available to this agent |
| `future auth status` | Whether the user is signed in (and to which platform) |
| `future skills list` | Catalogue skills with their install status — **not** a full list of what is installed (see the caveat below) |
| `future tools list` / `describe <name>` | Platform & browser tools the **CLI** can call (note: not the model's own tools — see below) |
| `future session list --json` | Every session, newest first, in a `{"sessions":[…]}` envelope: `id`, `sessionName`, `model`, `cwd`, `queryCount`, `updatedAtMs`, `firstMessage`, `parentSessionId`, `isStreaming` |
| `future session info <id> [--json]` | One session's **journal**: model, **cwd**, message/tool counts, lifetime tokens, cost |
| `future session status <id> [--json] [--metrics]` | One session's **live state**: effective permission, sandbox tier, context occupancy, context files, loaded skills, runs, pending approvals |
| `future session transcript --session <id>` | One session's records sliced and paged: every user message, thinking, a tool's inputs/outputs/paths, per-run outcomes (§5) |
| `future session forks <id>` | The user turns a session can be branched at |
| `future session approvals <id>` | Approval requests the session is waiting on |
| `future loop status` | Long-running goals, if any are open in this directory |

**`info` and `status` answer different questions and are easy to confuse.**
`info` reads what was recorded; `status` reads what the agent is doing and how
the session is configured *right now*. A session can run at `workspace`
permission while `future config get defaultPermissionLevel` says `all`, and be
using 40% of its context window while `info` reports 40M lifetime tokens —
only `status` is correct in either case. When a question is about the session's
current settings, its context, or what it is doing, reach for `status`.

Two things that look like "my tools" and are not:

- **`future tools` is the CLI's tool surface, not the model's.** It lists the
  platform and browser tools the *CLI* can invoke (`browser`, `parse_doc`,
  `image_edit`, …), and the remote ones need a login like §3. The tools the model
  is given are `read`, `write`, `edit`, `shell`. So `future tools describe shell`
  failing is expected, not a broken install; read `agent/src/tools/mod.rs` (§4)
  for that set.
- **A session's tool set is `future session set`, not `future run`.** Both take
  `--tools` / `--no-tools` / `--no-builtin-tools`, but `run`'s lasts one run
  while `set`'s applies to the live session — and `set` is the one
  `future session status` does not currently report back. Note that `read` being
  off silently disables skill loading, since skills are read from disk.
- **`future skills list` is a catalogue, not a full inventory — and not a
  loader.** It fetches the platform catalogue and marks which of *those* skills
  are installed, so a skill that is on this machine but absent from the
  catalogue does not appear at all (on a dev checkout `future-self`, `future-code`
  and `future-blog-post` are exactly that case). **`future doctor` is the command
  that lists every installed skill**, catalogue or not. The `description` column
  is the same text the system prompt shows, so it is a fair way to see what the
  agent can be told to do (`--json` is `{"skills":[…],"count":N}`). Reading it
  does not install or load anything.

**Most session and model commands need a running Agent.** `future session
list/info/status/transcript/history/forks/approvals` and `future models` ask the
Agent over local IPC; with none reachable they fail with `unable to connect to
Future Agent` (exit 1) rather than returning an empty result. The reads that work
with nothing running are `future config get`, `future desktop settings`,
`future version`, `future auth status`, `future skills list` and `future doctor`.

`future doctor` is the right first call when something looks wrong: it is one
pass over all of the above and reports what is missing rather than failing.

Note the split between the two session views, because the summary deliberately
carries **no** usage: `session list` gives identity and shape (who, what model,
how many turns, when), while tokens and cost live in `session info <id>`. A
question about spend needs the second command, not the first.

### Which session am I?

**You already have it: your own system prompt carries it.** The environment
section of the prompt you are running under contains

```
Current session ID: <your id>
You can reference this session ID when you need to identify or report which
conversation you are part of. This is your own session — you are self-aware of
this identifier.
```

Read it from there and use it directly — no lookup, no guessing. (Verified
against a live run: the id in the outgoing system message is byte-identical to
the session's row in `agent.db`.)

`future session list --json` is for the *other* sessions, and for two cases where
the prompt is not in front of you:

- **Confirming which row is you** when you want to cross-check, or when several
  sessions look alike. Every session with an active run reports
  `isStreaming: true`, so concurrent sessions can put several rows at `true` at
  once — the row that is *you* is the one whose `id` matches your system prompt,
  not merely the only row streaming.
- **Finding a session you are not in** (a previous conversation to resume), where
  `updatedAtMs` ordering (newest first) and `queryCount` are the signals.

What does **not** work: the Agent's `shell` tool does not export the session id
to the environment, so there is no `$FUTURE_SESSION_ID` to read. Do not infer
identity from the title either — several sessions can share one, and a fresh
session has none.

`future version --json` is the one to reach for when the *version string* is not
enough. It reports the full `gitCommit` this binary was built from — which a
release tag (`1.2.3`) or a coordinated test/nightly build (`0.0.2-<run>+test`)
does not carry in the version at all — plus `gitDirty`, `buildTarget` and
`buildProfile`. Use it before attributing a behaviour to source you just read;
`@§4` explains why that check matters. The running Agent reports the same facts
through `get_agent_info` (`gitCommit`, `gitDirty`, `buildTarget`,
`buildProfile`), which is how you compare the process answering you against
either the CLI or a checkout.

## 3. The account and the credit balance

This is the only part of this skill that talks to a **remote** service.

```bash
future account profile        # user ID, email, verification status, registered on
future account balance        # credit balance; --json for machine-readable output
future auth status            # whether a login is configured at all
```

- **Authentication is automatic.** The CLI reads the API key from `auth.json`
  itself — never load, print or pass a key. If a call reports no API key, the fix
  is `future auth login` (the user's decision), not hunting for the file. The one
  legitimate alternative the CLI itself suggests is the `FUTURE_API_KEY`
  environment variable, which takes precedence — mention it, do not set it on the
  user's behalf.
- **It needs the network and a login.** Unlike every other read in this skill,
  these fail offline and fail before `future auth login`. Report that as a
  configuration state, not as a broken account.
- **Account data is per-user and identified by the API key**, so it belongs to
  the signed-in user — relevant when several people share a machine.
- **Both commands are free** (zero credits). Reading the balance never spends
  it, so there is no cost to answering the question.
- **Do not create recharge or purchase orders**, and do not present a balance as
  a reason to act. If the balance is low, say so and stop; buying credits is the
  user's action on the platform, not a tool call you make.

## 4. Reading the code that implements you

The CLI tells you *what* is configured; the source tells you *why* it behaves
that way, which is what turns "the agent seems to ignore X" into an answer. Use
it when a behaviour is surprising, when a setting's effect is unclear, when the
user asks how something works, or when you are about to claim a limit.

**Find a checkout first.** The source lives in a git checkout, not in
`~/.future/`; the installed binary only carries its version and commit
(`future version --json`). A checkout is present when you are working inside one
(the repo root has `Cargo.toml` + `docs/`), or when the user points you at one.
If there is none, say so and answer from `future config get` / `future --help`
instead of reconstructing the implementation from memory.

The repository is **https://github.com/futuregene/future-os** (issues,
discussions and the wiki live there too, and its `README.md` is the entry point).
Two things live in separate repositories rather than in this one:

| What | Where |
|---|---|
| The skills in this list | https://github.com/futuregene/future-skills — the `skills/` submodule |
| Anything under `~/.future/` | Not version-controlled; it is this machine's state |

Do not clone a repository to answer a question about *this* installation: the
state is on disk and the version is in the binary. Cloning is for reading the
implementation, and it should be the user's call where it goes.

**Start from the maps, not from `rg` over the whole tree.** A fresh clone
carries its own orientation:

| Where | What it gives you |
|---|---|
| `CLAUDE.md` | Workspace layout: which crate owns what, and which slice of `~/.future/` |
| `docs/README.md` | The docs index — guides, architecture, internals |
| `docs/guide/` | User-facing behaviour: CLI, settings, sessions, channels, screenshots |
| `docs/architecture/` | The design behind a subsystem (loop control plane, storage, RPC) |
| `FUTURE.md` + `.future/memory/` | Institutional gotchas recorded by earlier sessions — read the matching entry before working in that area |
| `packages/rpc/proto/future.proto` | The RPC wire contract: the single source of truth for every command and event |

**Then trace one question to one file.** The mapping below covers the questions
that come up most:

| Question | Read |
|---|---|
| Which command does what, and what arguments does it take? | `cli/src/commands/<group>.rs`, help text in `cli/src/help.rs` |
| How is a command routed and answered? | `agent/src/rpc/commands/mod.rs` (the dispatcher), then the handler module |
| What does a setting actually change? | `agent/src/config/mod.rs` (fields, defaults, accessors), then `rg <field>` for its consumers |
| What are the desktop app's own settings, and where do they live? | `packages/app-settings/src/lib.rs` (the schema and the database location, shared with the CLI), then `desktop/src-tauri/src/store/app_settings.rs` (the app's connection pool and change events) |
| What is in my system prompt, and where does it come from? | `agent/src/prompt/mod.rs` (`build_prompt`), `agent/src/prompt/project_context.rs` |
| How are skills discovered, installed and tracked? | `agent/src/skills/` |
| How are sessions, entries and history recorded and read? | `agent/src/session/` (history recall: `history_query.rs`) |
| Which tools exist and what do they do? | `agent/src/tools/mod.rs` |
| What does a sandbox tier actually enforce? | `agent/src/sandbox/` |
| How is the version and commit stamped into a build? | `cli/build.rs`, `agent/build.rs`, and the version script they both mirror |

The docs describe released behaviour; the code describes *this* checkout. When
they disagree, prefer the code, and say which one you read.

**Two things that are easy to get wrong.** First, the running Agent is a built
binary: the checkout can be ahead of it, behind it, or mid-edit, so a source
claim is about the source, not about the process answering you — compare
`future version --json` (or the Agent's `get_agent_info`) against
`git rev-parse HEAD` before attributing behaviour to the code you just read.
Second, a checkout may hold another session's uncommitted work (`git status`,
`git log`); read it, but never commit, stash or reset anything in someone else's
tree.

## 5. Reading what happened with the user

```bash
future session list --json                                   # find the session
future session info <session-id>                             # what it contains
future session history search --session <id> --query <text> [--limit 5] [--json]
future session history search --all --query <text> [--sessions 50] [--json]
future session history get --session <id> --entry <entry-id> [--offset N] [--limit N] [--json]
```

`search` matches **literal text** (ASCII case insensitive) in user and assistant
text, tool arguments and tool results, or an exact tool-call id — not thinking.
Newest matches first. When the query has no match, the query is the problem:
shorten it, drop the punctuation, or try the identifier the user used.

`--all` searches across sessions instead of one. It scans the `--sessions` most
recently updated sessions (default 50) and every match carries its `sessionId`,
which is what makes "did we ever discuss X" answerable without knowing which
session. The response reports `scannedSessions` and `truncated`; when
`truncated` is true, older sessions were **not** searched.

`get` reads one entry's exact original text. Offset and limit are UTF-8 bytes,
not lines: follow the returned `nextOffset` rather than guessing, and pass a
search match's `byteOffset` straight through as `--offset` to land on the match.

### Slicing one session instead of searching it

Search answers "where does this text appear". `future session transcript` is the
surface for **processing** a conversation — enumerate it, choose fields, split a
tool's input from its output, page through it:

```bash
future session transcript --session <id> --counts --json            # what is in here
future session transcript --session <id> --select user --all --json # every user message
future session transcript --session <id> --select thinking --json   # reasoning
future session transcript --session <id> --tool shell --paths --json # a tool's file paths
future session transcript --session <id> --tool shell --input --truncate 500 --json
future session transcript --session <id> --tool shell --output --json
future session transcript --session <id> --grep "<text>" --all --json  # literal filter
future session transcript --session <id> --runs --json               # which runs failed, and why
```

- `--select` takes `user`, `assistant`, `thinking`, `tool-call`, `tool-result`,
  `session`, `compaction`, `all`. The default is `user,assistant,tool-call,
  tool-result` — **thinking is opt-in** here, and it is the opposite of
  `history search`, which cannot see reasoning at all.
- `--input` / `--output` keep only a tool call's arguments / a tool result's
  text. `--paths` keeps only the file paths a call's arguments or a result's text
  mention. `--tool` (comma-separated) restricts both halves to those tools.
- It pages in display-entry order: read `nextCursor` and continue with
  `--cursor nextCursor` until `hasMore` is false. `--limit` counts **matching**
  entries (default 50, max 500), `--all` removes the cap, `--max-bytes` bounds
  the output (default 256 KiB).
- `--counts` ignores the content filters and reports the window's distribution
  (entries, block kinds, tools, **run outcomes**, tokens, error results, bytes) —
  the cheap first look at a session you know nothing about.
- Every emitted entry also carries its run's outcome (`run`, `runId`) and, where
  recorded, its token `usage`; `--runs` is the same data as one row per run
  (status, duration, tokens, error). That is how "which run failed" is answered
  — no second command.
- `--truncate N` bounds every emitted string; `--json` is the machine form.
  `--select session` is the session's own metadata (cwd, model, thinking level,
  usage), and `future session info <id> --json` is the same identity at the top
  level with the computed stats.
- `--counts` and `--runs` are summaries: they ignore `--select`/`--tool`/`--grep`,
  refuse `--cursor`, and cover the whole session unless you bound them. Read a
  tool's results with `--tool` by starting at `--cursor 0`.

Two limits to state rather than hide: `--paths` is a heuristic (structured
path-ish argument keys, plus path-shaped tokens in result text), and `--tool`
attributes a tool *result* through the name of the call it pairs with — a result
whose call is outside the scanned window cannot be attributed, so it is skipped
and counted in `skippedUnattributedToolResults`. Start at `--cursor 0` when
filtering results by tool.

Cross-session search needs a current CLI. If `--all` is rejected as an unknown
option, fall back to `future session list --json` plus per-session `search`;
`transcript` is newer still, so treat an unknown-subcommand error the same way.

## 6. Changing this installation

Global settings (persist across sessions and restarts):

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
effect it would need is in §4, which is where to look before promising it.

The desktop app keeps its own preferences in `~/.future/app/app.db`
(`app_settings`): approval tier, hidden models, the completion bell, the
generated-title language, and so on. They are neither the agent settings
document above nor the models/providers/auth files that the app and the agent
share.

```bash
future desktop settings                       # everything, defaults included
future desktop settings get approvalTier      # one value, bare
future desktop settings set approvalTier manual
future desktop settings set hiddenModels "future/glm-5.3, future/kimi-k3"
```

Keys use the camelCase spelling of the desktop API, and `future desktop --help`
lists every key with its accepted values. **Every preference the app's own
Settings screen can change is settable here**, so the CLI and this skill cover
what the GUI covers. A list value is a JSON array or a comma-separated list;
values are validated before the database is touched; and a database the app has
never written reports the defaults rather than being created. Reads and writes
need no running desktop app — a running one picks the change up the next time it
reads the settings (a change made in its own Settings screen applies
immediately).

Session-scoped changes (this conversation only):

```bash
# recorded with the session
future session set <id> --model <id> --thinking <level> --cwd <dir> --title <name>
future session set <id> --parent <session-id>   # lineage only; "" detaches

# applied to the live session; `--json` reports what landed under `updated`
future session set <id> --tools read,shell --permission workspace --sandbox manual
future session set <id> --context-files off --auto-compact off --auto-retry on
future session set <id> --system-prompt "…" --append-system-prompt "…"

future session rename <id> <name>       # the shorter form of --title
future session compact --session <id>   # compact that session's context now
```

`--thinking` accepts `off`, `minimal`, `low`, `medium`, `high`, `xhigh`. The
model and thinking level reach the running session immediately; the title and cwd
are written straight away for a session that already has a record (§8 covers the
never-run case).
`future session compact` is the on-demand counterpart of the `compaction.*`
settings, and it is **asynchronous**: it returns an acknowledgement, not a
completed summary, and the Agent reports completion or failure through its
compaction events. Active runs are rejected, and it requires an explicit
`--session <id>` — there is no "the current one" default.

`--permission` is the approval gate (`all|workspace|none`) and `--sandbox` the
OS wrapping (`off|manual|sandbox`) — independent settings, and `sandbox` is
refused when the platform cannot provide one. `future session status <id>` reads
back the permission level, the sandbox tier (`sandboxTier`), auto-compact and the
context files — but **not** `--auto-retry`, the tool set or the system prompt, so
confirm those from `session set --json`, whose `updated` map names what it
applied. Check the read-back rather than assuming a change landed.

Stopping work and answering approvals — the CLI counterpart of the TUI's
`/stop`, `/cancel`, `/approve` and `/reject`:

```bash
future session abort <id>                              # active run + queue
future session cancel <id> --run <run-id>              # one queued run
future session approvals <id>                          # what it is waiting on
future session approve <id> <request-id> [--allow <glob> --access read|write]
future session reject <id> <request-id> [--note <text>]
```

Creating and branching: `future session new [--cwd <dir>] [--name <text>]`,
`forks <id>` → `fork <id> --entry <entry-id>`, `clone <id>`,
`title <id> [--lang en|zh] [--apply]` and `export <id> [--out <path>]`. `new`
creates a session that stays out of `session list` until its first run; `title`
is a **model call** (it spends credits, and only renames with `--apply`).
`set --parent` records lineage only, unlike `fork`, which copies history.

Two things not to do unasked: **`future session delete`** is destructive and not
recoverable from the CLI — it is also idempotent, so it prints `Deleted session
<id>` and exits 0 even for an id that never existed, which makes it useless as an
existence check — and **`future session set --model`** silently overrides a model
the user pinned. Both need an explicit request, not an inference.

Capabilities:

```bash
future skills list                     # what exists
future skills install [<name>]         # add one; with no name, all built-ins
future skills uninstall <name>         # remove one (it stays removed)
future skills update                   # upgrade installed skills
```

Installing a skill adds instructions, not permissions, but it does change what
the agent will reach for — say which one you are installing and why.

## 7. Building a picture of the user

The point of the above is a personal agent that needs less re-explaining.

- **Start from evidence, not from a template.** Settings the user changed,
  skills they installed, the model they keep choosing, and repeated phrasings in
  their prompts are observations. A profile you assume is a guess.
- **Keep quotations and inferences separate.** "You asked for responses in
  Chinese" (observed) is different from "you prefer terse answers" (inferred).
  Say which one you are acting on when it changes what you do.
- **Preferences are not stored anywhere by default.** If the user wants the
  agent to remember something, propose writing it down explicitly — a notes
  file in their workspace, or a `future config` value when the setting exists —
  and say where you put it. Do not silently accumulate a private profile.
- **Prefer asking to inferring when the cost of being wrong is real.** Changing
  a default model, permission level or sandbox tier on an inferred preference
  is not acceptable; on an explicit request it is.
- **Use it to reduce friction, not to fill silence.** Reading the previous
  session before asking "what were we working on?" is the win. Interrupting with
  advice nobody asked for is not.

## 8. Limits — state them, do not paper over them

- **Literal, not semantic.** No embeddings, no synonyms, no stemming. Two words
  are one substring. Refine the query instead of concluding there is nothing.
- **Bounded scan.** `--all` covers only the most recently updated `--sessions`
  sessions (1..500). `truncated: true` means the answer is partial.
- **Bounded matches.** At most 20 matches per search (1..20); `hasMore: true`
  means more exist.
- **Byte-addressed reads.** `get` offset/limit are UTF-8 bytes (4..32768 per
  read). Large entries need several reads; follow `nextOffset`.
- **Original records only.** `history search`/`get` exclude reasoning by
  design; `transcript --select thinking` does expose it. Media bodies and
  provider metadata are omitted (in `transcript` too), and compacted summaries
  are not exposed — so a session read here is not identical to what the model
  saw.
- **`transcript` is bounded by its window.** `--limit` is 1..500 matching
  entries, `--max-bytes` defaults to 256 KiB, and `--all` stops at that byte
  cap. A truncated run reports `hasMore: true` and a `nextCursor`; a caller that
  ignores them has read a prefix, not the session. `--grep` and `--tool` are
  also literal/heuristic, not semantic. `--counts` and `--runs` are the
  exception in one direction: they cover the whole session by default and only
  bound themselves when you pass `--max-bytes` yourself.
- **`status` is live; `info` is recorded.** `future session status` describes
  the running agent, so it is empty of settings a session never chose — an unset
  sandbox tier reads as `(default)` in the text and is *absent* from `--json`,
  not `off` — and it forgets everything when the agent restarts. It also does not
  report the session's `--auto-retry`, tool set or system prompt. `future session
  info` describes the journal and survives. Neither substitutes for the other.
- **A never-run session records a change only when it first runs.** A title or
  cwd set on a session that already has a record is written straight away, but a
  session that has never produced an entry stores it with its first run — so a
  `session set` on a brand-new session can look like it did nothing when read
  back from `session list`.
- **Local state is local; the account is not.** Agent settings, skills and all
  sessions live on this machine — sessions under another `FUTURE_HOME`, or on
  another device, are invisible, and there is no checkout to read unless one is
  actually here. The account commands (§3) are the exception: they reach the
  Future platform over the network and need a login, so they can fail for
  reasons no local state would explain.
- **The live views need a running Agent.** `session list/info/status/transcript/
  history/forks/approvals` and `future models` fail with `unable to connect to
  Future Agent` when nothing is running; only `config get`, `desktop settings`,
  `version`, `auth status`, `skills list` and `doctor` answer offline.
- **`future desktop settings` ignores `FUTURE_HOME`.** It reads and writes
  `~/.future/app/app.db` under the real home, exactly as the desktop app does,
  so a session running under another `FUTURE_HOME` still targets the real app
  database. That is the right file for a question about the app, but it is not
  the isolated installation the rest of this list scopes to.
- **Source is not behaviour.** A file in the checkout is not proof of what the
  running binary does (see §4); `future version --json` gives the version,
  commit and dirty state of the binary you are actually running.
- **No credentials, ever.** Not in reads, not in summaries, not in files you
  write for the user.

## 9. Worked examples

Resuming after a break, without asking:

```bash
future session list --json | head -40
future session history search --session <most-recent-id> --query "<topic>" --limit 5
future session history get --session <id> --entry <entry-id>
```

"What happened in this session, and where did it run?" — the shape first, then
only the slice you need:

```bash
future session info <id> --json                                  # cwd, model, counts, cost
future session transcript --session <id> --counts --json         # what kinds of records, which tools
future session transcript --session <id> --runs --json           # run by run: status, tokens, errors
future session transcript --session <id> --select user --all --json
future session transcript --session <id> --grep "<text>" --all --json
```

"how is this session configured right now, and what is it doing?" — the live
view, which is the only place these answers exist:

```bash
future session status <id>                 # permission, sandbox, context, runs
future session status <id> --json          # the agent's own state object
future session status <id> --metrics       # + journal health, broadcast lag
# A session at `workspace` while `config get defaultPermissionLevel` says `all`
# is normal — the session's own level is what it runs at.
```

"stop it" / "it is waiting on something":

```bash
future session abort <id>                  # the active run and everything queued
future session cancel <id> --run <run-id>  # one run that has not started
future session approvals <id>              # what it wants, with the request id
future session approve <id> <request-id>   # or reject; add --allow <glob> to stop asking
```

Answering "have we ever dealt with this?":

```bash
future session history search --all --query "<identifier>" --limit 20 --json
# truncated:true → say the search covered only the N most recent sessions
```

"why did you ignore my setting?" — read the value, then the code that consumes
it, before blaming either:

```bash
future config get <key>              # what the Agent would apply
rg -n "<field_name>" agent/src       # who reads it, and when
# A value that is right but not yet in effect is the usual answer: §6 lists
# which keys wait for the next session or the next Agent start.
```

A desktop-app preference works the same way, with a different store: read it
with `future desktop settings get <key>`, then check the shared schema in
`packages/app-settings/src/lib.rs` before blaming the value.

"which version am I actually running?" — the string is often not enough:

```bash
future version --json | jq '{version, gitCommit, gitDirty, buildTarget}'
git -C <checkout> rev-parse HEAD     # equal? then you are reading this code
```

"how is my account" / "what is my balance":

```bash
future account profile
future account balance --json
# Low balance: report it and stop. Do not create a recharge order.
```

"Compress this conversation" — `future session compact --session <id>` (§6):
report it as an asynchronous request, not a finished summary.

"Make your answers shorter from now on": a preference to write down, not a
setting. Ask where the user wants it recorded, record it there, quote it back.

"My agent uses the wrong model": read `future config get defaultModel` and
`future models --json` first — the file may already be right and the running
session may simply be older than the change.
