# Reading this installation

What the CLI can tell you about the agent, this machine and the recorded past.
Read state before acting, and read the *right* view: several commands here look
interchangeable and are not.

## The read surface

| Command | What it answers |
|---|---|
| `future config get [<key>] [--json]` | The effective global settings, defaults included |
| `future config get --help` | Every settable key, its values and its default |
| `future desktop settings [<key>] [--json]` | The desktop app's own settings (approval tier, hidden models, …), defaults included |
| `future desktop settings --help` | Every desktop setting, its values and its default |
| `future workspace list --json` | The desktop app's workspaces (see `desktop-app.md`) |
| `future version --json` | Which build this is: version, **commit**, target, dirty |
| `future doctor` | Whether login, agent, sandbox, providers, sessions and skills are healthy |
| `future models --json` | Which models are available to this agent |
| `future auth status` | Whether the user is signed in (and to which platform) |
| `future skills list` | Catalogue skills with their install status — **not** a full list of what is installed (see below) |
| `future tools list` / `describe <name>` | Platform & browser tools the **CLI** can call (note: not the model's own tools — see below) |
| `future session list --json` | Every session, newest first, in a `{"sessions":[…]}` envelope: `id`, `sessionName`, `model`, `cwd`, `queryCount`, `updatedAtMs`, `firstMessage`, `parentSessionId`, `isStreaming` |
| `future session info <id> [--json]` | One session's **journal**: model, **cwd**, message/tool counts, lifetime tokens, cost |
| `future session status <id> [--json] [--metrics]` | One session's **live state**: effective permission, sandbox tier, context occupancy, context files, loaded skills, runs, pending approvals |
| `future session transcript --session <id>` | One session's records sliced and paged: every user message, thinking, a tool's inputs/outputs/paths, per-run outcomes (`recall.md`) |
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

Note the split between the two session views, because the summary deliberately
carries **no** usage: `session list` gives identity and shape (who, what model,
how many turns, when), while tokens and cost live in `session info <id>`. A
question about spend needs the second command, not the first.

## Three things that look like "the tools" and are not

- **`future tools` is the CLI's tool surface, not the model's.** It lists the
  platform and browser tools the *CLI* can invoke (`browser`, `parse_doc`,
  `image_edit`, …), and the remote ones need a login like `account.md` describes.
  The tools the model is given are `read`, `write`, `edit`, `shell`. So
  `future tools describe shell` failing is expected, not a broken install; read
  `agent/src/tools/mod.rs` (`source.md`) for that set.
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

## What needs a running Agent

`future session list/info/status/transcript/history/forks/approvals` and
`future models` ask the Agent over local IPC; with none reachable they fail with
`unable to connect to Future Agent` (exit 1) rather than returning an empty
result. The reads that work with nothing running are `future config get`,
`future desktop settings`, `future workspace`, `future version`,
`future auth status`, `future skills list` and `future doctor`.

`future doctor` is the right first call when something looks wrong: it is one
pass over all of the above and reports what is missing rather than failing.

## Which session am I?

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

## Which build is this?

`future version --json` is the one to reach for when the *version string* is not
enough. It reports the full `gitCommit` this binary was built from — which a
release tag (`1.2.3`) or a coordinated test/nightly build (`0.0.2-<run>+test`)
does not carry in the version at all — plus `gitDirty`, `buildTarget` and
`buildProfile`. Use it before attributing a behaviour to source you just read;
`source.md` explains why that check matters. The running Agent reports the same
facts through `get_agent_info` (`gitCommit`, `gitDirty`, `buildTarget`,
`buildProfile`), which is how you compare the process answering you against
either the CLI or a checkout.

```bash
future version --json | jq '{version, gitCommit, gitDirty, buildTarget}'
git -C <checkout> rev-parse HEAD     # equal? then you are reading this code
```

## Reading a session's live configuration

"how is this session configured right now, and what is it doing?" — the live
view, which is the only place these answers exist:

```bash
future session status <id>                 # permission, sandbox, context, runs
future session status <id> --json          # the agent's own state object
future session status <id> --metrics       # + journal health, broadcast lag
# A session at `workspace` while `config get defaultPermissionLevel` says `all`
# is normal — the session's own level is what it runs at.
```
