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


def test_window_title_is_low_k8(app: MainWindow) -> None:
    assert app.title() == "Low-K8"


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


def test_theme_is_teal_not_mint() -> None:
    from digitizer import theme as T

    assert T.HEADER_BG.lower() != "#d1fae5"
    r = int(T.HEADER_BG[1:3], 16)
    b = int(T.HEADER_BG[5:7], 16)
    assert b >= r  # teal/cyan, not mint-green


def test_buttons_and_cards_are_rounded_not_raised_tk(app: MainWindow) -> None:
    from digitizer.chrome import PillButton, TealCard

    cap = app.controls["Capture Feature"]
    init = app.controls["Initialized"]
    preview_card = app.controls["DXF Preview"]
    assert isinstance(cap, PillButton)
    assert isinstance(init, PillButton)
    assert not isinstance(cap, tk.Button)
    assert init._pill is True  # noqa: SLF001
    assert cap._pill is True  # noqa: SLF001
    assert str(tk.Frame.cget(init, "relief")) == "flat"
    assert isinstance(preview_card, TealCard)
    assert preview_card._radius >= 12  # noqa: SLF001
    canvases = [w for w in cap.winfo_children() if isinstance(w, tk.Canvas)]
    assert canvases, "pill buttons draw on a canvas"
    app.update_idletasks()
    app.update()
    # Capsule Initialized: corner radius is half the height.
    h = init.winfo_height()
    w = init.winfo_width()
    assert h > 8 and w > h
    assert init._corner_radius(w, h) >= h / 2 - 2  # noqa: SLF001


def test_pill_buttons_fill_canvas_without_side_gutters(app: MainWindow) -> None:
    """Rectangular canvas leftover on left/right of the stadium is the shape bug."""
    from digitizer.chrome import PillButton

    for name in ("New File", "Capture Feature", "FINISH PROBING", "Initialized", "Y+"):
        btn = app.controls[name]
        assert isinstance(btn, PillButton)
        canvas = next(c for c in btn.winfo_children() if isinstance(c, tk.Canvas))
        bw, bh = btn.winfo_width(), btn.winfo_height()
        assert bw > 8 and bh > 8
        assert float(canvas.cget("width")) <= 8
        assert float(canvas.cget("height")) <= 8
        assert int(canvas.cget("highlightthickness")) == 0
        assert str(canvas.cget("highlightbackground")).lower() == str(btn.cget("bg")).lower()
        polys = [i for i in canvas.find_all() if canvas.type(i) == "polygon"]
        assert polys, name
        xs = canvas.coords(polys[0])[0::2]
        ys = canvas.coords(polys[0])[1::2]
        assert min(xs) <= 1.0, name
        assert max(xs) >= bw - 1.0, name
        assert min(ys) <= 1.0, name
        assert max(ys) >= bh - 1.0, name
        assert btn._corner_radius(bw, bh) >= min(bw, bh) / 2.0 - 0.5  # noqa: SLF001


def test_teal_card_header_band_is_edge_to_edge(app: MainWindow) -> None:
    """Header strip must fill the card width so side gutters are not CARD_BG."""
    from digitizer.chrome import TealCard
    from digitizer import theme as T

    assert T.HEADER_BG.lower() == "#c5ece8"

    def _cards(widget: tk.Misc) -> list[TealCard]:
        found: list[TealCard] = []
        if isinstance(widget, TealCard):
            found.append(widget)
        for child in widget.winfo_children():
            found.extend(_cards(child))
        return found

    app.update_idletasks()
    app.update()
    cards = _cards(app)
    titles = [c.title_label.cget("text") for c in cards]
    for need in ("DRO Position", "Status", "Jog", "Feature", "Messages", "DXF Preview"):
        assert need in titles, titles
    for card in cards:
        title = str(card.title_label.cget("text"))
        card_w = card.winfo_width()
        header_bottom = card.header.winfo_y() + card.header.winfo_height()
        min_x = min_y = 10**9
        max_x = max_y = -10**9
        found = False
        for item in card._canvas.find_withtag("card"):  # noqa: SLF001
            fill = str(card._canvas.itemcget(item, "fill")).lower()
            if fill != T.HEADER_BG.lower():
                continue
            coords = card._canvas.coords(item)
            if len(coords) < 4:
                continue
            xs, ys = coords[0::2], coords[1::2]
            min_x, max_x = min(min_x, min(xs)), max(max_x, max(xs))
            min_y, max_y = min(min_y, min(ys)), max(max_y, max(ys))
            found = True
        assert found, f"{title}: no teal header fill on canvas"
        assert min_x <= 2, f"{title}: left header gutter {min_x}"
        assert max_x >= card_w - 3, f"{title}: right header gutter {card_w - max_x}"
        assert max_y >= header_bottom - 1, f"{title}: header fill {max_y} < strip {header_bottom}"
        assert min_y <= 2, f"{title}: header fill starts at {min_y}"


