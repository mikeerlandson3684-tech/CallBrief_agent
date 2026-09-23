"""Tkinter chrome for the paralyzed main window.

Teal (not mint) rounded cards, pills, chips, and DRO frames.
Press animation is a darker fill — no raised square Tk look.
No GRBL, USB, file I/O, or probe cycles live here.
"""

from __future__ import annotations

import math
import tkinter as tk
import tkinter.font as tkfont
from collections.abc import Callable
from typing import Any

from digitizer import theme as T


def host_bg(widget: tk.Misc) -> str:
    try:
        bg = str(widget.cget("bg"))
        if bg:
            return bg
    except tk.TclError:
        pass
    return T.PAGE_BG


def shade(color: str, factor: float) -> str:
    raw = color.lstrip("#")
    if len(raw) != 6:
        return color
    r, g, b = int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)
    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))
    return f"#{r:02x}{g:02x}{b:02x}"


def round_rect(
    canvas: tk.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    radius: float,
    **kwargs: Any,
) -> int:
    """True circular-corner rounded rectangle (not a puffy spline)."""
    r = min(float(radius), max(0.0, (x2 - x1) / 2.0), max(0.0, (y2 - y1) / 2.0))
    if r <= 0.6:
        return canvas.create_rectangle(x1, y1, x2, y2, **kwargs)
    pts: list[float] = []
    corners = (
        (x2 - r, y1 + r, -90, 0),
        (x2 - r, y2 - r, 0, 90),
        (x1 + r, y2 - r, 90, 180),
        (x1 + r, y1 + r, 180, 270),
    )
    for cx, cy, a0, a1 in corners:
        a = a0
        while a <= a1:
            rad = math.radians(a)
            pts.extend((cx + r * math.cos(rad), cy + r * math.sin(rad)))
            a += 6
    kwargs.setdefault("smooth", False)
    return canvas.create_polygon(pts, **kwargs)


def round_top_rect(
    canvas: tk.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    radius: float,
    **kwargs: Any,
) -> int:
    """Rounded on the top corners, square along the bottom edge."""
    r = min(float(radius), max(0.0, (x2 - x1) / 2.0), max(0.0, (y2 - y1)))
    if r <= 0.6 or y2 - y1 < r:
        return canvas.create_rectangle(x1, y1, x2, y2, **kwargs)
    pts: list[float] = []
    for a in range(180, 271, 6):
        rad = math.radians(a)
        pts.extend((x1 + r + r * math.cos(rad), y1 + r + r * math.sin(rad)))
    for a in range(-90, 1, 6):
        rad = math.radians(a)
        pts.extend((x2 - r + r * math.cos(rad), y1 + r + r * math.sin(rad)))
    pts.extend((x2, y2, x1, y2))
    kwargs.setdefault("smooth", False)
    return canvas.create_polygon(pts, **kwargs)


def _inset_for_radius(radius: int) -> int:
    return max(int(round(radius * 0.36)), 4)


