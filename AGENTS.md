# Agents

How Cursor agents work on this GRBL digitizing repo.

Too many specialists is counterproductive; **only organizer + verifier + Mr. Fix-it exist now.**

## Custom agents

| Agent | File | Role |
| --- | --- | --- |
| Repository Organizer | [`.cursor/agents/repository-organizer.md`](.cursor/agents/repository-organizer.md) | Inspect layout, classify work, plan small tasks, keep maps/README/`AGENTS.md` current, prevent overlapping edits |
| Mr. Fix-it | [`.cursor/agents/mr-fix-it.md`](.cursor/agents/mr-fix-it.md) | Whole-system integration (preview, USB/GRBL, GUI, files). PR 4 only stores this instruction file. Invoke `/mr-fix-it` or ask for Mr. Fix-it |
| Verification specialist | [`.cursor/agents/verification-specialist.md`](.cursor/agents/verification-specialist.md) | After changes: run tests, check docs, Git status, report gaps |

Main Cursor chat → **Repository Organizer** → **Mr. Fix-it**, (later) GUI / Firmware / Documentation specialists, and **Verification specialist**.

Do not add GUI, firmware, or documentation specialist files until there is a distinct, recurring need. Invoke with `/repository-organizer`, `/mr-fix-it`, or `/verification-specialist`, or by asking in natural language. Descriptions are written so Agent can auto-delegate.

Mr. Fix-it owns [`docs/fix-it-log.md`](docs/fix-it-log.md) (and the store copy). He must read it before guessing. Checkpoints are last-known-good notes and git tags at minor/major [`VERSION`](VERSION) values — not a license to rewrite history or force-push.

**PR 4 only stores Mr. Fix-it’s instruction file** (`.cursor/agents/mr-fix-it.md`). His **scope is the whole digitizer system** (preview, USB/GRBL, GUI, files, integration), not this housekeeping PR. When woken, he inspects whatever is actually in play, including product code on other branches/PRs such as the preview.

## Wake Mr. Fix-it on the whole system

Current version: [`VERSION`](VERSION) (**0.2.0**). **0.2.0** is a **minor** bump: first paralyzed main window (new screen on PR 6). **The Project coordinator decides patch vs minor vs major. Mike does not classify.** Mr. Fix-it does not bump `VERSION`. He runs version-sweeps on **minor and major only** (woken separately for 0.2.0).

How the coordinator classifies:

- **Patch** (x.y.Z, e.g. 13.2.1 → 13.2.2) — small fix, wording, no new capability. Do **not** wake Mr. Fix-it for a sweep.
- **Minor** (x.Z.0, e.g. 13.2.x → 13.3.0) — new capability (new screen, new routine family, new integration). **Do** wake Mr. Fix-it on the whole system.
- **Major** (Z.y.0, e.g. → 14.0.0) — breaking change to files, USB/GRBL contract, motion/DRO meaning, or DXF/capture format. **Definitely** wake Mr. Fix-it.

On minor/major, tag or log a checkpoint (`vMAJOR.MINOR.PATCH`) so he can compare last-good vs now across the **whole system** (not only PR 4). Bugs, exceptions, and “it doesn’t work” still go to Mr. Fix-it even between bumps.

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
