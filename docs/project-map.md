# Project map

Maintained by the Repository Organizer. Reflects this git checkout only. Do not list firmware or GUI code that is not here yet.

## Tree

```
.
├── .cursor/agents/
│   ├── mr-fix-it.md              # Mr. Fix-it: isolate, report cause, then repair
│   ├── repository-organizer.md   # coordinates layout, planning, non-overlapping edits
│   └── verification-specialist.md  # tests, docs, Git status, gaps (read-only)
├── AGENTS.md                     # how agents work; approval gates
├── README.md                     # project entry
└── docs/
    ├── mr-fix-it-log.md          # Mr. Fix-it log book and last-known-good notes
    └── project-map.md            # this file
```

No other project directories exist in this checkout.

## Agent tree (intended)

```
Main Cursor chat
  └── Repository Organizer
        ├── Mr. Fix-it
        ├── (later) GUI specialist
        ├── (later) Firmware specialist
        ├── (later) Documentation specialist
        └── Verification specialist
```

Only **organizer**, **verifier**, and **Mr. Fix-it** exist now. Too many specialists is counterproductive. No GUI, firmware, or documentation specialist files.

## Authoritative specs (not in this git tree yet)

Hardware (MKS DLC32 v2.1, TMC2209 V2.0 MKS, NEMA 17, 20T GT2, 3-pin NC probe, series NC limits per axis end, GRBL) and host path (USB laptop ↔ board; WiFi unused; **Python**; **Tkinter as the starting UI default**, not a forever lock): Cursor project store `docs/project-context.md`. Do not invent a different board, probe, limit scheme, or UI toolkit.

Measurement intent and stylus offset math: Cursor project store `docs/probing-routines.md` (3-pin NC digital touch probe; ID increases displayed motion; OD shrinks it). Do not generate probe cycles or change offset math.

When those specs are copied into this repo, add their paths here.

## Approval gates

Moving authoritative firmware, deleting files, rewriting safety rules, or merging competing changes requires Mike’s approval. Ask before moving, deleting, or replacing authoritative files.
