# Version log

Running **requirements / goals / test** log for Mike’s GRBL digitizer.

This is paperwork, not product code. It does not implement GUI, USB, GRBL, or probe walks. Live copy: this file in git PR 4 **and** the Cursor project store `docs/version-log.md`.

## Who classifies

The **Project coordinator** classifies each bump as **patch**, **minor**, or **major**. **Mike does not classify.** **Mr. Fix-it does not bump** repo `VERSION` (he is woken separately on minor/major).

| Class | Pattern | Meaning | Wake Mr. Fix-it? |
| --- | --- | --- | --- |
| **Patch** | x.y.**Z** | Small fix or wording; no new capability | No sweep |
| **Minor** | x.**Z**.0 | New capability (new screen, routine family, integration) | Yes — whole system |
| **Major** | **Z**.y.0 | Breaking files / USB–GRBL / motion–DRO / DXF–capture | Definitely |

Repo `VERSION` lives on paperwork [PR 4](https://github.com/mikeerlandson3684-tech/CallBrief_agent/pull/4) (`cursor/preemptive-housekeeping-8f56`). Product GUI lives on [PR 6](https://github.com/mikeerlandson3684-tech/CallBrief_agent/pull/6) (`cursor/dxf-preview-c5e4`). Do not merge those PRs from this log.

## Every bump must update this log

When the coordinator bumps `VERSION`:

1. Classify patch / minor / major (rules above).
2. Add a **section on this page** or a **child file** under [`docs/iterations/`](iterations/) named `<VERSION>.md`.
3. Update the **index** below (class, goal, sheet link, product/paperwork PRs).
4. Point Mr. Fix-it and the verification specialist at the **current iteration sheet**. They **test against that sheet**, not against a remembered earlier slice.

Do not skip the sheet because the bump is “only paperwork.” The sheet is how later agents know what this VERSION was supposed to do.

## Index

| VERSION | Class | Goal | Sheet | Product code | Paperwork |
| --- | --- | --- | --- | --- | --- |
| **0.1.0** | start | Housekeeping only (organizer, verifier, Mr. Fix-it, `VERSION` file). No product GUI. | *(pre-log; no child sheet)* | — | [PR 4](https://github.com/mikeerlandson3684-tech/CallBrief_agent/pull/4) |
| **0.2.0** | **minor** | First paralyzed main window (PNG card-border layout around the envelope preview) | [`iterations/0.2.0.md`](iterations/0.2.0.md) | [PR 6](https://github.com/mikeerlandson3684-tech/CallBrief_agent/pull/6) `cursor/dxf-preview-c5e4` | [PR 4](https://github.com/mikeerlandson3684-tech/CallBrief_agent/pull/4) `VERSION` 0.2.0 |

Current sheet: **[`docs/iterations/0.2.0.md`](iterations/0.2.0.md)**.
