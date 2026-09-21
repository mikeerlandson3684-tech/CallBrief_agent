"""Envelope scale, grid, and Z→radius mapping."""

from digitizer.machine_config import WorkingEnvelope
from digitizer.preview_geom import (
    PROBE_RADIUS_FRAC_ZMAX,
    PROBE_RADIUS_FRAC_ZMIN,
    grid_step,
    iter_ticks,
    probe_radius_machine,
    view_transform,
)


def _env(**overrides: float | str) -> WorkingEnvelope:
    data: dict[str, float | str] = dict(
        x_min=0.0,
        x_max=12.0,
        y_min=0.0,
        y_max=12.0,
        z_min=0.0,
        z_max=4.0,
        units="in",
    )
    data.update(overrides)
    return WorkingEnvelope(
        x_min=float(data["x_min"]),
        x_max=float(data["x_max"]),
        y_min=float(data["y_min"]),
        y_max=float(data["y_max"]),
        z_min=float(data["z_min"]),
        z_max=float(data["z_max"]),
        units=str(data["units"]),
    )


def test_z_min_is_smallest_circle() -> None:
    env = _env()
    r = probe_radius_machine(env.z_min, env)
    assert r == PROBE_RADIUS_FRAC_ZMIN * env.min_xy_span()


def test_z_max_is_largest_circle() -> None:
    env = _env()
    r = probe_radius_machine(env.z_max, env)
    assert r == PROBE_RADIUS_FRAC_ZMAX * env.min_xy_span()


def test_z_plus_grows_z_minus_shrinks() -> None:
    env = _env()
    r_low = probe_radius_machine(0.5, env)
    r_high = probe_radius_machine(3.5, env)
    assert r_high > r_low


def test_z_is_clamped() -> None:
    env = _env()
    r_min = probe_radius_machine(env.z_min, env)
    r_max = probe_radius_machine(env.z_max, env)
    assert probe_radius_machine(-100.0, env) == r_min
    assert probe_radius_machine(100.0, env) == r_max


def test_mid_z_is_linear() -> None:
    env = _env()
    r_min = probe_radius_machine(env.z_min, env)
    r_max = probe_radius_machine(env.z_max, env)
    r_mid = probe_radius_machine(2.0, env)
    assert abs(r_mid - (r_min + r_max) / 2.0) < 1e-9


def test_zero_z_span_stays_at_rmin() -> None:
    env = _env(z_min=1.0, z_max=1.0)
    assert probe_radius_machine(1.0, env) == PROBE_RADIUS_FRAC_ZMIN * 12.0
    assert probe_radius_machine(9.0, env) == PROBE_RADIUS_FRAC_ZMIN * 12.0


def test_view_fits_full_envelope_not_part() -> None:
    env = _env()
    view = view_transform(env, 500, 500, margin_left=40, margin_right=16, margin_top=16, margin_bottom=32)
    bl = view.to_canvas(env.x_min, env.y_min)
    tr = view.to_canvas(env.x_max, env.y_max)
    # Y is up: min Y is lower on the canvas (larger pixel y).
    assert bl[1] > tr[1]
    assert bl[0] < tr[0]
    # Entire envelope is inside the canvas.
    assert 0 <= bl[0] <= 500 and 0 <= bl[1] <= 500
    assert 0 <= tr[0] <= 500 and 0 <= tr[1] <= 500
    # Square envelope in a square-minus-margins drawable stays square.
    width_px = tr[0] - bl[0]
    height_px = bl[1] - tr[1]
    assert abs(width_px - height_px) < 1e-6


def test_view_letterboxes_wide_canvas() -> None:
    env = _env()
    view = view_transform(env, 800, 400)
    bl = view.to_canvas(0, 0)
    tr = view.to_canvas(12, 12)
    used_w = tr[0] - bl[0]
    used_h = bl[1] - tr[1]
    assert abs(used_w - used_h) < 1e-6
    # Horizontal letterbox: leftover width on the sides.
    assert bl[0] > 40  # more than left margin alone on a wide canvas


def test_grid_step_inches() -> None:
    assert grid_step(12.0, "in") == 1.0


def test_grid_ticks_include_ends() -> None:
    ticks = iter_ticks(0.0, 12.0, 1.0)
    assert ticks[0] == 0.0
    assert ticks[-1] == 12.0
    assert 6.0 in ticks
