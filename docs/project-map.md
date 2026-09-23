# Project map

Maintained by the Repository Organizer. Reflects this git checkout only. Do not list firmware or GUI code that is not here yet.

## Tree

```
.
├── .cursor/agents/
│   ├── mr-fix-it.md              # Mr. Fix-it: isolate, report cause, then repair
│   ├── mr-grafix.md              # Mr. Grafix: graphic editing only; reports to Fix-it
│   ├── repository-organizer.md   # coordinates layout, planning, non-overlapping edits
│   └── verification-specialist.md  # tests, docs, Git status, gaps (read-only)
├── AGENTS.md                     # how agents work; approval gates; VERSION wake rules
├── README.md                     # project entry
├── VERSION                       # 0.2.0 minor: first paralyzed main window (PR 6)
└── docs/
    ├── fix-it-log.md             # Mr. Fix-it log book and last-known-good notes
    ├── project-map.md            # this file
    ├── version-log.md            # requirements/goals/test index; update on every VERSION bump
    └── iterations/
        └── 0.2.0.md              # current iteration sheet (test against this)
```

No firmware or product GUI in this checkout (product GUI is PR 6).

Mr. Fix-it and the verification specialist **test against the current iteration sheet**. Every `VERSION` bump must update `docs/version-log.md` and add a section or `docs/iterations/<VERSION>.md`.

## Agent tree (intended)

```
Main Cursor chat
  └── Repository Organizer
        ├── Mr. Fix-it
        │     └── Mr. Grafix          # graphics only; not a standing employee
        ├── (later) GUI specialist
        ├── (later) Firmware specialist
        ├── (later) Documentation specialist
        └── Verification specialist
```

**Organizer**, **verifier**, **Mr. Fix-it**, and **Mr. Grafix** exist now. Grafix reports to Fix-it for graphic tickets (not the coordinator). He is not a GUI specialist and not a standing employee. Too many specialists is counterproductive. No GUI, firmware, or documentation specialist files.

## Authoritative specs (not in this git tree yet)

Hardware (MKS DLC32 v2.1, TMC2209 V2.0 MKS, NEMA 17, 20T GT2, 3-pin NC probe, series NC limits per axis end, GRBL) and host path (USB laptop ↔ board; WiFi unused; **Python**; **Tkinter as the starting UI default**, not a forever lock): Cursor project store `docs/project-context.md`. Do not invent a different board, probe, limit scheme, or UI toolkit.

Measurement intent and stylus offset math: Cursor project store `docs/probing-routines.md` (3-pin NC digital touch probe; ID increases displayed motion; OD shrinks it). Do not generate probe cycles or change offset math.

Accuracy/precision (fail-closed, **not** a work-order): Cursor project store `docs/accuracy-gates.md`. Numeric capture/display **±0.002 in**. Visual close needs Mike. Agents do not close iteration-sheet rows. One lock cluster per pass.

**Version requirements/test log is in this tree:** [`docs/version-log.md`](version-log.md), current sheet [`docs/iterations/0.2.0.md`](iterations/0.2.0.md). Screenshots, GUI-direction specs, and accuracy gates remain in the store.

When remaining specs are copied into this repo, add their paths here.

## Approval gates

Moving authoritative firmware, deleting files, rewriting safety rules, or merging competing changes requires Mike’s approval. Ask before moving, deleting, or replacing authoritative files. **Visual lock close needs Mike** even after a Fix-it pass (store `docs/accuracy-gates.md`).
