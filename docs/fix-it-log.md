# Mr. Fix-it log book

Owned by **Mr. Fix-it**. Durable record of when things last worked, when they broke, and what changed.

Consult this **before guessing**. Newest entries first. Mirror the same entry in the Cursor project store `docs/fix-it-log.md`.

Checkpoints = dated rows here and git tags at **minor/major** `VERSION` values (`vMAJOR.MINOR.PATCH`). Compare last-good vs now on integration hunts. Do not rewrite history or force-push to “restore.”

`VERSION` starts at **0.1.0**. Coordinator or Mike bump it. Patch → do not wake a full-system look. Minor → full-system look. Major → definitely full-system look.

## How to mark a checkpoint

When a slice is working (verification specialist agrees, or Mike confirms), and after a minor/major bump that still holds:

1. Add a **Last known good** row: date, `VERSION`, branch, full commit SHA, what worked, how verified.
2. Optionally: `git tag -a vMAJOR.MINOR.PATCH -m "…"` (and/or `mr-fix-it/lkg-YYYY-MM-DD-<slug>`); `git push origin <tag>` (never `--force`).
3. Do not move or delete tags without Mike’s approval.

## Last known good

| Date (UTC) | VERSION | Git ref | Branch | What worked | Verified how |
| --- | --- | --- | --- | --- | --- |
| — | 0.1.0 | — | cursor/preemptive-housekeeping-8f56 | Version started (housekeeping only; no product GUI/firmware on this branch) | Documented start; not a product LKG |

## Incidents

_None yet._

Template (newest first):

```markdown
### YYYY-MM-DD — short title

- Last worked: (VERSION / tag / SHA)
- Broke at: (VERSION / SHA / date)
- What changed:
- Symptoms:
- Cause:
- Repair:
- Git: (branch, commit after repair)
```