class RoundedFrame(tk.Frame):
    """Parent-colored corners + canvas rounded fill. Children go on ``inner``."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        radius: int = T.RADIUS_CHIP,
        fill: str = T.CARD_BG,
        outline: str = T.BORDER,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=host_bg(master), highlightthickness=0, bd=0, **kwargs)
        self._radius = radius
        self._fill = fill
        self._outline = outline
        self._canvas = tk.Canvas(self, bg=host_bg(master), highlightthickness=0, bd=0)
        self._canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        inset = _inset_for_radius(radius)
        self.inner = tk.Frame(self, bg=fill, highlightthickness=0, bd=0)
        self.inner.pack(fill="both", expand=True, padx=inset, pady=inset)
        self.bind("<Configure>", self._redraw, add="+")

    def _redraw(self, _event: tk.Event | None = None) -> None:  # type: ignore[type-arg]
        w, h = self.winfo_width(), self.winfo_height()
        self._canvas.delete("chip")
        if w < 8 or h < 8:
            return
        round_rect(
            self._canvas,
            1,
            1,
            w - 2,
            h - 2,
            self._radius,
            fill=self._fill,
            outline=self._outline,
            width=1,
            tags="chip",
        )


class TealCard(tk.Frame):
    """White body, teal header strip, rounded border that actually shows."""

    def __init__(
        self,
        master: tk.Misc,
        title: str,
        *,
        logger: Callable[[str], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=host_bg(master), highlightthickness=0, bd=0, **kwargs)
        self._radius = T.RADIUS_CARD
        self._canvas = tk.Canvas(self, bg=host_bg(master), highlightthickness=0, bd=0)
        self._canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        inset = _inset_for_radius(self._radius)

        self.header = tk.Frame(self, bg=T.HEADER_BG, highlightthickness=0, bd=0)
        self.header.pack(fill="x", padx=inset, pady=(inset, 0))
        self._title_lbl = tk.Label(
            self.header,
            text=title,
            bg=T.HEADER_BG,
            fg=T.HEADER_FG,
            font=T.FONT_BOLD,
            anchor="w",
        )
        self._title_lbl.pack(side="left", padx=10, pady=6)
        self.title_label = self._title_lbl
        if logger is not None:
            for w in (self.header, self._title_lbl):
                w.bind("<Button-1>", lambda _e, n=title: logger(n), add="+")
                w.configure(cursor="hand2")

        self.body = tk.Frame(self, bg=T.CARD_BG, highlightthickness=0, bd=0)
        self.body.pack(fill="both", expand=True, padx=inset, pady=(4, inset))
        self.bind("<Configure>", self._redraw, add="+")

    def _redraw(self, _event: tk.Event | None = None) -> None:  # type: ignore[type-arg]
        w, h = self.winfo_width(), self.winfo_height()
        self._canvas.delete("card")
        if w < 12 or h < 12:
            return
        r = self._radius
        round_rect(
            self._canvas,
            1,
            1,
            w - 2,
            h - 2,
            r,
            fill=T.CARD_BG,
            outline=T.BORDER,
            width=1,
            tags="card",
        )
        hh = self.header.winfo_y() + self.header.winfo_height() + 2
        hh = min(max(hh, 22), h - 4)
        round_top_rect(
            self._canvas,
            1,
            1,
            w - 2,
            hh,
            r,
            fill=T.HEADER_BG,
            outline="",
            tags="card",
        )
        round_rect(
            self._canvas,
            1,
            1,
            w - 2,
            h - 2,
            r,
            fill="",
            outline=T.BORDER,
            width=1,
            tags="card",
        )


class PillButton(tk.Frame):
    """Canvas pill/rounded button. Press darkens the fill; never raised-square Tk."""

    def __init__(
        self,
        master: tk.Misc,
        text: str,
        logger: Callable[[str], None],
        *,
        name: str | None = None,
        command: Callable[[], None] | None = None,
        pill: bool = False,
        radius: int | None = None,
        **kwargs: Any,
    ) -> None:
        bg = host_bg(master)
        super().__init__(master, bg=bg, highlightthickness=0, bd=0)
        self.control_name = name or text
        self._logger = logger
        self._command = command
        self._text = text
        self._pill = pill
        self._radius = T.RADIUS_BUTTON if radius is None else radius
        self._fill = str(kwargs.pop("bg", T.BTN_BG))
        self._fg = str(kwargs.pop("fg", T.BTN_FG))
        self._active_fill = str(kwargs.pop("activebackground", T.BTN_ACTIVE))
        kwargs.pop("activeforeground", None)
        kwargs.pop("relief", None)
        kwargs.pop("overrelief", None)
        kwargs.pop("bd", None)
        kwargs.pop("highlightthickness", None)
        kwargs.pop("takefocus", None)
        self._font = kwargs.pop("font", T.FONT)
        self._padx = int(kwargs.pop("padx", 14))
        self._pady = int(kwargs.pop("pady", 6))
        self._char_width = kwargs.pop("width", None)
        cursor = str(kwargs.pop("cursor", "hand2"))
        if kwargs:
            super().configure(**kwargs)

        self.selected = False
        self._pressed = False
        self._canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0, cursor=cursor)
        self._canvas.pack(fill="both", expand=True)
        self.pack_propagate(False)
        self._apply_size()
        self.bind("<Configure>", self._redraw, add="+")
        for target in (self, self._canvas):
            target.bind("<ButtonPress-1>", self._on_press, add="+")
            target.bind("<ButtonRelease-1>", self._on_release, add="+")
            target.bind("<Leave>", self._on_leave, add="+")

    def _font_obj(self) -> tkfont.Font:
        try:
            return tkfont.Font(font=self._font)
        except tk.TclError:
            return tkfont.Font(family="TkDefaultFont", size=10)

    def _apply_size(self) -> None:
        f = self._font_obj()
        tw = f.measure(self._text)
        if self._char_width is not None:
            tw = max(tw, f.measure("0") * int(self._char_width))
        th = f.metrics("linespace")
        tk.Frame.configure(self, width=tw + 2 * self._padx, height=th + 2 * self._pady)

    def _fill_now(self) -> str:
        if self._pressed:
            return self._active_fill
        if self.selected:
            return T.BTN_SELECTED if self._fill == T.BTN_BG else shade(self._fill, 0.88)
        return self._fill

    def _outline_now(self) -> str:
        if self._pressed or self.selected:
            return T.HIGHLIGHT
        if self._fill in (T.GREEN, T.GREEN_ACTIVE):
            return shade(self._fill, 0.85)
        return T.BTN_BORDER

    def _corner_radius(self, width: int, height: int) -> float:
        cap = max(min(width, height) / 2.0 - 1.0, 1.0)
        if self._pill:
            return cap
        return min(float(self._radius), cap)

    def _redraw(self, _event: tk.Event | None = None) -> None:  # type: ignore[type-arg]
        w, h = self.winfo_width(), self.winfo_height()
        self._canvas.delete("all")
        if w < 8 or h < 8:
            return
        parent = host_bg(self.master)
        tk.Frame.configure(self, bg=parent)
        self._canvas.configure(bg=parent)
        inset = 1.5 if self._pressed else 1.0
        round_rect(
            self._canvas,
            inset,
            inset,
            w - inset,
            h - inset,
            self._corner_radius(w, h),
            fill=self._fill_now(),
            outline=self._outline_now(),
            width=1,
        )
        self._canvas.create_text(
            w / 2,
            h / 2 + (1 if self._pressed else 0),
            text=self._text,
            fill=self._fg,
            font=self._font,
        )

    def _on_press(self, _event: object | None = None) -> None:
        self._pressed = True
        self._redraw()

    def _on_leave(self, _event: object | None = None) -> None:
        if self._pressed:
            self._pressed = False
            self._redraw()

    def _on_release(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        was = self._pressed
        self._pressed = False
        self._redraw()
        if not was:
            return
        x, y = event.x, event.y
        if 0 <= x <= self.winfo_width() and 0 <= y <= self.winfo_height():
            self.invoke()

    def invoke(self) -> None:
        self._logger(self.control_name)
        if self._command is not None:
            self._command()

    def set_selected(self, value: bool) -> None:
        self.selected = value
        self._redraw()

    def configure(self, cnf: Any = None, **kwargs: Any) -> Any:  # type: ignore[override]
        if isinstance(cnf, str) and not kwargs:
            return tk.Frame.configure(self, cnf)
        if isinstance(cnf, dict):
            kwargs = {**cnf, **kwargs}
        if "relief" in kwargs:
            relief = kwargs.pop("relief")
            self.selected = str(relief) in ("sunken", "groove", "ridge")
        kwargs.pop("overrelief", None)
        kwargs.pop("bd", None)
        if "bg" in kwargs:
            self._fill = str(kwargs.pop("bg"))
        if "fg" in kwargs:
            self._fg = str(kwargs.pop("fg"))
        if "activebackground" in kwargs:
            self._active_fill = str(kwargs.pop("activebackground"))
        kwargs.pop("activeforeground", None)
        if "font" in kwargs:
            self._font = kwargs.pop("font")
        if "text" in kwargs:
            self._text = str(kwargs.pop("text"))
        if "padx" in kwargs:
            self._padx = int(kwargs.pop("padx"))
        if "pady" in kwargs:
            self._pady = int(kwargs.pop("pady"))
        if "width" in kwargs:
            self._char_width = kwargs.pop("width")
        if "cursor" in kwargs:
            self._canvas.configure(cursor=str(kwargs.pop("cursor")))
        result = super().configure(**kwargs) if kwargs else None
        self._apply_size()
        self._redraw()
        return result

    config = configure  # type: ignore[assignment]


class ToggleButton(PillButton):
    """Stays visually selected (teal fill) while on — still paralyzed."""

    def __init__(
        self,
        master: tk.Misc,
        text: str,
        logger: Callable[[str], None],
        *,
        name: str | None = None,
        grouped: list[ToggleButton] | None = None,
        **kwargs: Any,
    ) -> None:
        self.grouped = grouped
        super().__init__(master, text, logger, name=name, command=self._toggle, **kwargs)

    def _toggle(self) -> None:
        if self.grouped is not None:
            for other in self.grouped:
                other.set_selected(other is self)
            return
        self.set_selected(not self.selected)


class MessageLog(tk.Frame):
    """Scrolling transcript. The parent card header is the click target."""

    def __init__(self, master: tk.Misc, **kwargs: Any) -> None:
        super().__init__(master, bg=T.CARD_BG, highlightthickness=0, bd=0, **kwargs)
        self.lines: list[str] = []
        wrap = RoundedFrame(self, radius=T.RADIUS_ENTRY, fill=T.MSG_BG, outline=T.BORDER)
        wrap.pack(fill="both", expand=True)
        self.text = tk.Text(
            wrap.inner,
            height=6,
            wrap="word",
            bg=T.MSG_BG,
            fg=T.LABEL_FG,
            font=("Consolas", 9),
            relief="flat",
            bd=0,
            state="disabled",
            highlightthickness=0,
        )
        scroll = tk.Scrollbar(wrap.inner, command=self.text.yview, bd=0, relief="flat")
        self.text.configure(yscrollcommand=scroll.set)
        self.text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def append(self, line: str) -> None:
        self.lines.append(line)
        self.text.configure(state="normal")
        self.text.insert("end", line + "\n")
        self.text.see("end")
        self.text.configure(state="disabled")


class ProbeLamp(tk.Frame):
    """Clickable Probe Active lamp (gray until a later strike feed)."""

    def __init__(self, master: tk.Misc, logger: Callable[[str], None], **kwargs: Any) -> None:
        super().__init__(master, bg=host_bg(master), highlightthickness=0, bd=0, **kwargs)
        self._on = False
        self._canvas = tk.Canvas(
            self, width=18, height=18, bg=host_bg(master), highlightthickness=0, cursor="hand2"
        )
        self._canvas.pack(side="left")
        self._dot = self._canvas.create_oval(3, 3, 15, 15, fill=T.LAMP_OFF, outline="#94a3b8")
        self._label = tk.Label(
            self, text="Probe Active", bg=host_bg(master), fg=T.LABEL_FG, font=T.FONT, cursor="hand2"
        )
        self._label.pack(side="left", padx=(6, 0))
        for w in (self._canvas, self._label, self):
            w.bind("<ButtonPress-1>", self._press, add="+")
            w.bind("<ButtonRelease-1>", self._release, add="+")
        self._logger = logger

    def _press(self, _event: object | None = None) -> None:
        self._canvas.itemconfigure(self._dot, outline=T.HIGHLIGHT, width=2)

    def _release(self, _event: object | None = None) -> None:
        self._canvas.itemconfigure(self._dot, outline="#94a3b8", width=1)
        self._logger("Probe Active")

    def set_lit(self, on: bool) -> None:
        self._on = on
        self._canvas.itemconfigure(self._dot, fill=T.LAMP_ON if on else T.LAMP_OFF)


class RoundedEntry(RoundedFrame):
    """Flat entry sitting inside a rounded teal-outline chip."""

    def __init__(
        self,
        master: tk.Misc,
        logger: Callable[[str], None],
        name: str,
        *,
        textvariable: tk.StringVar | None = None,
        width: int = 8,
    ) -> None:
        super().__init__(master, radius=T.RADIUS_ENTRY, fill=T.ENTRY_BG, outline=T.BORDER)
        self._logger = logger
        self._name = name
        self.entry = tk.Entry(
            self.inner,
            textvariable=textvariable,
            width=width,
            relief="flat",
            bd=0,
            bg=T.ENTRY_BG,
            font=T.FONT,
            highlightthickness=0,
        )
        self.entry.pack(fill="x", ipady=2, padx=2)
        for w in (self, self.inner, self.entry):
            w.bind("<ButtonPress-1>", self._down, add="+")
            w.bind("<ButtonRelease-1>", self._up, add="+")

    def _down(self, _event: object | None = None) -> None:
        self._outline = T.HIGHLIGHT
        self._redraw()

    def _up(self, _event: object | None = None) -> None:
        self._outline = T.BORDER
        self._redraw()
        self._logger(self._name)
        self.entry.focus_set()


def pressable_entry(
    master: tk.Misc,
    logger: Callable[[str], None],
    name: str,
    *,
    textvariable: tk.StringVar | None = None,
    width: int = 8,
) -> RoundedEntry:
    return RoundedEntry(master, logger, name, textvariable=textvariable, width=width)


def pressable_label(
    master: tk.Misc,
    text: str,
    logger: Callable[[str], None],
    name: str,
    **kwargs: Any,
) -> tk.Label:
    kwargs.setdefault("bg", host_bg(master))
    kwargs.setdefault("fg", T.LABEL_FG)
    kwargs.setdefault("font", T.FONT)
    kwargs.setdefault("relief", "flat")
    kwargs.setdefault("bd", 0)
    kwargs.setdefault("highlightthickness", 0)
    kwargs.setdefault("cursor", "hand2")
    kwargs.setdefault("padx", 8)
    kwargs.setdefault("pady", 4)
    rest_fg = str(kwargs.get("fg", T.LABEL_FG))
    lbl = tk.Label(master, text=text, **kwargs)

    def _down(_event: object | None = None) -> None:
        lbl.configure(fg=T.HIGHLIGHT)

    def _up(_event: object | None = None) -> None:
        lbl.configure(fg=rest_fg)
        logger(name)

    lbl.bind("<ButtonPress-1>", _down, add="+")
    lbl.bind("<ButtonRelease-1>", _up, add="+")
    return lbl


def write_window_png(root: tk.Tk, path: str) -> None:
    """Grab the toplevel via the X11 window id (ImageMagick ``import``)."""
    import shutil
    import subprocess

    root.update_idletasks()
    root.update()
    try:
        root.attributes("-topmost", True)
        root.lift()
        root.focus_force()
    except tk.TclError:
        pass
    root.update_idletasks()
    root.update()
    wid = hex(root.winfo_id())
    if shutil.which("import"):
        subprocess.run(["import", "-window", wid, path], check=True)
        return
    if shutil.which("gnome-screenshot"):
        subprocess.run(["gnome-screenshot", "-w", "-f", path], check=True)
        return
    raise SystemExit(
        f"No screenshot tool (ImageMagick import / gnome-screenshot). Window id={wid}."
    )
