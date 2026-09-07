"""Test simulation logic and sensor validity functions."""


from fake_sensors import simulation_logic_and_validity
from fake_sensors.simulation_logic_and_validity import ErrorStatus

import pytest


@pytest.mark.parametrize('value, expected', [
    (0.0, 0.0),            # epoch start
    (1.3e9, 1.3),          # 1.3 s, well inside one period
    (59.9e9, 59.9),        # just before the wrap
    (60.0e9, 0.0),         # exactly at the wrap -> resets
    (60.1e9, 0.1),         # just after the wrap
    (144.0e9, 24.0),       # 144 s = 2 full periods + 24 s
])
def test_get_ground_truth_data(value, expected):
    """Verify the sawtooth phase wraps correctly at the ramp period."""
    actual = simulation_logic_and_validity.get_ground_truth_data(value)
    assert actual == pytest.approx(expected)


@pytest.mark.parametrize('value, expected', [
    (0.0, 20.0),           # base temperature at phase zero
    (10.0, 25.0),          # 20 + 0.5 * 10
    (30.0, 35.0),          # midpoint of the ramp
    (60.0, 50.0),          # top of the ramp
])
def test_temperature_conversion(value, expected):
    """Verify counter values map to the expected temperature."""
    actual = simulation_logic_and_validity.temperature_conversion(value)
    assert actual == pytest.approx(expected)


@pytest.mark.parametrize('value1, value2, expected', [
    (None, 50.0, ErrorStatus.DATA_INCONSISTENCY_ERROR),
    (45.2, None, ErrorStatus.DATA_INCONSISTENCY_ERROR),
    (None, None, ErrorStatus.DATA_INCONSISTENCY_ERROR),
    (50.1, 50.0, ErrorStatus.NO_ERROR),
])
def test_is_data_inconsistent(value1, value2, expected):
    """Verify missing sensor data is reported as inconsistent."""
    assert simulation_logic_and_validity.is_data_inconsistent(
        value1, value2) == expected


@pytest.mark.parametrize('value1, value2, expected', [
    # counter 10.0 -> expected temperature 25.0, tolerance 0.5
    (10.0, 25.0, ErrorStatus.NO_ERROR),           # exact agreement
    (10.0, 25.4, ErrorStatus.NO_ERROR),           # inside tolerance, high
    (10.0, 24.6, ErrorStatus.NO_ERROR),           # inside tolerance, low
    (10.0, 25.5, ErrorStatus.NO_ERROR),           # exactly at tolerance
    (10.0, 24.5, ErrorStatus.NO_ERROR),           # exactly at tolerance, low
    (10.0, 25.76, ErrorStatus.PLAUSI_ERROR),       # outside tolerance, high
    (10.0, 24.20, ErrorStatus.PLAUSI_ERROR),       # outside tolerance, low
    (30.0, 20.0, ErrorStatus.PLAUSI_ERROR),       # gross disagreement
])
def test_check_sensor_plausibility(value1, value2, expected):
    """Verify the cross-check flags disagreement beyond tolerance."""
    actual = simulation_logic_and_validity.check_sensor_plausibility(
        value1, value2)
    assert actual == expected


@pytest.mark.parametrize('value, threshold, expected', [
    (49.9, 50.0, ErrorStatus.NO_ERROR),
    (50.0, 50.0, ErrorStatus.NO_ERROR),
    (50.1, 50.0, ErrorStatus.THRESHOLD_ERROR),
])
def test_is_outside_threshold(value, threshold, expected):
    """Verify the threshold boundary uses > and not >=."""
    assert simulation_logic_and_validity.is_outside_threshold(
        value, threshold) == expected
