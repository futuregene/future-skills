---
version: 1.0.2
name: future-account
description: View Future account profile and credit balance via Future CLI. Use when the user asks about their account info, credits balance, remaining credits, or asks "how is my account" or "show me my balance".
allowed-tools: Bash(future:*)
category: tools
---

> **Authentication is automatic.** The `future` CLI reads credentials from `~/.future/agent/auth.json`. You do NOT need to find, configure, or pass API keys — just call the commands below.

# Account

## When to use this skill

Load this skill when the user asks to:
- Check their account profile or user information
- View their credit balance or remaining credits
- Ask "how is my account" or "show me my balance"

## Commands

### View account profile

```bash
future account profile
```

Returns: user ID, email, email verification status, registration date.

### View credit balance

```bash
future account balance
```

Returns: balance in credits. Use `--json` for machine-readable output.

## Notes

- Account data (user profile, wallet balance) is per-user and identified by the API key.
- All account commands are free (zero credits).
