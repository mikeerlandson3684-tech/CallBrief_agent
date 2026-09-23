"""Envelope-scaled preview geometry (no Tk, no GRBL).

Coordinate policy
-----------------
The drawable always shows the **entire working envelope**. Scale is
``min(available_px / x_span, available_px / y_span)`` with letterboxing.
Never zoom-to-part.

Probe circle vs Z (monotonic, clamped)
--------------------------------------
Let ``span = min(X span, Y span)``. Visual radius in machine units:

    r_min = PROBE_RADIUS_FRAC_ZMIN * span    # at Z− (z_min)
    r_max = PROBE_RADIUS_FRAC_ZMAX * span    # at Z+ (z_max)

    t = (z - z_min) / (z_max - z_min)        # 0 at Z−, 1 at Z+
    t = clamp(t, 0, 1)
    r = r_min + t * (r_max - r_min)

If ``z_max == z_min``, ``r = r_min``. Values below ``z_min`` stay at
``r_min``; values above ``z_max`` stay at ``r_max``.

This radius is a **Z cue**. It is not stylus diameter and not a captured
ID/OD. Circle **grows with Z+** and **shrinks with Z−**.

Grid
----
Simple axis-aligned lines in envelope coordinates. Step is a round
increment from the axis span and units (placeholder inches → 1 in).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from digitizer.machine_config import UNITS_MM, WorkingEnvelope

# Visual probe radius as a fraction of min(X span, Y span).
PROBE_RADIUS_FRAC_ZMIN = 0.025
PROBE_RADIUS_FRAC_ZMAX = 0.080


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def probe_radius_machine(z: float, envelope: WorkingEnvelope) -> float:
    """Map Z to probe-circle radius in machine units (monotonic, clamped)."""
    span = envelope.min_xy_span()
    r_min = PROBE_RADIUS_FRAC_ZMIN * span
    r_max = PROBE_RADIUS_FRAC_ZMAX * span
    z_span = envelope.z_span()
    if span <= 0:
        return 0.0
    if z_span <= 0:
        return r_min
    t = clamp((z - envelope.z_min) / z_span, 0.0, 1.0)
    return r_min + t * (r_max - r_min)


def grid_step(span: float, units: str) -> float:
    """Pick a simple grid increment for one axis span (about 8–15 lines)."""
    if span <= 0:
        return 1.0
    if units == UNITS_MM:
        candidates = (100.0, 50.0, 20.0, 10.0, 5.0, 2.0, 1.0)
        fallback = 1.0
    else:
        candidates = (5.0, 2.0, 1.0, 0.5, 0.25, 0.1)
        fallback = 0.1
    for step in candidates:
        if span / step >= 8:
            return step
    return fallback


def iter_ticks(lo: float, hi: float, step: float) -> list[float]:
    """Inclusive ticks from the first multiple of ``step`` at/after ``lo``."""
    if step <= 0 or hi < lo:
        return [lo, hi]
    start = math.ceil((lo / step) - 1e-9) * step
    ticks: list[float] = []
    v = start
    # Guard against float drift.
    while v <= hi + step * 1e-6:
        if v >= lo - step * 1e-6:
            ticks.append(round(v, 10))
        v += step
        if len(ticks) > 500:
            break
    if not ticks or abs(ticks[0] - lo) > step * 1e-6:
        ticks.insert(0, lo)
    if abs(ticks[-1] - hi) > step * 1e-6:
        ticks.append(hi)
    return ticks


@dataclass(frozen=True)
class ViewTransform:
    """Machine XY → canvas pixels. Full envelope visible; Y up."""

    envelope: WorkingEnvelope
    scale: float
    origin_x: float
    origin_y: float
    used_w: float
    used_h: float
    canvas_w: float
    canvas_h: float

    def to_canvas(self, x: float, y: float) -> tuple[float, float]:
        cx = self.origin_x + (x - self.envelope.x_min) * self.scale
        cy = self.origin_y + self.used_h - (y - self.envelope.y_min) * self.scale
        return (cx, cy)

    def radius_px(self, r_machine: float) -> float:
        return r_machine * self.scale


def view_transform(
    envelope: WorkingEnvelope,
    canvas_w: float,
    canvas_h: float,
    *,
    margin_left: float = 40.0,
    margin_right: float = 16.0,
    margin_top: float = 16.0,
    margin_bottom: float = 32.0,
) -> ViewTransform:
    """Fit the full envelope in the canvas; letterbox; never zoom-to-part."""
    avail_w = max(1.0, canvas_w - margin_left - margin_right)
    avail_h = max(1.0, canvas_h - margin_top - margin_bottom)
    x_span = max(envelope.x_span(), 1e-9)
    y_span = max(envelope.y_span(), 1e-9)
    scale = min(avail_w / x_span, avail_h / y_span)
    used_w = x_span * scale
    used_h = y_span * scale
    origin_x = margin_left + (avail_w - used_w) / 2.0
    origin_y = margin_top + (avail_h - used_h) / 2.0
    return ViewTransform(
        envelope=envelope,
        scale=scale,
        origin_x=origin_x,
        origin_y=origin_y,
        used_w=used_w,
        used_h=used_h,
        canvas_w=canvas_w,
        canvas_h=canvas_h,
    )
