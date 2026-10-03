# Mr. Fix-it log book

Owned by **Mr. Fix-it**. Durable record of when things last worked, when they broke, and what changed.

Consult this **before guessing**. Newest entries first. Mirror the same entry in the git repo `docs/fix-it-log.md` (PR 4, `cursor/preemptive-housekeeping-8f56`).

Checkpoints = dated rows here and git tags at **minor/major** `VERSION` values (`vMAJOR.MINOR.PATCH`). Compare last-good vs now on integration hunts. Do not rewrite history or force-push to “restore.”

Repo `VERSION` is **0.2.0** (coordinator). Mr. Fix-it does not bump `VERSION`. Product GUI hunts run on PR 6 (`cursor/dxf-preview-c5e4`). Paperwork lives on PR 4.

## How to mark a checkpoint

When a slice is working (verification specialist agrees, or Mike confirms), and after a minor/major bump that still holds:

1. Add a **Last known good** row: date, `VERSION`, branch, full commit SHA, what worked, how verified.
2. Optionally: `git tag -a vMAJOR.MINOR.PATCH -m "…"` (and/or `mr-fix-it/lkg-YYYY-MM-DD-<slug>`); `git push origin <tag>` (never `--force`).
3. Do not move or delete tags without Mike’s approval.

## Last known good

| Date (UTC) | VERSION | Git ref | Branch | What worked | Verified how |
| --- | --- | --- | --- | --- | --- |
| 2026-09-23 | 0.2.0 (not bumped here) | `081bccd626a6c7861792132ed06acf5920ac04dd` | cursor/dxf-preview-c5e4 | Same as `b925a7c` plus complete inset `create_line` outline rings on cards/pills/chips (bottom+right included). Teal `#c5ece8` unchanged. Visual close still needs Mike. | Fix-it review pass: `media/low-k8-outlines-complete.png` crops (Status/Jog/Messages/Preview/Feature/FINISH/toolbar/jog/DRO/sim bar); `python3 -m pytest tests` — 41 passed (`test_chrome_outlines_close_on_all_four_sides`). Did not merge. Did not edit chrome. |
| 2026-09-23 | 0.2.0 (not bumped here) | `b925a7cd6dcf91b466864e60641419868b6773c9` | cursor/dxf-preview-c5e4 | Paralyzed shell + stadium pills (`95d4428`) + TealCard headers edge-to-edge (Grafix). No rectangular CARD_BG gutters on header or pill sides. Teal `#c5ece8` unchanged. | Fix-it review pass: `grafix-headers.png` vs `teal-rounded-shell.png`; pills in `button-cutout-fixed.png`; `python3 -m pytest tests` — 36 passed. Did not merge. Did not edit chrome. |
| 2026-09-23 | 0.2.0 (not bumped here) | `95d442889822b0e7dddc8f4cae9b6994f2ff19a2` | cursor/dxf-preview-c5e4 | Same paralyzed shell as below, plus stadium pills/cards/chips with no left/right canvas gutters. Teal `#c5ece8` unchanged. Clicks still log to Messages. Headers still gutted until `b925a7c`. | `python3 -m pytest tests` — 35 passed; widget dumps (canvas 1×1, polygon edge-to-edge, radius = half height); `media/button-cutout-fixed.png` |
| 2026-09-23 | 0.2.0 (coordinator classifies; git `VERSION` still on PR 4 at 0.1.0, not bumped here) | `8b274462a44ae6ab2da8c4dbd90b3fcc6e05e869` | cursor/dxf-preview-c5e4 | Paralyzed three-column Tkinter shell + envelope preview: ID/OD separate, Save/Close present, no Bridge chip, clicks log to Messages, GO TO/jog do not move, Z-circle grows with Z+, minsize 1180×840 keeps Jog Speed / Custom increment / Measured Diameter above the sim bar, DRO poll cancelled on destroy | `python3 -m pytest tests` — 32 passed; widget geometry at minsize; screenshots at default, minsize, zmin/zmax, sample captures, Hotkeys |
| — | 0.1.0 | — | cursor/preemptive-housekeeping-8f56 | Version started (housekeeping only; no product GUI/firmware on this branch) | Documented start; not a product LKG |

