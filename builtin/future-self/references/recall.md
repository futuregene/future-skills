# Reading what happened with the user

Two surfaces, for two different jobs. `history search` answers "where does this
text appear"; `session transcript` is for **processing** a conversation —
enumerate it, choose fields, split a tool's input from its output, page through
it.

## Searching the recorded past

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
option, fall back to `future session list --json` plus per-session `search`;
`transcript` is newer still, so treat an unknown-subcommand error the same way.

## Slicing one session

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

A truncated run reports `hasMore: true` and a `nextCursor`; a caller that ignores
them has read a prefix, not the session. `history search` and `transcript
--grep`/`--tool` are literal or heuristic, never semantic. The numeric caps are
in `limits.md`.

## Worked examples

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

Answering "have we ever dealt with this?":

```bash
future session history search --all --query "<identifier>" --limit 20 --json
# truncated:true → say the search covered only the N most recent sessions
```
