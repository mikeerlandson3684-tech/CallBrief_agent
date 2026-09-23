"""Tkinter widget smoke tests (DISPLAY required)."""

from __future__ import annotations

import os

import pytest

from digitizer.machine_config import default_envelope, envelope_disclaimer
from digitizer.position import SimulatedPosition
from digitizer.preview import DxfPreview
from digitizer.preview_geom import probe_radius_machine, view_transform
from digitizer.session import CaptureSession, sample_session

pytestmark = pytest.mark.skipif(
    not os.environ.get("DISPLAY"),
    reason="Tkinter preview tests need a display",
)


@pytest.fixture
def tk_root():
    import tkinter as tk

    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def test_empty_file_draws_grid_and_probe_only(tk_root) -> None:
    pos = SimulatedPosition(6.0, 6.0, 2.0)
    session = CaptureSession()
    widget = DxfPreview(tk_root, position_source=pos, session=session, poll_ms=0)
    widget.pack(fill="both", expand=True)
    widget.canvas.config(width=400, height=400)
    widget.update_idletasks()
    widget.update()
    widget.redraw()

    kinds = [widget.canvas.type(i) for i in widget.canvas.find_all()]
    assert "line" in kinds  # grid / envelope / probe cross
    assert "oval" in kinds  # probe circle
    assert "polygon" not in kinds  # no Z diamond
    texts = [
        widget.canvas.itemcget(i, "text")
        for i in widget.canvas.find_all()
        if widget.canvas.type(i) == "text"
    ]
    joined = " ".join(texts)
    assert "ID" not in joined
    assert "OD" not in joined
    assert "DXF origin" not in joined
    assert "Placeholder envelope" in widget.envelope_disclaimer()
    widget.destroy()


def test_sample_file_draws_id_od_origin_and_z(tk_root) -> None:
    pos = SimulatedPosition(1.0, 1.0, 0.0)
    widget = DxfPreview(tk_root, position_source=pos, session=sample_session(), poll_ms=0)
    widget.pack(fill="both", expand=True)
    widget.canvas.config(width=400, height=400)
    widget.update()
    widget.redraw()
    texts = [
        widget.canvas.itemcget(i, "text")
        for i in widget.canvas.find_all()
        if widget.canvas.type(i) == "text"
    ]
    joined = " ".join(texts)
    assert "ID" in joined
    assert "OD" in joined
    assert "DXF origin" in joined
    assert "Z " in joined
    widget.destroy()


def test_probe_circle_grows_with_z(tk_root) -> None:
    env = default_envelope()
    pos = SimulatedPosition(6.0, 6.0, env.z_min)
    widget = DxfPreview(tk_root, position_source=pos, session=CaptureSession(), poll_ms=0)
    widget.pack(fill="both", expand=True)
    widget.canvas.config(width=400, height=400)
    widget.update()
    widget.redraw()

    def _probe_width() -> float:
        ovals = [
            i
            for i in widget.canvas.find_withtag("probe")
            if widget.canvas.type(i) == "oval"
        ]
        assert ovals
        x0, y0, x1, y1 = widget.canvas.coords(ovals[0])
        return x1 - x0

    small_w = _probe_width()
    pos.set_xyz(6.0, 6.0, env.z_max)
    widget.redraw()
    large_w = _probe_width()
    assert large_w > small_w
    canvas_w, canvas_h = widget._canvas_size()  # noqa: SLF001
    view = view_transform(env, float(canvas_w), float(canvas_h))
    expected = max(view.radius_px(probe_radius_machine(env.z_max, env)), 3.0)
    assert abs(large_w / 2.0 - expected) < 1.5
    widget.destroy()


def test_disclaimer_mentions_placeholder(tk_root) -> None:
    widget = DxfPreview(tk_root, poll_ms=0)
    widget.stop_polling()
    text = envelope_disclaimer()
    assert "Placeholder" in text
    assert widget._banner.get()  # noqa: SLF001 — banner is the on-screen disclaimer
    widget.destroy()
