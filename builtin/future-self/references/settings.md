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
# --cwd also files the conversation in the desktop app's workspace list — see
# `desktop-app.md`; the directory must exist for that part.

# applied to the live session; `--json` reports what landed under `updated`
future session set <id> --tools read,shell --permission workspace --sandbox manual
future session set <id> --context-files off --auto-compact off --auto-retry on
future session set <id> --system-prompt "…" --append-system-prompt "…"

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
back the permission level, the sandbox tier (`sandboxTier`), auto-compact and the
context files — but **not** `--auto-retry`, the tool set or the system prompt, so
confirm those from `session set --json`, whose `updated` map names what it
applied. Check the read-back rather than assuming a change landed.

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

## Creating and branching sessions

`future session new [--cwd <dir>] [--name <text>]`, `forks <id>` →
`fork <id> --entry <entry-id>`, `clone <id>`,
`title <id> [--lang en|zh] [--apply]` and `export <id> [--out <path>]`. `new`
creates a session that stays out of `session list` until its first run; `title`
is a **model call** (it spends credits, and only renames with `--apply`).
`set --parent` records lineage only, unlike `fork`, which copies history.

"Compress this conversation" — `future session compact --session <id>`: report it
as an asynchronous request, not a finished summary.

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
