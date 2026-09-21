"""Standalone window hosting the right-side DXF preview.

Simulated XYZ sliders are a stub until DRO / GRBL ``?`` is wired.
They are not motion control.
"""

from __future__ import annotations

import argparse
import sys
import tkinter as tk
from tkinter import ttk

from digitizer.machine_config import default_envelope
from digitizer.position import SimulatedPosition
from digitizer.preview import DxfPreview
from digitizer.session import CaptureSession, sample_session


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DXF preview panel for the GRBL digitizer (envelope-scaled, no GRBL)."
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Start with sample captured ID/OD circles (not a probe cycle).",
    )
    parser.add_argument(
        "--screenshot",
        metavar="PATH",
        help="Write a PNG of the window after first draw, then exit (needs DISPLAY).",
    )
    return parser


def build_window(
    *,
    sample: bool = False,
    position: SimulatedPosition | None = None,
) -> tuple[tk.Tk, DxfPreview, SimulatedPosition, CaptureSession]:
    env = default_envelope()
    pos = position or SimulatedPosition(
        x=(env.x_min + env.x_max) / 2.0,
        y=(env.y_min + env.y_max) / 2.0,
        z=(env.z_min + env.z_max) / 2.0,
    )
    session = sample_session() if sample else CaptureSession()

    root = tk.Tk()
    root.title("DXF Preview — GRBL digitizer")
    root.minsize(560, 640)
    root.geometry("640x760")

    preview = DxfPreview(root, position_source=pos, session=session)
    preview.pack(fill="both", expand=True)

    sim = tk.LabelFrame(
        root,
        text="Simulated position (not GRBL, not USB — stub until DRO / '?' is wired)",
        padx=8,
        pady=6,
    )
    sim.pack(fill="x", padx=8, pady=(0, 8))

    x_var = tk.DoubleVar(value=pos.get_xyz()[0])
    y_var = tk.DoubleVar(value=pos.get_xyz()[1])
    z_var = tk.DoubleVar(value=pos.get_xyz()[2])

    def _push(_event: object | None = None) -> None:
        pos.set_xyz(x_var.get(), y_var.get(), z_var.get())

    def _axis_row(parent: tk.Misc, label: str, var: tk.DoubleVar, lo: float, hi: float) -> None:
        row = tk.Frame(parent)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, width=3, anchor="w").pack(side="left")
        scale = ttk.Scale(row, from_=lo, to=hi, variable=var, command=lambda _v: _push())
        scale.pack(side="left", fill="x", expand=True, padx=6)
        readout = tk.Label(row, width=10, anchor="e")
        readout.pack(side="right")

        def _sync(*_args: object) -> None:
            readout.configure(text=f"{var.get():.3f} {env.units}")

        var.trace_add("write", _sync)
        _sync()

    _axis_row(sim, "X", x_var, env.x_min, env.x_max)
    _axis_row(sim, "Y", y_var, env.y_min, env.y_max)
    _axis_row(sim, "Z", z_var, env.z_min, env.z_max)
    tk.Label(
        sim,
        text="Z+ grows the probe circle; Z− shrinks it (clamped to envelope Z min/max).",
        fg="#475569",
        anchor="w",
        justify="left",
    ).pack(fill="x", pady=(4, 0))

    btns = tk.Frame(sim)
    btns.pack(fill="x", pady=(8, 0))

    def show_empty() -> None:
        session.clear()
        preview.set_session(session)

    def show_sample() -> None:
        filled = sample_session()
        session.circles = filled.circles
        session.z_heights = filled.z_heights
        session.dxf_origin = filled.dxf_origin
        preview.set_session(session)

    tk.Button(btns, text="Empty file", command=show_empty).pack(side="left")
    tk.Button(btns, text="Sample captures", command=show_sample).pack(side="left", padx=8)
    tk.Label(
        btns,
        text="Settings (later): working dimensions, units, commanded vs moved. Not this slice.",
        fg="#9a3412",
    ).pack(side="left", padx=8)

    return root, preview, pos, session


def _write_screenshot(root: tk.Tk, path: str) -> None:
    """Grab the toplevel via the X11 window id. ImageMagick `import` if present."""
    import shutil
    import subprocess

    root.update_idletasks()
    root.update()
    wid = hex(root.winfo_id())
    if shutil.which("import"):
        subprocess.run(["import", "-window", wid, path], check=True)
        return
    if shutil.which("gnome-screenshot"):
        subprocess.run(["gnome-screenshot", "-w", "-f", path], check=True)
        return
    # Fallback: canvas PostScript (vector, not PNG).
    ps_path = path.rsplit(".", 1)[0] + ".ps"
    # The preview canvas is the first Canvas child.
    canvases = [c for c in root.winfo_children() if isinstance(c, tk.Frame)]
    raise SystemExit(
        f"No screenshot tool (ImageMagick import / gnome-screenshot). "
        f"Window id={wid}. Cannot write {path} (ps fallback unused: {ps_path}, frames={len(canvases)})."
    )


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    root, _preview, _pos, _session = build_window(sample=args.sample)
    if args.screenshot:
        root.after(250, lambda: (_write_screenshot(root, args.screenshot), root.destroy()))
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
