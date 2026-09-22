# Mr. Fix-it log book

Durable record of failures, last-known-good checkpoints, causes, and repairs for **Mr. Fix-it**.

Consult this **before guessing**. Newest entries first. Mirror the same entry in the Cursor project store `docs/mr-fix-it-log.md`.

Checkpoints here (and optional git tags `mr-fix-it/lkg-YYYY-MM-DD-<slug>`) are restore **references**. Do not rewrite history or force-push to “restore.”

## How to mark a checkpoint

When a slice is working (verification specialist agrees, or Mike confirms):

1. Add a **Last known good** row below: date, branch, full commit SHA, what worked, how verified.
2. Optionally: `git tag -a mr-fix-it/lkg-YYYY-MM-DD-<slug> -m "…"` on that commit; `git push origin <tag>` (never `--force`).
3. Do not move or delete tags without Mike’s approval.

## Last known good

| Date (UTC) | Git ref | Branch | What worked | Verified how |
| --- | --- | --- | --- | --- |
| — | — | — | None yet (housekeeping only; no product GUI/firmware on this branch) | — |

## Incidents

_None yet._

Template for a new incident (newest first):

```markdown
### YYYY-MM-DD — short title

- Stopped working / became erroneous:
- Last known good: (SHA / tag / dated note)
- Symptoms:
- Cause:
- Repair:
- Git: (branch, commit after repair)
```
