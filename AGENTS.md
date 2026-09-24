# Agents

How Cursor agents work on this GRBL digitizing repo.

Too many specialists is counterproductive; **organizer + verifier + Mr. Fix-it + Mr. Grafix + Mr. Motion** exist now. Grafix is graphics-only and **not** a standing employee. **Mr. Motion** is graphics-none (motion/LS rules) and **not** a standing employee. Do not add a GUI, firmware, or documentation specialist. Do **not** rename Mr. Motion.

## Custom agents

| Agent | File | Role |
| --- | --- | --- |
| Repository Organizer | [`.cursor/agents/repository-organizer.md`](.cursor/agents/repository-organizer.md) | Inspect layout, classify work, plan small tasks, keep maps/README/`AGENTS.md` current, prevent overlapping edits |
| Mr. Fix-it | [`.cursor/agents/mr-fix-it.md`](.cursor/agents/mr-fix-it.md) | Whole-system integration (preview, USB/GRBL, GUI, files). May dispatch or review Grafix for chrome and **Mr. Motion** for motion/LS rules; still owns non-graphic bugs. PR 4 only stores this instruction file. Invoke `/mr-fix-it` or ask for Mr. Fix-it |
| Mr. Grafix | [`.cursor/agents/mr-grafix.md`](.cursor/agents/mr-grafix.md) | Graphic editing only (cards, headers, pills, chips, mockup match, rounded fill, cutouts). Reports to Mr. Fix-it, not the coordinator. Invoke `/mr-grafix` only when Mike asks or the iteration sheet has a visual row |
| Mr. Motion | [`.cursor/agents/mr-motion.md`](.cursor/agents/mr-motion.md) | Motion rules, LS/homing-routine precheck, allowed-jog table. Graphics-none. Reports to Mr. Fix-it. Invoke `/mr-motion` only when Mike asks or the iteration sheet has a motion/LS row. Do not rename |
| Verification specialist | [`.cursor/agents/verification-specialist.md`](.cursor/agents/verification-specialist.md) | After changes: run tests, check docs, Git status, report gaps |

Main Cursor chat → **Repository Organizer** → **Mr. Fix-it** (who may dispatch **Mr. Grafix** for chrome and **Mr. Motion** for motion/LS rules), (later) GUI / Firmware / Documentation specialists, and **Verification specialist**.

Do not add GUI, firmware, or documentation specialist files until there is a distinct, recurring need. **Mr. Grafix is not that GUI specialist.** **Mr. Motion is not a firmware specialist.** Invoke with `/repository-organizer`, `/mr-fix-it`, `/mr-grafix`, `/mr-motion`, or `/verification-specialist`, or by asking in natural language. Descriptions are written so Agent can auto-delegate.

Mr. Fix-it owns [`docs/fix-it-log.md`](docs/fix-it-log.md) (and the store copy). He must read it before guessing. Graphic isolate/repair from Grafix and motion-rules audits from **Mr. Motion** go in that same log. Checkpoints are last-known-good notes and git tags at minor/major [`VERSION`](VERSION) values — not a license to rewrite history or force-push.

**PR 4 only stores instruction files** (`.cursor/agents/mr-fix-it.md`, `.cursor/agents/mr-grafix.md`, `.cursor/agents/mr-motion.md`). Mr. Fix-it’s **scope is the whole digitizer system** (preview, USB/GRBL, GUI, files, integration), not this housekeeping PR. When woken, he inspects whatever is actually in play, including product code on other branches/PRs such as the preview.

## Wake Mr. Grafix (graphics only)

Reports to **Mr. Fix-it**, not the coordinator, for graphic tickets. Wake **only** when Mike asks for a graphic edit, or the current iteration sheet has a visual row / graphic miss. Not a standing employee. Color only when Mike locks it. First job (already assigned on PR 6, do not implement on this PR): header side cutouts.

Do **not** send Grafix GRBL/USB/wiring, probe cycles, version classification, whole-system sweeps, merging PRs, or deleting files.

## Wake Mr. Motion (motion rules only)

