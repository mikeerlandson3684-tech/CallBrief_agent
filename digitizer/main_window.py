"""Paralyzed main GUI around the existing envelope-scaled DXF preview.

Every control is clickable and shows a press. Clicks log ``'{name} pressed'``.
No GRBL, no USB, no probe cycles, no GO TO motion, no file I/O.
The preview’s Z-circle and grid stay live via SimulatedPosition sliders.
"""

from __future__ import annotations

import argparse
import sys
import tkinter as tk

from digitizer import theme as T
from digitizer.chrome import (
    MessageLog,
    PillButton,
    ProbeLamp,
    TealCard,
    ToggleButton,
    pressable_entry,
    pressable_label,
    write_window_png,
)
from digitizer.hotkeys import HotkeysWindow
from digitizer.machine_config import default_envelope
from digitizer.position import SimulatedPosition
from digitizer.preview import DxfPreview
from digitizer.session import CaptureSession, sample_session


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Paralyzed GRBL digitizer main window (no USB, no motion, no G-code)."
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Start with sample captured ID/OD circles (not a probe cycle).",
    )
    parser.add_argument(
        "--screenshot",
        metavar="PATH",
        help="Write a PNG of the window after first draw, then exit (needs DISPLAY).",
    )
    parser.add_argument(
        "--preview-only",
        action="store_true",
        help="Open the older standalone preview demo instead of the main window.",
    )
    return parser


