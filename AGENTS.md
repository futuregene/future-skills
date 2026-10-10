# Working in future-skills

FutureOS skill bundles. `builtin/` holds the shipped skills (one directory per skill, entry
point `SKILL.md`), `third-party/` curated external skills, and `skills.json` the registry
metadata FutureOS reads. This repository is checked out as the `skills` submodule of
[future-os](https://github.com/futuregene/future-os), and `~/.future/agent/skills/<name>` is
a symlink to `builtin/<name>`, so a change here reaches users only after it merges and the
future-os submodule pointer is bumped.

Several sessions work in this repository at the same time. Isolate every change in a
worktree under `.worktrees/` on a branch of its own, and never commit to `main`.

1. Branch from the current remote tip:
   `git fetch origin`, then
   `git worktree add --no-track .worktrees/<name> -b <type>/<name> origin/main`
   (`<type>` is `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `ci` or `chore`; `--no-track`
   keeps a plain `git push` from targeting `main`).
2. Edit, validate and commit inside the worktree. Re-fetch and merge `origin/main` before
   pushing, and re-run the checks the merge affects.
3. Push, open a PR against `main`, and let it squash-merge.
4. Clean up in the same session: `git worktree remove .worktrees/<name>`, delete the local and
   remote branch, `git worktree prune`, then fast-forward `main`
   (`git fetch origin && git merge --ff-only origin/main`).
5. Bump the pointer in the future-os repository so the shipped skills match:
   `git -C <future-os> submodule update --init --remote skills`, then commit and merge that
   pointer change there.

## Validating

The offline entry point needs PyYAML and no credentials; run it before opening a PR:

```bash
python -m pip install -r tests/requirements.txt
python tests/run_offline.py
```

It checks frontmatter, the registry, code fences and resource pointers, then runs the
deterministic skill regressions. Success is not evidence of model behavior or live APIs.

## Editing a skill

- One directory per skill under `builtin/`; `SKILL.md` needs `name` (equal to the directory
  slug), a semantic `version`, and a nonempty `description`.
- Bump `version` for behavior changes, and update `builtin/<name>/README.zh-CN.md` and
  `skills.json` when the entry itself changes.
- Every `references/`, `scripts/`, `assets/` or `tests/` path named in a skill must exist;
  `tests/check_builtin.py` verifies the pointers but not that a reference is linked from
  `SKILL.md`.
