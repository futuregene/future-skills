# The account and the credit balance

This is the only part of this skill that talks to a **remote** service; every
other read in it describes this disk.

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

```bash
future account profile
future account balance --json
# Low balance: report it and stop. Do not create a recharge order.
```
