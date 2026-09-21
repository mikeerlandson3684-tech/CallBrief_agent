"""Envelope → canvas scale and Z → probe-circle size.

The viewport always fits the **full working envelope** into the canvas
(uniform scale, letterboxed). Feature extents never change the scale
(no zoom-to-part).
"""

from __future__ import annotations

from dataclasses import dataclass

from digitizer.preview.envelope import WorkEnvelope

# Default visual size of the probe circle as a fraction of the shorter
# fitted envelope side. Z+ uses the max; Z− uses the min. Not stylus Ø.
DEFAULT_PROBE_RADIUS_MIN_FRAC = 0.025
DEFAULT_PROBE_RADIUS_MAX_FRAC = 0.09
DEFAULT_PADDING_PX = 28.0


@dataclass(frozen=True)
class Viewport:
    """Pixel mapping for one canvas size and one envelope."""

    envelope: WorkEnvelope
    canvas_width: float
    canvas_height: float
    scale: float
    origin_x: float
    origin_y: float
    drawn_width: float
    drawn_height: float
    padding: float

    def to_canvas(self, x: float, y: float) -> tuple[float, float]:
        """Map envelope XY to canvas pixels. Machine Y increases upward."""
        cx = self.origin_x + (x - self.envelope.x_min) * self.scale
        cy = self.origin_y + (self.envelope.y_max - y) * self.scale
        return cx, cy

    def length_to_pixels(self, machine_length: float) -> float:
        return machine_length * self.scale

    def envelope_corners_canvas(self) -> tuple[tuple[float, float], ...]:
        e = self.envelope
        return (
            self.to_canvas(e.x_min, e.y_min),
            self.to_canvas(e.x_max, e.y_min),
            self.to_canvas(e.x_max, e.y_max),
            self.to_canvas(e.x_min, e.y_max),
        )


def viewport_for(
    envelope: WorkEnvelope,
    canvas_width: float,
    canvas_height: float,
    padding: float = DEFAULT_PADDING_PX,
) -> Viewport:
    if canvas_width <= 0 or canvas_height <= 0:
        raise ValueError("canvas size must be positive")
    pad = max(0.0, padding)
    usable_w = max(1.0, canvas_width - 2.0 * pad)
    usable_h = max(1.0, canvas_height - 2.0 * pad)
    scale = min(usable_w / envelope.x_span, usable_h / envelope.y_span)
    drawn_w = envelope.x_span * scale
    drawn_h = envelope.y_span * scale
    origin_x = (canvas_width - drawn_w) / 2.0
    origin_y = (canvas_height - drawn_h) / 2.0
    return Viewport(
        envelope=envelope,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        scale=scale,
        origin_x=origin_x,
        origin_y=origin_y,
        drawn_width=drawn_w,
        drawn_height=drawn_h,
        padding=pad,
    )


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def z_normalized(z: float, envelope: WorkEnvelope) -> float:
    """0 at Z min, 1 at Z max (clamped)."""
    return clamp((z - envelope.z_min) / envelope.z_span, 0.0, 1.0)


def probe_circle_radius(
    z: float,
    envelope: WorkEnvelope,
    *,
    min_radius: float,
    max_radius: float,
) -> float:
    """Canvas radius of the probe location circle.

    Grows with Z+ and shrinks with Z−. ``min_radius`` is at envelope Z min;
    ``max_radius`` is at envelope Z max. Linear in between.
    """
    if max_radius < min_radius:
        raise ValueError("probe max_radius must be >= min_radius")
    t = z_normalized(z, envelope)
    return min_radius + t * (max_radius - min_radius)


def default_probe_radius_range(viewport: Viewport) -> tuple[float, float]:
    shorter = min(viewport.drawn_width, viewport.drawn_height)
    return (
        shorter * DEFAULT_PROBE_RADIUS_MIN_FRAC,
        shorter * DEFAULT_PROBE_RADIUS_MAX_FRAC,
    )
