"""Runnable preview host with simulated XYZ and a fake feature list.

No USB, GRBL, probe walks, or G-code. Envelope min/max are placeholder
settings, not a measured machine.
"""

from __future__ import annotations

import argparse
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from digitizer.preview.envelope import (
    PLACEHOLDER_GRID_STEP,
    PLACEHOLDER_WORK_ENVELOPE,
    WorkEnvelope,
)
from digitizer.preview.features import (
    DxfOriginMarker,
    IdCircleFeature,
    OdCircleFeature,
    SessionFeature,
    ZHeightMarker,
)
from digitizer.preview.position import MachinePosition
from digitizer.preview.widget import PreviewCanvas

# Fake session data so the canvas can show ID/OD + markers. Not harvested
# from hardware and not a probe-cycle spec.
FAKE_FEATURES: tuple[SessionFeature, ...] = (
    IdCircleFeature(center_x=3.0, center_y=5.0, diameter=1.6, top_height=1.2),
    OdCircleFeature(center_x=7.0, center_y=2.5, diameter=1.2, top_height=1.2),
    ZHeightMarker(x=3.0, y=5.0, z=1.2),
    DxfOriginMarker(x=1.0, y=1.0),
)


def _float_var(value: float) -> tk.DoubleVar:
    return tk.DoubleVar(value=value)


