# GRBL digitizing control UI

Probe-only 3-axis gantry: place it over an existing part, drive a digital probe in XYZ, log features, and write them to DXF at the measured coordinates. This is not a mill, lathe, or printer — it does not add or remove material.

Host: a **desktop program on the laptop**, connected **USB ↔ GRBL**. Board WiFi, if present, is unused for control in this iteration.

This git checkout is the digitizer project. It previously held only a CallBrief README placeholder. Application source is not here yet. Laptop app stack (language / UI toolkit) is **not chosen** — do not invent one.

## First slice (planned, not built)

Jog/move over USB, switch and probe inputs, homing, **ID circle** and **OD circle** as separate routines (center, diameter, top height), files, status, and DRO. Measurement intent and stylus offset math are in the store specs, not in generated G-code cycles.

## Authoritative specs

Product intent lives in the project store, not as a second copy in this repo:

- [`docs/project-context.md`](/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/project-context.md)
- [`docs/first-iteration-plan.md`](/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/first-iteration-plan.md)
- [`docs/probing-routines.md`](/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/probing-routines.md)

Repo layout: [`docs/project-map.md`](docs/project-map.md). How agents operate: [`AGENTS.md`](AGENTS.md).

## How to use the organizer

Custom Cursor subagents are in [`.cursor/agents/`](.cursor/agents/). Cursor can auto-delegate from their descriptions.

1. Start a request with **`/repository-organizer`** (or ask the agent to use the repository organizer).
2. The organizer inspects the tree and Git status, reads the specs, classifies the work (GUI / firmware / protocol / documentation / mixed), and returns a small plan.
3. It delegates non-overlapping tasks. Today the only other project subagent is **`/verification-specialist`** (read-only checks). There is no GUI, firmware, or docs specialist yet.
4. After claimed-complete work, run **`/verification-specialist`** before treating the change as done.

The organizer must ask before moving firmware, deleting files, rewriting safety rules, or merging competing changes. See [`AGENTS.md`](AGENTS.md) and [agent housekeeping](/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/agent-housekeeping.md).
