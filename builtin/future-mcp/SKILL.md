---
version: 1.1.0
name: future-mcp
description: >
  Use MCP (Model Context Protocol) servers from the Future `future mcp` CLI group:
  check whether a configured server is actually usable, list its tools, read one
  tool's argument schema, call it, hold one session across many calls, and add or
  remove servers in ~/.future/mcp.json. Use when a task needs a capability that
  arrives as an MCP server (a local tool server, a search or documentation
  service, an analysis engine such as REA), when the user names an MCP server or
  asks what MCP servers are configured, when a previously working MCP tool call
  fails, or when the user asks to add or remove one.
allowed-tools: Bash(future:*)
category: tools
---

# MCP servers

## The one rule: read the schema, never guess it

A server owns its own arguments and can change them between releases. Ask the CLI
and it answers from the running server:

```bash
future mcp list                                # what is configured
future mcp status [<server>]                   # is it actually usable
future mcp tools <server> --query <text>       # which tools exist
future mcp describe <server> <tool>            # exact argument schema
future mcp call <server> <tool> --args '{"key":"value"}'
```

Do not infer an eventual name, an argument, or a default from memory, from a
similar tool, or from another server. `describe` prints the JSON Schema the
server published, and `call` sends only what that schema allows.

## Find before you list

`list` says what is configured; it does not say whether the server works. When a
call has to succeed, `status` answers that first — it starts each server,
completes the handshake, reports the tool count and handshake time, and stops it,
without calling a tool. A missing engine or credential shows up here, with the
server's own stderr, before you have spent a call finding out. It is also the
cheap way to tell "the server is broken" from "my arguments are wrong".

Some servers are large: REA advertises **207 tools**, and a full listing is
tens of thousands of characters. `tools` prints one row per tool and pages
(`--limit`, default 50, capped at 500; `--offset` continues; `--query` matches
the name and description case-insensitively). So:

- Put the subject in `--query` (`--query binary`, `--query sqlite`) instead of
  paging through everything.
- Read one tool's schema with `describe` rather than accepting a whole
  `tools --json` dump.
- A name that does not match gets you the closest five in the error message —
  use it instead of re-listing.

## Hold one session when startup is expensive

Every subcommand except `serve` starts the server, uses it once and stops it,
which costs nothing for a fast server and a lot for an engine that analyses the
target on launch — a Ghidra cold start through REA is about **four minutes**, so
five calls cost five of them. `serve` pays that once and takes requests on stdin,
one JSON object per line:

```bash
printf '%s\n' '{"tool":"open_binary","args":{"path":"/bin/ls"}}' \
              '{"tool":"open_binary","args":{"path":"/bin/ls"}}' \
  | future mcp serve rea
# {"ok":true,"ready":true,"server":"rea","toolCount":207}
# {"ok":true,"isError":false,"result":{...}}
# {"ok":true,"isError":false,"result":{...}}
```

- Wait for the `ready` line rather than guessing how long analysis takes; when a
  shell tool needs a bounded call, that is what makes a long `serve` session
  predictable instead of a race against a timeout.
- Requests are answered in order, one at a time. Do not try to drive one session
  concurrently; start a second `serve` if you need parallelism.
- A request that fails reports itself on its own line (`{"ok":false,"error":...}`,
  with the server's stderr) and **the session keeps running**, so batch the work.
- Closing stdin ends the session. The engine's state is gone afterwards.

## Bound what you read

`call` prints at most `--max-bytes` (default 64 KB) and tells you the prefix it
showed. A tool result can be far larger than that (an Electron analysis through
REA was one 207 MB document), so:

- Redirect the complete result to a file and read the part you need:

```bash
future mcp call <server> <tool> --args '{...}' --out /tmp/result.json
jq '.normalized_result.summary' /tmp/result.json
```

- `--json` prints the MCP result envelope instead of joining its text blocks —
  use it when you are going to parse the output rather than read it.
- Never let a large result go to `stdout` unfiltered: the shell tool keeps only
  the last 500 KB of a command's output, so a big payload silently loses its
  head.

## Read failures correctly

| Exit | Meaning | What to do |
| --- | --- | --- |
| 1, `unknown MCP server` | Not configured. The message names the file and the configured servers | Configure it only if the user wants that |
| 1, `failed its handshake` | The process started but does not speak MCP; the message quotes its **stderr** | Report the real cause (a missing engine, a bad key, a bad command) — do not retry unchanged. Run `future mcp status <server>` to see it without a call |
| 1, `larger than N bytes` | A frame exceeded the **read** budget, which `--max-bytes` does not affect | Raise it with `--max-frame-bytes`, or lower the server's own response budget — not by trimming `--max-bytes` |
| 1, `[the tool reported an error]` on stderr | The server ran and refused. The payload is the server's own error, usually naming the argument at fault | Fix that argument and retry |
| 1, timed out | The server was slow to start or to answer | Retry with `--timeout <secs>` (default 60) for a server known to be slow |
| 0 | The tool returned content on stdout | Use it, and keep the server's own observations/limits in mind |

A tool that reports an error writes to **stderr** and exits 1, so `--out` and
shell redirection leave you a complete error document rather than a truncated
one.

## Adding and removing servers

```bash
future mcp add <name> --command <program> --arg <value>... --env KEY=VALUE... --cwd <dir>
future mcp remove <name>
```

- Server names accept letters, digits, `.`, `_` and `-`.
- `--arg` takes its value verbatim, so a flag-shaped argument works:
  `future mcp add rea --command rea --arg --mcp`.
- Everything runs as a **local process over stdio**; there is no HTTP/SSE
  transport yet, and no credentials store. Pass a key through `--env`, and
  prefer a reference over a literal value where the server supports one.
- `"enabled": false` keeps an entry in the file while refusing it by name.
- Each `future mcp` call starts the server and stops it again, so a call costs
  one startup and nothing is left running. A server that keeps process state
  loses it between calls — use `serve` when that startup is expensive.
- `--env KEY=VALUE` is how a server gets its configuration from the file rather
  than from the environment the agent runs in. An engine path belongs here (for
  example `--env GHIDRA_INSTALL_DIR=/path/to/ghidra`, `--env JAVA_HOME=/path/to/jdk`),
  so it works from any session without a shell profile.
- Adding or removing edits `~/.future/mcp.json`. Do it when the user asked for
  it, and say what you wrote.

The FutureOS agent itself has no MCP client: its tools are `read`, `write`,
`edit` and `shell`. This CLI group is how a session reaches an MCP server, so
an MCP-using skill or workflow calls `future mcp` the same way it calls any
other command — through `shell`.

## Check before concluding

A tool's output is a claim by one program, not evidence you verified. Keep the
server's own stated limits (unavailable provider, partial coverage, "unknown"
fields) in the answer, say which server and tool produced it, and do not present
a negative result as proof of absence when the tool says its coverage was
partial.
