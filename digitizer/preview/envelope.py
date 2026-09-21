"""Configurable working-envelope settings.

X/Y/Z min/max are **not measured** on the machine yet. Values here are
labeled placeholders so the preview has something to scale to — they are
not the real travel of any physical gantry.
"""

from __future__ import annotations

from dataclasses import dataclass

PLACEHOLDER_SOURCE = "placeholder-not-measured"


@dataclass(frozen=True)
class WorkEnvelope:
    """Axis limits used to scale the preview.

    ``source`` must stay ``placeholder-not-measured`` until real travel is
    recorded. Preview code must not treat these numbers as calibrated
    machine limits.
    """

    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float
    source: str = PLACEHOLDER_SOURCE
    units_label: str = "machine units (placeholder)"

    def __post_init__(self) -> None:
        if self.x_max <= self.x_min:
            raise ValueError("envelope X max must be greater than X min")
        if self.y_max <= self.y_min:
            raise ValueError("envelope Y max must be greater than Y min")
        if self.z_max <= self.z_min:
            raise ValueError("envelope Z max must be greater than Z min")

    @property
    def x_span(self) -> float:
        return self.x_max - self.x_min

    @property
    def y_span(self) -> float:
        return self.y_max - self.y_min

    @property
    def z_span(self) -> float:
        return self.z_max - self.z_min

    @property
    def is_placeholder(self) -> bool:
        return self.source == PLACEHOLDER_SOURCE

    def contains_xy(self, x: float, y: float) -> bool:
        return self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max


# Obvious stand-in numbers, not a measured machine. Operators replace these
# in settings once travel is known.
PLACEHOLDER_WORK_ENVELOPE = WorkEnvelope(
    x_min=0.0,
    x_max=10.0,
    y_min=0.0,
    y_max=8.0,
    z_min=0.0,
    z_max=4.0,
    source=PLACEHOLDER_SOURCE,
    units_label="machine units (placeholder)",
)

PLACEHOLDER_GRID_STEP = 1.0
