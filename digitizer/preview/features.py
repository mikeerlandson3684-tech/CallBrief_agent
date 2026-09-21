"""Session features for the current file.

Preview draws whatever is already captured. It does not run ID/OD walks,
rectangles, or G-code. Circles are center + diameter at their XY.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class IdCircleFeature:
    """Inside-of-hole capture: center and diameter in envelope coordinates."""

    center_x: float
    center_y: float
    diameter: float
    top_height: float | None = None

    def __post_init__(self) -> None:
        if self.diameter <= 0:
            raise ValueError("ID circle diameter must be positive")

    @property
    def radius(self) -> float:
        return self.diameter / 2.0


@dataclass(frozen=True)
class OdCircleFeature:
    """Outside-of-boss capture: center and diameter in envelope coordinates."""

    center_x: float
    center_y: float
    diameter: float
    top_height: float | None = None

    def __post_init__(self) -> None:
        if self.diameter <= 0:
            raise ValueError("OD circle diameter must be positive")

    @property
    def radius(self) -> float:
        return self.diameter / 2.0


@dataclass(frozen=True)
class ZHeightMarker:
    """A captured Z height, shown at the XY where it was recorded."""

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class DxfOriginMarker:
    """Drawing datum (Set DXF Origin), not GRBL WCS internals."""

    x: float
    y: float
    z: float | None = None


SessionFeature = Union[
    IdCircleFeature,
    OdCircleFeature,
    ZHeightMarker,
    DxfOriginMarker,
]
