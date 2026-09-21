"""Live XYZ for the DXF preview.

The preview reads position from a ``PositionSource``. Until GRBL is wired,
``SimulatedPosition`` is the stub. A later DRO / ``?`` status reader should
implement the same ``get_xyz()`` contract.

This module does **not** open USB, talk to GRBL, or own motion.
"""

from __future__ import annotations

from typing import Protocol


class PositionSource(Protocol):
    """Anything that can report current machine XYZ (DRO, ``?``, or a stub)."""

    def get_xyz(self) -> tuple[float, float, float]:
        """Return ``(x, y, z)`` in the same units as the working envelope."""
        ...


class SimulatedPosition:
    """In-memory XYZ stub. Not GRBL. Not USB. Not a motion owner.

    Demo sliders and tests write here. Swap for a DRO/``?`` source later
    without changing the preview widget.
    """

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)

    def set_xyz(self, x: float, y: float, z: float) -> None:
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)

    def get_xyz(self) -> tuple[float, float, float]:
        return (self._x, self._y, self._z)
