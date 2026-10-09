# Reading the code that implements you

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
| What are the desktop app's workspaces, and who writes them? | `packages/app-workspaces/src/lib.rs` (table and rules), `desktop/src-tauri/src/store/workspaces.rs` (the app's path), `cli/src/commands/workspace.rs` (the CLI's) |
| What is in my system prompt, and where does it come from? | `agent/src/prompt/mod.rs` (`build_prompt`), `agent/src/prompt/project_context.rs` |
| How are skills discovered, installed and tracked? | `agent/src/skills/` |
| How are sessions, entries and history recorded and read? | `agent/src/session/` (history recall: `history_query.rs`) |
| Which tools exist and what do they do? | `agent/src/tools/mod.rs` |
| What does a sandbox tier actually enforce? | `agent/src/sandbox/` |
| How is the version and commit stamped into a build? | `cli/build.rs`, `agent/build.rs`, and the version script they both mirror |

The docs describe released behaviour; the code describes *this* checkout. When
they disagree, prefer the code, and say which one you read.

## Two things that are easy to get wrong

First, the running Agent is a built binary: the checkout can be ahead of it,
behind it, or mid-edit, so a source claim is about the source, not about the
process answering you — compare `future version --json` (or the Agent's
`get_agent_info`) against `git rev-parse HEAD` before attributing behaviour to
the code you just read.

Second, a checkout may hold another session's uncommitted work (`git status`,
`git log`); read it, but never commit, stash or reset anything in someone else's
tree.

```bash
future version --json | jq '{version, gitCommit, gitDirty, buildTarget}'
git -C <checkout> rev-parse HEAD     # equal? then you are reading this code
```

## Never patch the source to change your own behaviour

A local edit forks the installation from the release the user actually has, and
it disappears at the next update — so it is not a fix, it is a bug that hides
until the next upgrade. Behaviour that has a knob goes through `future config
set`, `future desktop settings set`, `future session set` or a skill
(`settings.md`); anything else is a bug to report, not to fix behind the user's
back.
