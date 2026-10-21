# Backing up, verifying and restoring the local record

Everything in this skill so far reads the installation. This is the one area
that replaces it wholesale, so it is the one to slow down for.

```bash
future data backup  <new-directory>          # a full offline copy of this machine's record
future data verify  <backup-directory>       # check a copy before trusting it
future data restore <backup-directory> --yes # put it back, over this installation
future data resume                           # finish an interrupted restore
future data rollback                         # give up on one, back to the previous files
```

## What a backup actually holds

Both databases (the agent's `agent.db` and the desktop app's `app.db`), managed
attachments, workspaces and review data, legacy sources, and the Agent
configuration — **including credentials**. Treat the directory as being as
sensitive as the FutureOS home itself: never copy it somewhere shared, never
commit it, never paste its contents into a conversation.

It is a file copy, not a live snapshot: **stop Desktop, Agent and any other
writer first**, or the backup can catch a database mid-write.

## Restoring

- It targets the **original** FutureOS home; paths and user workspaces keep
  their original meaning rather than being rewritten for a different machine.
- It needs `--yes`; without it nothing is replaced.
- An **incomplete** restore fences startup — no Desktop or Agent will start from
  that home — until `future data resume` finishes it or `future data rollback`
  puts the previous files back. That fence is a safety net, not a broken build:
  report it as the state it is and offer the two exits.
- The previous files stay in the restore work directory **after** a successful
  restore too, so a restore is not the last word.
- Run `future data verify` on a backup before restoring from it, and read the
  backup's date to the user: restoring is measured in what is lost since then.

## What this is not

`future session delete` and `future session prune` are **not** backups, and
nothing in the CLI recovers a deleted session afterwards. If the user is about to
delete a lot of history, or asks whether it can be recovered, the honest answer
is: only from a `future data backup` taken before it. Offer the backup first
(`references/settings.md` covers the deletion commands themselves).

A backup is also not a sync: it is not a running replica, and the CLI has no
"back up nightly" switch — that is a scheduled task
(`future-scheduled-task`), if the user wants one.
