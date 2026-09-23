"""Paralyzed main-window smoke tests (DISPLAY required)."""

from __future__ import annotations

import inspect
import os
import tkinter as tk

import pytest

from digitizer.main_window import MainWindow
from digitizer.machine_config import default_envelope
from digitizer.preview_geom import probe_radius_machine, view_transform

pytestmark = pytest.mark.skipif(
    not os.environ.get("DISPLAY"),
    reason="Tkinter main-window tests need a display",
)

REQUIRED_CONTROLS = (
    "Main",
    "Hotkeys",
    "Initialized",
    "New File",
    "Open File",
    "Save",
    "Close",
    "Settings",
    "Calibration",
    "DRO X",
    "DRO Y",
    "DRO Z",
    "GO TO X",
    "GO TO Y",
    "GO TO Z",
    "GO TO",
    "HOMED",
    "STATE",
    "Y+",
    "X-",
    "Home",
    "X+",
    "Y-",
    "Z+",
    "Z-",
    "Jog Speed",
    "ID Circle",
    "OD Circle",
    "Probe Active",
    "Capture Feature",
    "Capture Z Height",
    "Lock Z",
    "Z Value",
    "Set DXF Origin",
    '.001"',
    '.010"',
    '.100"',
    "Custom",
    "Custom increment",
    "Measured Diameter",
    "FINISH PROBING",
    "Discard Since Last Save",
    "Messages",
    "DXF Preview",
    "Empty file",
    "Sample captures",
)


@pytest.fixture
def app():
    win = MainWindow()
    win.update_idletasks()
    win.update()
    yield win
    win.destroy()


def test_required_controls_exist(app: MainWindow) -> None:
    missing = [name for name in REQUIRED_CONTROLS if name not in app.controls]
    assert missing == []


def test_every_control_logs_pressed(app: MainWindow) -> None:
    before = list(app.messages.lines)
    for name in REQUIRED_CONTROLS:
        app.click_control(name)
        assert any(line == f"{name} pressed" for line in app.messages.lines[len(before) :]), name
    # Preview stays a live widget, not a paralyzed dead canvas.
    assert app.preview.canvas.find_all()


def test_save_and_close_exist_bridge_does_not(app: MainWindow) -> None:
    assert "Save" in app.controls
    assert "Close" in app.controls
    assert "Bridge" not in app.controls
    texts = _widget_texts(app)
    joined = " ".join(texts)
    assert "Bridge" not in joined
    assert "COM4" not in joined
    assert "Rectangle" not in joined
    assert "Inner" not in joined
    assert "Outer" not in joined
    assert "Stylus" not in joined


def test_id_and_od_are_separate_controls(app: MainWindow) -> None:
    assert "ID Circle" in app.controls
    assert "OD Circle" in app.controls
    app.click_control("OD Circle")
    assert app._od_btn.selected  # noqa: SLF001
    assert not app._id_btn.selected  # noqa: SLF001
    app.click_control("ID Circle")
    assert app._id_btn.selected  # noqa: SLF001


def test_goto_and_jog_do_not_move(app: MainWindow) -> None:
    before = app.position.get_xyz()
    app.click_control("GO TO")
    app.click_control("Y+")
    app.click_control("Home")
    app.click_control("FINISH PROBING")
    app.click_control("Capture Feature")
    app.click_control("New File")
    assert app.position.get_xyz() == before


def test_preview_z_circle_still_grows(app: MainWindow) -> None:
    env = default_envelope()
    app.position.set_xyz(6.0, 6.0, env.z_min)
    app.preview.redraw()
    app.update()

    def _probe_width() -> float:
        ovals = [
            i
            for i in app.preview.canvas.find_withtag("probe")
            if app.preview.canvas.type(i) == "oval"
        ]
        assert ovals
        x0, y0, x1, y1 = app.preview.canvas.coords(ovals[0])
        return x1 - x0

    small = _probe_width()
    app.position.set_xyz(6.0, 6.0, env.z_max)
    app.preview.redraw()
    app.update()
    large = _probe_width()
    assert large > small
    canvas_w, canvas_h = app.preview._canvas_size()  # noqa: SLF001
    view = view_transform(env, float(canvas_w), float(canvas_h))
    expected = max(view.radius_px(probe_radius_machine(env.z_max, env)), 3.0)
    assert abs(large / 2.0 - expected) < 1.5


def test_hotkeys_stub_has_bind_boxes(app: MainWindow) -> None:
    app.click_control("Hotkeys")
    assert app._hotkeys is not None  # noqa: SLF001
    box = app._hotkeys.bind_boxes["Capture Feature"]
    box.event_generate("<ButtonPress-1>")
    box.event_generate("<ButtonRelease-1>")
    app.update()
    assert any("Capture Feature bind box pressed" in line for line in app.messages.lines)
    app._close_hotkeys()


def test_minsize_keeps_footer_above_sim_bar(app: MainWindow) -> None:
    min_w, min_h = app.minsize()
    assert min_h >= 840
    app.geometry(f"{int(min_w)}x{int(min_h)}")
    app.update_idletasks()
    app.update()
    sim_top = app._sim_bar.winfo_rooty()  # noqa: SLF001
    ay = app.winfo_rooty()
    ah = app.winfo_height()
    for name in ("Jog Speed", "Custom increment", "Measured Diameter"):
        widget = app.controls[name]
        y = widget.winfo_rooty()
        height = widget.winfo_height()
        assert widget.winfo_width() > 1 and height >= 20, name
        assert y + height <= ay + ah + 2, name
        assert y + height <= sim_top + 2, name


def test_incremental_hint_wraps_inside_card(app: MainWindow) -> None:
    min_w, min_h = app.minsize()
    app.geometry(f"{int(min_w)}x{int(min_h)}")
    app.update_idletasks()
    app.update()
    note = app._inc_note  # noqa: SLF001
    wrap = int(float(note.cget("wraplength")))
    assert wrap <= note.winfo_width() + 2
    assert wrap >= 80
    assert "Not GO TO" in note.cget("text")


def test_destroy_cancels_dro_poll() -> None:
    win = MainWindow()
    win.update()
    assert win._dro_job is not None  # noqa: SLF001
    win.destroy()
    win2 = MainWindow()
    win2.update_idletasks()
    win2.update()
    win2.destroy()


def test_main_window_is_not_a_motion_or_gcode_client() -> None:
    from digitizer import chrome, hotkeys, main_window

    for mod in (main_window, chrome, hotkeys):
        source = inspect.getsource(mod)
        lower = source.lower()
        assert "import serial" not in source
        assert "g38" not in lower
        assert "g90" not in lower
        assert "g91" not in lower
        assert "g-code" in lower or "grbl" in lower  # mentioned as what this is not


def _widget_texts(widget: tk.Misc) -> list[str]:
    out: list[str] = []
    try:
        out.append(str(widget.cget("text")))
    except tk.TclError:
        pass
    for child in widget.winfo_children():
        out.extend(_widget_texts(child))
    return out