class MainWindow(tk.Tk):
    """Three-column paralyzed shell matching the mockup card layout."""

    def __init__(self, *, sample: bool = False) -> None:
        super().__init__()
        self.title("CNC Probe System")
        self.configure(bg=T.PAGE_BG)
        self.minsize(1180, 760)
        self.geometry("1280x840")

        env = default_envelope()
        self.env = env
        self.position = SimulatedPosition(
            x=(env.x_min + env.x_max) / 2.0,
            y=(env.y_min + env.y_max) / 2.0,
            z=(env.z_min + env.z_max) / 2.0,
        )
        self.session = sample_session() if sample else CaptureSession()
        self.controls: dict[str, tk.Widget] = {}
        self._hotkeys: HotkeysWindow | None = None
        self._lock_z = False
        self._feature = "id"
        self._increment = tk.StringVar(value=".100\"")
        self._dro_x = tk.StringVar()
        self._dro_y = tk.StringVar()
        self._dro_z = tk.StringVar()
        self._custom_inc = tk.StringVar(value="0.1000")
        self._goto_x = tk.StringVar(value="0.000")
        self._goto_y = tk.StringVar(value="0.000")
        self._goto_z = tk.StringVar(value="0.000")
        self._z_value = tk.StringVar(value="Z Value: 0.000")
        self._diameter = tk.StringVar(value="Measured Diameter: ---")
        self._jog_speed = tk.DoubleVar(value=0.0)
        self._speed_readout = tk.StringVar(value="0.000 in/sec")

        self._build()
        self._refresh_dro()
        self.after(50, self._poll_dro)

    def log(self, name: str) -> None:
        self.messages.append(f"{name} pressed")

    def click_control(self, name: str) -> None:
        """Test helper: press a registered control so it logs ``'{name} pressed'``."""
        widget = self.controls[name]
        if isinstance(widget, (tk.Button, tk.Radiobutton)):
            widget.invoke()
        elif isinstance(widget, ProbeLamp):
            widget._release()  # noqa: SLF001 — same path as mouse release
        elif isinstance(widget, TealCard):
            widget.title_label.event_generate("<Button-1>")
        elif isinstance(widget, MessageLog):
            self.log("Messages")
        else:
            widget.event_generate("<ButtonPress-1>")
            widget.event_generate("<ButtonRelease-1>")
        self.update_idletasks()
        self.update()

    def _remember(self, name: str, widget: tk.Widget) -> tk.Widget:
        self.controls[name] = widget
        return widget

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._build_tabs()
        self._build_toolbar()

        cols = tk.Frame(self, bg=T.PAGE_BG)
        cols.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 6))
        cols.columnconfigure(0, weight=0, minsize=260)
        cols.columnconfigure(1, weight=1, minsize=380)
        cols.columnconfigure(2, weight=1, minsize=380)
        cols.rowconfigure(0, weight=1)

        left = tk.Frame(cols, bg=T.PAGE_BG)
        center = tk.Frame(cols, bg=T.PAGE_BG)
        right = tk.Frame(cols, bg=T.PAGE_BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        center.grid(row=0, column=1, sticky="nsew", padx=(0, 8))
        right.grid(row=0, column=2, sticky="nsew")
        for col in (left, center, right):
            col.columnconfigure(0, weight=1)

        self._build_left(left)
        self._build_center(center)
        self._build_right(right)
        self._build_sim_bar()

    def _build_tabs(self) -> None:
        bar = tk.Frame(self, bg=T.PAGE_BG)
        bar.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
        self._tab_main = PillButton(bar, "Main", self.log, command=self._show_main)
        self._tab_main.configure(relief="sunken")
        self._tab_main.pack(side="left")
        self._tab_hotkeys = PillButton(bar, "Hotkeys", self.log, command=self._open_hotkeys)
        self._tab_hotkeys.pack(side="left", padx=(6, 0))
        self._remember("Main", self._tab_main)
        self._remember("Hotkeys", self._tab_hotkeys)

    def _show_main(self) -> None:
        self._tab_main.configure(relief="sunken")
        self._tab_hotkeys.configure(relief="raised")

    def _open_hotkeys(self) -> None:
        self._tab_hotkeys.configure(relief="sunken")
        self._tab_main.configure(relief="raised")
        if self._hotkeys is not None and self._hotkeys.winfo_exists():
            self._hotkeys.lift()
            self._hotkeys.focus_set()
            return
        self._hotkeys = HotkeysWindow(self, self.log, on_close=self._close_hotkeys)
        self._hotkeys.protocol("WM_DELETE_WINDOW", self._close_hotkeys)

    def _close_hotkeys(self) -> None:
        if self._hotkeys is not None:
            self._hotkeys.destroy()
            self._hotkeys = None
        self._show_main()

    def _build_toolbar(self) -> None:
        bar = tk.Frame(self, bg=T.PAGE_BG)
        bar.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        init = PillButton(
            bar,
            "Initialized",
            self.log,
            bg=T.GREEN,
            fg=T.GREEN_FG,
            activebackground=T.GREEN_ACTIVE,
            activeforeground=T.GREEN_FG,
            font=T.FONT_BOLD,
            padx=16,
        )
        init.pack(side="left")
        self._remember("Initialized", init)

        for name in ("New File", "Open File", "Save", "Close", "Settings", "Calibration"):
            btn = PillButton(bar, name, self.log)
            btn.pack(side="left", padx=(8, 0))
            self._remember(name, btn)

    def _build_left(self, parent: tk.Frame) -> None:
        parent.rowconfigure(2, weight=1)

        dro = TealCard(parent, "DRO Position", logger=self.log)
        dro.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self._build_dro(dro.body)

        status = TealCard(parent, "Status", logger=self.log)
        status.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self._build_status(status.body)

        jog = TealCard(parent, "Jog", logger=self.log)
        jog.grid(row=2, column=0, sticky="nsew")
        self._build_jog(jog.body)

    def _build_dro(self, body: tk.Frame) -> None:
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        axes = (("X", self._dro_x), ("Y", self._dro_y), ("Z", self._dro_z))
        for i, (axis, var) in enumerate(axes):
            chip = tk.Frame(body, bg=T.DRO_CHIP_BG, highlightbackground=T.BORDER, highlightthickness=1)
            chip.grid(row=i, column=0, sticky="ew", pady=3, padx=(0, 8))
            pressable_label(
                chip, f"{axis}:", self.log, f"DRO {axis}", bg=T.DRO_CHIP_BG, font=T.FONT_DRO, bd=0, relief="flat"
            ).pack(side="left", padx=(6, 4))
            val = tk.Label(
                chip,
                textvariable=var,
                bg=T.DRO_CHIP_BG,
                fg=T.LABEL_FG,
                font=T.FONT_DRO,
                width=8,
                anchor="w",
                cursor="hand2",
                relief="raised",
                bd=1,
            )
            val.pack(side="left", padx=(0, 6), pady=4)

            def _down(_e: object, w: tk.Label = val) -> None:
                w.configure(relief="sunken")

            def _up(_e: object, w: tk.Label = val, name: str = f"DRO {axis}") -> None:
                w.configure(relief="raised")
                self.log(name)

            val.bind("<ButtonPress-1>", _down, add="+")
            val.bind("<ButtonRelease-1>", _up, add="+")
            self._remember(f"DRO {axis}", val)

        goto = tk.Frame(body, bg=T.CARD_BG)
        goto.grid(row=0, column=1, rowspan=3, sticky="n")
        tk.Label(goto, text="GO TO", bg=T.CARD_BG, fg=T.MUTED_FG, font=T.FONT_SMALL).pack()
        for axis, var in (("X", self._goto_x), ("Y", self._goto_y), ("Z", self._goto_z)):
            row = tk.Frame(goto, bg=T.CARD_BG)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=axis, bg=T.CARD_BG, fg=T.MUTED_FG, font=T.FONT_SMALL, width=2).pack(side="left")
            entry = pressable_entry(row, self.log, f"GO TO {axis}", textvariable=var, width=8)
            entry.pack(side="left")
            self._remember(f"GO TO {axis}", entry)
        go = PillButton(goto, "GO TO", self.log)
        go.pack(pady=(6, 0), fill="x")
        self._remember("GO TO", go)

    def _build_status(self, body: tk.Frame) -> None:
        for key, value in (("HOMED", "YES"), ("STATE", "READY")):
            row = tk.Frame(body, bg=T.CARD_BG)
            row.pack(fill="x", pady=2)
            pressable_label(
                row, f"{key}:", self.log, key, bg=T.CARD_BG, bd=1, width=10, anchor="w"
            ).pack(side="left")
            val = pressable_label(row, value, self.log, key, bg=T.CARD_BG, bd=1, width=8, anchor="w")
            val.pack(side="left", padx=8)
            self._remember(key, val)

    def _build_jog(self, body: tk.Frame) -> None:
        pad = tk.Frame(body, bg=T.CARD_BG)
        pad.pack()
        pad.columnconfigure(0, weight=1)
        pad.columnconfigure(1, weight=1)
        pad.columnconfigure(2, weight=1)

        def _jog(text: str, row: int, col: int, **kw: object) -> PillButton:
            btn = PillButton(pad, text, self.log, width=int(kw.get("width", 4)))
            if "font" in kw:
                btn.configure(font=kw["font"])  # type: ignore[arg-type]
            btn.grid(row=row, column=col, padx=4, pady=3, sticky="nsew")
            self._remember(text, btn)
            return btn

        _jog("Y+", 0, 1)
        _jog("X-", 1, 0)
        _jog("Home", 1, 1, font=T.FONT_JOG_HOME, width=6)
        _jog("X+", 1, 2)
        _jog("Y-", 2, 1)
        _jog("Z+", 3, 1)
        _jog("Z-", 4, 1)

        speed_row = tk.Frame(body, bg=T.CARD_BG)
        speed_row.pack(fill="x", pady=(12, 0))
        tk.Label(
            speed_row, text="Jog Speed", bg=T.CARD_BG, fg=T.LABEL_FG, font=T.FONT, cursor="hand2"
        ).pack(anchor="w")

        def _speed_press(_event: object | None = None) -> None:
            self.log("Jog Speed")

        scale = tk.Scale(
            speed_row,
            from_=0.0,
            to=10.0,
            resolution=0.001,
            orient="horizontal",
            variable=self._jog_speed,
            showvalue=0,
            bg=T.CARD_BG,
            highlightthickness=0,
            troughcolor="#99e6dd",
            sliderrelief="raised",
            bd=2,
            command=lambda _v: self._speed_readout.set(f"{self._jog_speed.get():.3f} in/sec"),
        )
        scale.pack(fill="x")
        scale.bind("<ButtonPress-1>", _speed_press, add="+")
        self._remember("Jog Speed", scale)
        tk.Label(
            speed_row,
            textvariable=self._speed_readout,
            bg=T.CARD_BG,
            fg=T.MUTED_FG,
            font=T.FONT_SMALL,
        ).pack(anchor="e")

    def _build_center(self, parent: tk.Frame) -> None:
        feature = TealCard(parent, "Feature", logger=self.log)
        feature.pack(fill="x", pady=(0, 8))
        row = tk.Frame(feature.body, bg=T.CARD_BG)
        row.pack(fill="x")
        self._id_btn = ToggleButton(row, "ID Circle", self.log)
        self._od_btn = ToggleButton(row, "OD Circle", self.log)
        group = [self._id_btn, self._od_btn]
        self._id_btn.grouped = group
        self._od_btn.grouped = group
        self._id_btn.set_selected(True)
        self._id_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))
        self._od_btn.pack(side="left", expand=True, fill="x")
        self._remember("ID Circle", self._id_btn)
        self._remember("OD Circle", self._od_btn)
        tk.Label(
            feature.body,
            text="ID circle and OD circle are separate routines.",
            bg=T.CARD_BG,
            fg=T.MUTED_FG,
            font=T.FONT_SMALL,
            wraplength=360,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(6, 0))

        capture = TealCard(parent, "Capture", logger=self.log)
        capture.pack(fill="x", pady=(0, 8))
        cap_row = tk.Frame(capture.body, bg=T.CARD_BG)
        cap_row.pack(fill="x")
        self.lamp = ProbeLamp(cap_row, self.log)
        self.lamp.pack(side="right")
        self._remember("Probe Active", self.lamp)
        cap_btn = PillButton(capture.body, "Capture Feature", self.log, pady=10)
        cap_btn.pack(fill="x", pady=(8, 0))
        self._remember("Capture Feature", cap_btn)

        zcard = TealCard(parent, "Z Control", logger=self.log)
        zcard.pack(fill="x", pady=(0, 8))
        zrow = tk.Frame(zcard.body, bg=T.CARD_BG)
        zrow.pack(fill="x")
        zrow.columnconfigure(0, weight=1)
        zrow.columnconfigure(1, weight=1)
        cap_z = PillButton(zrow, "Capture Z Height", self.log, pady=10)
        cap_z.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        lock = ToggleButton(zrow, "Lock Z", self.log, pady=10)
        lock.grid(row=0, column=1, sticky="ew")
        self._remember("Capture Z Height", cap_z)
        self._remember("Lock Z", lock)
        zval = pressable_label(
            zcard.body, "", self.log, "Z Value", textvariable=self._z_value, bg=T.CARD_BG, bd=1
        )
        zval.pack(pady=(8, 0))
        self._remember("Z Value", zval)

        datum = TealCard(parent, "Datum", logger=self.log)
        datum.pack(fill="x", pady=(0, 8))
        origin = PillButton(datum.body, "Set DXF Origin", self.log, pady=8)
        origin.pack()
        self._remember("Set DXF Origin", origin)

        inc = TealCard(parent, "Incremental", logger=self.log)
        inc.pack(fill="x", pady=(0, 8))
        tk.Label(
            inc.body,
            text="Incremental Jog (hold Ctrl, then jog). Predetermined steps. Not GO TO.",
            bg=T.CARD_BG,
            fg=T.MUTED_FG,
            font=T.FONT_SMALL,
            wraplength=360,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(0, 6))
        radios = tk.Frame(inc.body, bg=T.CARD_BG)
        radios.pack(fill="x")
        for label in ('.001"', '.010"', '.100"', "Custom"):
            rb = tk.Radiobutton(
                radios,
                text=label,
                value=label,
                variable=self._increment,
                bg=T.CARD_BG,
                font=T.FONT,
                activebackground=T.CARD_BG,
                highlightthickness=0,
                command=lambda n=label: self.log(n),
            )
            rb.pack(side="left", padx=(0, 10))
            self._remember(label, rb)
        custom = pressable_entry(
            inc.body, self.log, "Custom increment", textvariable=self._custom_inc, width=16
        )
        custom.pack(anchor="w", pady=(6, 0))
        self._remember("Custom increment", custom)

        diam = pressable_label(
            parent,
            "",
            self.log,
            "Measured Diameter",
            textvariable=self._diameter,
            bg=T.PAGE_BG,
            bd=1,
            anchor="w",
        )
        diam.pack(fill="x", pady=(4, 0))
        self._remember("Measured Diameter", diam)

    def _build_right(self, parent: tk.Frame) -> None:
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

        preview_card = TealCard(parent, "DXF Preview", logger=self.log)
        preview_card.grid(row=0, column=0, sticky="nsew", pady=(0, 8))

        self.preview = DxfPreview(
            preview_card.body,
            position_source=self.position,
            session=self.session,
            show_header=False,
        )
        self.preview.pack(fill="both", expand=True)
        self._remember("DXF Preview", preview_card)

        finish = PillButton(parent, "FINISH PROBING", self.log, pady=8)
        finish.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        self._remember("FINISH PROBING", finish)

        discard = PillButton(parent, "Discard Since Last Save", self.log, pady=8)
        discard.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        self._remember("Discard Since Last Save", discard)

        msg_card = TealCard(parent, "Messages", logger=self.log)
        msg_card.grid(row=3, column=0, sticky="ew")
        self.messages = MessageLog(msg_card.body)
        self.messages.pack(fill="both", expand=True)
        self.messages.append("Paralyzed GUI — clicks log here. No GRBL, USB, motion, or file I/O.")
        self._remember("Messages", self.messages)

    def _build_sim_bar(self) -> None:
        """Live SimulatedPosition sliders so the preview Z-circle/grid stay alive."""
        bar = tk.Frame(self, bg=T.CARD_BG, highlightbackground=T.BORDER, highlightthickness=1)
        bar.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        tk.Label(
            bar,
            text="Simulated position (not GRBL, not USB)",
            bg=T.CARD_BG,
            fg=T.MUTED_FG,
            font=T.FONT_SMALL,
        ).pack(side="left", padx=(8, 10))

        self._x_var = tk.DoubleVar(value=self.position.get_xyz()[0])
        self._y_var = tk.DoubleVar(value=self.position.get_xyz()[1])
        self._z_var = tk.DoubleVar(value=self.position.get_xyz()[2])

        def _push(_event: object | None = None) -> None:
            self.position.set_xyz(self._x_var.get(), self._y_var.get(), self._z_var.get())

        def _axis(label: str, var: tk.DoubleVar, lo: float, hi: float) -> None:
            tk.Label(bar, text=label, bg=T.CARD_BG, font=T.FONT_SMALL).pack(side="left")
            scale = tk.Scale(
                bar,
                from_=lo,
                to=hi,
                resolution=0.001,
                orient="horizontal",
                variable=var,
                showvalue=0,
                bg=T.CARD_BG,
                highlightthickness=0,
                length=140,
                command=lambda _v: _push(),
            )
            scale.pack(side="left", padx=(2, 8))

        _axis("X", self._x_var, self.env.x_min, self.env.x_max)
        _axis("Y", self._y_var, self.env.y_min, self.env.y_max)
        _axis("Z", self._z_var, self.env.z_min, self.env.z_max)

        def show_empty() -> None:
            self.session.clear()
            self.preview.set_session(self.session)

        def show_sample() -> None:
            filled = sample_session()
            self.session.circles = filled.circles
            self.session.z_heights = filled.z_heights
            self.session.dxf_origin = filled.dxf_origin
            self.preview.set_session(self.session)

        empty = PillButton(bar, "Empty file", self.log, command=show_empty)
        empty.pack(side="left", padx=(8, 0))
        sample = PillButton(bar, "Sample captures", self.log, command=show_sample)
        sample.pack(side="left", padx=8)
        self._remember("Empty file", empty)
        self._remember("Sample captures", sample)

    def _poll_dro(self) -> None:
        self._refresh_dro()
        try:
            self.after(50, self._poll_dro)
        except tk.TclError:
            pass

    def _refresh_dro(self) -> None:
        x, y, z = self.position.get_xyz()
        self._dro_x.set(f"{x:.3f}")
        self._dro_y.set(f"{y:.3f}")
        self._dro_z.set(f"{z:.3f}")


def build_window(*, sample: bool = False) -> MainWindow:
    return MainWindow(sample=sample)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.preview_only:
        from digitizer.demo_app import main as preview_main

        raw = list(argv) if argv is not None else sys.argv[1:]
        filtered = [a for a in raw if a != "--preview-only"]
        return preview_main(filtered)
    root = build_window(sample=args.sample)
    if args.screenshot:
        root.after(400, lambda: (write_window_png(root, args.screenshot), root.destroy()))
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
