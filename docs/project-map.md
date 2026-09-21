# Project map

Maintained by the Repository Organizer. Reflects this git checkout only. Do not list firmware or GUI code that is not here yet.

## Tree

```
.
├── .cursor/agents/
│   ├── repository-organizer.md   # coordinates layout, planning, non-overlapping edits
│   └── verification-specialist.md  # tests, docs, Git status, gaps (read-only)
├── AGENTS.md                     # how agents work; approval gates
├── README.md                     # project entry
└── docs/
    └── project-map.md            # this file
```

No other project directories exist in this checkout.

## Agent tree (intended)

```
Main Cursor chat
  └── Repository Organizer
        ├── (later) GUI specialist
        ├── (later) Firmware specialist
        ├── (later) Documentation specialist
        └── Verification specialist
```

Only **organizer** and **verifier** exist now. Too many specialists is counterproductive.

## Authoritative specs (not in this git tree yet)

Measurement intent and stylus offset math: Cursor project store `docs/probing-routines.md` (ID increases displayed motion; OD shrinks it). Do not generate probe cycles.

When those specs are copied into this repo, add their paths here.

## Approval gates

Moving authoritative firmware, deleting files, rewriting safety rules, or merging competing changes requires Mike’s approval. Ask before moving, deleting, or replacing authoritative files.
