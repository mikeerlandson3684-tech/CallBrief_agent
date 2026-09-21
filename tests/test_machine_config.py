"""Tests for placeholder envelope defaults."""

from digitizer.machine_config import (
    PLACEHOLDER_UNITS,
    PLACEHOLDER_X_MAX,
    PLACEHOLDER_X_MIN,
    PLACEHOLDER_Y_MAX,
    PLACEHOLDER_Y_MIN,
    PLACEHOLDER_Z_MAX,
    PLACEHOLDER_Z_MIN,
    default_envelope,
    envelope_disclaimer,
)


def test_placeholder_envelope_is_obvious_and_labeled() -> None:
    env = default_envelope()
    assert env.x_min == PLACEHOLDER_X_MIN
    assert env.x_max == PLACEHOLDER_X_MAX
    assert env.y_min == PLACEHOLDER_Y_MIN
    assert env.y_max == PLACEHOLDER_Y_MAX
    assert env.z_min == PLACEHOLDER_Z_MIN
    assert env.z_max == PLACEHOLDER_Z_MAX
    assert env.units == PLACEHOLDER_UNITS
    assert env.x_span() == 12.0
    assert env.y_span() == 12.0
    assert env.z_span() == 4.0
    text = envelope_disclaimer(env)
    assert "Placeholder envelope" in text
    assert "not measured" in text
    assert "Settings later" in text