## Incidents

### 2026-09-23 — Fix-it review: Grafix complete outlines **pass**

- Reviewed: PR 6 `cursor/dxf-preview-c5e4` `081bccd626a6c7861792132ed06acf5920ac04dd`. Evidence `media/low-k8-outlines-complete.png`.
- Pass/fail: **pass** (geometry). Every checked card/control that should have an outline has a complete ring (all four sides + corner joins). Bottom and right are present on TealCards, PillButtons, RoundedFrame chips, Messages well, sim bar. Visual close still needs **Mike**.
- Checks: `stroke_round_rect` is a closed inset `create_line` (`STROKE_INSET` 1px), not an edge-hugging polygon stroke. Pytest `test_chrome_outlines_close_on_all_four_sides` + `test_safe_stroke_box_insets_every_side`; full `tests` — 41 passed. Pixel crops of Status/Jog BL+BR, Messages BR, DXF Preview bottom-right, Feature/Z/Datum/Incremental, Capture Feature, FINISH/Discard, toolbar, tabs, jog pads, DRO/GO TO chips, sim bar — no missing segment.
- Did not re-edit chrome. Did not merge.

### 2026-09-23 — Grafix: complete outline rings (reports to Fix-it)

- Last worked: header fill `b925a7cd6dcf91b466864e60641419868b6773c9` + title **Low-K8** `6f9db73` (did not revert).
- Broke at: rounded chrome `59e01e3` / `335775c` (`cursor/dxf-preview-c5e4`). Visible on Mike Try Live: outline **borders incomplete** (bottom and right straight segments missing most; not only those sides).
- What changed: `round_rect` stroke in `digitizer/chrome.py` only. Fill/header/pill stadiums unchanged. Teal `#c5ece8` unchanged. No GRBL/USB/files.
- Symptoms: card/pill/chip/DRO/preview/Messages/jog/tab rings dropped sides. Hollow Tk `create_polygon` outline on the canvas edge; X11 clips the last row/column so bottom+right vanish first, and corner joins can gap.
- Cause: polygon stroke at `(w-0.5, h-0.5)` is clipped; empty-fill polygon can also skip an edge.
- Repair (**Mr. Grafix**, graphics-only, reports to Mr. Fix-it): fill stays a polygon; visible ring is a **closed `create_line`** inset 1px (`STROKE_INSET`) on all four sides so corners join. Widgets checked: TealCards (DRO Position, Status, Jog, Feature, Capture, Z Control, Datum, Incremental, DXF Preview, Messages), PillButtons (tabs, toolbar, Initialized, GO TO, jog pad, ID/OD, Capture Feature, Z/Lock, Set DXF Origin, FINISH/Discard, Empty/Sample), RoundedFrame chips (DRO X/Y/Z, GO TO entries, Messages transcript, sim bar). Pytest 39 passed (`test_chrome_outlines_close_on_all_four_sides`; 46 rings, 0 missing sides on pixel sample). Did not merge.
- Git: `cursor/dxf-preview-c5e4` `081bccd626a6c7861792132ed06acf5920ac04dd` / https://github.com/mikeerlandson3684-tech/CallBrief_agent/pull/6
- Evidence: `media/low-k8-outlines-complete.png` (1280×840 full window, not a crop). Visual row stays **needs Mike accept**.

### 2026-09-23 — Fix-it review: Grafix header fill **pass**

- Reviewed: PR 6 `cursor/dxf-preview-c5e4` `b925a7cd6dcf91b466864e60641419868b6773c9` (headers) after pills `95d442889822b0e7dddc8f4cae9b6994f2ff19a2`.
- Pass/fail: **pass**. No rectangular background showing through header sides or pill sides.
- Checks: `grafix-headers.png` vs `teal-rounded-shell.png` — Status/Jog mid-header 4 px white `CARD_BG` gutters are gone; teal meets the rounded border. Pills in `button-cutout-fixed.png` / `grafix-headers.png` are stadiums to the widget edge (Capture Feature, FINISH PROBING, toolbar). `T.HEADER_BG` still `#c5ece8`. Pytest 36 passed (`test_teal_card_header_band_is_edge_to_edge`, `test_pill_buttons_fill_canvas_without_side_gutters`).
- Did not re-edit chrome. Did not merge. Did not change teal.

