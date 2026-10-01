---
version: 1.2.0
name: future-self
description: Inspect and adjust this FutureOS installation — global agent settings, sessions, skills, tools and models, the account and credit balance, the user's recorded conversations, and the source that implements the agent — to answer "how am I configured", "why do I behave this way", "what do I know about you", "what did we do before", "how is my account" or "show me my balance", and to personalise or proactively help. Use for self-inspection, cross-session recall of past conversations, reading or changing global agent settings, understanding the code behind a behaviour, or account profile and credit balance. Never for reading credentials, and not for ordinary task work on the user's project.
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
  session set` / skills (§6); anything else is a bug to report, not to fix
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
| `future version --json` | Which build this is: version, **commit**, target, dirty |
| `future doctor` | Whether login, agent, sandbox, providers, sessions and skills are healthy |
| `future models --json` | Which models are available to this agent |
| `future auth status` | Whether the user is signed in (and to which platform) |
| `future skills list` | Installed vs. catalogue skills — i.e. what this agent can already do |
| `future tools list` / `describe <name>` | The tool surface, with arguments and examples |
| `future session list --json` | Every session, newest first (id, title, model, usage) |
| `future session info <id>` | One session in detail: model, cwd, message/tool counts, tokens, cost |
| `future loop status` | Long-running goals, if any are open in this directory |

`future doctor` is the right first call when something looks wrong: it is one
pass over all of the above and reports what is missing rather than failing.

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
  itself — never load, print or pass a key. If a call reports no API key, the
  fix is `future auth login` (the user's decision), not hunting for the file.
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

Cross-session search needs a current CLI. If `--all` is rejected as an unknown
option, fall back to `future session list --json` plus per-session `search`.

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

Session-scoped changes (this conversation only):

```bash
future session set <id> --model <id> --thinking <level> --cwd <dir> --title <name>
```

`--thinking` accepts `off`, `minimal`, `low`, `medium`, `high`, `xhigh`. The
model and thinking level reach the running session immediately.

Capabilities:

```bash
future skills list                     # what exists
future skills install <name>           # add one
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
- **Original records only.** Reasoning/thinking is excluded by design, media
  bodies and provider metadata are omitted, and compacted summaries are not
  exposed — so a session read here is not identical to what the model saw.
- **Local state is local; the account is not.** Agent settings, skills and all
  sessions live on this machine — sessions under another `FUTURE_HOME`, or on
  another device, are invisible, and there is no checkout to read unless one is
  actually here. The account commands (§3) are the exception: they reach the
  Future platform over the network and need a login, so they can fail for
  reasons no local state would explain.
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

"Make your answers shorter from now on": a preference to write down, not a
setting. Ask where the user wants it recorded, record it there, quote it back.

"My agent uses the wrong model": read `future config get defaultModel` and
`future models --json` first — the file may already be right and the running
session may simply be older than the change.