def _chrome_widgets(widget: tk.Misc) -> list[tk.Misc]:
    from digitizer.chrome import PillButton, RoundedFrame, TealCard

    found: list[tk.Misc] = []
    if isinstance(widget, (TealCard, RoundedFrame, PillButton)):
        found.append(widget)
    for child in widget.winfo_children():
        found.extend(_chrome_widgets(child))
    return found


def test_safe_stroke_box_insets_every_side() -> None:
    from digitizer.chrome import STROKE_INSET, _safe_stroke_box

    x1, y1, x2, y2 = _safe_stroke_box(0.5, 0.5, 299.5, 199.5, STROKE_INSET)
    assert (x1, y1, x2, y2) == (1.0, 1.0, 299.0, 199.0)


def test_chrome_outlines_close_on_all_four_sides(app: MainWindow) -> None:
    """Ring is a closed line inset from the canvas edge on every side, not a clipped polygon."""
    from digitizer.chrome import PillButton, RoundedFrame, TealCard
    from digitizer import theme as T

    assert T.HEADER_BG.lower() == "#c5ece8"
    assert T.BORDER.lower() == "#b7d4d0"

    app.update_idletasks()
    app.update()
    widgets = _chrome_widgets(app)
    kinds = {type(w).__name__ for w in widgets}
    assert "TealCard" in kinds
    assert "PillButton" in kinds
    assert "RoundedFrame" in kinds
    titles = [
        str(w.title_label.cget("text"))  # type: ignore[attr-defined]
        for w in widgets
        if isinstance(w, TealCard)
    ]
    for need in (
        "DRO Position",
        "Status",
        "Jog",
        "Feature",
        "Capture",
        "Z Control",
        "Datum",
        "Incremental",
        "DXF Preview",
        "Messages",
    ):
        assert need in titles, titles

    checked = 0
    for widget in widgets:
        canvas = getattr(widget, "_canvas", None)
        if canvas is None:
            continue
        bw, bh = widget.winfo_width(), widget.winfo_height()
        if bw < 12 or bh < 12:
            continue
        rings = list(canvas.find_withtag("ring"))
        assert rings, f"{widget}: no outline ring"
        for item in rings:
            assert canvas.type(item) == "line", f"{widget}: outline is {canvas.type(item)}, not line"
            coords = canvas.coords(item)
            assert len(coords) >= 10, f"{widget}: outline too short {len(coords)}"
            assert abs(coords[0] - coords[-2]) < 0.05, f"{widget}: outline not closed x"
            assert abs(coords[1] - coords[-1]) < 0.05, f"{widget}: outline not closed y"
            xs, ys = coords[0::2], coords[1::2]
            assert min(xs) >= 0.9, f"{widget}: left stroke at {min(xs)} would clip"
            assert min(ys) >= 0.9, f"{widget}: top stroke at {min(ys)} would clip"
            assert max(xs) <= bw - 0.9, f"{widget}: right stroke at {max(xs)} of {bw} would clip"
            assert max(ys) <= bh - 0.9, f"{widget}: bottom stroke at {max(ys)} of {bh} would clip"
            assert min(xs) <= 2.5, f"{widget}: left side missing ({min(xs)})"
            assert min(ys) <= 2.5, f"{widget}: top side missing ({min(ys)})"
            assert max(xs) >= bw - 2.5, f"{widget}: right side missing ({max(xs)} vs {bw})"
            assert max(ys) >= bh - 2.5, f"{widget}: bottom side missing ({max(ys)} vs {bh})"
        checked += 1
    assert checked >= 20, f"too few outlined widgets checked: {checked}"


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
