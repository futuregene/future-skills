---
version: 1.0.0
name: future-self
description: Inspect and adjust this FutureOS installation's own state — global agent settings, sessions, skills, tools and models, and the user's recorded conversations — to answer "how am I configured", "what do I know about you", or "what did we do before", and to personalise or proactively help. Use for self-inspection, cross-session recall of past conversations, reading or changing global agent settings, or building a picture of the user's preferences. Not for reading credentials, and not for ordinary task work on the user's project.
allowed-tools: Bash(future:*)
category: tools
---

# Knowing yourself and the user

Everything this installation knows is local and readable through the `future`
CLI: how the agent is configured, which skills and tools are installed, every
conversation that was recorded, and what it cost. This skill is the entry point
for using that, so the agent can adapt instead of asking for something that is
already on disk.

Read state before acting; ask before changing anything that outlives this turn.

## 1. Ground rules

- **Never read or print `~/.future/agent/auth.json`.** It holds API keys.
  `future config get` deliberately returns no credential material, and
  `future auth credential` exists for shell scripts, not for browsing — do not
  run it to "see what is configured".
- **Never report a negative you cannot prove.** History search covers a bounded
  window of sessions and is literal matching (see §6). "We never discussed
  that" is only defensible when the response says `truncated: false` and
  `hasMore: false`.
- **Changes to settings are the user's decision.** They persist past this
  session and change how every future session behaves. Propose the change and
  the old value; make it only when the user agrees (or when they asked for it).
  Report what you changed and when it takes effect.
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
| `future doctor` | Whether login, agent, sandbox, providers, sessions and skills are healthy |
| `future models --json` | Which models are available to this agent |
| `future auth status` | Whether the user is signed in (and to which platform) |
| `future account profile` / `balance` | Who the user is, and what the account has left |
| `future skills list` | Installed vs. catalogue skills — i.e. what this agent can already do |
| `future tools list` / `describe <name>` | The tool surface, with arguments and examples |
| `future session list --json` | Every session, newest first (id, title, model, usage) |
| `future session info <id>` | One session in detail: model, cwd, message/tool counts, tokens, cost |
| `future loop status` | Long-running goals, if any are open in this directory |

`future doctor` is the right first call when something looks wrong: it is one
pass over all of the above and reports what is missing rather than failing.

## 3. Reading what happened with the user

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

## 4. Changing this installation

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

## 5. Building a picture of the user

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

## 6. Limits — state them, do not paper over them

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
- **Local and single-machine.** Sessions on another machine or another
  `FUTURE_HOME` are not visible. Compiled-in facts (this version's defaults)
  come from the running binary; if behaviour contradicts `future config get`,
  the running Agent may predate the file.
- **No credentials, ever.** Not in reads, not in summaries, not in files you
  write for the user.

## 7. Worked examples

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

"Make your answers shorter from now on": a preference to write down, not a
setting. Ask where the user wants it recorded, record it there, quote it back.

"My agent uses the wrong model": read `future config get defaultModel` and
`future models --json` first — the file may already be right and the running
session may simply be older than the change.
