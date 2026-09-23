"""Tkinter chrome for the paralyzed main window.

Approximate rounded teal cards and raised/sunken press feedback.
No GRBL, USB, file I/O, or probe cycles live here.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from typing import Any

from digitizer import theme as T


def round_rect(
    canvas: tk.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    radius: float,
    **kwargs: Any,
) -> int:
    """Smooth polygon approximating a rounded rectangle."""
    r = min(radius, max(0.0, (x2 - x1) / 2.0), max(0.0, (y2 - y1) / 2.0))
    points = (
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
        x1 + r, y1,
    )
    return canvas.create_polygon(points, smooth=True, **kwargs)


class TealCard(tk.Frame):
    """White body, mint header strip, approximated rounded border."""

    def __init__(
        self,
        master: tk.Misc,
        title: str,
        *,
        logger: Callable[[str], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=T.PAGE_BG, **kwargs)
        self._radius = 14
        self._canvas = tk.Canvas(self, bg=T.PAGE_BG, highlightthickness=0, bd=0)
        self._canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        pad = 3
        self._shell = tk.Frame(self, bg=T.CARD_BG)
        self._shell.pack(fill="both", expand=True, padx=pad, pady=pad)

        self.header = tk.Frame(self._shell, bg=T.HEADER_BG)
        self.header.pack(fill="x")
        self._title_lbl = tk.Label(
            self.header,
            text=title,
            bg=T.HEADER_BG,
            fg=T.HEADER_FG,
            font=T.FONT_BOLD,
            anchor="w",
        )
        self._title_lbl.pack(side="left", padx=10, pady=5)
        self.title_label = self._title_lbl
        if logger is not None:
            for w in (self.header, self._title_lbl):
                w.bind("<Button-1>", lambda _e, n=title: logger(n), add="+")
                w.configure(cursor="hand2")

        self.body = tk.Frame(self._shell, bg=T.CARD_BG)
        self.body.pack(fill="both", expand=True, padx=8, pady=8)
        self.bind("<Configure>", self._redraw, add="+")

    def _redraw(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        w, h = event.width, event.height
        self._canvas.delete("card")
        if w < 10 or h < 10:
            return
        round_rect(
            self._canvas,
            1,
            1,
            w - 2,
            h - 2,
            self._radius,
            fill=T.CARD_BG,
            outline=T.BORDER,
            width=1,
            tags="card",
        )
        hh = max(self.header.winfo_height() + 3, 22)
        round_rect(
            self._canvas,
            1,
            1,
            w - 2,
            min(hh + 8, h - 2),
            self._radius,
            fill=T.HEADER_BG,
            outline="",
            tags="card",
        )
        self._canvas.create_rectangle(
            2,
            hh - 4,
            w - 3,
            hh + 4,
            fill=T.HEADER_BG,
            outline="",
            tags="card",
        )


class PillButton(tk.Button):
    """Raised control that sinks on press and reports ``'{name} pressed'``."""

    def __init__(
        self,
        master: tk.Misc,
        text: str,
        logger: Callable[[str], None],
        *,
        name: str | None = None,
        command: Callable[[], None] | None = None,
        **kwargs: Any,
    ) -> None:
        self.control_name = name or text
        kwargs.setdefault("relief", "raised")
        kwargs.setdefault("bd", 2)
        kwargs.setdefault("bg", T.BTN_BG)
        kwargs.setdefault("fg", T.BTN_FG)
        kwargs.setdefault("activebackground", T.BTN_ACTIVE)
        kwargs.setdefault("activeforeground", T.BTN_FG)
        kwargs.setdefault("highlightthickness", 0)
        kwargs.setdefault("cursor", "hand2")
        kwargs.setdefault("font", T.FONT)
        kwargs.setdefault("pady", 4)
        kwargs.setdefault("padx", 10)
        kwargs.setdefault("overrelief", "sunken")
        kwargs.setdefault("takefocus", 1)

        def _cmd() -> None:
            logger(self.control_name)
            if command is not None:
                command()

        super().__init__(master, text=text, command=_cmd, **kwargs)


class ToggleButton(PillButton):
    """Stays sunken while selected (visual only)."""

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
        self.selected = False
        self.grouped = grouped
        super().__init__(master, text, logger, name=name, command=self._toggle, **kwargs)

    def _toggle(self) -> None:
        if self.grouped is not None:
            for other in self.grouped:
                other.set_selected(other is self)
            return
        self.set_selected(not self.selected)

    def set_selected(self, value: bool) -> None:
        self.selected = value
        self.configure(relief="sunken" if value else "raised")


class MessageLog(tk.Frame):
    """Scrolling transcript. The parent card header is the click target."""

    def __init__(self, master: tk.Misc, **kwargs: Any) -> None:
        super().__init__(master, bg=T.CARD_BG, **kwargs)
        self.lines: list[str] = []
        wrap = tk.Frame(self, bg=T.CARD_BG)
        wrap.pack(fill="both", expand=True)
        self.text = tk.Text(
            wrap,
            height=8,
            wrap="word",
            bg=T.MSG_BG,
            fg=T.LABEL_FG,
            font=("Consolas", 9),
            relief="sunken",
            bd=1,
            state="disabled",
            highlightthickness=0,
        )
        scroll = tk.Scrollbar(wrap, command=self.text.yview)
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
        super().__init__(master, bg=T.CARD_BG, **kwargs)
        self._on = False
        self._canvas = tk.Canvas(
            self, width=18, height=18, bg=T.CARD_BG, highlightthickness=0, cursor="hand2"
        )
        self._canvas.pack(side="left")
        self._dot = self._canvas.create_oval(3, 3, 15, 15, fill=T.LAMP_OFF, outline="#94a3b8")
        self._label = tk.Label(
            self, text="Probe Active", bg=T.CARD_BG, fg=T.LABEL_FG, font=T.FONT, cursor="hand2"
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


def pressable_entry(
    master: tk.Misc,
    logger: Callable[[str], None],
    name: str,
    *,
    textvariable: tk.StringVar | None = None,
    width: int = 8,
) -> tk.Entry:
    entry = tk.Entry(
        master,
        textvariable=textvariable,
        width=width,
        relief="sunken",
        bd=2,
        bg=T.ENTRY_BG,
        font=T.FONT,
        highlightthickness=1,
        highlightcolor=T.HIGHLIGHT,
        highlightbackground=T.BORDER,
    )

    def _down(_event: object | None = None) -> None:
        entry.configure(relief="sunken", bd=3)

    def _up(_event: object | None = None) -> None:
        entry.configure(relief="sunken", bd=2)
        logger(name)

    entry.bind("<ButtonPress-1>", _down, add="+")
    entry.bind("<ButtonRelease-1>", _up, add="+")
    return entry


def pressable_label(
    master: tk.Misc,
    text: str,
    logger: Callable[[str], None],
    name: str,
    **kwargs: Any,
) -> tk.Label:
    kwargs.setdefault("bg", T.DRO_CHIP_BG)
    kwargs.setdefault("fg", T.LABEL_FG)
    kwargs.setdefault("font", T.FONT)
    kwargs.setdefault("relief", "raised")
    kwargs.setdefault("bd", 2)
    kwargs.setdefault("cursor", "hand2")
    kwargs.setdefault("padx", 8)
    kwargs.setdefault("pady", 4)
    lbl = tk.Label(master, text=text, **kwargs)

    def _down(_event: object | None = None) -> None:
        lbl.configure(relief="sunken")

    def _up(_event: object | None = None) -> None:
        lbl.configure(relief="raised")
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
