# Agents

How Cursor agents work on this GRBL digitizing repo.

Too many specialists is counterproductive; **only organizer + verifier exist now.**

## Custom agents

| Agent | File | Role |
| --- | --- | --- |
| Repository Organizer | [`.cursor/agents/repository-organizer.md`](.cursor/agents/repository-organizer.md) | Inspect layout, classify work, plan small tasks, keep maps/README/`AGENTS.md` current, prevent overlapping edits |
| Verification specialist | [`.cursor/agents/verification-specialist.md`](.cursor/agents/verification-specialist.md) | After changes: run tests, check docs, Git status, report gaps |

Main Cursor chat → **Repository Organizer** → (later) GUI / Firmware / Documentation specialists, and **Verification specialist**.

Do not add GUI, firmware, or documentation specialist files until there is a distinct, recurring need. Invoke with `/repository-organizer` or `/verification-specialist`, or by asking in natural language. Descriptions are written so Agent can auto-delegate.

## Approval gates (Mike)

Do **not** independently:

- Move authoritative firmware
- Delete files
- Rewrite safety rules
- Merge competing changes

Ask permission before moving, deleting, or replacing authoritative files.

## Project rules for every agent

- This checkout is greenfield for the digitizer. Do not pretend firmware or UI code exists until it is in the tree.
- Do not invent a laptop app stack, GRBL/G-code, probe cycles, or approach paths.
- ID circle (inside of a hole) and OD circle (outside of a boss/cylinder) are separate routines. **ID increases the displayed value of the motion; OD shrinks it.** Offset is per strike and per direction.
- Authoritative measurement intent lives in the Cursor project store (`docs/probing-routines.md` there) until it is copied into this repo. Match it; do not generate probe sequences.
- Maintain [`docs/project-map.md`](docs/project-map.md) when the tree changes.
