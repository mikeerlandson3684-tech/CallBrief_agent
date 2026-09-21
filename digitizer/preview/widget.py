"""Tkinter canvas that paints a PreviewScene.

Push position, envelope, and the current file's features. This widget
does not open USB or send GRBL.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Sequence

from digitizer.preview.envelope import PLACEHOLDER_GRID_STEP, WorkEnvelope
from digitizer.preview.features import SessionFeature
from digitizer.preview.position import MachinePosition
from digitizer.preview.scene import (
    ENVELOPE_BORDER_KIND,
    GRID_KIND,
    ID_CIRCLE_KIND,
    OD_CIRCLE_KIND,
    ORIGIN_MARKER_KIND,
    PROBE_KIND,
    Z_MARKER_KIND,
    PreviewScene,
    build_scene,
)

BG = "#f7fafc"
GRID_COLOR = "#d4dde6"
BORDER_COLOR = "#334e68"
PROBE_COLOR = "#c0392b"
ID_COLOR = "#2b6cb0"
OD_COLOR = "#2f855a"
Z_COLOR = "#6b46c1"
ORIGIN_COLOR = "#1a202c"
CAPTION_COLOR = "#4a5568"
MARKER_SIZE = 7


class PreviewCanvas(tk.Frame):
    """Right-side DXF/preview window: envelope, grid, probe circle, features."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        envelope: WorkEnvelope,
        position: MachinePosition,
        features: Sequence[SessionFeature] = (),
        grid_step: float = PLACEHOLDER_GRID_STEP,
        width: int = 420,
        height: int = 360,
    ) -> None:
        super().__init__(master, bg=BG)
        self._envelope = envelope
        self._position = position
        self._features: tuple[SessionFeature, ...] = tuple(features)
        self._grid_step = grid_step
        self._scene: PreviewScene | None = None
        self._last_size: tuple[int, int] | None = None

        header = tk.Frame(self, bg="#c8eadc")
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="DXF Preview",
            bg="#c8eadc",
            fg="#1a202c",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor=tk.W, padx=10, pady=6)

        self._caption = tk.Label(
            self,
            text="",
            bg=BG,
            fg=CAPTION_COLOR,
            font=("Segoe UI", 8),
            justify=tk.LEFT,
            wraplength=width - 16,
        )
        self._caption.pack(fill=tk.X, padx=8, pady=(4, 0))

        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            bg=BG,
            highlightthickness=1,
            highlightbackground="#cbd5e0",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.canvas.bind("<Configure>", self._on_configure)

    @property
    def scene(self) -> PreviewScene | None:
        return self._scene

    def set_state(
        self,
        *,
        position: MachinePosition | None = None,
        features: Sequence[SessionFeature] | None = None,
        envelope: WorkEnvelope | None = None,
        grid_step: float | None = None,
    ) -> None:
        if position is not None:
            self._position = position
        if features is not None:
            self._features = tuple(features)
        if envelope is not None:
            self._envelope = envelope
        if grid_step is not None:
            self._grid_step = grid_step
        self.refresh()

    def refresh(self) -> None:
        width = max(self.canvas.winfo_width(), 2)
        height = max(self.canvas.winfo_height(), 2)
        self._scene = build_scene(
            self._envelope,
            self._position,
            self._features,
            canvas_width=float(width),
            canvas_height=float(height),
            grid_step=self._grid_step,
        )
        self._paint(self._scene)
        self._update_caption()

    def _on_configure(self, event: tk.Event) -> None:
        if event.widget is not self.canvas:
            return
        size = (event.width, event.height)
        if size == self._last_size:
            return
        self._last_size = size
        self.refresh()

    def _update_caption(self) -> None:
        e = self._envelope
        placeholder = (
            "Working envelope: PLACEHOLDER settings — not a measured machine. "
            if e.is_placeholder
            else ""
        )
        self._caption.configure(
            text=(
                f"{placeholder}"
                f"X {e.x_min:g}…{e.x_max:g}  Y {e.y_min:g}…{e.y_max:g}  "
                f"Z {e.z_min:g}…{e.z_max:g}  ({e.units_label}). "
                "Full envelope visible (not zoom-to-part). "
                f"This file: {len(self._features)} captured item(s)."
            )
        )

    def _paint(self, scene: PreviewScene) -> None:
        c = self.canvas
        c.delete("all")
        for line in scene.lines_of(GRID_KIND):
            c.create_line(
                line.x1,
                line.y1,
                line.x2,
                line.y2,
                fill=GRID_COLOR,
                width=1,
                tags=("grid",),
            )
        for line in scene.lines_of(ENVELOPE_BORDER_KIND):
            c.create_line(
                line.x1,
                line.y1,
                line.x2,
                line.y2,
                fill=BORDER_COLOR,
                width=2,
                tags=("envelope",),
            )
        e = scene.viewport.envelope
        min_pt = scene.viewport.to_canvas(e.x_min, e.y_min)
        max_pt = scene.viewport.to_canvas(e.x_max, e.y_max)
        c.create_text(
            min_pt[0] + 4,
            min_pt[1] - 10,
            anchor=tk.SW,
            text=f"({e.x_min:g}, {e.y_min:g})",
            fill=CAPTION_COLOR,
            font=("Segoe UI", 8),
            tags=("label",),
        )
        c.create_text(
            max_pt[0] - 4,
            max_pt[1] + 10,
            anchor=tk.NE,
            text=f"({e.x_max:g}, {e.y_max:g})",
            fill=CAPTION_COLOR,
            font=("Segoe UI", 8),
            tags=("label",),
        )
        for circle in scene.circles:
            if circle.kind == PROBE_KIND:
                self._draw_circle(
                    circle.cx,
                    circle.cy,
                    circle.radius,
                    outline=PROBE_COLOR,
                    width=2,
                    tags=("probe",),
                )
                c.create_oval(
                    circle.cx - 2,
                    circle.cy - 2,
                    circle.cx + 2,
                    circle.cy + 2,
                    fill=PROBE_COLOR,
                    outline=PROBE_COLOR,
                    tags=("probe",),
                )
            elif circle.kind == ID_CIRCLE_KIND:
                self._draw_circle(
                    circle.cx,
                    circle.cy,
                    circle.radius,
                    outline=ID_COLOR,
                    width=2,
                    dash=(6, 3),
                    tags=("id_circle",),
                )
                c.create_text(
                    circle.cx,
                    circle.cy - circle.radius - 8,
                    text="ID",
                    fill=ID_COLOR,
                    font=("Segoe UI", 8, "bold"),
                    tags=("id_circle",),
                )
            elif circle.kind == OD_CIRCLE_KIND:
                self._draw_circle(
                    circle.cx,
                    circle.cy,
                    circle.radius,
                    outline=OD_COLOR,
                    width=2,
                    tags=("od_circle",),
                )
                c.create_text(
                    circle.cx,
                    circle.cy - circle.radius - 8,
                    text="OD",
                    fill=OD_COLOR,
                    font=("Segoe UI", 8, "bold"),
                    tags=("od_circle",),
                )
        for marker in scene.markers:
            if marker.kind == Z_MARKER_KIND:
                self._draw_diamond(marker.cx, marker.cy, Z_COLOR, tags=("z_marker",))
                c.create_text(
                    marker.cx + 10,
                    marker.cy,
                    anchor=tk.W,
                    text=marker.label or "Z",
                    fill=Z_COLOR,
                    font=("Segoe UI", 8),
                    tags=("z_marker",),
                )
            elif marker.kind == ORIGIN_MARKER_KIND:
                s = MARKER_SIZE + 2
                c.create_line(
                    marker.cx - s,
                    marker.cy,
                    marker.cx + s,
                    marker.cy,
                    fill=ORIGIN_COLOR,
                    width=2,
                    tags=("dxf_origin",),
                )
                c.create_line(
                    marker.cx,
                    marker.cy - s,
                    marker.cx,
                    marker.cy + s,
                    fill=ORIGIN_COLOR,
                    width=2,
                    tags=("dxf_origin",),
                )
                c.create_text(
                    marker.cx + 10,
                    marker.cy - 8,
                    anchor=tk.W,
                    text=marker.label or "origin",
                    fill=ORIGIN_COLOR,
                    font=("Segoe UI", 8),
                    tags=("dxf_origin",),
                )

    def _draw_circle(
        self,
        cx: float,
        cy: float,
        radius: float,
        **kwargs: object,
    ) -> None:
        r = max(radius, 1.0)
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="", **kwargs)

    def _draw_diamond(
        self, cx: float, cy: float, color: str, *, tags: tuple[str, ...]
    ) -> None:
        s = MARKER_SIZE
        self.canvas.create_polygon(
            cx,
            cy - s,
            cx + s,
            cy,
            cx,
            cy + s,
            cx - s,
            cy,
            fill=color,
            outline=color,
            tags=tags,
        )
