"""Right-side DXF preview widget.

Consumes envelope + position source + current-file captures.
Does **not** own USB, GRBL, or motion. Does **not** zoom-to-part.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from digitizer.machine_config import WorkingEnvelope, default_envelope, envelope_disclaimer
from digitizer.position import PositionSource, SimulatedPosition
from digitizer.preview_geom import (
    grid_step,
    iter_ticks,
    probe_radius_machine,
    view_transform,
)
from digitizer.session import CaptureSession, CapturedCircle

# Colors are example UI chrome, not a cycle spec and not the PNG glyph.
_BG = "#f8fafc"
_CANVAS_BG = "#ffffff"
_GRID = "#d9e2ec"
_BORDER = "#334155"
_LABEL = "#475569"
_PROBE_FILL = "#99f6e4"
_PROBE_OUTLINE = "#0f766e"
_ID = "#2563eb"
_OD = "#7c3aed"
_ORIGIN = "#111827"
_ZMARK = "#b45309"
_HEADER = "#d1fae5"


class DxfPreview(tk.Frame):
    """Envelope-scaled canvas: grid, Z-sized probe circle, session features."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        envelope_provider: Callable[[], WorkingEnvelope] | None = None,
        position_source: PositionSource | None = None,
        session: CaptureSession | None = None,
        poll_ms: int = 50,
        **kwargs: object,
    ) -> None:
        super().__init__(master, bg=_BG, **kwargs)
        self._envelope_provider = envelope_provider or default_envelope
        self._position = position_source or SimulatedPosition()
        self._session = session if session is not None else CaptureSession()
        self._poll_ms = poll_ms
        self._poll_job: str | None = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = tk.Frame(self, bg=_HEADER, padx=10, pady=6)
        header.grid(row=0, column=0, sticky="ew")
        tk.Label(
            header,
            text="DXF Preview",
            bg=_HEADER,
            fg="#064e3b",
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")
        self._xyz_var = tk.StringVar(value="")
        tk.Label(header, textvariable=self._xyz_var, bg=_HEADER, fg="#115e59").pack(side="right")

        self._banner = tk.StringVar(value="")
        tk.Label(
            self,
            textvariable=self._banner,
            bg=_BG,
            fg="#9a3412",
            font=("Segoe UI", 8),
            wraplength=420,
            justify="left",
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 0))

        self.canvas = tk.Canvas(self, bg=_CANVAS_BG, highlightthickness=1, highlightbackground="#cbd5e1")
        self.canvas.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)
        self.canvas.bind("<Configure>", self._on_configure)

        footer = tk.Frame(self, bg=_BG)
        footer.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 6))
        tk.Label(
            footer,
            text="Full working envelope (not zoom-to-part).  "
            "Probe circle grows with Z+ / shrinks with Z−.  "
            "Empty file = grid + probe only.",
            bg=_BG,
            fg=_LABEL,
            font=("Segoe UI", 8),
            wraplength=480,
            justify="left",
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        self._refresh_banner()
        self.redraw()
        if self._poll_ms > 0:
            self.start_polling()

    def set_session(self, session: CaptureSession) -> None:
        self._session = session
        self.redraw()

    def set_position_source(self, source: PositionSource) -> None:
        self._position = source
        self.redraw()

    def start_polling(self) -> None:
        self.stop_polling()
        self._poll()

    def stop_polling(self) -> None:
        if self._poll_job is not None:
            try:
                self.after_cancel(self._poll_job)
            except tk.TclError:
                pass
            self._poll_job = None

    def destroy(self) -> None:
        self.stop_polling()
        super().destroy()

    def _poll(self) -> None:
        self.redraw()
        try:
            self._poll_job = self.after(self._poll_ms, self._poll)
        except tk.TclError:
            self._poll_job = None

    def _on_configure(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        self.redraw()

    def _refresh_banner(self) -> None:
        self._banner.set(self.envelope_disclaimer())

    def envelope_disclaimer(self) -> str:
        return envelope_disclaimer(self._envelope_provider())

    def _canvas_size(self) -> tuple[int, int]:
        w = int(self.canvas.winfo_width())
        h = int(self.canvas.winfo_height())
        if w <= 2:
            w = int(float(self.canvas.cget("width") or 400))
        if h <= 2:
            h = int(float(self.canvas.cget("height") or 400))
        return max(w, 2), max(h, 2)

    def redraw(self) -> None:
        env = self._envelope_provider()
        session = self._session
        x, y, z = self._position.get_xyz()
        self._xyz_var.set(f"probe  X {x:.3f}  Y {y:.3f}  Z {z:.3f} {env.units}")
        self._refresh_banner()

        w, h = self._canvas_size()
        self.canvas.delete("all")
        view = view_transform(env, float(w), float(h))

        self._draw_grid(env, view)
        self._draw_envelope(env, view)
        self._draw_features(env, view, session)
        self._draw_probe(env, view, x, y, z)

    def _draw_grid(self, env: WorkingEnvelope, view) -> None:  # type: ignore[no-untyped-def]
        x_step = grid_step(env.x_span(), env.units)
        y_step = grid_step(env.y_span(), env.units)
        for gx in iter_ticks(env.x_min, env.x_max, x_step):
            x0, y0 = view.to_canvas(gx, env.y_min)
            x1, y1 = view.to_canvas(gx, env.y_max)
            self.canvas.create_line(x0, y0, x1, y1, fill=_GRID)
        for gy in iter_ticks(env.y_min, env.y_max, y_step):
            x0, y0 = view.to_canvas(env.x_min, gy)
            x1, y1 = view.to_canvas(env.x_max, gy)
            self.canvas.create_line(x0, y0, x1, y1, fill=_GRID)

    def _draw_envelope(self, env: WorkingEnvelope, view) -> None:  # type: ignore[no-untyped-def]
        x0, y0 = view.to_canvas(env.x_min, env.y_max)
        x1, y1 = view.to_canvas(env.x_max, env.y_min)
        self.canvas.create_rectangle(x0, y0, x1, y1, outline=_BORDER, width=2)
        self.canvas.create_text(
            (x0 + x1) / 2,
            y1 + 14,
            text=f"X {env.x_min:g} … {env.x_max:g} {env.units}",
            fill=_LABEL,
            font=("Segoe UI", 8),
        )
        self.canvas.create_text(
            x0 - 12,
            (y0 + y1) / 2,
            text=f"Y {env.y_min:g} … {env.y_max:g} {env.units}",
            fill=_LABEL,
            font=("Segoe UI", 8),
            angle=90,
        )

    def _draw_features(self, env: WorkingEnvelope, view, session: CaptureSession) -> None:  # type: ignore[no-untyped-def]
        if session.dxf_origin is not None:
            ox, oy = view.to_canvas(session.dxf_origin.x, session.dxf_origin.y)
            arm = 8
            self.canvas.create_line(ox - arm, oy, ox + arm, oy, fill=_ORIGIN, width=2)
            self.canvas.create_line(ox, oy - arm, ox, oy + arm, fill=_ORIGIN, width=2)
            self.canvas.create_text(
                ox + 10,
                oy - 10,
                text="DXF origin",
                fill=_ORIGIN,
                font=("Segoe UI", 8),
                anchor="w",
            )

        for zh in session.z_heights:
            px, py = view.to_canvas(zh.x, zh.y)
            s = 5
            self.canvas.create_polygon(
                px,
                py - s,
                px + s,
                py,
                px,
                py + s,
                px - s,
                py,
                outline=_ZMARK,
                fill="#fde68a",
                width=1,
            )
            self.canvas.create_text(
                px + 8,
                py + 10,
                text=f"Z {zh.z:.3f} {env.units}",
                fill=_ZMARK,
                font=("Segoe UI", 8),
                anchor="w",
            )

        for circle in session.circles:
            self._draw_captured_circle(env, view, circle)

    def _draw_captured_circle(self, env: WorkingEnvelope, view, circle: CapturedCircle) -> None:  # type: ignore[no-untyped-def]
        color = _ID if circle.kind == "id" else _OD
        label = "ID" if circle.kind == "id" else "OD"
        cx, cy = view.to_canvas(circle.center_x, circle.center_y)
        r = view.radius_px(circle.diameter / 2.0)
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=color, width=2)
        self.canvas.create_line(cx - 4, cy, cx + 4, cy, fill=color)
        self.canvas.create_line(cx, cy - 4, cx, cy + 4, fill=color)
        self.canvas.create_text(
            cx,
            cy - r - 10,
            text=f"{label} Ø{circle.diameter:.3f}  top Z {circle.top_height:.3f} {env.units}",
            fill=color,
            font=("Segoe UI", 8),
        )

    def _draw_probe(self, env: WorkingEnvelope, view, x: float, y: float, z: float) -> None:  # type: ignore[no-untyped-def]
        r_m = probe_radius_machine(z, env)
        r = max(view.radius_px(r_m), 3.0)
        cx, cy = view.to_canvas(x, y)
        self.canvas.create_oval(
            cx - r,
            cy - r,
            cx + r,
            cy + r,
            outline=_PROBE_OUTLINE,
            fill=_PROBE_FILL,
            width=2,
            tags=("probe",),
        )
        self.canvas.create_line(cx - 5, cy, cx + 5, cy, fill=_PROBE_OUTLINE, tags=("probe",))
        self.canvas.create_line(cx, cy - 5, cx, cy + 5, fill=_PROBE_OUTLINE, tags=("probe",))
