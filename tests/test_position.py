"""Tests for the GRBL-free position stub."""

from digitizer.position import SimulatedPosition


def test_simulated_position_roundtrip() -> None:
    pos = SimulatedPosition(1.0, 2.0, 3.0)
    assert pos.get_xyz() == (1.0, 2.0, 3.0)
    pos.set_xyz(4.5, 5.5, 0.25)
    assert pos.get_xyz() == (4.5, 5.5, 0.25)


def test_simulated_position_is_not_a_grbl_client() -> None:
    """Guard: this module must stay a stub (no serial/USB imports in position.py)."""
    import digitizer.position as mod
    import inspect

    source = inspect.getsource(mod)
    assert "serial" not in source.lower()
    assert "usb" not in source.lower() or "Not USB" in source
    assert "grbl" in source.lower()  # mentioned as what it is not
