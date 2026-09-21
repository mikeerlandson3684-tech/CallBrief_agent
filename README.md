# GRBL digitizing control — DXF preview slice

Probe-only 3-axis gantry: capture existing part features and write them to DXF.
This PR adds the **right-side DXF/preview canvas** only.

Python + Tkinter (starting default). The preview widget consumes **position +
working envelope + this file’s feature list**. It does **not** own USB, GRBL,
or motion. No ID/OD probe walks, no G-code, no rectangular routines.

## Run the preview (simulated XYZ)

From the repo root:

```
python3 -m digitizer.preview
```

Sliders are fake DRO. Buttons switch between an empty file (envelope + grid +
probe circle) and a fake ID/OD + Z + origin list so the drawing rules are
visible. Envelope X/Y/Z min/max fields are **placeholders, not a measured
machine**.

```
python3 -m digitizer.preview --mode empty
python3 -m digitizer.preview --screenshot /tmp/preview.png --mode features
```

## Tests

```
python3 -m unittest discover -s tests -v
```

Covers envelope→canvas scale (full envelope, not zoom-to-part), Z→probe circle
size, and captured features drawn in envelope coordinates.

## Preview rules

- Always scaled to the **full machine working envelope** (not zoom-to-part)
- Probe location is a **circle** that **grows with Z+** and **shrinks with Z−**
- **Simple grid**
- All captured data for this file: ID/OD as **center + diameter**; Z and DXF-origin markers if present
- Empty file = envelope + grid + probe circle only

Authoritative product direction lives in the Cursor project store
(`docs/gui-direction.md`). Hardware / host stack: store `docs/project-context.md`.