### 2026-09-23 — Grafix: TealCard header side gutters filled (reports to Fix-it)

- Last worked: pill stadium fill `95d442889822b0e7dddc8f4cae9b6994f2ff19a2` (pills already repaired; headers still gutted). Isolate: Fix-it handoff above.
- Broke at: PR 6 `59e01e3` / `335775c` (`cursor/dxf-preview-c5e4`). Visible on `media/teal-rounded-shell.png`.
- What changed: `TealCard` canvas header fill in `digitizer/chrome.py` only. **Did not revert** `PillButton` stadium fill.
- Symptoms: rectangular white `CARD_BG` gutters on left and right of every card header (Status / Jog / Messages / DRO Position / Feature / …) inside the rounded border. Teal `#c5ece8` was already correct (Mike).
- Cause: packed square header strip is inset by `_inset_for_radius`; parent `Configure` redrew `round_top_rect` before the strip had its real height (`hh` stuck at 22 px), so canvas teal never covered the side gutters.
- Repair (**Mr. Grafix**, graphics-only, reports to Mr. Fix-it): redraw on header `Configure`; paint a full-width teal band (`create_rectangle` + `round_top_rect`) down to the measured strip. Color stays `#c5ece8`. No GRBL/USB/files/probe cycles. Did not merge. PillButton code left as `95d4428`.
- Git: `cursor/dxf-preview-c5e4` `b925a7cd6dcf91b466864e60641419868b6773c9` / https://github.com/mikeerlandson3684-tech/CallBrief_agent/pull/6
- Evidence: `media/grafix-headers.png`. `python3 -m pytest tests` — 36 passed (`test_teal_card_header_band_is_edge_to_edge` plus existing pill test).

### 2026-09-23 — paralyzed GUI buttons missing a rectangular section on each side

- Last worked: teal chrome `335775c` (color accepted; shape not). Prior LKG `8b27446` (minsize/DRO). A Fix-it isolate pass logged the gutters and paused for a Grafix handoff; Mike then assigned Fix-it to repair.
- Broke at: PR 6 `59e01e3` / `335775c` (`cursor/dxf-preview-c5e4`) — canvas `PillButton` / `round_rect` chrome.
- What changed: Tkinter canvases drawing inset stadiums on a rectangular widget (default canvas size 378×265, highlight `#d9d9d9`, radius 12 not half-height). `TealCard` inner frames also left side gutters vs the rounded border.
- Symptoms: every paralyzed button has a rectangular area cut off on the left and right where the page/card background shows through. Shape error on all buttons. Press + Messages log still worked. Teal color was correct (Mike).
- Cause: rectangular canvas with the pill inset; leftover left/right strips are canvas/parent bg. Not GRBL/USB/files.
- Repair: stadium radius = half the short side; fill to the widget edge (outline inset 0.5 px); canvas `width=1`/`height=1` + `place` fill; `highlightbackground` = parent; inner inset keeps rectangular children inside the corners. Press still darkens/shrinks. No VERSION bump, no merge, teal `#c5ece8` untouched.
- Git: `cursor/dxf-preview-c5e4` `95d442889822b0e7dddc8f4cae9b6994f2ff19a2` / https://github.com/mikeerlandson3684-tech/CallBrief_agent/pull/6
- Evidence: `media/button-cutout-before.png`, `media/button-cutout-fixed.png`. `python3 -m pytest tests` — 35 passed.

### 2026-09-23 — header/button side cutouts isolated; chrome handoff to Grafix

