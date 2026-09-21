# GRBL digitizing control

Probe-only 3-axis gantry control for capturing existing part features and writing them to DXF. Not a mill, lathe, or printer.

This git checkout is **greenfield**. There is no firmware tree or GUI application here yet — only project housekeeping so later work stays organized.

## Hardware (v1, decided)

- MakerBase MKS DLC32 v2.1, GRBL
- TMC2209 V2.0 MKS drivers, NEMA 17, 20 tooth GT2 pulleys
- 3-pin NC digital touch probe
- Two NC micro switches in series on each end of all 3 axes (5V; which end was hit is inferred from motion direction at the strike)
- USB laptop ↔ board (DLC32 WiFi unused)

Desktop program on the laptop: **Python**, with **Tkinter as the starting UI default** (not a forever lock; Qt/WPF/etc. are not chosen). Full stack: Cursor project store `docs/project-context.md`.

## Agents

How agents work on this repo: [`AGENTS.md`](AGENTS.md)

Custom agents (organizer + verifier only):

- [`.cursor/agents/repository-organizer.md`](.cursor/agents/repository-organizer.md)
- [`.cursor/agents/verification-specialist.md`](.cursor/agents/verification-specialist.md)

Current layout: [`docs/project-map.md`](docs/project-map.md)
