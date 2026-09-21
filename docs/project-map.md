# Project map

Current checkout vs intended layout for the GRBL digitizing control UI. This is a map, not a product spec. Authoritative intent lives in the project store (see below).

Do not invent a language, UI toolkit, or firmware tree. Do not create GUI or firmware directories until implementation starts.

## What exists today

The git remote is still `CallBrief_agent`. The tree is otherwise greenfield for the digitizer.

```
.
├── AGENTS.md                          # how agents work in this repo
├── README.md                          # digitizer overview (replaces CallBrief placeholder)
├── docs/
│   └── project-map.md                 # this file
└── .cursor/agents/
    ├── repository-organizer.md        # coordinator subagent
    └── verification-specialist.md     # read-only verifier
```

No host application source, no tests, no custom firmware tree.

### Duplicate / misplaced

- The original `README.md` described CallBrief (an AI call logger). That is leftover from the placeholder checkout, not digitizer documentation. The current `README.md` is the digitizer README.
- Product specs are **not** copied into this repo. They stay in the store so there is one source of truth.

## Intended layout (light; not created)

When work lands, keep it in separate lanes. Names below are roles, not a chosen stack:

| Lane | Intended home | Status |
| --- | --- | --- |
| Host GUI | a desktop-program tree (toolkit undecided) | greenfield |
| Firmware | only if this repo later versions GRBL config or controller notes | none; controller runs GRBL |
| Protocol / measurement intent | store docs listed below | written in the store |
| Repo agent + map docs | `AGENTS.md`, `docs/`, `.cursor/agents/` | present |
| Tests | beside whatever implementation lands | none yet |

Do not pre-seed `src/`, `firmware/`, `gui/`, or similar empty trees.

## Authoritative specs (project store)

These are outside the git tree:

- `/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/project-context.md`
- `/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/first-iteration-plan.md`
- `/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/probing-routines.md`
- `/cursor/stores/bc-27da14eb-edfa-4f35-8aee-7f9a35ad1e5c/docs/agent-housekeeping.md`

## File ownership for agents

- One agent edits a given file set at a time.
- Organizer may update this map when the layout actually changes.
- Verifier is read-only.
- Moving authoritative firmware, deleting files, rewriting safety rules, or merging competing changes requires Mike's approval first.

When GUI / firmware / docs specialist agents exist, assign those lanes separately. Today only organizer and verifier are defined.