- Last worked: teal rounded chrome on PR 6 `335775c6a26d22684171802764a73ff3e0bcda4d` (color accepted; shape not).
- Broke at: same commit (`cursor/dxf-preview-c5e4`). Visible on `media/teal-rounded-shell.png`.
- What changed: canvas `round_rect` / `round_top_rect` cards, pills, chips (`digitizer/chrome.py`).
- Symptoms: each header and pill has a **rectangular notch on left and right** where card/page background shows through (Status/Jog/Messages headers ~4 px white gutters inside the border; same family on toolbar pills, DRO chips, jog pads, Capture/FINISH buttons). Color is correct (teal `#c5ece8`).
- Cause: `TealCard` header/body are inset by `_inset_for_radius` so a square teal strip does not reach the rounded card edges; canvas `round_top_rect` does not fill those side gutters, so `CARD_BG` shows through. Same chrome path on `PillButton` / `RoundedFrame`.
- Repair: **none from Fix-it.** Mike assigned **Mr. Grafix** (graphics-only, reports to Fix-it) to implement header fill on PR 6. Fix-it did not edit cards/headers/pills/buttons. Tree left clean on `335775c`. Idle until Grafix lands; then review as Fix-it (non-graphic bugs still ours). Teal stays. Did not merge.
- Git: `cursor/dxf-preview-c5e4` `335775c6a26d22684171802764a73ff3e0bcda4d` / https://github.com/mikeerlandson3684-tech/CallBrief_agent/pull/6 (unchanged)

### 2026-09-23 — paralyzed main window minsize clips footer; DRO poll leaks on destroy

- Last worked: no product LKG (0.1.0 housekeeping only). Preview commits `edf9eea` / `dda7ce7` were geometry-only.
- Broke at: PR 6 `1ec4b9adcbd317986d99cb205fe3212bf15dfb5e` (`cursor/dxf-preview-c5e4`) — first paralyzed shell, coordinator classifying this as minor **0.2.0**.
- What changed: Tkinter three-column shell (`digitizer/main_window.py`) around the live envelope preview.
- Symptoms:
  1. Window `minsize(1180, 760)` lets the operator shrink below the layout. At **760** px height, **Jog Speed**, **Custom increment**, and **Measured Diameter** leave the client (covered or clipped). At **800** px, Measured Diameter is still hidden under the simulated-position bar. Default **1280×840** is fine. At minsize **width 1180**, Incremental hint clips to `Not GO T` (`wraplength=360` wider than the card).
  2. Destroying the window prints `invalid command name "…_poll_dro"` (`after` script). `_poll_dro` is not cancelled (preview polling is).
- Cause: `minsize` height is 40–60 px short of the packed cards + bottom sim bar. Hint labels use a fixed wraplength. DRO poll is `after(50, self._poll_dro)` with no job id / `after_cancel` in `destroy`.
- Intended repair (PR 6 only, no features, no VERSION bump): raise minsize height so footer controls stay above the sim bar; bind hint `wraplength` to the label width; cancel the DRO `after` job on destroy; add a regression test.
- Repair: `minsize(1180, 840)`; `_bind_wraplength` on Feature/Incremental hints; `_dro_job` + `destroy()` `after_cancel`; tests for footer-above-sim-bar, wraplength, and destroy. Did not bump `VERSION`. Did not merge. Did not touch PR 4.
- Git: `cursor/dxf-preview-c5e4` `8b274462a44ae6ab2da8c4dbd90b3fcc6e05e869` / https://github.com/mikeerlandson3684-tech/CallBrief_agent/pull/6

Sweep (not bugs): ID/OD are separate; no Bridge/COM chip; Save/Close present; clicks log `{name} pressed`; GO TO/jog/Capture/Finish do not move SimulatedPosition or write files; preview Z-circle grows with Z+ / shrinks with Z− (zmin width 11.35 px, zmax 36.32 px); no serial/G38/G90/G91/walks. After repair: `python3 -m pytest tests` — 32 passed. PR 6 has no `docs/fix-it-log.md`; not adding one. PR 4 not touched. No `v0.2.0` tag (VERSION file lives on PR 4).

Template (newest first):

```markdown
### YYYY-MM-DD — short title

- Last worked: (VERSION / tag / SHA)
- Broke at: (VERSION / SHA / date)
- What changed:
- Symptoms:
- Cause:
- Repair:
- Git: (branch, commit after repair)
```
