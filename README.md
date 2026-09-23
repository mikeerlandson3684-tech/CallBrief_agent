# GRBL digitizing control

Probe-only 3-axis gantry: drive a digital probe in XYZ, log features, write DXF. Not a mill, lathe, or printer.

Language is **Python**. UI toolkit is **Tkinter as the starting default** (not a forever lock; Qt/WPF are not chosen).

## This slice — paralyzed main window + DXF preview

Full main GUI around the existing envelope-scaled preview. Controls are **clickable and show a press**; they log `"{name} pressed"` in Messages. No GRBL, no USB, no probe cycles, no GO TO motion, no file I/O. The preview Z-circle and grid stay live via simulated XYZ sliders.

### How to run

Needs Python 3.11+ with Tkinter (`python3-tk` on Debian/Ubuntu).

```bash
python3 -m digitizer
```

Optional:

```bash
python3 -m digitizer --sample          # show demo ID/OD captures on the preview
python3 -m digitizer --preview-only    # older standalone preview demo
python3 -m pytest tests                # geometry + widget tests
```

Toolbar includes **Save** and **Close** (decided; omitted from the mockup PNG). **Bridge: COMx** is dropped. Feature entry is **ID Circle** and **OD Circle** as separate paralyzed controls (no Circle/Rectangle toggle, no Inner/Outer finder). Stylus diameter is not on this screen. **Hotkeys** opens a stub bind-box window (click a box; no real key capture yet).

Simulated XYZ sliders in the preview card are a stub until a DRO / GRBL `?` status reader implements the same `PositionSource.get_xyz()` contract in `digitizer/position.py`. They are not jogging and not USB. Jog / GO TO buttons do **not** move the stub.

### Envelope scale

The canvas always shows the **entire working envelope** (letterboxed, aspect preserved). It does **not** zoom to the part.

Placeholder envelope (not measured machine travel): **X 0–12 in, Y 0–12 in, Z 0–4 in**. Values live in `digitizer/machine_config.py` so a later Settings tab can write them.

### Probe circle vs Z

The live probe is **one circle** at current XY.

Linear mapping, clamped to envelope Z min/max:

```
span = min(X span, Y span)
r_min = 0.025 * span     # at Z− (z_min)
r_max = 0.080 * span     # at Z+ (z_max)
t = clamp((z - z_min) / (z_max - z_min), 0, 1)
r = r_min + t * (r_max - r_min)
```

Circle **grows with Z+** and **shrinks with Z−**. This is a height cue, not stylus diameter and not a captured ID/OD.

### Grid and captures

Simple axis-aligned grid in envelope coordinates (1 in on the placeholder inch envelope).

The canvas shows **all captured data for the current file**: ID/OD circles as center + diameter + top height; Z markers and DXF-origin markers if those records exist. Empty file = envelope + grid + probe circle only.

### Settings — later, not this slice

A later Settings tab will:

- input working dimensions
- specify units
- calibrate / reconcile distance commanded vs distance moved

Do **not** treat `machine_config.py` as a finished calibration system. The preview already reads envelope/units from that module.

## Hardware (v1, decided)

- MakerBase MKS DLC32 v2.1, GRBL
- TMC2209 V2.0 MKS, NEMA 17, 20 tooth GT2 pulleys
- 3-pin NC digital touch probe
- Two NC micro switches in series on each end of all 3 axes (5V; which end was hit is inferred from motion direction)
- USB laptop ↔ board (DLC32 WiFi unused)

Stylus offset math is unchanged (ID increases displayed motion; OD shrinks it; per strike/direction). Motion ownership is still open. Preview does not own USB, GRBL, or motion.

## Layout

```
digitizer/
  machine_config.py   # placeholder envelope + units
  position.py         # PositionSource + SimulatedPosition
  session.py          # current-file captures (ID/OD, Z, origin)
  preview_geom.py     # envelope fit, grid, Z→radius
  preview.py          # Tkinter DxfPreview widget
  chrome.py           # teal (not mint) rounded cards, pills, chips
  theme.py            # teal palette + corner radii
  main_window.py      # paralyzed three-column GUI
  hotkeys.py          # stub bind-box window
  demo_app.py         # standalone preview (`--preview-only`)
tests/
```
