# Agent instructions — GRBL digitizing control UI

This repository is Mike E's **probe-only** 3-axis GRBL gantry digitizer (desktop host over USB). It is not a mill, lathe, printer, or the leftover CallBrief logger described in the original README.

Do not invent a laptop app stack, GRBL/G-code probe cycles, approach paths, or WCS/work-offset math. Digitizer GUI and firmware are not in this checkout yet.

## How agents work here

Cursor custom subagents live in [`.cursor/agents/`](.cursor/agents/) (see [Cursor subagents](https://cursor.com/docs/subagents)). The parent agent can auto-delegate from each file's `description`, or you can invoke by name (`/repository-organizer`, `/verification-specialist`).

| Agent | File | Role |
| --- | --- | --- |
| **repository-organizer** | [`.cursor/agents/repository-organizer.md`](.cursor/agents/repository-organizer.md) | Classify work, plan, prevent overlapping edits, keep maps current. Does not implement GUI/firmware. |
| **verification-specialist** | [`.cursor/agents/verification-specialist.md`](.cursor/agents/verification-specialist.md) | Read-only check that claimed work matches protocol, tests, and docs. Does not implement. |

No GUI, firmware, or documentation specialist agents exist yet. Do not add them unless Mike asks. Until they exist, the organizer plans and the parent (or a later specialist) implements; the verifier checks.

Layout and what exists vs greenfield: [`docs/project-map.md`](docs/project-map.md).

### Organizer workflow

1. Inspect repository structure and Git status.
2. Read this file and the authoritative specs below.
3. Classify: GUI, firmware, protocol, documentation, or mixed.
4. Produce a small work plan.
5. Delegate isolated tasks when useful (today: organizer + verifier only).
6. Prevent overlapping edits (one agent per file set).
7. Check implementation against the motion/probe protocol.
8. Run available verification, or hand to `/verification-specialist`.
9. Report changed files, test results, and unresolved risks.
10. Ask permission before moving, deleting, or replacing authoritative files.

## Approval gates (ask Mike first)

The organizer must **not** independently:

- Move authoritative firmware
- Delete files
- Rewrite safety rules
- Merge competing changes

Those need Mike's approval.

## Authoritative specifications

Store docs are the source of truth for product intent. Repo files point here; they do not replace these:

- [`/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/project-context.md`](/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/project-context.md)
- [`/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/first-iteration-plan.md`](/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/first-iteration-plan.md)
- [`/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/probing-routines.md`](/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/probing-routines.md)

Agent arrangement (user-facing): [`/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/agent-housekeeping.md`](/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/agent-housekeeping.md).

## Protocol reminders (do not relax)

- **ID circle** = inside of a hole. **OD circle** = outside of a boss/cylinder. Separate routines, not a toggle.
- Stylus **diameter** is operator input; **radius = diameter / 2**; tool offset on a hidden layer; **per probe strike and per direction**.
- **ID increases the displayed value of the motion. OD shrinks the displayed value of the motion.**
- Capture/export must stay routine-agnostic. Do not generate find-sequences or fancy approach paths.
- Host is a **desktop program on the laptop**, USB to GRBL. Board WiFi is not the v1 control path.
- Location derivation follows DRO / work-coordinate output once that exists — do not invent GRBL WCS.

## After changes

Check Git status before and after. Confirm tests (when they exist) and required documentation were updated. Hand the result to `/verification-specialist` before calling the work done.
