"""Captured data for the current file (preview input only).

ID and OD are separate circle records (not one Inner/Outer toggle).
No rectangles. No probe walks. No G-code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


CircleKind = Literal["id", "od"]


@dataclass(frozen=True)
class CapturedCircle:
    """One captured ID or OD circle: center, diameter, top height."""

    kind: CircleKind
    center_x: float
    center_y: float
    diameter: float
    top_height: float


@dataclass(frozen=True)
class CapturedZHeight:
    """A captured Z at an XY (Lock Z / Capture Z result, if present)."""

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class DxfOrigin:
    """Drawing datum for the DXF. Not GRBL WCS internals."""

    x: float
    y: float
    z: float = 0.0


@dataclass
class CaptureSession:
    """All harvested features for the open file. Empty = circles/Z/origin unset."""

    circles: list[CapturedCircle] = field(default_factory=list)
    z_heights: list[CapturedZHeight] = field(default_factory=list)
    dxf_origin: DxfOrigin | None = None

    def is_empty(self) -> bool:
        return not self.circles and not self.z_heights and self.dxf_origin is None

    def clear(self) -> None:
        self.circles.clear()
        self.z_heights.clear()
        self.dxf_origin = None


def sample_session() -> CaptureSession:
    """Demo captures inside the placeholder envelope. Not a probe cycle."""
    return CaptureSession(
        circles=[
            CapturedCircle("id", center_x=3.0, center_y=8.0, diameter=1.0, top_height=1.25),
            CapturedCircle("od", center_x=8.5, center_y=4.0, diameter=2.0, top_height=0.50),
        ],
        z_heights=[CapturedZHeight(x=5.5, y=6.5, z=2.0)],
        dxf_origin=DxfOrigin(x=1.0, y=1.0, z=0.0),
    )