class PreviewDemo(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("DXF Preview — simulated (no USB/GRBL)")
        self.geometry("980x560")
        self.minsize(820, 480)
        self.configure(bg="#eef2f6")

        self._envelope = PLACEHOLDER_WORK_ENVELOPE
        self._features: tuple[SessionFeature, ...] = ()
        self._x = _float_var(2.0)
        self._y = _float_var(2.0)
        self._z = _float_var(0.5)
        self._xmin = _float_var(self._envelope.x_min)
        self._xmax = _float_var(self._envelope.x_max)
        self._ymin = _float_var(self._envelope.y_min)
        self._ymax = _float_var(self._envelope.y_max)
        self._zmin = _float_var(self._envelope.z_min)
        self._zmax = _float_var(self._envelope.z_max)
        self._grid = _float_var(PLACEHOLDER_GRID_STEP)

        self._build()
        self._sync_slider_ranges()
        self.after_idle(self._push)

    def _build(self) -> None:
        left = tk.Frame(self, bg="#eef2f6", padx=12, pady=12)
        left.pack(side=tk.LEFT, fill=tk.Y)
        right = tk.Frame(self, bg="#eef2f6", padx=8, pady=12)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(
            left,
            text="Simulated position",
            bg="#eef2f6",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor=tk.W)
        tk.Label(
            left,
            text="Fake XYZ only. Preview consumes position +\n"
            "envelope + feature list. No motion ownership.",
            bg="#eef2f6",
            fg="#4a5568",
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(0, 8))

        self._xyz_frame = tk.Frame(left, bg="#eef2f6")
        self._xyz_frame.pack(fill=tk.X)
        self._x_scale = self._axis_slider(self._xyz_frame, "X", self._x)
        self._y_scale = self._axis_slider(self._xyz_frame, "Y", self._y)
        self._z_scale = self._axis_slider(self._xyz_frame, "Z", self._z)

        ttk.Separator(left).pack(fill=tk.X, pady=10)
        tk.Label(
            left,
            text="Working envelope (placeholder, not measured)",
            bg="#eef2f6",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W)
        env = tk.Frame(left, bg="#eef2f6")
        env.pack(fill=tk.X, pady=4)
        self._env_entries = []
        for row, label, var in (
            (0, "X min", self._xmin),
            (1, "X max", self._xmax),
            (2, "Y min", self._ymin),
            (3, "Y max", self._ymax),
            (4, "Z min", self._zmin),
            (5, "Z max", self._zmax),
            (6, "Grid step", self._grid),
        ):
            tk.Label(env, text=label, bg="#eef2f6", width=10, anchor=tk.W).grid(
                row=row, column=0, sticky=tk.W, pady=1
            )
            entry = tk.Entry(env, textvariable=var, width=10)
            entry.grid(row=row, column=1, sticky=tk.W)
            entry.bind("<Return>", lambda _e: self._apply_envelope())
            entry.bind("<FocusOut>", lambda _e: self._apply_envelope())
            self._env_entries.append(entry)
        tk.Button(left, text="Apply envelope placeholders", command=self._apply_envelope).pack(
            anchor=tk.W, pady=(6, 0)
        )

        ttk.Separator(left).pack(fill=tk.X, pady=10)
        tk.Label(
            left,
            text="This file's captured data",
            bg="#eef2f6",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W)
        tk.Button(left, text="Empty file", command=self.show_empty).pack(
            anchor=tk.W, pady=2
        )
        tk.Button(
            left,
            text="Fake ID/OD + Z + origin",
            command=self.show_fake_features,
        ).pack(anchor=tk.W, pady=2)
        tk.Label(
            left,
            text="ID/OD are center+diameter. Not a\nprobe walk. No rectangles.",
            bg="#eef2f6",
            fg="#4a5568",
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(6, 0))

        self.preview = PreviewCanvas(
            right,
            envelope=self._envelope,
            position=self.position,
            features=self._features,
            grid_step=float(self._grid.get()),
        )
        self.preview.pack(fill=tk.BOTH, expand=True)

    def _axis_slider(
        self, parent: tk.Misc, name: str, var: tk.DoubleVar
    ) -> tk.Scale:
        row = tk.Frame(parent, bg="#eef2f6")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=name, bg="#eef2f6", width=3, anchor=tk.W).pack(side=tk.LEFT)
        scale = tk.Scale(
            row,
            variable=var,
            from_=0.0,
            to=1.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            length=220,
            command=lambda _v: self._push(),
            bg="#eef2f6",
            highlightthickness=0,
        )
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        return scale

    @property
    def position(self) -> MachinePosition:
        return MachinePosition(
            x=float(self._x.get()),
            y=float(self._y.get()),
            z=float(self._z.get()),
        )

    def show_empty(self) -> None:
        self._features = ()
        self._push()

    def show_fake_features(self) -> None:
        self._features = FAKE_FEATURES
        self._push()

    def _apply_envelope(self) -> None:
        try:
            self._envelope = WorkEnvelope(
                x_min=float(self._xmin.get()),
                x_max=float(self._xmax.get()),
                y_min=float(self._ymin.get()),
                y_max=float(self._ymax.get()),
                z_min=float(self._zmin.get()),
                z_max=float(self._zmax.get()),
            )
        except (tk.TclError, ValueError):
            return
        self._sync_slider_ranges()
        self._push()

    def _sync_slider_ranges(self) -> None:
        e = self._envelope
        self._x_scale.configure(from_=e.x_min, to=e.x_max)
        self._y_scale.configure(from_=e.y_min, to=e.y_max)
        self._z_scale.configure(from_=e.z_min, to=e.z_max)
        self._x.set(_clamp(self._x.get(), e.x_min, e.x_max))
        self._y.set(_clamp(self._y.get(), e.y_min, e.y_max))
        self._z.set(_clamp(self._z.get(), e.z_min, e.z_max))

    def _push(self) -> None:
        self.preview.set_state(
            position=self.position,
            features=self._features,
            envelope=self._envelope,
            grid_step=float(self._grid.get()),
        )

    def apply_mode(self, mode: str) -> None:
        if mode == "empty":
            self.show_empty()
        elif mode == "features":
            self.show_fake_features()
        elif mode == "zmin":
            self.show_fake_features()
            self._z.set(self._envelope.z_min)
            self._push()
        elif mode == "zmax":
            self.show_fake_features()
            self._z.set(self._envelope.z_max)
            self._push()
        else:
            raise ValueError(f"unknown screenshot mode: {mode}")


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def grab_window_png(window: tk.Tk, path: Path) -> None:
    window.update_idletasks()
    window.update()
    path.parent.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []

    x = window.winfo_rootx()
    y = window.winfo_rooty()
    w = window.winfo_width()
    h = window.winfo_height()
    try:
        from PIL import ImageGrab

        image = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        if image.getbbox():
            image.save(path)
            return
        errors.append("ImageGrab returned an empty image")
    except Exception as exc:  # pragma: no cover - display-dependent
        errors.append(f"ImageGrab: {exc}")

    import shutil
    import subprocess
    import tempfile

    wid = str(window.winfo_id())
    if shutil.which("import"):
        result = subprocess.run(
            ["import", "-window", wid, str(path)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and path.exists() and path.stat().st_size > 0:
            return
        errors.append(f"import: {result.stderr.strip() or result.returncode}")

    if shutil.which("xwd") and shutil.which("convert"):
        with tempfile.NamedTemporaryFile(suffix=".xwd", delete=False) as handle:
            xwd_path = Path(handle.name)
        try:
            result = subprocess.run(
                ["xwd", "-id", wid, "-out", str(xwd_path)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                converted = subprocess.run(
                    ["convert", str(xwd_path), str(path)],
                    capture_output=True,
                    text=True,
                )
                if converted.returncode == 0 and path.exists():
                    return
                errors.append(f"convert: {converted.stderr.strip()}")
            else:
                errors.append(f"xwd: {result.stderr.strip() or result.returncode}")
        finally:
            xwd_path.unlink(missing_ok=True)

    preview = getattr(window, "preview", None)
    canvas = getattr(preview, "canvas", None)
    if canvas is not None and shutil.which("gs"):
        with tempfile.NamedTemporaryFile(suffix=".ps", delete=False) as handle:
            ps_path = Path(handle.name)
        try:
            canvas.postscript(file=str(ps_path), colormode="color")
            result = subprocess.run(
                [
                    "gs",
                    "-dSAFER",
                    "-dBATCH",
                    "-dNOPAUSE",
                    "-sDEVICE=png16m",
                    f"-sOutputFile={path}",
                    str(ps_path),
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and path.exists():
                return
            errors.append(f"ghostscript: {result.stderr.strip()}")
        finally:
            ps_path.unlink(missing_ok=True)

    raise RuntimeError("could not capture preview window: " + "; ".join(errors))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Envelope-scaled DXF preview demo (simulated position)."
    )
    parser.add_argument(
        "--screenshot",
        type=Path,
        help="Write a PNG of the window and exit.",
    )
    parser.add_argument(
        "--mode",
        choices=("empty", "features", "zmin", "zmax"),
        default="features",
        help="Session contents used for a screenshot or initial view.",
    )
    parser.add_argument(
        "--screenshots-dir",
        type=Path,
        help="Write empty/features/zmin/zmax PNGs and exit.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    app = PreviewDemo()
    if args.screenshots_dir:
        dest = args.screenshots_dir
        dest.mkdir(parents=True, exist_ok=True)
        mapping = {
            "empty": dest / "preview_empty_file.png",
            "features": dest / "preview_session_features.png",
            "zmin": dest / "preview_probe_zmin.png",
            "zmax": dest / "preview_probe_zmax.png",
        }

        def _shot(remaining: list[str]) -> None:
            if not remaining:
                app.destroy()
                return
            mode = remaining[0]
            app.apply_mode(mode)
            app.update_idletasks()
            app.update()
            grab_window_png(app, mapping[mode])
            app.after(80, lambda: _shot(remaining[1:]))

        app.after(200, lambda: _shot(["empty", "features", "zmin", "zmax"]))
        app.mainloop()
        return 0
    if args.screenshot:
        app.apply_mode(args.mode)
        app.after(200, lambda: (grab_window_png(app, args.screenshot), app.destroy()))
        app.mainloop()
        return 0
    app.apply_mode(args.mode)
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
