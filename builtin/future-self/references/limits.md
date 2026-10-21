# Limits — state them, do not paper over them

Every claim this skill enables has a bound behind it. Reporting a negative or a
total that the command did not actually establish is the failure mode this file
exists to prevent.

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
  actually here. The account commands (`account.md`) are the exception: they
  reach the Future platform over the network and need a login, so they can fail
  for reasons no local state would explain.
- **One directory is one workspace.** `future workspace add` resolves identity by
  canonical path, so a path that already has a workspace reopens it instead of
  creating a second row, and the directory must already exist. A workspace row is
  bookkeeping, not a conversation: adding one creates no session.
- **The live views need a running Agent.** `session list/info/status/transcript/
  history/forks/wait/approvals` and `future models` fail with `unable to connect
  to Future Agent` when nothing is running; only `config get`, `desktop settings`,
  `workspace`, `version`, `auth status`, `skills list` and `doctor` answer
  offline.
- **A pairing book is not the runtime.** `future remote devices`/`peers` read a
  file, but whether a bridge is connected, whether a device is present and
  whether the machine is serving live in the running Desktop. With none running
  those fields are **null** — "the book cannot know" — and `future remote
  status` exit 0 covers `off`, `failed` and `revoked` too: a machine that is off
  answered the question. Test `state`, not the exit code (`remote.md`).
- **Prune's clock is the newest history entry, and deletion has no undo.**
  `--older-than` does not read the file's mtime or `session list`'s `UPDATED:`,
  and nothing in the CLI restores a deleted session — only a `future data
  backup` taken beforehand does (`data.md`).
- **`future desktop settings` and `future workspace` ignore `FUTURE_HOME`.**
  They read and write `~/.future/app/app.db` under the real home, exactly as the
  desktop app does, so a session running under another `FUTURE_HOME` still
  targets the real app database. That is the right file for a question about the
  app, but it is not the isolated installation the rest of this list scopes to.
- **Source is not behaviour.** A file in the checkout is not proof of what the
  running binary does (`source.md`); `future version --json` gives the version,
  commit and dirty state of the binary you are actually running.
- **`future skills list` is a catalogue, not an inventory.** `future doctor` is
  the command that lists every installed skill (`inspecting.md`).
- **No credentials, ever.** Not in reads, not in summaries, not in files you
  write for the user.