Reports to **Mr. Fix-it**, not the coordinator. Graphics-none. Owns motion rules, LS/homing-routine precheck, allowed-jog table, and auditing those rules against the current iteration sheet. Store spec: `docs/motion-rules.md`. **Do not rename this agent.**

Wake **only** when Mike asks, or the current iteration sheet has a motion/LS row. Not a standing employee. Does **not** invent probe cycles, implement GRBL, recode the GUI, or merge PRs.

H4 precheck and the per-axis table are Mike **OK**. Home is a location. An LS is pressed/cleared. Never write “Home is pressed.”

## Wake Mr. Fix-it on the whole system

Current version: [`VERSION`](VERSION) (**0.2.0**). **0.2.0** is a **minor** bump: first paralyzed main window (new screen on PR 6). **The Project coordinator decides patch vs minor vs major. Mike does not classify.** Mr. Fix-it does not bump `VERSION`. He runs version-sweeps on **minor and major only** (woken separately for 0.2.0). **Every `VERSION` bump must update [`docs/version-log.md`](docs/version-log.md)** (index + section or [`docs/iterations/<VERSION>.md`](docs/iterations/0.2.0.md)). **Mr. Fix-it and the verification specialist test against the current iteration sheet.**

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

Ask permission before moving, deleting, or replacing authoritative files. **Visual lock close needs Mike** even after a Fix-it pass (store `docs/accuracy-gates.md`).

## Accuracy gates (fail-closed)

Not a work-order system. Full rules: Cursor project store `docs/accuracy-gates.md`. Locks live on the **current iteration sheet**.

- A sheet row is **fail until evidence**. **Partial is not shippable.**
- Do not tell Mike a lock is met without evidence in hand (screenshot path, pytest, measurement). “Looks good” / “Tk approximation” is fail.
- Visual: screenshot vs mockup/sheet. **Mike’s Try Live / eye rejects even if Fix-it passed.** 0.2.0 visual (rounded fill, no gutters) stays open until Mike accepts.
- Numeric: captured or displayed length/position **±0.002 in** unless Mike sets another. Tests must assert that tolerance. No eyeball numbers.
- Changed locks: update the iteration sheet **first**, then code. Chat memory is not the spec.
- Grafix = graphics only (reports to Fix-it). **Mr. Motion** = motion/LS rules (reports to Fix-it; graphics-none). Fix-it = non-graphic bugs + review. Verifier = test against the current sheet. **None of them close a row**; coordinator closes only with evidence; **visual close needs Mike**.
- One lock cluster per pass, not the whole window.

## Project rules for every agent

- Product name is **Low-K8** (that spelling). Do not rename the `digitizer` package. Do not invent other product names.
- This checkout is greenfield for the digitizer. Do not pretend firmware or UI code exists until it is in the tree.
- Hardware is decided: MakerBase MKS DLC32 v2.1, TMC2209 V2.0 MKS, NEMA 17, 20 tooth GT2, 3-pin NC digital touch probe, two NC micro switches in series on each end of all 3 axes, GRBL. v1 control is USB laptop ↔ board (WiFi unused). Do not invent a different board, probe, or limit scheme. Detail: Cursor project store `docs/project-context.md`. Motion/LS rules: store `docs/motion-rules.md`. **Home is a location.** An LS is pressed/cleared. Never “Home is pressed.”
- Language is **Python**; **Tkinter is the starting UI default** (not a forever lock; do not treat Qt, WPF, or other toolkits as chosen). Do not invent a different stack, GRBL/G-code, probe cycles, or approach paths.
- ID circle (inside of a hole) and OD circle (outside of a boss/cylinder) are separate routines. **ID increases the displayed value of the motion; OD shrinks it.** Offset is per strike and per direction.
- Authoritative measurement intent lives in the Cursor project store (`docs/probing-routines.md` there) until it is copied into this repo. Match it; do not generate probe sequences. Probe hardware there is a 3-pin NC digital touch probe; do not change offset math.
- Maintain [`docs/project-map.md`](docs/project-map.md) when the tree changes.
