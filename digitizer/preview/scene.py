"""Drawable preview scene in canvas pixels.

Built from envelope + position + feature list. Scale is envelope-only.
"""

from __future__ import annotations

from dataclasses import dataclass

from digitizer.preview.envelope import WorkEnvelope
from digitizer.preview.features import (
    DxfOriginMarker,
    IdCircleFeature,
    OdCircleFeature,
    SessionFeature,
    ZHeightMarker,
)
from digitizer.preview.mapping import (
    Viewport,
    default_probe_radius_range,
    probe_circle_radius,
    viewport_for,
)
from digitizer.preview.position import MachinePosition

GRID_KIND = "grid"
ENVELOPE_BORDER_KIND = "envelope_border"
PROBE_KIND = "probe"
ID_CIRCLE_KIND = "id_circle"
OD_CIRCLE_KIND = "od_circle"
Z_MARKER_KIND = "z_marker"
ORIGIN_MARKER_KIND = "dxf_origin"


@dataclass(frozen=True)
class CanvasLine:
    x1: float
    y1: float
    x2: float
    y2: float
    kind: str


@dataclass(frozen=True)
class CanvasCircle:
    cx: float
    cy: float
    radius: float
    kind: str
    label: str | None = None
    machine_x: float | None = None
    machine_y: float | None = None
    machine_diameter: float | None = None


@dataclass(frozen=True)
class CanvasMarker:
    cx: float
    cy: float
    kind: str
    label: str | None = None
    machine_x: float | None = None
    machine_y: float | None = None
    machine_z: float | None = None


@dataclass(frozen=True)
class PreviewScene:
    viewport: Viewport
    lines: tuple[CanvasLine, ...]
    circles: tuple[CanvasCircle, ...]
    markers: tuple[CanvasMarker, ...]
    envelope_is_placeholder: bool

    @property
    def scale(self) -> float:
        return self.viewport.scale

    def circles_of(self, kind: str) -> tuple[CanvasCircle, ...]:
        return tuple(c for c in self.circles if c.kind == kind)

    def markers_of(self, kind: str) -> tuple[CanvasMarker, ...]:
        return tuple(m for m in self.markers if m.kind == kind)

    def lines_of(self, kind: str) -> tuple[CanvasLine, ...]:
        return tuple(line for line in self.lines if line.kind == kind)


def _grid_positions(start: float, stop: float, step: float) -> list[float]:
    if step <= 0:
        raise ValueError("grid step must be positive")
    epsilon = step * 1e-9
    values: list[float] = []
    n = 0
    while start + n * step <= stop + epsilon:
        values.append(start + n * step)
        n += 1
        if n > 10_000:
            raise ValueError("grid step too small for envelope span")
    if not values or abs(values[-1] - stop) > epsilon:
        values.append(stop)
    return values


def build_scene(
    envelope: WorkEnvelope,
    position: MachinePosition,
    features: tuple[SessionFeature, ...] | list[SessionFeature],
    *,
    canvas_width: float,
    canvas_height: float,
    grid_step: float,
    padding: float | None = None,
    probe_min_radius: float | None = None,
    probe_max_radius: float | None = None,
) -> PreviewScene:
    kwargs = {}
    if padding is not None:
        kwargs["padding"] = padding
    viewport = viewport_for(envelope, canvas_width, canvas_height, **kwargs)

    lines: list[CanvasLine] = []
    x_ticks = _grid_positions(envelope.x_min, envelope.x_max, grid_step)
    y_ticks = _grid_positions(envelope.y_min, envelope.y_max, grid_step)
    top_left = viewport.to_canvas(envelope.x_min, envelope.y_max)
    bottom_right = viewport.to_canvas(envelope.x_max, envelope.y_min)
    for x in x_ticks:
        cx, _ = viewport.to_canvas(x, envelope.y_min)
        lines.append(
            CanvasLine(
                x1=cx,
                y1=top_left[1],
                x2=cx,
                y2=bottom_right[1],
                kind=GRID_KIND,
            )
        )
    for y in y_ticks:
        _, cy = viewport.to_canvas(envelope.x_min, y)
        lines.append(
            CanvasLine(
                x1=top_left[0],
                y1=cy,
                x2=bottom_right[0],
                y2=cy,
                kind=GRID_KIND,
            )
        )
    corners = viewport.envelope_corners_canvas()
    border_pairs = (
        (corners[3], corners[2]),  # y_max edge
        (corners[2], corners[1]),  # x_max edge
        (corners[1], corners[0]),  # y_min edge
        (corners[0], corners[3]),  # x_min edge
    )
    for (x1, y1), (x2, y2) in border_pairs:
        lines.append(CanvasLine(x1=x1, y1=y1, x2=x2, y2=y2, kind=ENVELOPE_BORDER_KIND))

    min_r, max_r = default_probe_radius_range(viewport)
    if probe_min_radius is not None:
        min_r = probe_min_radius
    if probe_max_radius is not None:
        max_r = probe_max_radius
    probe_cx, probe_cy = viewport.to_canvas(position.x, position.y)
    circles: list[CanvasCircle] = [
        CanvasCircle(
            cx=probe_cx,
            cy=probe_cy,
            radius=probe_circle_radius(
                position.z, envelope, min_radius=min_r, max_radius=max_r
            ),
            kind=PROBE_KIND,
            label="probe",
            machine_x=position.x,
            machine_y=position.y,
        )
    ]
    markers: list[CanvasMarker] = []
    for feature in features:
        if isinstance(feature, IdCircleFeature):
            cx, cy = viewport.to_canvas(feature.center_x, feature.center_y)
            circles.append(
                CanvasCircle(
                    cx=cx,
                    cy=cy,
                    radius=viewport.length_to_pixels(feature.radius),
                    kind=ID_CIRCLE_KIND,
                    label="ID",
                    machine_x=feature.center_x,
                    machine_y=feature.center_y,
                    machine_diameter=feature.diameter,
                )
            )
        elif isinstance(feature, OdCircleFeature):
            cx, cy = viewport.to_canvas(feature.center_x, feature.center_y)
            circles.append(
                CanvasCircle(
                    cx=cx,
                    cy=cy,
                    radius=viewport.length_to_pixels(feature.radius),
                    kind=OD_CIRCLE_KIND,
                    label="OD",
                    machine_x=feature.center_x,
                    machine_y=feature.center_y,
                    machine_diameter=feature.diameter,
                )
            )
        elif isinstance(feature, ZHeightMarker):
            cx, cy = viewport.to_canvas(feature.x, feature.y)
            markers.append(
                CanvasMarker(
                    cx=cx,
                    cy=cy,
                    kind=Z_MARKER_KIND,
                    label=f"Z {feature.z:g}",
                    machine_x=feature.x,
                    machine_y=feature.y,
                    machine_z=feature.z,
                )
            )
        elif isinstance(feature, DxfOriginMarker):
            cx, cy = viewport.to_canvas(feature.x, feature.y)
            z_part = "" if feature.z is None else f" Z {feature.z:g}"
            markers.append(
                CanvasMarker(
                    cx=cx,
                    cy=cy,
                    kind=ORIGIN_MARKER_KIND,
                    label=f"origin{z_part}",
                    machine_x=feature.x,
                    machine_y=feature.y,
                    machine_z=feature.z,
                )
            )
        else:
            raise TypeError(f"unsupported session feature: {type(feature)!r}")

    return PreviewScene(
        viewport=viewport,
        lines=tuple(lines),
        circles=tuple(circles),
        markers=tuple(markers),
        envelope_is_placeholder=envelope.is_placeholder,
    )
