"""Live machine position consumed by the preview (no motion ownership)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MachinePosition:
    x: float
    y: float
    z: float
