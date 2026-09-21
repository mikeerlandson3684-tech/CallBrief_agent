"""Envelope-scaled DXF/preview canvas.

Consumes machine position, a working-envelope setting, and this file's
feature list. Does not own USB, GRBL, or motion.
"""

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
from digitizer.preview.mapping import Viewport, probe_circle_radius, viewport_for
from digitizer.preview.position import MachinePosition
from digitizer.preview.scene import PreviewScene, build_scene
from digitizer.preview.widget import PreviewCanvas

__all__ = [
    "DxfOriginMarker",
    "IdCircleFeature",
    "MachinePosition",
    "OdCircleFeature",
    "PLACEHOLDER_GRID_STEP",
    "PLACEHOLDER_WORK_ENVELOPE",
    "PreviewCanvas",
    "PreviewScene",
    "SessionFeature",
    "Viewport",
    "WorkEnvelope",
    "ZHeightMarker",
    "build_scene",
    "probe_circle_radius",
    "viewport_for",
]
