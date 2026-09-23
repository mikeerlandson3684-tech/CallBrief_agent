"""Placeholder working envelope and units for the DXF preview.

These numbers are **not** measured machine travel. A later Settings tab
will let the operator:

- input working dimensions (X/Y/Z min and max)
- specify units
- calibrate / reconcile distance commanded vs distance moved

This module is the single read path for envelope + units so Settings can
write here later. It is **not** a final calibration system.
"""

from __future__ import annotations

from dataclasses import dataclass

UNITS_INCH = "in"
UNITS_MM = "mm"

# Obvious placeholders — not the real gantry, not claimed as travel limits.
PLACEHOLDER_X_MIN = 0.0
PLACEHOLDER_X_MAX = 12.0
PLACEHOLDER_Y_MIN = 0.0
PLACEHOLDER_Y_MAX = 12.0
PLACEHOLDER_Z_MIN = 0.0
PLACEHOLDER_Z_MAX = 4.0
PLACEHOLDER_UNITS = UNITS_INCH


@dataclass(frozen=True)
class WorkingEnvelope:
    """Axis extents the preview always fits on screen (full envelope, not zoom-to-part)."""

    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float
    units: str

    def x_span(self) -> float:
        return self.x_max - self.x_min

    def y_span(self) -> float:
        return self.y_max - self.y_min

    def z_span(self) -> float:
        return self.z_max - self.z_min

    def min_xy_span(self) -> float:
        return min(self.x_span(), self.y_span())

    def is_placeholder(self) -> bool:
        return True


def default_envelope() -> WorkingEnvelope:
    """Return the current placeholder envelope. Settings will replace this later."""
    return WorkingEnvelope(
        x_min=PLACEHOLDER_X_MIN,
        x_max=PLACEHOLDER_X_MAX,
        y_min=PLACEHOLDER_Y_MIN,
        y_max=PLACEHOLDER_Y_MAX,
        z_min=PLACEHOLDER_Z_MIN,
        z_max=PLACEHOLDER_Z_MAX,
        units=PLACEHOLDER_UNITS,
    )


def envelope_disclaimer(envelope: WorkingEnvelope | None = None) -> str:
    env = envelope or default_envelope()
    return (
        f"Placeholder envelope: X {env.x_min:g}–{env.x_max:g} {env.units}, "
        f"Y {env.y_min:g}–{env.y_max:g} {env.units}, "
        f"Z {env.z_min:g}–{env.z_max:g} {env.units} "
        "(not measured machine travel; Settings later)"
    )
