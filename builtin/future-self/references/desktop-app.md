# The desktop app's store: settings and workspaces

The FutureOS desktop app keeps its own records in `~/.future/app/app.db`. Two
tables matter here: `app_settings` (the app's preferences) and `workspaces` (the
directories workspace conversations are filed under). They are neither the
agent's settings document (`future config`, `~/.future/agent/settings.json`) nor
the models/providers/auth files, which the app and the agent share.

Both are readable and writable from the CLI with **no running desktop app**, and
the app picks a change up on its next read.

> **Both commands ignore `FUTURE_HOME`.** They target the real
> `~/.future/app/app.db` under the home directory, exactly as the app does, so a
> session running under another `FUTURE_HOME` still writes the real app
> database. That is the right file for a question about the app — but it is not
> the isolated installation the rest of this skill scopes to.

## The app's preferences

```bash
future desktop settings                       # everything, defaults included
future desktop settings get approvalTier      # one value, bare
future desktop settings set approvalTier manual
future desktop settings set hiddenModels "future/glm-5.3, future/kimi-k3"
```

Keys use the camelCase spelling of the desktop API, and `future desktop --help`
lists every key with its accepted values. **Every preference the app's own
Settings screen can change is settable here**, so the CLI covers what the GUI
covers. A list value is a JSON array or a comma-separated list; values are
validated before the database is touched; and a database the app has never
written reports the defaults rather than being created. A running app picks the
change up the next time it reads the settings; a change made in its own Settings
screen applies immediately.

A desktop-app preference is diagnosed the same way as a global one: read it with
`future desktop settings get <key>`, then check the shared schema in
`packages/app-settings/src/lib.rs` (`source.md`) before blaming the value.

## Workspaces

A **workspace** is the directory a workspace conversation is filed under (a chat
conversation brings its own temporary directory instead and needs none). Its
records are the app's, which is why a workspace added from the terminal shows up
in the desktop app's sidebar and on a paired phone — the app republishes its
catalogue on its next tick.

```bash
future workspace list                 # the user's own workspaces
future workspace list --json
future workspace add ~/projects/demo  # register an existing directory
future workspace add /srv/app --name "Service"
```

- **The directory must already exist.** A workspace points at a directory; it
  does not create one. A path that is missing or is not a directory is refused
  with the store's own reason and nothing is written.
- **One directory is one workspace**, however the path is spelled: `~`, a
  symlinked path and a trailing separator all resolve to the same row, by
  canonical path. `add` on a directory that already has a workspace **reopens**
  it rather than adding a second one.
- **The name defaults to the directory's own name.** Reopening keeps the stored
  name, not the one just passed in.
- **`add` says which case it was**, which is what makes it safe to run twice:
  `Added workspace <name> (<id>)` versus `already covers this directory`, or
  `"created": true|false` with `--json`.

`--json` returns the workspace record itself (`id`, `name`, `kind`, `path`,
`pinned`, timestamps — the same shape the phone receives) plus `created` and the
`database` path it wrote to. `list` returns an array of those records, the user's
own workspaces only: the app's chat scratch directories live in the same table
and are filtered out.

Workspaces also appear without `add`: **`future session set <id> --cwd <dir>`
files that conversation under the directory's workspace**, the same way the
desktop app does when it observes a cwd change. So the desktop-side record no
longer depends on the app being open at the moment of the change. The command
reports the outcome in its output (`workspace: created "name" for <path>` /
`workspace: filed under …`, or `notes` with `--json`), and a directory that does
not exist is a note rather than a failure — the agent-side cwd change really did
happen, and the fix is the one the note names.

> `future workspace` manages the **desktop app's** records. A session's working
> directory is an agent-side property (`future session set <id> --cwd`); setting
> it is what files the conversation, and the app derives a workspace row by the
> same rule when it imports an agent session.

Where the code splits, if a question goes deeper: the table and the rules are
`packages/app-workspaces/src/lib.rs`, the schema is
`desktop/src-tauri/src/store/schema.rs`, the app's own read/write path is
`desktop/src-tauri/src/store/workspaces.rs`, and the phone's copy of the
creation flow is `remote_host/business/catalog.rs` (command
`create_workspace`, mobile-side `mobile/src/remote/useSessionCatalog.ts`).
