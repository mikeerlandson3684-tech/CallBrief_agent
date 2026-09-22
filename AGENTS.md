# Agents

How Cursor agents work on this GRBL digitizing repo.

Too many specialists is counterproductive; **only organizer + verifier + Mr. Fix-it exist now.**

## Custom agents

| Agent | File | Role |
| --- | --- | --- |
| Repository Organizer | [`.cursor/agents/repository-organizer.md`](.cursor/agents/repository-organizer.md) | Inspect layout, classify work, plan small tasks, keep maps/README/`AGENTS.md` current, prevent overlapping edits |
| Mr. Fix-it | [`.cursor/agents/mr-fix-it.md`](.cursor/agents/mr-fix-it.md) | Integration bugs (GUI + GRBL/USB + preview + files): consult log book, isolate, report the cause, then repair. Invoke `/mr-fix-it` or ask for Mr. Fix-it |
| Verification specialist | [`.cursor/agents/verification-specialist.md`](.cursor/agents/verification-specialist.md) | After changes: run tests, check docs, Git status, report gaps |

Main Cursor chat → **Repository Organizer** → **Mr. Fix-it**, (later) GUI / Firmware / Documentation specialists, and **Verification specialist**.

Do not add GUI, firmware, or documentation specialist files until there is a distinct, recurring need. Invoke with `/repository-organizer`, `/mr-fix-it`, or `/verification-specialist`, or by asking in natural language. Descriptions are written so Agent can auto-delegate.

Mr. Fix-it owns [`docs/fix-it-log.md`](docs/fix-it-log.md) (and the store copy). He must read it before guessing. Checkpoints are last-known-good notes and git tags at minor/major [`VERSION`](VERSION) values — not a license to rewrite history or force-push.

## Wake Mr. Fix-it on the whole system

Current version: [`VERSION`](VERSION) (starts at **0.1.0**). **Mike or the Project coordinator decide the bump.** Mr. Fix-it does not bump `VERSION`. He runs version-sweeps on **minor and major only**.

- **Patch** (e.g. 13.2.1 → 13.2.2): do **not** wake him.
- **Minor** (e.g. 13.2.x → 13.3.0): **do** turn him loose on the whole system.
- **Major** (e.g. → 14.0.0): **definitely**.

On minor/major, tag or log a checkpoint (`vMAJOR.MINOR.PATCH`) so he can compare last-good vs now. Bugs, exceptions, and “it doesn’t work” still go to Mr. Fix-it even between bumps.

## Approval gates (Mike)

Do **not** independently:

- Move authoritative firmware
- Delete files
- Rewrite safety rules
- Merge competing changes

Ask permission before moving, deleting, or replacing authoritative files.

## Project rules for every agent

- This checkout is greenfield for the digitizer. Do not pretend firmware or UI code exists until it is in the tree.
- Hardware is decided: MakerBase MKS DLC32 v2.1, TMC2209 V2.0 MKS, NEMA 17, 20 tooth GT2, 3-pin NC digital touch probe, two NC micro switches in series on each end of all 3 axes, GRBL. v1 control is USB laptop ↔ board (WiFi unused). Do not invent a different board, probe, or limit scheme. Detail: Cursor project store `docs/project-context.md`.
- Language is **Python**; **Tkinter is the starting UI default** (not a forever lock; do not treat Qt, WPF, or other toolkits as chosen). Do not invent a different stack, GRBL/G-code, probe cycles, or approach paths.
- ID circle (inside of a hole) and OD circle (outside of a boss/cylinder) are separate routines. **ID increases the displayed value of the motion; OD shrinks it.** Offset is per strike and per direction.
- Authoritative measurement intent lives in the Cursor project store (`docs/probing-routines.md` there) until it is copied into this repo. Match it; do not generate probe sequences. Probe hardware there is a 3-pin NC digital touch probe; do not change offset math.
- Maintain [`docs/project-map.md`](docs/project-map.md) when the tree changes.
