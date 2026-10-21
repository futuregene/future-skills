# This machine as a host, and as a client

`future remote` covers two roles that are deliberately kept apart, each with its
own credential book, runtime and file:

```bash
future remote status [--json]                          # is it serving, and who is connected
future remote enable|disable [--json]                  # the autoConnectRemote switch
future remote devices [list|add] [--json]              # devices allowed to drive THIS machine
future remote devices remove <id|#> [--yes] [--all]    # unpair one, or every one
future remote devices use <id|#>                       # hand this machine to one device
future remote peers [list] [--json]                    # desktops THIS machine drives
future remote peers add <invitation>                   # pair with one, by pasting its link
future remote peers connect|disconnect <id|#>          # take one up or down now
future remote peers rename <id|#> <name> [--clear]     # this machine's private label
future remote peers remove <id|#> [--yes]              # unpair it
```

- **Devices** are the phones and computers that drive this machine — this one is
  the host. Their book is `remote_pairings.json` in the FutureOS home.
- **Peers** are the machines this one drives — this one is the client. Their
  book is `remote_peers.json` beside it.
- A pairing in one direction says nothing about the other: separate
  credentials, separate runtimes, separate files.

## `status` answers two different questions

```bash
future remote status --json | jq -e '.state == "serving"'   # test state, not the exit code
```

- **Runtime state** — whether this machine is serving right now. Only a running
  Desktop can answer (the window, or `future headless`); with none running the
  human output reads *off — no Desktop is running*, and `--json` says
  `desktopRunning: false` with whatever half it could read from disk.
- **`switch.autoConnectRemote`** — the stored value the window's Remote page
  writes, which decides whether the machine serves again at the next launch.

`state` is the word to test in a script (`off | unknown | on | connecting |
serving | degraded | failed | revoked`); `serving`, `reachable`, `phase`,
`reason`, `recovery`, `active`, `devices[]`, `endpoint`, `signedIn`,
`agentAvailable` and `transport` (credentials already scrubbed) are the rest of
the `--json` document.

**Exit 0 means the status was read** — including `off`, `failed` and `revoked`:
a machine that is off answered the question. Exit 1 means it was **not** read (a
Desktop that owns the data directory did not answer — an older build, or one
that died mid-request — or the settings store was unreadable), and `--json` still
prints a document with `state: "unknown"`.

`enable` / `disable` are that switch from a terminal: they take effect at once
when a Desktop is running and are stored for the next launch either way, so
neither needs a restart. Say which of the two you changed and that it hands
(or stops handing) the whole machine to a paired device — it is the user's
security decision, not a way to check whether the feature works.

## What needs a running Desktop, and what the book answers alone

`list`, `use` and `rename` read or write the books directly, so they work with
nothing running — and `rename` never leaves this machine. `add`, `remove`,
`connect`, `disconnect` and `use` additionally ask the running Desktop, because
an invitation is only usable while that pairing's bridge is connected, a removal
only takes effect *now* if the bridge is stopped, and control is an in-memory
pointer in that process.

Read the nulls correctly: `connected`, `present`, `stopped`, `error` and
`agentAvailable` are null when no Desktop answered. That is the honest reading of
"the book cannot know" — not "nothing is connected". `peers list` reports
`{desktopRunning, answered, peers}` for exactly this reason.

`remove` revokes the device where it was minted before dropping it locally: an
undeliverable platform revoke is queued and retried by the next Desktop, while a
self-hosted relay has no account to queue against, so a room deletion that cannot
be delivered is reported and the room expires on its own. Ids are the
`desktopId` a peer row shows (the `desktop_` prefix is optional); a row number
like `#1` names the same row.

## Hosting without the window: `future headless`

```bash
future headless                                   # serve this machine's remote desktop
future headless --relay https://relay.example [--relay-ca ca.pem]
```

The foreground application host in a terminal (Ctrl+C stops it), with no
background service installed. Without `--relay` it needs a Future OS account and
runs the login flow before serving; **with `--relay` there is no account at
all**. First-time setup needs an interactive terminal. The remote-desktop switch
is shared with the window: with it off, the host starts and stays idle instead of
exiting, which is why `future remote enable` takes effect without a restart.
`future remote devices` works from any terminal while it runs.

## Self-hosted, account-free relay: `future relay`

For a machine that must not depend on the Future platform:

```bash
future relay init  --dir DIR [--listen ADDR] [--public-url URL] \
                   [--nats-url URL] [--nats-ws-url URL] \
                   [--tls-cert PEM --tls-key PEM] [--allow-plaintext-upstream] [--force]
future relay serve --config FILE
```

`init` writes the trust setup once — operator and account NKey, their JWTs, an
`nats-server` configuration and `relay.json` — and overwrites nothing without
`--force`. `serve` runs the HTTP API that turns a signed invitation into a
short-lived NATS credential. The relay keeps no account and no database: rooms
live in a JSON file beside `relay.json`, so a restart costs no re-pairing, and it
stores only hashes of the invitation and refresh tokens.

The listeners and the URLs they advertise have to agree: a `tls://` or `wss://`
endpoint needs `--tls-cert`/`--tls-key`, and a plaintext listener advertised as
TLS is refused unless `--allow-plaintext-upstream` says something in front is
terminating TLS. Point a desktop at it with `futureos --relay URL` or
`future headless --relay URL`; the invitation it prints then carries the relay's
address, and the choice is recorded per pairing, so devices paired through the
Future platform keep working. A relay with a private CA needs no extra flag in
`future remote` — name it with `FUTURE_RELAY_CA` and it is applied to that
relay's requests.

## Two things not to do

- **Do not print an invitation link into a file, a log or a message you keep.**
  It is a credential for pairing a device; `status --json` deliberately never
  prints the code. Read it back to the user once, or have `add` print it to their
  terminal.
- **Do not enable the remote desktop, or hand control to a device, on your own
  initiative.** Both let a paired device operate this machine. Propose the
  command; run it when the user asks.
