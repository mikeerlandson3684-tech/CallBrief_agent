"""Paralyzed Hotkeys stub window.

Click a bind box associated with a function. Real chord capture is later.
No GRBL, no USB, no motion.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from digitizer import theme as T
from digitizer.chrome import PillButton, TealCard, pressable_entry

HOTKEY_TARGETS = (
    "Y+",
    "Y-",
    "X+",
    "X-",
    "Z+",
    "Z-",
    "Home",
    "GO TO",
    "ID Circle",
    "OD Circle",
    "Capture Feature",
    "Capture Z Height",
    "Lock Z",
    "Set DXF Origin",
    "FINISH PROBING",
    "New File",
    "Open File",
    "Save",
    "Close",
)


class HotkeysWindow(tk.Toplevel):
    """Stub bind-a-chord window. Boxes log presses; keys are not captured yet."""

    def __init__(
        self,
        master: tk.Misc,
        logger: Callable[[str], None],
        *,
        on_close: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(master)
        self.title("Hotkeys")
        self.configure(bg=T.PAGE_BG)
        self.geometry("720x520")
        self.minsize(560, 420)
        self.logger = logger
        self.bind_boxes: dict[str, tk.Entry] = {}

        card = TealCard(self, "Hotkeys", logger=logger)
        card.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(
            card.body,
            text="Click a box next to a function. The next keyboard input or chord "
            "would bind that command (not captured yet).",
            bg=T.CARD_BG,
            fg=T.MUTED_FG,
            font=T.FONT_SMALL,
            wraplength=660,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        grid = tk.Frame(card.body, bg=T.CARD_BG)
        grid.pack(fill="both", expand=True)
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(3, weight=1)

        split = (len(HOTKEY_TARGETS) + 1) // 2
        for i, name in enumerate(HOTKEY_TARGETS):
            col = 0 if i < split else 2
            row = i if i < split else i - split
            lbl = tk.Label(
                grid,
                text=name,
                bg=T.CARD_BG,
                fg=T.LABEL_FG,
                font=T.FONT,
                anchor="w",
            )
            lbl.grid(row=row, column=col, sticky="w", pady=2, padx=(0, 8))
            box_name = f"{name} bind box"
            entry = pressable_entry(grid, logger, box_name, width=16)
            entry.grid(row=row, column=col + 1, sticky="ew", pady=2, padx=(0, 16))
            self.bind_boxes[name] = entry

        def _close() -> None:
            if on_close is not None:
                on_close()
            else:
                self.destroy()

        close = PillButton(card.body, "Close Hotkeys", logger, command=_close)
        close.pack(pady=(10, 0))
        self.close_btn = close
